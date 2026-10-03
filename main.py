import json
import os
import urllib.parse
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
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        if response.status_code == 200:
            return data["choices"][0]["message"]["content"]
        else:
            error_msg = data.get("error", {}).get(
                "message", "Kesalahan API OpenRouter"
            )
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
    payload = {"target": target, "message": text_message}
    headers = {"Authorization": fonnte_token}

    try:
        res = requests.post(
            fonnte_url, data=payload, headers=headers, timeout=15
        )
        print("[FONNTE RESPONSE]", res.text)
    except Exception as e:
        print("[FONNTE SEND ERROR]", str(e))


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data_dict = {}

    # 1. Coba ekstraksi dari Form Data (Multipart)
    try:
        form_data = await request.form()
        for k, v in form_data.items():
            data_dict[k] = str(v)
    except Exception:
        pass

    # 2. Fallback ke JSON
    if not data_dict:
        try:
            data_dict = await request.json()
        except Exception:
            pass

    # 3. Fallback ke Raw Body String (URL-Encoded)
    if not data_dict:
        try:
            body_bytes = await request.body()
            body_str = body_bytes.decode("utf-8", errors="ignore")
            parsed = urllib.parse.parse_qs(body_str)
            for k, v in parsed.items():
                data_dict[k] = v[0] if isinstance(v, list) and v else str(v)
        except Exception:
            pass

    sender = str(data_dict.get("sender") or data_dict.get("from") or "")
    message = str(
        data_dict.get("message") or data_dict.get("text") or ""
    ).strip()

    group_id = str(
        data_dict.get("group")
        or data_dict.get("target")
        or data_dict.get("group_id")
        or ""
    )

    print(f"[ALL DATA RECEIVED] {data_dict}")
    print(
        f"[INCOMING PARSED] Sender: '{sender}' | Group: '{group_id}' | Msg:"
        f" '{message}'"
    )

    if not message:
        return {"status": "ignored", "reason": "Pesan kosong"}

    # Tentukan nomor/ID tujuan pengiriman balasan
    # Jika group_id ada, gunakan group_id. Jika kosong, kirim ke sender atau grup default.
    reply_target = group_id if group_id else (sender if sender else TARGET_GROUP_ID)

    # Pengecekan kecocokan grup:
    # Lolos jika ID grup cocok ATAU jika group_id kosong (pesan dipicu oleh kata kunci langsung)
    is_group_valid = (
        not group_id
        or (TARGET_GROUP_ID in group_id or group_id in TARGET_GROUP_ID)
    )

    if is_group_valid:
        msg_lower = message.lower()

        # Pemicu !rekap
        if msg_lower.startswith("!rekap"):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, admin rekapitulasi di grup"
                " WhatsApp. Tugasmu adalah menganalisis teks daftar"
                " pesanan/data dari anggota grup, lalu menyusun rekapannya"
                " dengan rapi dan ringkas. Gunakan bahasa Indonesia yang santai"
                " dan profesional."
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(reply_target, ai_reply)
            return {"status": "processed", "type": "rekap"}

        # Pemicu !sup, !bot, !tanya
        elif any(msg_lower.startswith(trig) for trig in TRIGGERS):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, asisten cerdas di grup WhatsApp."
                " Bantu jawab pertanyaan anggota grup secara singkat, ramah,"
                " dan jelas."
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(reply_target, ai_reply)
            return {"status": "processed", "type": "chat"}

    print(f"[REJECTED] Group ID '{group_id}' atau pemicu tidak sesuai.")
    return {"status": "ignored", "reason": "Bukan pemicu atau grup berbeda"}
