from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests

app = FastAPI(title="Paparaka AI Agent")

# Model data untuk menerima input JSON
class ChatRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return {"status": "AI Agent Running", "message": "Server Agent Aktif!"}

# Endpoint khusus untuk mencegah server sleep di Render (dipakai UptimeRobot)
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Endpoint utama untuk chat dengan Qwen via OpenRouter
@app.post("/chat")
def chat(request: ChatRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="OPENROUTER_API_KEY belum dipasang di Environment Variables Render!"
        )
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen/qwen-2.5-coder-32b-instruct:free",
        "messages": [
            {
                "role": "system", 
                "content": "Kamu adalah AI Agent serbaguna milik Paparaka. Jawablah dengan jelas, membantu, dan menggunakan bahasa Indonesia yang baik."
            },
            {
                "role": "user", 
                "content": request.prompt
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            ai_reply = data["choices"][0]["message"]["content"]
            return {"status": "success", "response": ai_reply}
        else:
            return {"status": "error", "details": data}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
