import os
import time
import logging
import requests
from collections import deque
from itertools import count
from typing import List
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
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
    possible_paths = [
        os.path.join(STATIC_DIR, "index.html"),
        os.path.join(BASE_DIR, "index.html"),
        os.path.join(BASE_DIR, "index (1).html"),
    ]
    
    for path in possible_paths:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache"})
                
    return JSONResponse({"detail": "File index.html tidak ditemukan di static/ atau root"}, status_code=404)


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


def ask_openrouter(prompt_text: str, history=None) -> str:
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
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *(history or []),
                             {"role": "user", "content": prompt_text}],
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


# ==========================================
# Chat interaktif dari board 3D + aktivitas WhatsApp
# ==========================================
EVENTS = deque(maxlen=30)
_ids = count(1)
_hits = {}
SHOW_ACTIVITY = os.getenv("SHOW_ACTIVITY", "0") == "1"   # default mati: pesan WA tidak dibuka ke publik


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    history: List[dict] = []


def rate_ok(ip: str, limit: int = 12) -> bool:
    now = time.time()
    q = [x for x in _hits.get(ip, []) if now - x < 60]
    ok = len(q) < limit
    if ok:
        q.append(now)
    _hits[ip] = q
    return ok


@app.post("/api/chat")
async def api_chat(body: ChatIn, request: Request):
    ip = request.client.host if request.client else "unknown"
    if not rate_ok(ip):
        return JSONResponse({"detail": "Terlalu banyak permintaan"}, status_code=429)
    history = [
        {"role": h["role"], "content": str(h.get("content", ""))[:1000]}
        for h in body.history[-6:] if h.get("role") in ("user", "assistant")
    ]
    reply = await run_in_threadpool(ask_openrouter, body.message.strip(), history)
    return {"reply": reply}


@app.get("/api/activity")
async def api_activity(since: int = 0):
    if not SHOW_ACTIVITY:
        return {"events": [], "last": 0}
    events = [e for e in EVENTS if e["id"] > since]
    return {"events": events, "last": EVENTS[-1]["id"] if EVENTS else 0}


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
            reply = await run_in_threadpool(ask_openrouter, message)
            await run_in_threadpool(send_whatsapp_message, group_id or sender, reply)
            EVENTS.append({"id": next(_ids), "sender": "…" + str(sender)[-4:], "message": str(message)[:80], "reply": reply[:160]})

        return {"status": "success"}
    except Exception as e:
        log.exception("Webhook error")
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)
