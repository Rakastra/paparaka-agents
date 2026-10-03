import json
import os
import urllib.parse
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="AI Agent - Sup Virtual Office")

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
        <title>3D Stylized Sims-Style Virtual Office - AI Agent - Sup</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body { margin: 0; overflow: hidden; background-color: #0f172a; font-family: 'Plus Jakarta Sans', sans-serif; user-select: none; }
            #webgl-container { width: 100vw; height: 100vh; display: block; }
            canvas { cursor: grab; }
            canvas:active { cursor: grabbing; }
        </style>
        <!-- Import Three.js & OrbitControls via Free Public CDN -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>

        <!-- UI OVERLAY: HEADER TOP-LEFT -->
        <div class="absolute top-5 left-5 z-20 bg-slate-900/85 backdrop-blur-md border border-slate-700/60 text-white p-4 rounded-2xl shadow-2xl max-w-sm pointer-events-auto">
            <div class="flex items-center gap-3">
                <div class="w-11 h-11 bg-emerald-500/20 border border-emerald-400/40 rounded-2xl flex items-center justify-center text-2xl shadow-inner">
                    💎
                </div>
                <div>
                    <h1 class="font-bold text-sm text-emerald-400 tracking-wide uppercase">Sims-Style 3D Office</h1>
                    <p class="text-[11px] text-slate-400 font-medium">Isometric Architectural Cutaway — AI Agent - Sup</p>
                </div>
            </div>
            <div id="room-label" class="mt-3 bg-slate-800/90 border border-slate-700/80 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-200 flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span id="current-room-text">Lokasi: RECEPTION & LOBBY</span>
            </div>
        </div>

        <!-- UI OVERLAY: TOP-RIGHT (MINI MAP & STATUS) -->
        <div class="absolute top-5 right-5 z-20 flex flex-col items-end gap-3 pointer-events-auto">
            <div class="bg-slate-900/85 backdrop-blur-md border border-slate-700/60 px-4 py-2 rounded-2xl shadow-2xl text-xs font-bold text-emerald-400 flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
                <span>Agent Status: Active</span>
            </div>

            <!-- MINI MAP CANVAS -->
            <div class="bg-slate-900/85 backdrop-blur-md border border-slate-700/60 p-2.5 rounded-2xl shadow-2xl text-center">
                <div class="text-[10px] font-bold text-slate-400 mb-1.5 tracking-wider uppercase">Mini Map</div>
                <canvas id="minimap" width="160" height="110" class="border border-slate-800 rounded-xl bg-slate-950"></canvas>
            </div>
        </div>

        <!-- WELCOME BANNER -->
        <div id="welcome-banner" class="absolute top-1/4 left-1/2 -translate-x-1/2 z-30 bg-slate-900/95 border border-emerald-500/40 text-white px-8 py-5 rounded-3xl shadow-2xl text-center transition-all duration-1000 pointer-events-none">
            <h2 class="text-xl font-bold text-emerald-400 mb-1">Interactive The Sims 3D Office</h2>
            <p class="text-xs text-slate-300">Gunakan WASD untuk berjalan, Mouse Drag untuk Orbit 360°, dan Scroll untuk Zoom In/Out.</p>
        </div>

        <!-- UI OVERLAY: BOTTOM CONTROLS & TEST CONSOLE -->
        <div class="absolute bottom-5 left-5 right-5 z-20 flex flex-col md:flex-row justify-between items-end gap-4 pointer-events-none">
            
            <!-- Controls Legend -->
            <div class="bg-slate-900/85 backdrop-blur-md border border-slate-700/60 text-slate-300 p-4 rounded-2xl shadow-2xl text-xs space-y-1.5 pointer-events-auto">
                <div class="font-bold text-emerald-400 mb-1">🎮 Kontrol Sim / Kamera</div>
                <div><span class="bg-slate-800 border border-slate-700 px-2 py-0.5 rounded text-[10px] text-white font-mono">WASD</span> — Jalan/Navigasi Agent</div>
                <div><span class="bg-slate-800 border border-slate-700 px-2 py-0.5 rounded text-[10px] text-white font-mono">Klik Drag</span> — Putar Kamera 360° (Build Mode)</div>
                <div><span class="bg-slate-800 border border-slate-700 px-2 py-0.5 rounded text-[10px] text-white font-mono">Scroll</span> — Zoom Kamera In/Out</div>
                <div><span class="bg-slate-800 border border-slate-700 px-2 py-0.5 rounded text-[10px] text-white font-mono">C</span> — Ganti Kamera (Isometric / Agent View)</div>
            </div>

            <!-- Command Simulator -->
            <div class="bg-slate-900/85 backdrop-blur-md border border-slate-700/60 p-4 rounded-2xl shadow-2xl w-full max-w-md pointer-events-auto">
                <div class="text-xs font-bold text-slate-300 mb-2 flex items-center justify-between">
                    <span>🧪 Simulator WhatsApp / Webhook</span>
                    <span class="text-[10px] text-emerald-400 font-mono">Fonnte Connected</span>
                </div>
                <div class="flex gap-2">
                    <input id="test-input" type="text" placeholder="Kirim perintah (!rekap, !sup, !tanya)..." class="flex-1 bg-slate-950 border border-slate-800 px-3.5 py-2 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500">
                    <button onclick="sendSimulatedCommand()" class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-bold transition">
                        Kirim
                    </button>
                </div>
            </div>
        </div>

        <div id="webgl-container"></div>

        <script>
            // Banner Auto Fade
            setTimeout(() => {
                const banner = document.getElementById('welcome-banner');
                if (banner) {
                    banner.style.opacity = '0';
                    setTimeout(() => banner.remove(), 1000);
                }
            }, 4500);

            // --- THREE.JS SCENE SETUP ---
            const container = document.getElementById('webgl-container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0f172a); // Slate-900 Atmosphere

            // CAMERA SETUP (Sims 4 Isometric Viewpoint)
            const camera = new THREE.PerspectiveCamera(36, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(30, 28, 34);

            // RENDERER WITH ACES FILMIC TONE MAPPING (Sims/GTA Stylized Look)
            const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.outputEncoding = THREE.sRGBEncoding;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.15;
            container.appendChild(renderer.domElement);

            // ORBIT CONTROLS
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.maxPolarAngle = Math.PI / 2 - 0.05;
            controls.minDistance = 6;
            controls.maxDistance = 70;
            controls.target.set(0, 0, 0);

            // LIGHTING (Warm Stylized Sunlight + Ambient Occlusion Simulation)
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
            scene.add(ambientLight);

            const sunLight = new THREE.DirectionalLight(0xfff7ed, 1.2);
            sunLight.position.set(28, 42, 22);
            sunLight.castShadow = true;
            sunLight.shadow.mapSize.width = 2048;
            sunLight.shadow.mapSize.height = 2048;
            sunLight.shadow.bias = -0.0001;
            scene.add(sunLight);

            const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.4);
            fillLight.position.set(-25, 20, -25);
            scene.add(fillLight);

            // --- MATERIAL PALETTE (Stylized Sims Aesthetic) ---
            const materials = {
                woodFloor: new THREE.MeshStandardMaterial({ color: 0x854d0e, roughness: 0.35, metalness: 0.05 }),
                carpetSlate: new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.85 }),
                polishedTile: new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.15 }),
                ceramicPantry: new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.25 }),
                wallExterior: new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 }),
                wallInterior: new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.7 }),
                wallLowCutaway: new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.5 }),
                glassArchitectural: new THREE.MeshPhysicalMaterial({ color: 0xe0f2fe, transparent: true, opacity: 0.3, transmission: 0.85, roughness: 0.1 }),
                woodDesk: new THREE.MeshStandardMaterial({ color: 0x7c2d12, roughness: 0.4 }),
                fabricSofaBlue: new THREE.MeshStandardMaterial({ color: 0x2563eb, roughness: 0.8 }),
                fabricChairDark: new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.7 }),
                metalChrome: new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.1 }),
                screenGlow: new THREE.MeshBasicMaterial({ color: 0x38bdf8 }),
                plantGreen: new THREE.MeshStandardMaterial({ color: 0x16a34a, roughness: 0.5 }),
                agentShirt: new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.4 }),
                agentSkin: new THREE.MeshStandardMaterial({ color: 0xfde047, roughness: 0.3 }),
                plumbobGreen: new THREE.MeshBasicMaterial({ color: 0x22c55e })
            };

            const collisionBoxes = [];
            const roomRegions = [];

            function addCollisionBox(x, z, w, d) {
                collisionBoxes.push({ minX: x - w / 2, maxX: x + w / 2, minZ: z - d / 2, maxZ: z + d / 2 });
            }

            // --- FLOOR PLAN (30m x 20m) ---
            const officeWidth = 30;
            const officeDepth = 20;

            function createFloorSection(x, z, w, d, mat) {
                const geo = new THREE.BoxGeometry(w, 0.2, d);
                const mesh = new THREE.Mesh(geo, mat);
                mesh.position.set(x, -0.1, z);
                mesh.receiveShadow = true;
                scene.add(mesh);
            }

            // Zones
            createFloorSection(0, 4, 10, 8, materials.polishedTile);    // Lobby
            createFloorSection(0, -4, 18, 8, materials.carpetSlate);    // Open Office
            createFloorSection(-10, -5, 10, 10, materials.woodFloor);   // Manager Office
            createFloorSection(10, -5, 10, 10, materials.carpetSlate);   // Meeting Room
            createFloorSection(-10, 5, 10, 8, materials.woodFloor);     // HR / Finance
            createFloorSection(10, 5, 10, 8, materials.ceramicPantry);  // Pantry

            // CUTAWAY WALLS (Building Frame)
            function buildWall(x, z, w, h, d, mat = materials.wallInterior, isGlass = false) {
                const geo = new THREE.BoxGeometry(w, h, d);
                const mesh = new THREE.Mesh(geo, mat);
                mesh.position.set(x, h / 2, z);
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                scene.add(mesh);
                if (!isGlass) addCollisionBox(x, z, w, d);
            }

            buildWall(0, -10, 30, 3.2, 0.4, materials.wallExterior);  // Rear Wall
            buildWall(-15, 0, 0.4, 3.2, 20, materials.wallExterior);  // Left Exterior
            buildWall(15, 0, 0.4, 3.2, 20, materials.wallExterior);   // Right Exterior
            buildWall(-10, 10, 10, 0.6, 0.4, materials.wallLowCutaway); // Front Low Cutaway
            buildWall(10, 10, 10, 0.6, 0.4, materials.wallLowCutaway);
            buildWall(0, 10, 10, 2.8, 0.1, materials.glassArchitectural, true); // Glass Door Entrance

            // Glass Partitions
            buildWall(-5, -5, 0.15, 2.8, 10, materials.glassArchitectural, true);
            buildWall(5, -5, 0.15, 2.8, 10, materials.glassArchitectural, true);

            // --- FURNITURE & PROPS (SIMS QUALITY) ---

            // 1. Reception Counter & Sofa
            const recepCounter = new THREE.Mesh(new THREE.BoxGeometry(3.4, 1.1, 1.1), materials.woodDesk);
            recepCounter.position.set(0, 0.55, 4.8);
            recepCounter.castShadow = true;
            scene.add(recepCounter);
            addCollisionBox(0, 4.8, 3.4, 1.1);

            const sofa = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.7, 0.9), materials.fabricSofaBlue);
            sofa.position.set(-3.2, 0.35, 7.5);
            sofa.castShadow = true;
            scene.add(sofa);
            addCollisionBox(-3.2, 7.5, 2.4, 0.9);

            // 2. Workstations (12 Modern Desks with Glowing Screens)
            function createStylizedDesk(x, z) {
                const group = new THREE.Group();
                const desk = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.75, 0.85), materials.woodDesk);
                desk.position.y = 0.375;
                desk.castShadow = true;
                group.add(desk);

                // Chair
                const chair = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.85, 0.5), materials.fabricChairDark);
                chair.position.set(0, 0.425, 0.65);
                group.add(chair);

                // Monitor with Screen Glow
                const monBase = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.38, 0.05), materials.metalChrome);
                monBase.position.set(0, 0.95, -0.2);
                const monScreen = new THREE.Mesh(new THREE.PlaneGeometry(0.46, 0.32), materials.screenGlow);
                monScreen.position.set(0, 0.95, -0.17);
                group.add(monBase, monScreen);

                group.position.set(x, 0, z);
                scene.add(group);
                addCollisionBox(x, z, 1.7, 1.3);
            }

            for (let r = 0; r < 3; r++) {
                for (let c = 0; c < 4; c++) {
                    createStylizedDesk(-4.5 + c * 3.0, -2.5 - r * 2.5);
                }
            }

            // 3. Plants & Decor
            function addSimsPlant(x, z) {
                const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.2, 0.6, 12), materials.polishedTile);
                pot.position.set(x, 0.3, z);
                const leaves = new THREE.Mesh(new THREE.DodecahedronGeometry(0.55), materials.plantGreen);
                leaves.position.set(x, 0.85, z);
                leaves.castShadow = true;
                scene.add(pot, leaves);
                addCollisionBox(x, z, 0.6, 0.6);
            }
            addSimsPlant(-4.8, 5.2);
            addSimsPlant(4.8, 5.2);
            addSimsPlant(-14, -9);
            addSimsPlant(14, -9);

            // --- SIMS AGENT (MAIN AVATAR WITH GREEN PLUMBOB) ---
            const agentGroup = new THREE.Group();

            const head = new THREE.Mesh(new THREE.SphereGeometry(0.26, 16, 16), materials.agentSkin);
            head.position.y = 1.55;
            head.castShadow = true;
            agentGroup.add(head);

            const body = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.26, 0.7, 12), materials.agentShirt);
            body.position.y = 1.0;
            body.castShadow = true;
            agentGroup.add(body);

            // Iconic Sims Green Plumbob Diamond above Head
            const plumbobGeo = new THREE.OctahedronGeometry(0.18, 0);
            const plumbob = new THREE.Mesh(plumbobGeo, materials.plumbobGreen);
            plumbob.position.y = 2.15;
            agentGroup.add(plumbob);

            agentGroup.position.set(0, 0, 2.5);
            scene.add(agentGroup);

            // ROOM REGIONS
            roomRegions.push(
                { name: "RECEPTION & LOBBY", minX: -5, maxX: 5, minZ: 2, maxZ: 10 },
                { name: "OPEN OFFICE AREA", minX: -5, maxX: 5, minZ: -9, maxZ: 1 },
                { name: "MANAGER OFFICE", minX: -15, maxX: -5, minZ: -10, maxZ: -1 },
                { name: "MEETING ROOMS", minX: 5, maxX: 15, minZ: -10, maxZ: -1 },
                { name: "PANTRY & BREAK AREA", minX: 5, maxX: 15, minZ: 2, maxZ: 10 },
                { name: "HR & FINANCE DIVISION", minX: -15, maxX: -5, minZ: 2, maxZ: 10 }
            );

            // --- NAVIGATION & CONTROLS ---
            const keysPressed = {};
            const moveSpeed = 0.13;

            window.addEventListener('keydown', (e) => {
                keysPressed[e.key.toLowerCase()] = true;
                if (e.key.toLowerCase() === 'c') cameraMode = (cameraMode + 1) % 2;
            });
            window.addEventListener('keyup', (e) => keysPressed[e.key.toLowerCase()] = false);

            let cameraMode = 0; // 0 = Build/Isometric Orbit Mode, 1 = Agent Follow View

            function checkCollision(newX, newZ) {
                const r = 0.35;
                for (let box of collisionBoxes) {
                    if (newX + r > box.minX && newX - r < box.maxX && newZ + r > box.minZ && newZ - r < box.maxZ) return true;
                }
                return false;
            }

            function updateAgent() {
                let dx = 0, dz = 0;
                if (keysPressed['w'] || keysPressed['arrowup']) dz -= moveSpeed;
                if (keysPressed['s'] || keysPressed['arrowdown']) dz += moveSpeed;
                if (keysPressed['a'] || keysPressed['arrowleft']) dx -= moveSpeed;
                if (keysPressed['d'] || keysPressed['arrowright']) dx += moveSpeed;

                if (dx !== 0 || dz !== 0) {
                    const newX = agentGroup.position.x + dx;
                    const newZ = agentGroup.position.z + dz;
                    if (Math.abs(newX) < officeWidth / 2 - 0.5 && !checkCollision(newX, agentGroup.position.z)) agentGroup.position.x = newX;
                    if (Math.abs(newZ) < officeDepth / 2 - 0.5 && !checkCollision(agentGroup.position.x, newZ)) agentGroup.position.z = newZ;
                    agentGroup.rotation.y = Math.atan2(dx, dz);
                }

                // Rotating Plumbob Diamond
                plumbob.rotation.y += 0.04;
                plumbob.position.y = 2.15 + Math.sin(Date.now() * 0.005) * 0.06;

                // Camera Logic
                if (cameraMode === 0) {
                    controls.target.lerp(new THREE.Vector3(0, 0, 0), 0.05);
                } else {
                    controls.target.lerp(agentGroup.position.clone().add(new THREE.Vector3(0, 1.2, 0)), 0.08);
                    camera.position.lerp(agentGroup.position.clone().add(new THREE.Vector3(0, 4.0, 5.5)), 0.05);
                }

                // Room Indicator UI
                let currentRoom = "CORRIDOR";
                for (let reg of roomRegions) {
                    if (agentGroup.position.x >= reg.minX && agentGroup.position.x <= reg.maxX &&
                        agentGroup.position.z >= reg.minZ && agentGroup.position.z <= reg.maxZ) {
                        currentRoom = reg.name;
                        break;
                    }
                }
                document.getElementById('current-room-text').innerText = "Lokasi: " + currentRoom;
            }

            // --- MINI MAP ---
            const minimapCanvas = document.getElementById('minimap');
            const mmCtx = minimapCanvas.getContext('2d');

            function drawMiniMap() {
                mmCtx.clearRect(0, 0, minimapCanvas.width, minimapCanvas.height);
                const scaleX = minimapCanvas.width / officeWidth;
                const scaleY = minimapCanvas.height / officeDepth;

                mmCtx.strokeStyle = "#475569";
                mmCtx.lineWidth = 1;
                mmCtx.strokeRect(0, 0, minimapCanvas.width, minimapCanvas.height);

                const mmX = (agentGroup.position.x + officeWidth / 2) * scaleX;
                const mmY = (agentGroup.position.z + officeDepth / 2) * scaleY;

                mmCtx.fillStyle = "#22c55e";
                mmCtx.beginPath();
                mmCtx.arc(mmX, mmY, 4, 0, Math.PI * 2);
                mmCtx.fill();
            }

            // ANIMATION LOOP
            function animate() {
                requestAnimationFrame(animate);
                updateAgent();
                controls.update();
                renderer.render(scene, camera);
                drawMiniMap();
            }
            animate();

            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });

            function sendSimulatedCommand() {
                const input = document.getElementById('test-input');
                const val = input.value.trim();
                if (!val) return;
                alert("Simulasi WhatsApp dikirim: " + val);
                input.value = '';
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
            return f"Maaf, AI mengalami kendala: {error_msg}"
    except Exception as e:
        return f"Error koneksi ke OpenRouter: {str(e)}"


def send_fonnte_message(target: str, text_message: str):
    fonnte_token = (
        os.getenv("FONNTE_TOKEN")
        or os.getenv("FONNTE_API_TOKEN")
        or os.getenv("TOKEN_FONNTE")
    )
    if not fonnte_token:
        print("[ERROR] FONNTE_TOKEN tidak ditemukan!")
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

        if msg_lower.startswith("!rekap"):
            system_prompt = (
                "Kamu adalah sistem rekapitulasi data otomatis berbasis AI Agent. Tugasmu adalah menyusun laporan rekapitulasi data secara formal, lugas, dan rapi berdasarkan teks pesan yang diterima.\n\n"
                "Aturan Format Balasan:\n"
                "1. DILARANG menggunakan salam atau kata pembuka informal.\n"
                "2. Awali langsung dengan judul formal (*LAPORAN REKAPITULASI DATA PESANAN*).\n"
                "3. Kelompokkan setiap item berdasarkan KATEGORI secara rapi.\n"
                "4. Sertakan subtotal per kategori dan TOTAL KESELURUHAN di akhir laporan.\n"
                "5. Pada bagian paling bawah laporan, wajib cantumkan:\n\n"
                "Diproses oleh: AI Agent - Sup (Model: OpenRouter / Free LLM Engine)\n"
                "Daftar Perintah Pemicu: !rekap, !sup, !tanya, !bot"
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(reply_target, ai_reply)
            return {"status": "processed", "type": "rekap"}

        elif any(msg_lower.startswith(trig) for trig in TRIGGERS):
            system_prompt = (
                "Kamu adalah AI Agent - Sup, asisten cerdas berbasis Large Language Model (LLM). "
                "Jawab pertanyaan anggota grup secara jelas, sopan, dan formal.\n\n"
                "Di bagian paling bawah balasanmu, wajib tambahkan:\n\n"
                "Model AI: AI Agent - Sup (OpenRouter LLM Engine)\n"
                "Daftar Perintah Pemicu: !rekap, !sup, !tanya, !bot"
            )
            ai_reply = ask_openrouter(message, system_prompt)
            send_fonnte_message(reply_target, ai_reply)
            return {"status": "processed", "type": "chat"}

    return {"status": "ignored", "reason": "Bukan pemicu atau grup berbeda"}
