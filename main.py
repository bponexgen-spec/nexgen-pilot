import os
import json
import uuid
import time
import requests
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NexGen BPO - Pilot (Co-Founder Edition)")

# Allow all origins for testing (can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, JS, images)
if not os.path.exists("static"):
    os.makedirs("static")

# Mount the static folder for assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root
@app.get("/")
async def serve_home():
    return FileResponse("index.html")

# File to store submissions
SUBMISSIONS_FILE = os.path.join("static", "submissions.json")
if not os.path.exists(SUBMISSIONS_FILE):
    with open(SUBMISSIONS_FILE, "w") as f:
        json.dump([], f)

# ElevenLabs API settings
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE", "Bella")

def elevenlabs_tts(text, voice=ELEVENLABS_VOICE):
    """Send text to ElevenLabs API and return audio bytes"""
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
            return r.content
    except Exception as e:
        print("Error calling ElevenLabs:", e)
    return None

@app.post("/submit")
async def submit_form(name: str = Form(...), message: str = Form(...)):
    """Store submissions in a JSON file"""
    data = {"id": str(uuid.uuid4()), "name": name, "message": message, "timestamp": time.time()}
    with open(SUBMISSIONS_FILE, "r+") as f:
        submissions = json.load(f)
        submissions.append(data)
        f.seek(0)
        json.dump(submissions, f, indent=2)
    return JSONResponse({"status": "success", "data": data})

@app.post("/tts")
async def tts_endpoint(text: str = Form(...)):
    """Convert text to speech using ElevenLabs"""
    audio_data = elevenlabs_tts(text)
    if not audio_data:
        raise HTTPException(status_code=500, detail="TTS failed or API key missing")
    filename = f"static/{uuid.uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(audio_data)
    return JSONResponse({"status": "success", "file": filename})



