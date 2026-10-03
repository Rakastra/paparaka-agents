import os
import requests
from typing import Optional
from fastapi import FastAPI, Form, Request

app = FastAPI(title="AI Agent - Sup")

TARGET_GROUP_ID = "120363387413264013@g.us"
TRIGGERS = ["!rekap", "!bot", "!tanya", "!sup"]


@app.get("/")
def home():
    return {"status": "AI Agent Running", "message": "Server Vercel Aktif!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


def ask_openrouter(user_message: str, system_prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY tidak ditemukan!")
        return "Error: API Key OpenRouter belum terpasang."

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
            error_msg = data.get("error", {}).get("message", "Kesalahan API")
            return f"Maaf, AI mengalami kendala: {error_msg}"
    except Exception as e:
        return f"Error koneksi ke OpenRouter: {str(e)}"


def send_fonnte_message(target: str, text_message: str):
    fonnte_token = os.getenv("FONNTE_TOKEN")
    if not fonnte_token:
        print("[ERROR] FONNTE_TOKEN tidak ditemukan!")
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


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    sender: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    group: Optional[str] = Form(None),
    target: Optional[str] = Form(None)
):
    sender_val = sender or ""
    message_val = (message or "").strip()
    group_id = group or target or ""

    print(f"[INCOMING PARSED] Sender: '{sender_val}' | Group: '{group_id}' | Msg: '{message_val}'")

    if not message_val:
        return {"status": "ignored", "reason": "Pesan kosong"}

    if TARGET_GROUP_ID in group_id or group_id in TARGET_GROUP_ID:
        msg_lower = message_val.lower()
        
        if msg_lower.startswith("!rekap"):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, admin rekapitulasi di grup WhatsApp. "
                "Tugasmu adalah menganalisis teks daftar pesanan/data dari anggota grup, lalu menyusun "
                "rekapannya dengan rapi dan ringkas. Gunakan bahasa Indonesia yang santai dan profesional."
            )
            ai_reply = ask_openrouter(message_val, system_prompt)
            send_fonnte_message(group_id, ai_reply)
            return {"status": "processed", "type": "rekap"}

        elif any(msg_lower.startswith(trig) for trig in TRIGGERS):
            system_prompt = (
                "Kamu meupakan AI Agent - Sup, asisten cerdas di grup WhatsApp. "
                "Bantu jawab pertanyaan anggota grup secara singkat, ramah, dan jelas."
            )
            ai_reply = ask_openrouter(message_val, system_prompt)
            send_fonnte_message(group_id, ai_reply)
            return {"status": "processed", "type": "chat"}

    print(f"[REJECTED] Group ID '{group_id}' atau pemicu tidak sesuai.")
    return {"status": "ignored", "reason": "Bukan pemicu atau grup berbeda"}
