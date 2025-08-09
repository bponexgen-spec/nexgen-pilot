import os, json, uuid, time, requests
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NexGen BPO - Pilot (Co-Founder Edition)")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Serve static files
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

SUBMISSIONS_FILE = os.path.join("static", "submissions.json")
if not os.path.exists(SUBMISSIONS_FILE):
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump([], f)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE", "Bella")

def elevenlabs_tts(text, voice=ELEVENLABS_VOICE):
    if not ELEVENLABS_API_KEY:
        return None
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type":"application/json"}
    payload = {"text": text, "voice_settings":{"stability":0.4,"similarity_boost":0.75}}
    try:
        r = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
        if r.status_code == 200:
            out = f"static/voice_{uuid.uuid4().hex}.mp3"
            with open(out, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)
            return out
    except Exception:
        return None
    return None

@app.post("/voice_demo")
async def voice_demo(scenario: str = Form(...), language: str = Form("en")):
    scenarios = {
        "outbound_dutch": "Goedemiddag, ik bel namens NexGen om een afspraak in te plannen voor een gratis consult over onze AI-diensten.",
        "inbound_dutch": "Welkom bij NexGen klantenservice. Hoe kan ik u vandaag van dienst zijn?",
        "appointment_plumber_nl": "Goedemiddag, ik bel namens Jans Loodgietersbedrijf om een afspraak in te plannen voor een gratis offerte.",
        "sales_closer_en": "Good afternoon, I am calling from NexGen Realty to follow up and discuss the offer.",
        "appointment_realestate_en": "Good afternoon, I'm calling from GreenKey Realty to schedule a private viewing for the property you inquired about."
    }
    text = scenarios.get(scenario, "Hello from NexGen demo")
    audio_path = elevenlabs_tts(text)
    return JSONResponse({"audio_url": f"/{audio_path}" if audio_path else None, "transcript": text, "note": None if audio_path else "No TTS key configured"})

@app.post("/contact")
async def contact(name: str = Form(...), email: str = Form(...), plan: str = Form(None), message: str = Form(None)):
    entry = {"id": str(uuid.uuid4()), "name": name, "email": email, "plan": plan, "message": message, "ts": time.time()}
    try:
        with open(SUBMISSIONS_FILE, "r+") as f:
            try:
                data = json.load(f)
            except:
                data = []
            data.append(entry)
            f.seek(0); json.dump(data, f, indent=2); f.truncate()
        return JSONResponse({"status":"ok","detail":"Submission received"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
