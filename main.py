import os
import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AI Agent - Sup")

# ==========================================
# 1. MOUNT STATIC FILES (3D OFFICE)
# ==========================================
STATIC_DIR = "static"

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/api/models")
async def list_models():
    """Mengecek apakah ada file glb lokal di folder static/models"""
    models_dir = os.path.join(STATIC_DIR, "models")
    glb_files = []
    
    if os.path.exists(models_dir):
        for root, _, files in os.walk(models_dir):
            for file in files:
                if file.lower().endswith(".glb"):
                    rel_path = os.path.relpath(os.path.join(root, file), STATIC_DIR)
                    url_path = f"/static/{rel_path.replace(os.sep, '/')}"
                    glb_files.append(url_path)
    
    return JSONResponse(content={"models": glb_files})

@app.get("/", response_class=HTMLResponse)
async def serve_3d_office():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>File index.html tidak ditemukan di folder static/</h1>"

# ==========================================
# 2. AI AGENT & WEBHOOK CONFIGURATION
# ==========================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
FONNTE_TOKEN = os.getenv("FONNTE_TOKEN")
TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID")

SYSTEM_PROMPT = """
Kamu adalah AI Agent - Sup, asisten cerdas dan responsif.
Tugas utama kamu adalah membantu anggota grup WhatsApp dalam:
1. Menjawab pertanyaan seputar operasional, data, dan umum secara singkat dan tepat.
2. Membantu mengekstrak data transaksi atau rincian tagihan (Split Bill).
3. Tetap bersikap sopan, membantu, dan profesional.
"""

def send_whatsapp_message(target: str, message: str):
    if not FONNTE_TOKEN:
        return
    url = "https://api.fonnte.com/send"
    headers = {"Authorization": FONNTE_TOKEN}
    payload = {"target": target, "message": message}
    try:
        requests.post(url, headers=headers, data=payload)
    except Exception as e:
        print(f"[FONNTE ERROR] {e}")

def ask_openrouter(prompt_text: str) -> str:
    if not OPENROUTER_API_KEY:
        return "Maaf, API Key OpenRouter belum dikonfigurasi."
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "google/gemini-2.0-flash-lite-001",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_text}
        ]
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        res_json = res.json()
        if "choices" in res_json and len(res_json["choices"]) > 0:
            return res_json["choices"][0]["message"]["content"]
        return "Maaf, AI sedang tidak dapat merespons saat ini."
    except Exception as e:
        return f"Terjadi kesalahan: {e}"

@app.post("/webhook")
async def fonnte_webhook(request: Request):
    try:
        data = await request.form()
        if not data:
            data = await request.json()
            
        sender = data.get("sender")
        message = data.get("message")
        group_id = data.get("id") or data.get("group")

        if TARGET_GROUP_ID and str(group_id) != str(TARGET_GROUP_ID):
            return JSONResponse(content={"status": "ignored"})

        if message:
            ai_reply = ask_openrouter(message)
            reply_target = group_id if group_id else sender
            send_whatsapp_message(reply_target, ai_reply)

        return JSONResponse(content={"status": "success"})
    except Exception as e:
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=500)
