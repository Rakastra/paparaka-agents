from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# 1. Mount folder 'static' agar browser bisa membaca file .glb & assets di /static/models/office/
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Route Utama (Root Endpoint): Menampilkan 3D Virtual Office
@app.get("/", response_class=HTMLResponse)
async def serve_3d_office():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>File index.html tidak ditemukan di folder static/</h1>"

# 3. Route Webhook AI Agent (Fonnte / OpenRouter)
@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    
    # Masukkan logika pemrosesan AI Agent (AI Agent - Sup) di sini
    print("Pesan masuk:", data)
    
    return {"status": "success", "message": "Pesan berhasil diproses AI Agent"}
