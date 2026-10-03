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
# Memastikan folder /static/ terhubung agar index.html & file .glb dapat diakses
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Route Tampilan Utama (3D Virtual Office)
@app.get("/", response_class=HTMLResponse)
async def serve_3d_office():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>File index.html tidak ditemukan di folder static/</h1>"

# ==========================================
# 2. AI AGENT CONFIGURATION & SYSTEM PROMPT
# ==========================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
FONNTE_TOKEN = os.getenv("FONNTE_TOKEN")
TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID")  # ID Grup WhatsApp yang diizinkan

SYSTEM_PROMPT = """
Kamu adalah AI Agent - Sup, asisten cerdas dan responsif.
Tugas utama kamu adalah membantu anggota grup WhatsApp dalam:
1. Menjawab pertanyaan seputar operasional, data, dan umum secara singkat dan tepat.
2. Membantu mengekstrak data transaksi atau rincian tagihan (Split Bill) dari teks pesan atau foto struk yang dikirimkan.
3. Tetap bersikap sopan, membantu, dan profesional.
"""

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def send_whatsapp_message(target: str, message: str):
    """Fungsi untuk mengirim balasan pesan via Fonnte API"""
    if not FONNTE_TOKEN:
        print("[ERROR] FONNTE_TOKEN tidak ditemukan di environment variable.")
        return

    url = "https://api.fonnte.com/send"
    headers = {"Authorization": FONNTE_TOKEN}
    payload = {
        "target": target,
        "message": message
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        print(f"[FONNTE RESPONSE] {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[FONNTE ERROR] Gagal mengirim pesan: {e}")

def ask_openrouter(prompt_text: str) -> str:
    """Fungsi untuk memanggil OpenRouter LLM API"""
    if not OPENROUTER_API_KEY:
        return "Maaf, API Key OpenRouter belum dikonfigurasi."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "google/gemini-2.0-flash-lite-001",  # Atau model pilihan kamu
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
        print(f"[OPENROUTER ERROR] {e}")
        return "Terjadi kesalahan saat menghubungkan ke AI Service."

# ==========================================
# 4. WEBHOOK FONNTE (WHATSAPP AGENT)
# ==========================================
@app.post("/webhook")
async def fonnte_webhook(request: Request):
    try:
        data = await request.form()
        if not data:
            data = await request.json()
            
        sender = data.get("sender")
        message = data.get("message")
        group_id = data.get("id") or data.get("group")  # Mendapatkan ID grup jika dari WA Group
        
        print(f"[WEBHOOK RECEIVED] From: {sender} | Group: {group_id} | Message: {message}")

        # Batasi respons hanya untuk grup tertentu jika TARGET_GROUP_ID dikonfigurasi
        if TARGET_GROUP_ID and str(group_id) != str(TARGET_GROUP_ID):
            print(f"[IGNORED] Pesan berasal dari grup/pengirim yang tidak terdaftar: {group_id}")
            return JSONResponse(content={"status": "ignored"})

        if message:
            # Panggil OpenRouter untuk mendapatkan balasan AI
            ai_reply = ask_openrouter(message)
            
            # Kirim balasan kembali ke WhatsApp
            reply_target = group_id if group_id else sender
            send_whatsapp_message(reply_target, ai_reply)

        return JSONResponse(content={"status": "success"})
    except Exception as e:
        print(f"[WEBHOOK ERROR] {e}")
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=500)
