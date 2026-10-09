import os
import logging
import requests
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sup")

app = FastAPI(title="AI Agent - Sup")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def serve_office():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path, headers={"Cache-Control": "no-cache"})
    return JSONResponse({"detail": "static/index.html tidak ditemukan"}, status_code=404)


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


# ==========================================
# AI Agent & Webhook
# ==========================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
FONNTE_TOKEN = os.getenv("FONNTE_TOKEN")
TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID")
MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-lite-001")
TIMEOUT = 30

SYSTEM_PROMPT = """
Kamu adalah AI Agent - Sup, asisten cerdas dan responsif.
Tugas utama kamu adalah membantu anggota grup WhatsApp dalam:
1. Menjawab pertanyaan seputar operasional, data, dan umum secara singkat dan tepat.
2. Membantu mengekstrak data transaksi atau rincian tagihan (Split Bill).
3. Tetap bersikap sopan, membantu, dan profesional.
"""


def send_whatsapp_message(target: str, message: str):
    if not FONNTE_TOKEN or not target:
        return
    try:
        requests.post(
            "https://api.fonnte.com/send",
            headers={"Authorization": FONNTE_TOKEN},
            data={"target": target, "message": message},
            timeout=TIMEOUT,
        )
    except requests.RequestException as e:
        log.error("Fonnte error: %s", e)


def ask_openrouter(prompt_text: str) -> str:
    if not OPENROUTER_API_KEY:
        return "Maaf, API Key OpenRouter belum dikonfigurasi."
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_text},
                ],
            },
            timeout=TIMEOUT,
        )
        choices = res.json().get("choices") or []
        if choices:
            return choices[0]["message"]["content"]
        log.warning("OpenRouter tanpa choices: %s", res.text[:300])
        return "Maaf, AI sedang tidak dapat merespons saat ini."
    except Exception as e:
        log.error("OpenRouter error: %s", e)
        return "Maaf, terjadi kendala saat menghubungi AI. Coba lagi sebentar."


@app.post("/webhook")
async def fonnte_webhook(request: Request):
    try:
        ctype = request.headers.get("content-type", "")
        data = await request.json() if "json" in ctype else await request.form()

        sender = data.get("sender")
        message = data.get("message")
        group_id = data.get("id") or data.get("group")

        if TARGET_GROUP_ID and str(group_id) != str(TARGET_GROUP_ID):
            return {"status": "ignored"}

        if message:
            send_whatsapp_message(group_id or sender, ask_openrouter(message))

        return {"status": "success"}
    except Exception as e:
        log.exception("Webhook error")
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)
