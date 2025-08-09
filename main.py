import os, json, uuid, time, requests
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="NexGen BPO - Pilot (Co-Founder Edition)")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Serve static files
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

SUBMISSIONS_FILE = os.path.join("static", "submissions.json")
if not os.path.exists(SUBMISSIONS_FILE):
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump([], f)

# Environment variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE", "Bella")

# ElevenLabs text-to-speech
def elevenlabs_tts(text, voice=ELEVENLABS_VOICE):
    if not ELEVENLABS_API_KEY:
        return None
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.75}
    }
    try:
        r = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
        if r.status_code == 200:
            audio_path = os.path.join("static", f"{uuid.uuid4()}.mp3")
            with open(audio_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return f"/static/{os.path.basename(audio_path)}"
    except Exception as e:
        print(f"Error: {e}")
    return None

# API route for form submission
@app.post("/submit")
async def submit(name: str = Form(...), message: str = Form(...)):
    new_entry = {"id": str(uuid.uuid4()), "name": name, "message": message, "time": time.time()}
    try:
        with open(SUBMISSIONS_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(new_entry)
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump(data, f)

    # Generate audio
    audio_file = elevenlabs_tts(f"Hello {name}, thank you for your message!")
    return JSONResponse(content={"status": "success", "audio": audio_file})

# Root homepage
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head><title>NexGen BPO Pilot</title></head>
    <body style="text-align:center;font-family:sans-serif;">
        <h1>🚀 NexGen BPO Pilot is Live</h1>
        <p>Your AI Agent platform is running!</p>
        <p><a href="/static">View static files</a></p>
    </body>
    </html>
    """

# Start server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
