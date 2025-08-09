import os
import json
import uuid
import time
import requests
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(title="NexGen BPO - Pilot (Co-Founder Edition)")

# Allow CORS for all origins (for testing, you can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Submissions file path
SUBMISSIONS_FILE = os.path.join("static", "submissions.json")
if not os.path.exists(SUBMISSIONS_FILE):
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump([], f)

# Load environment variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE", "Bella")

# ElevenLabs TTS function
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
            return audio_path
        else:
            return None
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

# API route for TTS
@app.post("/api/tts")
async def generate_tts(text: str = Form(...)):
    audio_file = elevenlabs_tts(text)
    if not audio_file:
        raise HTTPException(status_code=500, detail="TTS generation failed.")
    return {"audio_url": f"/{audio_file}"}

# API route to store submissions
@app.post("/api/submit")
async def submit_data(name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    new_entry = {"name": name, "email": email, "message": message, "timestamp": time.time()}
    with open(SUBMISSIONS_FILE, "r+") as f:
        data = json.load(f)
        data.append(new_entry)
        f.seek(0)
        json.dump(data, f, indent=2)
    return JSONResponse(content={"status": "success", "message": "Data saved successfully."})

# Run locally or on Render
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)


