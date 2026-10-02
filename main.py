from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "AI Agent Running", "message": "Server Render Aktif!"}

# Endpoint khusus agar server tidak "tidur" saat di-ping oleh UptimeRobot
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Contoh endpoint untuk memanggil AI (bisa disesuaikan nanti)
@app.post("/chat")
def chat(prompt: str):
    # Ambil API Key dari Environment Variable Render
    api_key = os.getenv("GEMINI_API_KEY") 
    
    # Logika AI Agent kamu ditulis di sini
    return {"response": f"Agent memproses: {prompt}"}
