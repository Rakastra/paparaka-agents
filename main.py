import json
import os
import urllib.parse
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="AI Agent - Sup")

TARGET_GROUP_ID = "120363387413264013@g.us"
TRIGGERS = ["!rekap", "!bot", "!tanya", "!sup"]


@app.get("/", response_class=HTMLResponse)
@app.get("/office", response_class=HTMLResponse)
def virtual_office():
    html_content = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Virtual Office - AI Agent - Sup</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; }
            .office-floor {
                background-color: #1e293b;
                background-image:  radial-gradient(#334155 1px, transparent 1px), radial-gradient(#334155 1px, #1e293b 1px);
                background-size: 40px 40px;
                background-position: 0 0, 20px 20px;
            }
            @keyframes pulse-slow {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.03); opacity: 0.9; }
            }
            .working-agent { animation: pulse-slow 2s infinite ease-in-out; }
        </style>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-4 md:p-8">

        <div class="max-w-6xl mx-auto space-y-6">
            
            <!-- Header Kantor -->
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-xl gap-4">
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center justify-center text-2xl">
                        🏢
                    </div>
                    <div>
                        <h1 class="text-xl font-bold text-white flex items-center gap-2">
                            Ruang Kerja AI Agent - Sup
                            <span class="text-xs font-normal bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 px-2.5 py-0.5 rounded-full">v1.0 Online</span>
                        </h1>
                        <p class="text-xs text-slate-400">Virtual Office & Real-time Command Center (Vercel Serverless)</p>
                    </div>
                </div>
                <div class="flex gap-3 text-xs font-medium">
                    <div class="bg-slate-800 border border-slate-700 px-3 py-2 rounded-xl flex items-center gap-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
                        <span>Fonnte Webhook Active</span>
                    </div>
                    <div class="bg-slate-800 border border-slate-700 px-3 py-2 rounded-xl flex items-center gap-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                        <span>OpenRouter Engine</span>
                    </div>
                </div>
            </div>

            <!-- RUANG KANTOR VIRTUAL (VISUAL FLOOR PLAN) -->
            <div class="office-floor border-2 border-slate-800 rounded-3xl p-6 md:p-10 relative min-h-[420px] shadow-2xl overflow-hidden flex flex-col justify-between">
                
                <!-- Dinding Atas / Papan Tulis & Rak File -->
                <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
                    <!-- Papan Tulis / Rules -->
                    <div class="bg-slate-900/90 backdrop-blur border border-slate-700/80 p-4 rounded-2xl shadow-lg hover:border-emerald-500/50 transition cursor-pointer" onclick="alert('Trigger Pemicu Aktif:\\n!rekap\\n!sup\\n!tanya\\n!bot')">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">📋 Papan Instruksi</span>
                            <span class="text-xs text-emerald-400 font-mono">TRIGGERS</span>
                        </div>
                        <p class="text-xs text-slate-300 font-mono">Pemicu: !rekap, !sup, !tanya, !bot</p>
                        <p class="text-[11px] text-slate-500 mt-1">Status: Siap memproses pesan grup</p>
                    </div>

                    <!-- Rak Arsip Rekap -->
                    <div class="bg-slate-900/90 backdrop-blur border border-slate-700/80 p-4 rounded-2xl shadow-lg hover:border-blue-500/50 transition cursor-pointer">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">📁 Rak Dokumen</span>
                            <span class="text-xs text-blue-400 font-mono">REKAP</span>
                        </div>
                        <p class="text-xs text-slate-300 font-mono">Format: Laporan Formal</p>
                        <p class="text-[11px] text-slate-500 mt-1">Otomatisasi pengelompokan kategori</p>
                    </div>

                    <!-- Area Breakroom -->
                    <div class="hidden md:block bg-slate-900/90 backdrop-blur border border-slate-700/80 p-4 rounded-2xl shadow-lg">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">☕ Coffee Station</span>
                            <span class="text-xs text-amber-400 font-mono">READY</span>
                        </div>
                        <p class="text-xs text-slate-300">Sistem berjalan 24/7 tanpa henti.</p>
                    </div>
                </div>

                <!-- TAMPILAN MEJA KERJA UTAMA AI AGENT -->
                <div class="flex justify-center my-4">
                    <div class="relative bg-slate-900/95 border-2 border-slate-700 rounded-3xl p-6 md:p-8 w-full max-w-lg shadow-2xl text-center working-agent">
                        <!-- Indikator Lampu Kerja -->
                        <div class="absolute -top-3 left-1/2 -translate-x-1/2 bg-slate-800 border border-slate-700 px-4 py-1 rounded-full flex items-center gap-2 text-xs">
                            <span id="agent-status-dot" class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                            <span id="agent-status-text" class="font-semibold text-emerald-400">Agent Sup: Standby di Meja</span>
                        </div>

                        <!-- Avatar & Computer Setup -->
                        <div class="mt-2 flex justify-center items-center gap-6">
                            <div class="text-6xl select-none filter drop-shadow-lg">
                                🤖
                            </div>
                            <div class="text-left">
                                <div class="text-3xl select-none mb-1">💻</div>
                                <h2 class="text-lg font-bold text-white">AI Agent - Sup</h2>
                                <p class="text-xs text-slate-400">Main Processor: OpenRouter LLM</p>
                            </div>
                        </div>

                        <!-- Meja Surface -->
                        <div class="mt-4 pt-4 border-t border-slate-800 flex justify-around text-xs text-slate-400">
                            <span>📝 Rekapitulasi Data</span>
                            <span>•</span>
                            <span>💬 Asisten Grup WA</span>
                            <span>•</span>
                            <span>📊 Laporan Formal</span>
                        </div>
                    </div>
                </div>

                <!-- Dinding Bawah / Live Monitor Console -->
                <div class="mt-8 bg-slate-900/90 backdrop-blur border border-slate-800 p-4 rounded-2xl">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                            Monitor Aktivitas Kantor
                        </span>
                        <span class="text-[11px] text-slate-500 font-mono">Live Webhook Log</span>
                    </div>
                    <div id="office-log" class="font-mono text-xs text-slate-300 bg-slate-950 p-3 rounded-xl h-24 overflow-y-auto space-y-1 border border-slate-800/80">
                        <div class="text-slate-500">[SYSTEM]: Ruang kerja AI Agent - Sup siap digunakan.</div>
                        <div class="text-emerald-400">[SYSTEM]: Menunggu pesan WhatsApp dari grup...</div>
                    </div>
                </div>

            </div>

            <!-- SIMULATOR PENGUJIAN PESAN KANTOR -->
            <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
                <h3 class="text-sm font-bold text-white mb-3 flex items-center gap-2">
                    🧪 Testing Console (Simulasi Pesan WhatsApp)
                </h3>
                <div class="flex gap-3">
                    <input id="test-msg" type="text" placeholder="Masukkan contoh pesan (misal: !rekap Nasi Goreng 2 porsi Rp 30000)..." class="flex-1 bg-slate-950 border border-slate-800 px-4 py-2.5 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500">
                    <button onclick="simulateOfficeMessage()" class="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2.5 rounded-xl text-xs font-semibold transition">
                        Kirim ke Meja Agent
                    </button>
                </div>
            </div>

        </div>

        <script>
            function simulateOfficeMessage() {
                const input = document.getElementById('test-msg');
                const log = document.getElementById('office-log');
                const statusText = document.getElementById('agent-status-text');
                const statusDot = document.getElementById('agent-status-dot');
                
                const val = input.value.trim();
                if (!val) return;

                // Log Input
                log.innerHTML += `<div class="text-blue-400">[WA INPUT]: ${val}</div>`;
                input.value = '';

                // Set Agent Status Bekerja
                statusText.innerText = "Agent Sup: Sedang Memproses Data...";
                statusText.className = "font-semibold text-amber-400";
                statusDot.className = "w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping";

                log.innerHTML += `<div class="text-amber-400">[AGENT]: Memproses respons melalui OpenRouter API...</div>`;
                log.scrollTop = log.scrollHeight;

                // Reset Status
                setTimeout(() => {
                    statusText.innerText = "Agent Sup: Standby di Meja";
                    statusText.className = "font-semibold text-emerald-400";
                    statusDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-400";
                    log.innerHTML += `<div class="text-emerald-400">[AGENT]: Balasan berhasil dikirim ke target!</div>`;
                    log.scrollTop = log.scrollHeight;
                }, 1500);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


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
    fonnte_token = (
        os.getenv("FONNTE_TOKEN")
        or os.getenv("FONNTE_API_TOKEN")
        or os.getenv("TOKEN_FONNTE")
    )
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

    try:
        form_data = await request.form()
        for k, v in form_data.items():
            data_dict[k] = str(v)
    except Exception:
        pass

    if not data_dict:
        try:
            data_dict = await request.json()
        except Exception:
            pass

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

    reply_target = (
        group_id if group_id else (sender if sender else TARGET_GROUP_ID)
    )
    is_group_valid = not group_id or (
        TARGET_GROUP_ID in group_id or group_id in TARGET_GROUP_ID
    )

    if is_group_valid:
        msg_lower = message.lower()

        # Pemicu !rekap
        if msg_lower.startswith("!rekap"):
            system_prompt = (
                "Kamu adalah sistem rekapitulasi data otomatis berbasis AI Agent. Tugasmu adalah menyusun laporan rekapitulasi data secara formal, lugas, dan rapi berdasarkan teks pesan yang diterima.\n\n"
                "Aturan Format Balasan:\n"
                "1. DILARANG menggunakan salam atau kata pembuka informal (seperti 'Halo', 'Bentar lagi ya', 'Ini dia').\n"
                "2. Awali langsung dengan judul formal dalam cetak tebal (contoh: *LAPORAN REKAPITULASI DATA PESANAN*).\n"
                "3. Kelompokkan setiap item berdasarkan KATEGORI secara rapi menggunakan simbol poin (•).\n"
                "4. Sertakan subtotal per kategori dan TOTAL KESELURUHAN di akhir laporan.\n"
                "5. Pada bagian paling bawah laporan, wajib cantumkan daftar perintah pemicu dan identitas model AI dalam format berikut persis:\n\n"
                "Diproses oleh: AI Agent - Sup (Model: OpenRouter / Free LLM Engine)\n"
                "Daftar Perintah Pemicu: !rekap, !sup, !tanya, !bot"
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(reply_target, ai_reply)
            return {"status": "processed", "type": "rekap"}

        # Pemicu !sup, !bot, !tanya
        elif any(msg_lower.startswith(trig) for trig in TRIGGERS):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, asisten cerdas berbasis Large Language Model (LLM). "
                "Jawab pertanyaan anggota grup secara jelas, sopan, dan formal.\n\n"
                "Di bagian paling bawah balasanmu, wajib tambahkan teks keterangan berikut:\n\n"
                "Model AI: AI Agent - Sup (OpenRouter LLM Engine)\n"
                "Daftar Perintah Pemicu: !rekap, !sup, !tanya, !bot"
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(reply_target, ai_reply)
            return {"status": "processed", "type": "chat"}

    print(f"[REJECTED] Group ID '{group_id}' atau pemicu tidak sesuai.")
    return {"status": "ignored", "reason": "Bukan pemicu atau grup berbeda"}
