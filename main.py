import urllib.parse
import json

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data_dict = {}
    
    # 1. Ambil raw body dari request Fonnte
    raw_body = await request.body()
    body_str = raw_body.decode("utf-8", errors="ignore")
    
    # 2. Coba parse sebagai Form Data / URL-Encoded
    parsed_form = urllib.parse.parse_qs(body_str)
    if parsed_form:
        for key, val in parsed_form.items():
            data_dict[key] = val[0] if isinstance(val, list) and len(val) > 0 else str(val)
    
    # 3. Jika gagal parse form, coba parse sebagai JSON
    if not data_dict and body_str:
        try:
            data_dict = json.loads(body_str)
        except Exception:
            pass

    sender = str(data_dict.get("sender", ""))
    message = str(data_dict.get("message", "")).strip()
    
    # Fonnte bisa mengirim ID grup di 'group', 'target', atau 'from'
    group_id = str(data_dict.get("group") or data_dict.get("target") or data_dict.get("from") or "")

    print(f"[INCOMING RAW] Body: {body_str}")
    print(f"[INCOMING PARSED] Sender: '{sender}' | Group: '{group_id}' | Msg: '{message}'")

    if not message:
        return {"status": "ignored", "reason": "Pesan kosong atau gagal parse data"}

    # Pengecekan grup
    if TARGET_GROUP_ID in group_id or group_id in TARGET_GROUP_ID:
        msg_lower = message.lower()
        
        if msg_lower.startswith("!rekap"):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, admin rekapitulasi di grup WhatsApp. "
                "Tugasmu adalah menganalisis teks daftar pesanan/data dari anggota grup, lalu menyusun "
                "rekapannya dengan rapi dan ringkas. Gunakan bahasa Indonesia yang santai dan profesional."
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(group_id, ai_reply)
            return {"status": "processed", "type": "rekap"}

        elif any(msg_lower.startswith(trig) for trig in TRIGGERS):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, asisten cerdas di grup WhatsApp. "
                "Bantu jawab pertanyaan anggota grup secara singkat, ramah, dan jelas."
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(group_id, ai_reply)
            return {"status": "processed", "type": "chat"}

    print(f"[REJECTED] Group ID '{group_id}' atau pemicu tidak sesuai.")
    return {"status": "ignored", "reason": "Bukan pemicu atau grup berbeda"}
