import json
import os
import urllib.parse
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

# TOP-LEVEL VARIABLE (Wajib untuk Vercel Python Builder)
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
        <title>3D Photorealistic Virtual Office - AI Agent - Sup</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { margin: 0; overflow: hidden; background-color: #0f172a; font-family: 'Inter', sans-serif; user-select: none; }
            #webgl-container { width: 100vw; height: 100vh; display: block; }
            /* Custom Canvas crosshair / overlay cursor */
            canvas { cursor: grab; }
            canvas:active { cursor: grabbing; }
        </style>
        <!-- Import Three.js & OrbitControls via CDN -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>

        <!-- UI OVERLAY: HEADER TOP-LEFT -->
        <div class="absolute top-4 left-4 z-20 bg-slate-900/90 backdrop-blur border border-slate-700/80 text-white p-4 rounded-2xl shadow-2xl max-w-sm pointer-events-auto">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-emerald-500/20 border border-emerald-500/40 rounded-xl flex items-center justify-center text-xl">
                    🏢
                </div>
                <div>
                    <h1 class="font-bold text-sm text-emerald-400 tracking-wide">VIRTUAL OFFICE</h1>
                    <p class="text-[11px] text-slate-400">AI Agent - Sup Command Center</p>
                </div>
            </div>
            <div id="room-label" class="mt-3 bg-slate-800 border border-slate-700/80 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-200 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span id="current-room-text">Lokasi: RECEPTION AREA</span>
            </div>
        </div>

        <!-- UI OVERLAY: TOP-RIGHT (AGENT STATUS & MINI MAP) -->
        <div class="absolute top-4 right-4 z-20 flex flex-col items-end gap-3 pointer-events-auto">
            <div class="bg-slate-900/90 backdrop-blur border border-slate-700/80 px-3.5 py-2 rounded-2xl shadow-2xl text-xs font-semibold text-emerald-400 flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                <span>Agent: Online</span>
            </div>

            <!-- MINI MAP CANVAS -->
            <div class="bg-slate-900/90 backdrop-blur border border-slate-700/80 p-2 rounded-2xl shadow-2xl text-center">
                <div class="text-[10px] font-bold text-slate-400 mb-1 tracking-wider uppercase">Mini Map</div>
                <canvas id="minimap" width="160" height="110" class="border border-slate-800 rounded-xl bg-slate-950"></canvas>
            </div>
        </div>

        <!-- INTERACTION PROMPT -->
        <div id="interaction-prompt" class="hidden absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 bg-emerald-600/90 backdrop-blur text-white px-5 py-2.5 rounded-2xl shadow-2xl text-xs font-bold border border-emerald-400 animate-bounce pointer-events-none">
            Press E to Interact
        </div>

        <!-- WELCOME BANNER (DISAPPEARS IN 4s) -->
        <div id="welcome-banner" class="absolute top-1/4 left-1/2 -translate-x-1/2 z-30 bg-slate-900/95 border border-emerald-500/50 text-white px-8 py-4 rounded-3xl shadow-2xl text-center transition-opacity duration-1000 pointer-events-none">
            <h2 class="text-lg font-bold text-emerald-400 mb-1">Welcome to Virtual Office</h2>
            <p class="text-xs text-slate-300">Eksplorasi kantor 3D profesional dengan kontrol navigasi WASD dan Mouse Kamera 360°</p>
        </div>

        <!-- UI OVERLAY: BOTTOM CONTROLS & COMMAND CENTER -->
        <div class="absolute bottom-4 left-4 right-4 z-20 flex flex-col md:flex-row justify-between items-end gap-4 pointer-events-none">
            
            <!-- Controls Legend -->
            <div class="bg-slate-900/90 backdrop-blur border border-slate-700/80 text-slate-300 p-3.5 rounded-2xl shadow-2xl text-xs space-y-1 pointer-events-auto">
                <div class="font-bold text-emerald-400 mb-1">🎮 Navigasi & Kamera</div>
                <div><span class="bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded text-[10px] text-white">WASD</span> — Move Agent</div>
                <div><span class="bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded text-[10px] text-white">Mouse Drag</span> — Rotate / Orbit 360°</div>
                <div><span class="bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded text-[10px] text-white">Scroll</span> — Zoom In / Out</div>
                <div><span class="bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded text-[10px] text-white">C</span> — Change Camera Mode</div>
            </div>

            <!-- Command Simulator -->
            <div class="bg-slate-900/90 backdrop-blur border border-slate-700/80 p-3.5 rounded-2xl shadow-2xl w-full max-w-md pointer-events-auto">
                <div class="text-xs font-bold text-slate-300 mb-2 flex items-center justify-between">
                    <span>🧪 WhatsApp Testing Console</span>
                    <span class="text-[10px] text-emerald-400 font-mono">Fonnte Active</span>
                </div>
                <div class="flex gap-2">
                    <input id="test-input" type="text" placeholder="Masukkan perintah (!rekap, !sup, !tanya)..." class="flex-1 bg-slate-950 border border-slate-800 px-3 py-2 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500">
                    <button onclick="sendSimulatedCommand()" class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-semibold transition">
                        Kirim
                    </button>
                </div>
            </div>
        </div>

        <!-- THREE.JS CANVAS CONTAINER -->
        <div id="webgl-container"></div>

        <script>
            // Welcome banner auto fade-out
            setTimeout(() => {
                const banner = document.getElementById('welcome-banner');
                if (banner) {
                    banner.style.opacity = '0';
                    setTimeout(() => banner.remove(), 1000);
                }
            }, 4000);

            // --- THREE.JS ENGINE INITIALIZATION ---
            const container = document.getElementById('webgl-container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0f172a);
            scene.fog = new THREE.FogExp2(0x0f172a, 0.018);

            // CAMERA SETUP
            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 12, 18);

            // RENDERER SETUP
            const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.outputEncoding = THREE.sRGBEncoding;
            container.appendChild(renderer.domElement);

            // ORBIT CONTROLS SETUP
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.maxPolarAngle = Math.PI / 2 - 0.02; // Prevents camera going below floor
            controls.minDistance = 3;
            controls.maxDistance = 45;

            // LIGHTING SETUP
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            const mainLight = new THREE.DirectionalLight(0xfff7ed, 0.8);
            mainLight.position.set(20, 35, 15);
            mainLight.castShadow = true;
            mainLight.shadow.mapSize.width = 2048;
            mainLight.shadow.mapSize.height = 2048;
            mainLight.shadow.camera.near = 0.5;
            mainLight.shadow.camera.far = 80;
            mainLight.shadow.camera.left = -20;
            mainLight.shadow.camera.right = 20;
            mainLight.shadow.camera.top = 20;
            mainLight.shadow.camera.bottom = -20;
            scene.add(mainLight);

            // Soft Office Indoor Ceiling Spotlights
            function addCeilingSpot(x, z, color=0xffffff) {
                const spot = new THREE.PointLight(color, 0.5, 10);
                spot.position.set(x, 3.8, z);
                scene.add(spot);
            }

            // --- MATERIAL PALETTE ---
            const materials = {
                carpet: new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.8 }),
                polishedTile: new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.2 }),
                woodParquet: new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.4 }),
                ceramicTile: new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.3 }),
                wallPaint: new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.7 }),
                wallDark: new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 }),
                glass: new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.35, roughness: 0.1, transmission: 0.85 }),
                woodFurniture: new THREE.MeshStandardMaterial({ color: 0x451a03, roughness: 0.5 }),
                metalBlack: new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8, roughness: 0.2 }),
                fabricBlue: new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.7 }),
                plantGreen: new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.6 }),
                agentBody: new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.5 }),
                agentHead: new THREE.MeshStandardMaterial({ color: 0xfde047, roughness: 0.4 })
            };

            // --- COLLISION ARRAY & ROOM REGIONS ---
            const collisionBoxes = [];
            const roomRegions = [];

            function addCollisionBox(x, z, width, depth) {
                collisionBoxes.push({
                    minX: x - width / 2,
                    maxX: x + width / 2,
                    minZ: z - depth / 2,
                    maxZ: z + depth / 2
                });
            }

            // --- FLOOR PLAN CONSTRUCTIONS (30m x 20m) ---
            const officeWidth = 30;
            const officeDepth = 20;

            // 1. Base Floors with Regional Material Transitions
            function createFloorSection(x, z, w, d, mat) {
                const geo = new THREE.BoxGeometry(w, 0.2, d);
                const mesh = new THREE.Mesh(geo, mat);
                mesh.position.set(x, -0.1, z);
                mesh.receiveShadow = true;
                scene.add(mesh);
            }

            // Reception & Entrance (Polished Tile)
            createFloorSection(0, 7.5, 12, 5, materials.polishedTile);
            // Open Office (Carpet)
            createFloorSection(0, 0, 16, 10, materials.carpet);
            // Manager & Executive Offices (Wood Parquet)
            createFloorSection(-10, -5, 10, 10, materials.woodParquet);
            // Meeting Rooms (Carpet)
            createFloorSection(10, -5, 10, 10, materials.carpet);
            // Pantry & Toilet (Ceramic Tile)
            createFloorSection(10, 6, 10, 8, materials.ceramicTile);
            // Other Rooms & Corridors
            createFloorSection(-10, 6, 10, 8, materials.carpet);

            // 2. Wall Building Helper
            function buildWall(x, z, w, h, d, mat = materials.wallPaint, isGlass = false) {
                const geo = new THREE.BoxGeometry(w, h, d);
                const mesh = new THREE.Mesh(geo, mat);
                mesh.position.set(x, h / 2, z);
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                scene.add(mesh);

                if (!isGlass) {
                    addCollisionBox(x, z, w, d);
                }
            }

            // Outer Perimeter Walls
            buildWall(0, -10, 30, 4, 0.4, materials.wallDark); // Back
            buildWall(-15, 0, 0.4, 4, 20, materials.wallDark); // Left
            buildWall(15, 0, 0.4, 4, 20, materials.wallDark);  // Right
            buildWall(-9, 10, 12, 4, 0.4, materials.wallDark); // Front Left
            buildWall(9, 10, 12, 4, 0.4, materials.wallDark);  // Front Right

            // Glass Entrance Door Frame
            buildWall(0, 10, 6, 4, 0.2, materials.glass, true);

            // Room Partitions
            buildWall(-5, -5, 0.3, 4, 10, materials.wallPaint); // Left Zone Divider
            buildWall(5, -5, 0.3, 4, 10, materials.wallPaint);  // Right Zone Divider
            buildWall(-10, 2, 10, 4, 0.3, materials.wallPaint); // North Left Corridor Wall
            buildWall(10, 2, 10, 4, 0.3, materials.wallPaint);  // North Right Corridor Wall

            // Spotlights setup across rooms
            addCeilingSpot(0, 7.5);   // Reception
            addCeilingSpot(0, 0);     // Open Office
            addCeilingSpot(-10, -5);  // Manager
            addCeilingSpot(10, -5);   // Meeting Room
            addCeilingSpot(10, 6);    // Pantry

            // --- FURNITURE BUILDERS ---

            // Desk & Chair Combo Generator
            function createWorkstation(x, z, angle = 0) {
                const deskGroup = new THREE.Group();
                
                // Desk Table
                const deskGeo = new THREE.BoxGeometry(1.6, 0.75, 0.8);
                const deskMesh = new THREE.Mesh(deskGeo, materials.woodFurniture);
                deskMesh.position.y = 0.375;
                deskMesh.castShadow = true;
                deskGroup.add(deskMesh);

                // Monitor
                const monGeo = new THREE.BoxGeometry(0.6, 0.4, 0.05);
                const monMesh = new THREE.Mesh(monGeo, materials.metalBlack);
                monMesh.position.set(0, 0.95, -0.2);
                deskGroup.add(monMesh);

                // Chair
                const chairGeo = new THREE.BoxGeometry(0.5, 0.8, 0.5);
                const chairMesh = new THREE.Mesh(chairGeo, materials.fabricBlue);
                chairMesh.position.set(0, 0.4, 0.6);
                deskGroup.add(chairMesh);

                deskGroup.position.set(x, 0, z);
                deskGroup.rotation.y = angle;
                scene.add(deskGroup);

                addCollisionBox(x, z, 1.8, 1.2);
            }

            // 12 Open Office Workstations
            for (let i = 0; i < 3; i++) {
                for (let j = 0; j < 4; j++) {
                    createWorkstation(-4.5 + j * 3, -3 + i * 2.5);
                }
            }

            // Reception Counter
            const recepCounter = new THREE.Mesh(new THREE.BoxGeometry(3.5, 1.1, 1.2), materials.woodDark || materials.woodFurniture);
            recepCounter.position.set(0, 0.55, 6);
            recepCounter.castShadow = true;
            scene.add(recepCounter);
            addCollisionBox(0, 6, 3.5, 1.2);

            // Meeting Room 1 Table
            const meetTable = new THREE.Mesh(new THREE.BoxGeometry(4, 0.75, 1.8), materials.woodFurniture);
            meetTable.position.set(10, 0.375, -5);
            meetTable.castShadow = true;
            scene.add(meetTable);
            addCollisionBox(10, -5, 4.2, 2.0);

            // Pantry Kitchen Counter
            const pantryCounter = new THREE.Mesh(new THREE.BoxGeometry(4.5, 0.9, 0.8), materials.metalBlack);
            pantryCounter.position.set(10, 0.45, 8.5);
            pantryCounter.castShadow = true;
            scene.add(pantryCounter);
            addCollisionBox(10, 8.5, 4.5, 0.8);

            // Decorative Plants
            function createPlant(x, z) {
                const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.2, 0.6, 12), materials.polishedTile);
                pot.position.set(x, 0.3, z);
                const leaves = new THREE.Mesh(new THREE.DodecahedronGeometry(0.5), materials.plantGreen);
                leaves.position.set(x, 0.8, z);
                scene.add(pot);
                scene.add(leaves);
                addCollisionBox(x, z, 0.6, 0.6);
            }
            createPlant(-5.5, 7.5);
            createPlant(5.5, 7.5);
            createPlant(-13, -8);
            createPlant(13, -8);

            // --- ROOM REGIONS DEFINITION FOR UI LABEL ---
            roomRegions.push(
                { name: "RECEPTION AREA", minX: -6, maxX: 6, minZ: 4, maxZ: 10 },
                { name: "OPEN OFFICE", minX: -5, maxX: 5, minZ: -4, maxZ: 3 },
                { name: "MANAGER & PRIVATE OFFICES", minX: -15, maxX: -5, minZ: -10, maxZ: 2 },
                { name: "MEETING ROOM", minX: 5, maxX: 15, minZ: -10, maxZ: 2 },
                { name: "PANTRY & BREAK AREA", minX: 5, maxX: 15, minZ: 3, maxZ: 10 },
                { name: "HR, FINANCE & IT AREA", minX: -15, maxX: -5, minZ: 3, maxZ: 10 }
            );

            // --- MAIN CONTROLLABLE AGENT (HUMAN AVATAR) ---
            const agentGroup = new THREE.Group();

            // Head
            const headMesh = new THREE.Mesh(new THREE.SphereGeometry(0.25, 16, 16), materials.agentHead);
            headMesh.position.y = 1.55;
            headMesh.castShadow = true;
            agentGroup.add(headMesh);

            // Body / Torso
            const torsoMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.25, 0.7, 12), materials.agentBody);
            torsoMesh.position.y = 1.0;
            torsoMesh.castShadow = true;
            agentGroup.add(torsoMesh);

            // Legs
            const legLeft = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.65, 0.12), materials.metalBlack);
            legLeft.position.set(-0.1, 0.325, 0);
            agentGroup.add(legLeft);

            const legRight = legLeft.clone();
            legRight.position.set(0.1, 0.325, 0);
            agentGroup.add(legRight);

            // "YOU" Indicator Above Head
            const indicatorGeo = new THREE.ConeGeometry(0.12, 0.25, 4);
            const indicatorMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
            const indicator = new THREE.Mesh(indicatorGeo, indicatorMat);
            indicator.rotation.x = Math.PI;
            indicator.position.y = 2.0;
            agentGroup.add(indicator);

            // Set Starting Position at Reception
            agentGroup.position.set(0, 0, 7.5);
            scene.add(agentGroup);

            // --- WASD NAVIGATION & CAMERA TRACKING LOGIC ---
            const keysPressed = {};
            const moveSpeed = 0.12;

            window.addEventListener('keydown', (e) => {
                keysPressed[e.key.toLowerCase()] = true;
                if (e.key.toLowerCase() === 'c') {
                    toggleCameraMode();
                }
            });

            window.addEventListener('keyup', (e) => {
                keysPressed[e.key.toLowerCase()] = false;
            });

            // Camera Modes: 0 = Third Person Follow, 1 = Close Third Person, 2 = Free Orbit
            let cameraMode = 0;
            function toggleCameraMode() {
                cameraMode = (cameraMode + 1) % 3;
            }

            function checkCollision(newX, newZ) {
                const radius = 0.35;
                for (let box of collisionBoxes) {
                    if (newX + radius > box.minX && newX - radius < box.maxX &&
                        newZ + radius > box.minZ && newZ - radius < box.maxZ) {
                        return true; // Collision detected
                    }
                }
                return false;
            }

            function updateAgentMovement() {
                let dx = 0;
                let dz = 0;

                if (keysPressed['w'] || keysPressed['arrowup']) dz -= moveSpeed;
                if (keysPressed['s'] || keysPressed['arrowdown']) dz += moveSpeed;
                if (keysPressed['a'] || keysPressed['arrowleft']) dx -= moveSpeed;
                if (keysPressed['d'] || keysPressed['arrowright']) dx += moveSpeed;

                if (dx !== 0 || dz !== 0) {
                    const newX = agentGroup.position.x + dx;
                    const newZ = agentGroup.position.z + dz;

                    // Check boundaries & collisions
                    if (Math.abs(newX) < officeWidth / 2 - 0.5 && !checkCollision(newX, agentGroup.position.z)) {
                        agentGroup.position.x = newX;
                    }
                    if (Math.abs(newZ) < officeDepth / 2 - 0.5 && !checkCollision(agentGroup.position.x, newZ)) {
                        agentGroup.position.z = newZ;
                    }

                    // Rotate agent facing direction
                    const targetAngle = Math.atan2(dx, dz);
                    agentGroup.rotation.y = targetAngle;

                    // Idle bobbing / walk animation
                    indicator.position.y = 2.0 + Math.sin(Date.now() * 0.01) * 0.05;
                }

                // Update Controls Target to Agent
                controls.target.copy(agentGroup.position).add(new THREE.Vector3(0, 1.2, 0));

                if (cameraMode === 0) {
                    // Third Person Follow
                    const offset = new THREE.Vector3(0, 4, 6);
                    camera.position.lerp(agentGroup.position.clone().add(offset), 0.08);
                } else if (cameraMode === 1) {
                    // Close Third Person
                    const offset = new THREE.Vector3(0, 2.2, 3.2);
                    camera.position.lerp(agentGroup.position.clone().add(offset), 0.08);
                }
                // Mode 2 = Free Orbit (Camera handled strictly by OrbitControls)

                // Check Current Room Label
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

            // --- MINI MAP RENDERER ---
            const minimapCanvas = document.getElementById('minimap');
            const mmCtx = minimapCanvas.getContext('2d');

            function drawMiniMap() {
                mmCtx.clearRect(0, 0, minimapCanvas.width, minimapCanvas.height);
                
                // Map Scale
                const scaleX = minimapCanvas.width / officeWidth;
                const scaleY = minimapCanvas.height / officeDepth;

                // Draw Outer Boundary
                mmCtx.strokeStyle = "#334155";
                mmCtx.lineWidth = 2;
                mmCtx.strokeRect(0, 0, minimapCanvas.width, minimapCanvas.height);

                // Draw Agent Marker
                const mmAgentX = (agentGroup.position.x + officeWidth / 2) * scaleX;
                const mmAgentY = (agentGroup.position.z + officeDepth / 2) * scaleY;

                mmCtx.fillStyle = "#10b981";
                mmCtx.beginPath();
                mmCtx.arc(mmAgentX, mmAgentY, 4, 0, Math.PI * 2);
                mmCtx.fill();
            }

            // --- MAIN ANIMATION LOOP ---
            function animate() {
                requestAnimationFrame(animate);
                updateAgentMovement();
                controls.update();
                renderer.render(scene, camera);
                drawMiniMap();
            }
            animate();

            // Resize Responsive Handler
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });

            // Simulator Whatsapp Trigger
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
