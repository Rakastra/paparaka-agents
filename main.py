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
        print("[ERROR] OPENROUTER_API_KEY tidak ditemukan di Environment Variables!")
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
            error_msg = data.get("error", {}).get("message", "Kesalahan API OpenRouter")
            print(f"[OPENROUTER ERROR] {data}")
            return f"Maaf, AI mengalami kendala: {error_msg}"
    except Exception as e:
        print(f"[OPENROUTER EXCEPTION] {str(e)}")
        return f"Error koneksi ke OpenRouter: {str(e)}"


def send_fonnte_message(target: str, text_message: str):
    fonnte_token = os.getenv("FONNTE_TOKEN")
    if not fonnte_token:
        print("[ERROR] FONNTE_TOKEN tidak ditemukan di Environment Variables!")
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
    
    # Fonnte mengirimkan ID grup di field 'group' atau 'target'
    group_id = data_dict.get("group") or data_dict.get("target") or ""

    print(f"[INCOMING MSG] Sender: {sender} | Group ID: {group_id} | Message: '{message}'")

    if not message:
        return {"status": "ignored", "reason": "Pesan kosong"}

    # Mengecek apakah pesan berasal dari grup yang ditargetkan
    if TARGET_GROUP_ID in group_id or group_id in TARGET_GROUP_ID:
        msg_lower = message.lower()
        
        # 1. Pemicu Rekapitulasi (!rekap)
        if msg_lower.startswith("!rekap"):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, asisten rekapitulasi otomatis di grup WhatsApp. "
                "Tugasmu adalah menganalisis pesan, daftar pesanan, atau percakapan dari grup, "
                "lalu menyusun rekapannya dengan ringkas, rapi, dan mudah dibaca (gunakan poin-poin atau format tabel sederhana). "
                "Gunakan bahasa Indonesia yang santai tapi profesional."
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(group_id, ai_reply)
            return {"status": "processed", "type": "rekap"}

        # 2. Pemicu Tanya/Chat Umum (!sup, !bot, !tanya)
        elif any(msg_lower.startswith(trig) for trig in TRIGGERS):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, asisten AI cerdas di grup WhatsApp. "
                "Bantu jawab pertanyaan anggota grup secara singkat, ramah, dan informatif."
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(group_id, ai_reply)
            return {"status": "processed", "type": "chat"}

    print(f"[REJECTED] Pesan diabaikan (bukan dari grup target atau tidak memakai pemicu)")
    return {"status": "ignored", "reason": "Bukan pemicu atau grup berbeda"}
