Berdasarkan gambar referensi yang Anda berikan, tampilan tersebut adalah tampilan **3D Isometrik / Low-Poly 3D Office Space** (seperti pada platform *Gather.town*, *Sims*, atau *Topview Virtual Office*) lengkap dengan beberapa area (ruang rapat, meja kerja linier, lounge/breakroom, dan avatar AI dengan balon status).

Untuk membuat tampilan **Full 3D dengan fitur kontrol kamera (rotasi, zoom, pan)** yang berjalan langsung di browser via FastAPI/Vercel, teknologi standar industri yang paling tepat digunakan adalah **Three.js** (dikombinasikan dengan **OrbitControls**).

---

### Architecture & Framework 3D

1. **Three.js (WebGL Engine)**: Untuk merender objek 3D (ruangan, lantai, meja, kursi, tanaman, dinding kaca) di browser secara *real-time*.
2. **OrbitControls**: Memungkinkan kamera di-rotasi (drag klik kiri), di-pan/geser (klik kanan), dan di-zoom (scroll mouse).
3. **HTML3D / Sprite Label**: Menampilkan status avatar AI dan chat bubble di atas karakter AI secara dinamis.

---

### Kode Complete `main.py` (Full 3D Virtual Office)

Berikut adalah kode lengkap `main.py` yang sudah mengintegrasikan halaman HTML 3D menggunakan Three.js. Ketika Anda membuka `/` atau `/office` di browser, Anda bisa **memutar kamera (rotasi 360°)**, **zoom in/out**, serta melihat ruangan kantor 3D lengkap dengan AI Agent - Sup di mejanya:

```python
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
def virtual_office_3d():
    html_content = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>3D Virtual Office - AI Agent - Sup</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { margin: 0; overflow: hidden; background-color: #1a1a24; font-family: sans-serif; }
            #webgl-container { width: 100vw; height: 100vh; display: block; }
        </style>
        <!-- Import Three.js dan OrbitControls dari CDN -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>

        <!-- UI Overlay Control Panel -->
        <div class="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur border border-slate-700 text-white p-4 rounded-2xl shadow-2xl max-w-sm pointer-events-auto">
            <div class="flex items-center gap-3 mb-2">
                <span class="text-2xl">🏢</span>
                <div>
                    <h1 class="font-bold text-sm text-emerald-400">3D Virtual Office: AI Agent - Sup</h1>
                    <p class="text-[11px] text-slate-400">Gunakan Mouse: Klik Kiri = Rotasi | Klik Kanan = Geser | Scroll = Zoom</p>
                </div>
            </div>
            <div id="status-badge" class="mt-2 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 px-3 py-1 rounded-xl text-xs font-semibold flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Agent Sup: Standby di Meja Utama</span>
            </div>
        </div>

        <!-- Testing Simulator Overlay -->
        <div class="absolute bottom-4 left-4 right-4 md:left-auto md:right-4 z-10 bg-slate-900/90 backdrop-blur border border-slate-700 p-4 rounded-2xl shadow-2xl max-w-md pointer-events-auto">
            <h2 class="text-xs font-bold text-slate-300 mb-2 uppercase tracking-wider">🧪 Testing Command Center</h2>
            <div class="flex gap-2">
                <input id="test-input" type="text" placeholder="Tes pesan (misal: !rekap Nasi Goreng 2)..." class="flex-1 bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500">
                <button onclick="trigger3dAction()" class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-semibold transition">
                    Kirim
                </button>
            </div>
        </div>

        <!-- Canvas Container untuk Three.js -->
        <div id="webgl-container"></div>

        <script>
            // --- THREE.JS SETUP ---
            const container = document.getElementById('webgl-container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0xdce5ed);

            // Camera Setup (Isometrik 3D View)
            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(25, 20, 25);

            // Renderer Setup
            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            container.appendChild(renderer.domElement);

            // Orbit Controls (Rotasi, Zoom, Pan)
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.maxPolarAngle = Math.PI / 2 - 0.05; // Mencegah kamera tembus ke bawah lantai
            controls.target.set(0, 2, 0);

            // Lighting Setup
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(20, 40, 20);
            dirLight.castShadow = true;
            dirLight.shadow.mapSize.width = 2048;
            dirLight.shadow.mapSize.height = 2048;
            scene.add(dirLight);

            // --- DEKORASI KANTOR 3D (PARQUET FLOOR, WALLS, FURNITURE) ---

            // 1. Lantai Kayu Parquet
            const floorGeo = new THREE.BoxGeometry(30, 0.4, 18);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0xc49a6c, roughness: 0.4 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.position.y = -0.2;
            floor.receiveShadow = true;
            scene.add(floor);

            // Helper function pembuat dinding
            function createWall(w, h, d, x, y, z, color = 0xeeeeee) {
                const geo = new THREE.BoxGeometry(w, h, d);
                const mat = new THREE.MeshStandardMaterial({ color: color });
                const mesh = new THREE.Mesh(geo, mat);
                mesh.position.set(x, y, z);
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                scene.add(mesh);
            }

            // Dinding Belakang & Samping Left
            createWall(30, 6, 0.4, 0, 3, -9, 0x2c3e50);
            createWall(0.4, 6, 18, -15, 3, 0, 0x34495e);

            // Dinding Kaca Ruang Rapat (Glass Partition)
            const glassGeo = new THREE.BoxGeometry(0.2, 5.5, 8);
            const glassMat = new THREE.MeshPhysicalMaterial({
                color: 0xffffff, transparent: true, opacity: 0.3, roughness: 0.1, transmission: 0.9
            });
            const glassWall = new THREE.Mesh(glassGeo, glassMat);
            glassWall.position.set(-7, 2.75, -5);
            scene.add(glassWall);

            // 2. Meja & Komputer AI Agent (Center Desk)
            const deskGeo = new THREE.BoxGeometry(4, 1.2, 2.5);
            const deskMat = new THREE.MeshStandardMaterial({ color: 0x4a3525 });
            const desk = new THREE.Mesh(deskGeo, deskMat);
            desk.position.set(0, 0.6, 0);
            desk.castShadow = true;
            desk.receiveShadow = true;
            scene.add(desk);

            // Laptop di atas meja
            const laptopGeo = new THREE.BoxGeometry(0.8, 0.05, 0.6);
            const laptopMat = new THREE.MeshStandardMaterial({ color: 0x111111 });
            const laptop = new THREE.Mesh(laptopGeo, laptopMat);
            laptop.position.set(0, 1.22, 0);
            scene.add(laptop);

            // 3. Avatar AI Agent - Sup (3D Character Mesh)
            const agentGroup = new THREE.Group();
            
            // Kepala AI
            const headGeo = new THREE.SphereGeometry(0.4, 32, 32);
            const headMat = new THREE.MeshStandardMaterial({ color: 0x3498db });
            const head = new THREE.Mesh(headGeo, headMat);
            head.position.y = 2.1;
            agentGroup.add(head);

            // Badan AI
            const bodyGeo = new THREE.CylinderGeometry(0.3, 0.4, 0.9, 16);
            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x2ecc71 });
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            body.position.y = 1.45;
            agentGroup.add(body);

            agentGroup.position.set(0, 0, -1); // Duduk di belakang meja
            scene.add(agentGroup);

            // Tanaman Hias Pot (Decoration Plant)
            function createPlant(x, z) {
                const potGeo = new THREE.CylinderGeometry(0.5, 0.3, 0.8, 16);
                const potMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
                const pot = new THREE.Mesh(potGeo, potMat);
                pot.position.set(x, 0.4, z);

                const plantGeo = new THREE.DodecahedronGeometry(0.7);
                const plantMat = new THREE.MeshStandardMaterial({ color: 0x27ae60 });
                const plant = new THREE.Mesh(plantGeo, plantMat);
                plant.position.set(x, 1.1, z);

                scene.add(pot);
                scene.add(plant);
            }
            createPlant(-13, -7);
            createPlant(13, -7);

            // --- ANIMATION LOOP ---
            let isWorking = false;
            function animate() {
                requestAnimationFrame(animate);

                // Animasi idle berayun halus pada AI Agent
                if (agentGroup) {
                    agentGroup.rotation.y = Math.sin(Date.now() * 0.002) * 0.15;
                    if (isWorking) {
                        agentGroup.position.y = Math.sin(Date.now() * 0.01) * 0.1;
                    } else {
                        agentGroup.position.y = 0;
                    }
                }

                controls.update();
                renderer.render(scene, camera);
            }
            animate();

            // Resize Responsive
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });

            // Trigger Simulasi Aktivitas 3D
            function trigger3dAction() {
                const input = document.getElementById('test-input');
                const val = input.value.trim();
                if (!val) return;

                const badge = document.getElementById('status-badge');
                badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span><span>Agent Sup: Sedang Memproses Pesan...</span>`;
                badge.className = "mt-2 bg-amber-500/20 text-amber-400 border border-amber-500/40 px-3 py-1 rounded-xl text-xs font-semibold flex items-center gap-2";

                headMat.color.setHex(0xf39c12); // Mengubah warna kepala AI saat bekerja
                isWorking = true;
                input.value = '';

                setTimeout(() => {
                    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span><span>Agent Sup: Standby di Meja Utama</span>`;
                    badge.className = "mt-2 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 px-3 py-1 rounded-xl text-xs font-semibold flex items-center gap-2";
                    headMat.color.setHex(0x3498db);
                    isWorking = false;
                }, 2000);
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

```
