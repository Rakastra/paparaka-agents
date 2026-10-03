import os
import requests
from fastapi import FastAPI, Request

app = FastAPI(title="AI Agent - Sup")

# ==========================================
# KONFIGURASI BOT & GRUP
# ==========================================
# ID Grup khusus yang diizinkan untuk di-rekap & direspon oleh bot
TARGET_GROUP_ID = "120363387413264013@g.us"

# Kata pemicu pesan di grup
TRIGGERS = ["!rekap", "!bot", "!tanya", "!sup"]


@app.get("/")
def home():
    return {"status": "AI Agent Running", "message": "Server Vercel Aktif!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Endpoint manual untuk uji coba di /docs
@app.post("/chat")
def chat(request_data: dict):
    prompt = request_data.get("prompt", "")
    if not prompt:
        return {"status": "error", "message": "Prompt tidak boleh kosong"}
    
    system_prompt = (
        "Kamu adalah AI Agent - Sup, asisten cerdas yang responsif dan fleksibel. "
        "Jawablah pertanyaan dengan ramah, singkat, dan informatif."
    )
    reply = ask_openrouter(prompt, system_prompt)
    return {"status": "success", "response": reply}


# Fungsi panggil OpenRouter API
def ask_openrouter(user_message: str, system_prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: API Key OpenRouter belum terpasang di Vercel Environment Variables."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        if response.status_code == 200:
            return data["choices"][0]["message"]["content"]
        else:
            error_msg = data.get("error", {}).get("message", "Terjadi kesalahan pada model API.")
            return f"Maaf, AI mengalami kendala: {error_msg}"
    except Exception as e:
        return f"Error koneksi ke OpenRouter: {str(e)}"


# Fungsi kirim pesan balik via Fonnte API
def send_fonnte_message(target: str, text_message: str):
    fonnte_token = os.getenv("FONNTE_TOKEN")
    if not fonnte_token:
        print("[FONNTE ERROR] FONNTE_TOKEN belum diset di Vercel!")
        return

    fonnte_url = "https://api.fonnte.com/send"
    payload = {
        "target": target,
        "message": text_message
    }
    headers = {
        "Authorization": fonnte_token
    }
    
    try:
        res = requests.post(fonnte_url, data=payload, headers=headers, timeout=15)
        print("[FONNTE RESPONSE]", res.text)
    except Exception as e:
        print("[FONNTE SEND ERROR]", str(e))


# Webhook untuk menerima pesan dari Fonnte
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.form()
    data_dict = dict(data)
    
    sender = data_dict.get("sender", "")      # Nomor pengirim
    message = data_dict.get("message", "").strip()  # Isi pesan
    group_id = data_dict.get("group", "")    # ID Grup dari Fonnte

    print(f"[INCOMING MSG] Sender: {sender} | Group: {group_id} | Msg: {message}")

    if not message:
        return {"status": "ignored", "reason": "Pesan kosong"}

    # Hanya proses pesan jika berasal dari grup yang sudah ditentukan (TARGET_GROUP_ID)
    if group_id == TARGET_GROUP_ID:
        # Cek apakah pesan diawali kata pemicu !rekap
        if message.lower().startswith("!rekap"):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, admin rekapitulasi di grup WhatsApp. "
                "Tugasmu adalah menganalisis teks daftar pesanan atau data dari anggota grup, lalu menyusun "
                "rekapannya dengan rapi (bentuk daftar/tabel ringkas beserta total kuantitas/harga jika ada). "
                "Gunakan bahasa Indonesia yang sopan, jelas, dan profesional."
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(group_id, ai_reply)
            return {"status": "processed", "type": "group_rekap"}
        
        # Cek apakah pesan diawali pemicu lainnya (!bot, !tanya, !sup)
        elif any(message.lower().startswith(trig) for trig in TRIGGERS):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, asisten cerdas di grup WhatsApp. "
                "Bantu jawab pertanyaan anggota grup seputar topik yang ditanyakan dengan singkat, ramah, dan sopan."
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(group_id, ai_reply)
            return {"status": "processed", "type": "group_chat"}

    return {"status": "ignored", "reason": "Bukan pesan pemicu atau berasal dari luar grup terdaftar"}
