import os
import requests
from fastapi import FastAPI, Request

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
async def whatsapp_webhook(request: Request):
    data = await request.form()
    data_dict = dict(data)
    
    sender = data_dict.get("sender", "")
    message = data_dict.get("message", "").strip()
    # Fonnte kadang mengirim ID grup di 'group' atau 'target'
    group_id = data_dict.get("group") or data_dict.get("target") or ""

    print(f"[LOG INCOMING] Sender: {sender} | Group ID: {group_id} | Msg: {message}")

    if not message:
        return {"status": "ignored", "reason": "Pesan kosong"}

    # Pengecekan grup (mencakup pencocokan ID grup)
    if TARGET_GROUP_ID in group_id or group_id in TARGET_GROUP_ID:
        if message.lower().startswith("!rekap"):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, admin rekapitulasi di grup WhatsApp. "
                "Tugasmu adalah menganalisis teks daftar pesanan/data dari anggota grup, lalu menyusun "
                "rekapannya dengan rapi (daftar/tabel ringkas beserta total jika ada). "
                "Gunakan bahasa Indonesia yang sopan, jelas, dan profesional."
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(group_id, ai_reply)
            return {"status": "processed", "type": "group_rekap"}
        
        elif any(message.lower().startswith(trig) for trig in TRIGGERS):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, asisten cerdas di grup WhatsApp. "
                "Bantu jawab pertanyaan anggota grup dengan singkat, ramah, dan sopan."
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(group_id, ai_reply)
            return {"status": "processed", "type": "group_chat"}

    print(f"[REJECTED] Group ID '{group_id}' tidak cocok dengan TARGET '{TARGET_GROUP_ID}'")
    return {"status": "ignored", "reason": "Bukan pesan pemicu atau grup tidak cocok"}
