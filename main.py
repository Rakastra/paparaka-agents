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
        <title>3D Isometric Architectural Cutaway Virtual Office - AI Agent - Sup</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { margin: 0; overflow: hidden; background-color: #0b0f19; font-family: 'Inter', sans-serif; user-select: none; }
            #webgl-container { width: 100vw; height: 100vh; display: block; }
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
                    <h1 class="font-bold text-sm text-emerald-400 tracking-wide">3D ARCHITECTURAL OFFICE</h1>
                    <p class="text-[11px] text-slate-400">Isometric Cutaway Model — AI Agent - Sup</p>
                </div>
            </div>
            <div id="room-label" class="mt-3 bg-slate-800 border border-slate-700/80 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-200 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span id="current-room-text">Lokasi: RECEPTION & LOBBY</span>
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

        <!-- WELCOME BANNER -->
        <div id="welcome-banner" class="absolute top-1/4 left-1/2 -translate-x-1/2 z-30 bg-slate-900/95 border border-emerald-500/50 text-white px-8 py-4 rounded-3xl shadow-2xl text-center transition-opacity duration-1000 pointer-events-none">
            <h2 class="text-lg font-bold text-emerald-400 mb-1">Interactive 3D Miniature Cutaway Office</h2>
            <p class="text-xs text-slate-300">Satu lantai kantor lengkap (30m x 20m). Putar kamera 360°, Zoom In, atau gunakan WASD untuk navigasi agent.</p>
        </div>

        <!-- UI OVERLAY: BOTTOM CONTROLS & COMMAND CENTER -->
        <div class="absolute bottom-4 left-4 right-4 z-20 flex flex-col md:flex-row justify-between items-end gap-4 pointer-events-none">
            
            <!-- Controls Legend -->
            <div class="bg-slate-900/90 backdrop-blur border border-slate-700/80 text-slate-300 p-3.5 rounded-2xl shadow-2xl text-xs space-y-1 pointer-events-auto">
                <div class="font-bold text-emerald-400 mb-1">🎮 Modus Kamera & Navigasi</div>
                <div><span class="bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded text-[10px] text-white">WASD</span> — Move Main Agent</div>
                <div><span class="bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded text-[10px] text-white">Mouse Drag</span> — Rotate 360° / Orbit</div>
                <div><span class="bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded text-[10px] text-white">Scroll</span> — Zoom Deep Desk / Full View</div>
                <div><span class="bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded text-[10px] text-white">C</span> — Switch Mode (Architectural / Agent View)</div>
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
            }, 4500);

            // --- THREE.JS ENGINE INITIALIZATION ---
            const container = document.getElementById('webgl-container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0b0f19);

            // CAMERA SETUP (Elevated 3/4 Isometric Perspective)
            const camera = new THREE.PerspectiveCamera(38, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(28, 26, 32); // Elevated isometric viewpoint

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
            controls.maxPolarAngle = Math.PI / 2 - 0.05; // Keep above floor line
            controls.minDistance = 4;
            controls.maxDistance = 65;
            controls.target.set(0, 0, 0); // Center on office miniature

            // LIGHTING SETUP (Architectural Studio Quality)
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
            scene.add(ambientLight);

            const sunLight = new THREE.DirectionalLight(0xfffaf0, 0.95);
            sunLight.position.set(25, 40, 20);
            sunLight.castShadow = true;
            sunLight.shadow.mapSize.width = 2048;
            sunLight.shadow.mapSize.height = 2048;
            sunLight.shadow.camera.near = 0.5;
            sunLight.shadow.camera.far = 100;
            sunLight.shadow.camera.left = -22;
            sunLight.shadow.camera.right = 22;
            sunLight.shadow.camera.top = 18;
            sunLight.shadow.camera.bottom = -18;
            scene.add(sunLight);

            // Soft Fill Light for Cutaway Visibility
            const fillLight = new THREE.DirectionalLight(0x93c5fd, 0.35);
            fillLight.position.set(-20, 20, -20);
            scene.add(fillLight);

            // --- MATERIAL PALETTE (Realistic Corporate) ---
            const materials = {
                carpet: new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.8 }),
                woodFloor: new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.4 }),
                polishedTile: new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.2 }),
                ceramicTile: new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.3 }),
                outerWall: new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.5 }),
                innerWall: new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.7 }),
                lowWall: new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.6 }),
                glass: new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.25, roughness: 0.05, transmission: 0.9 }),
                woodFurniture: new THREE.MeshStandardMaterial({ color: 0x451a03, roughness: 0.5 }),
                metalDark: new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8, roughness: 0.2 }),
                fabricBlue: new THREE.MeshStandardMaterial({ color: 0x1d4ed8, roughness: 0.7 }),
                plantGreen: new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.6 }),
                agentBody: new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.5 }),
                agentHead: new THREE.MeshStandardMaterial({ color: 0xfde047, roughness: 0.4 }),
                npcBody: new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.5 })
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

            // --- FLOOR PLAN CONSTRUCTIONS (30m x 20m Cutaway Architectural) ---
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
            createFloorSection(0, 4, 10, 8, materials.polishedTile);    // Reception / Lobby
            createFloorSection(0, -4, 18, 8, materials.carpet);          // Open Office Area
            createFloorSection(-10, -5, 10, 10, materials.woodFloor);    // Manager & Private Offices
            createFloorSection(10, -5, 10, 10, materials.carpet);        // Meeting Rooms
            createFloorSection(-10, 5, 10, 8, materials.carpet);         // HR, Finance, IT
            createFloorSection(10, 5, 10, 8, materials.ceramicTile);     // Pantry, Storage, Toilet

            // WALL BUILDING HELPER (Low/Cutaway Front Walls for Unobstructed View)
            function buildWall(x, z, w, h, d, mat = materials.innerWall, isGlass = false) {
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

            // Cutaway Outer Frame (Rear & Side Walls High, Front Wall Removed/Low)
            buildWall(0, -10, 30, 3.2, 0.4, materials.outerWall);  // Rear Back Wall (Full)
            buildWall(-15, 0, 0.4, 3.2, 20, materials.outerWall);  // Left Exterior Wall
            buildWall(15, 0, 0.4, 3.2, 20, materials.outerWall);   // Right Exterior Wall
            buildWall(-10, 10, 10, 0.6, 0.4, materials.lowWall);   // Cutaway Front Left Wall
            buildWall(10, 10, 10, 0.6, 0.4, materials.lowWall);    // Cutaway Front Right Wall

            // Front Glass Entrance
            buildWall(0, 10, 10, 2.8, 0.1, materials.glass, true);

            // Interior Partitions (Glass and Low Walls to maximize interior view)
            buildWall(-5, -5, 0.2, 2.8, 10, materials.glass, true); // Left Zone Partition
            buildWall(5, -5, 0.2, 2.8, 10, materials.glass, true);  // Right Zone Partition
            buildWall(-10, 1, 10, 2.8, 0.2, materials.innerWall);   // HR/Finance Division Wall
            buildWall(10, 1, 10, 2.8, 0.2, materials.innerWall);    // Pantry/Storage Division Wall

            // --- FURNITURE DENSITY & SPECIFIC ROOM OBJECTS ---

            // 1. Reception & Waiting Area
            const recepCounter = new THREE.Mesh(new THREE.BoxGeometry(3.2, 1.0, 1.0), materials.woodFurniture);
            recepCounter.position.set(0, 0.5, 5);
            recepCounter.castShadow = true;
            scene.add(recepCounter);
            addCollisionBox(0, 5, 3.2, 1.0);

            // Reception PC & Chair
            const monRec = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.35, 0.05), materials.metalDark);
            monRec.position.set(0, 1.15, 4.8);
            scene.add(monRec);

            // Waiting Sofas
            const sofa = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.6, 0.8), materials.fabricBlue);
            sofa.position.set(-3, 0.3, 7.5);
            sofa.castShadow = true;
            scene.add(sofa);
            addCollisionBox(-3, 7.5, 2.0, 0.8);

            // 2. Open Office (12 Workstations with Natural Variations)
            function createWorkstation(x, z, type = 0) {
                const group = new THREE.Group();
                
                // Desk
                const desk = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.75, 0.8), materials.woodFurniture);
                desk.position.y = 0.375;
                desk.castShadow = true;
                group.add(desk);

                // Chair
                const chair = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.8, 0.5), materials.fabricBlue);
                chair.position.set(0, 0.4, 0.65);
                group.add(chair);

                // Equipment Variation
                if (type === 0) { // Dual Monitor
                    const m1 = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.35, 0.04), materials.metalDark);
                    m1.position.set(-0.25, 0.92, -0.2);
                    m1.rotation.y = 0.15;
                    const m2 = m1.clone();
                    m2.position.set(0.25, 0.92, -0.2);
                    m2.rotation.y = -0.15;
                    group.add(m1, m2);
                } else if (type === 1) { // Laptop & Coffee
                    const laptop = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.02, 0.3), materials.metalDark);
                    laptop.position.set(0, 0.76, -0.1);
                    const cup = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.03, 0.1), materials.polishedTile);
                    cup.position.set(0.4, 0.8, 0.1);
                    group.add(laptop, cup);
                } else { // Single Monitor & Notebook
                    const m1 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.38, 0.04), materials.metalDark);
                    m1.position.set(0, 0.94, -0.2);
                    const book = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.02, 0.28), materials.fabricBlue);
                    book.position.set(-0.4, 0.76, 0.1);
                    group.add(m1, book);
                }

                group.position.set(x, 0, z);
                scene.add(group);
                addCollisionBox(x, z, 1.6, 1.2);
            }

            // Layout 12 Desks
            for (let r = 0; r < 3; r++) {
                for (let c = 0; c < 4; c++) {
                    createWorkstation(-4.5 + c * 3.0, -2.5 - r * 2.5, (r + c) % 3);
                }
            }

            // 3. Manager Office
            const mgrDesk = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.8, 1.0), materials.woodFurniture);
            mgrDesk.position.set(-10, 0.4, -6);
            mgrDesk.castShadow = true;
            scene.add(mgrDesk);
            addCollisionBox(-10, -6, 2.4, 1.2);

            // 4. Meeting Rooms
            const meetTable1 = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.75, 1.6), materials.woodFurniture);
            meetTable1.position.set(10, 0.375, -6);
            meetTable1.castShadow = true;
            scene.add(meetTable1);
            addCollisionBox(10, -6, 3.8, 1.8);

            // Wall Display Screen in Meeting Room
            const tvScreen = new THREE.Mesh(new THREE.BoxGeometry(2.0, 1.1, 0.05), materials.metalDark);
            tvScreen.position.set(10, 2.0, -9.8);
            scene.add(tvScreen);

            // 5. Sales Area Dashboard Screen
            const salesBoard = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.0, 0.05), materials.metalDark);
            salesBoard.position.set(-14.7, 2.0, 5);
            salesBoard.rotation.y = Math.PI / 2;
            scene.add(salesBoard);

            // 6. Pantry
            const pantryBar = new THREE.Mesh(new THREE.BoxGeometry(4.0, 0.9, 0.8), materials.metalDark);
            pantryBar.position.set(10, 0.45, 8.5);
            pantryBar.castShadow = true;
            scene.add(pantryBar);
            addCollisionBox(10, 8.5, 4.0, 0.8);

            // Decorative Plants
            function addPlant(x, z) {
                const pot = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.2, 0.5, 12), materials.polishedTile);
                pot.position.set(x, 0.25, z);
                const leaves = new THREE.Mesh(new THREE.DodecahedronGeometry(0.45), materials.plantGreen);
                leaves.position.set(x, 0.7, z);
                scene.add(pot, leaves);
                addCollisionBox(x, z, 0.5, 0.5);
            }
            addPlant(-4.8, 5.0);
            addPlant(4.8, 5.0);
            addPlant(-14, -9);
            addPlant(14, -9);

            // 7. Decorative NPC Employees
            function addNPC(x, z, rot = 0) {
                const npc = new THREE.Group();
                const head = new THREE.Mesh(new THREE.SphereGeometry(0.22, 12, 12), materials.agentHead);
                head.position.y = 1.45;
                const body = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.22, 0.65, 10), materials.npcBody);
                body.position.y = 0.95;
                npc.add(head, body);
                npc.position.set(x, 0, z);
                npc.rotation.y = rot;
                scene.add(npc);
            }
            addNPC(-10, -5, Math.PI / 4); // Manager sitting
            addNPC(10, -5, -Math.PI / 2); // Meeting member
            addNPC(2, 5, 0);             // Reception visitor

            // --- ROOM REGIONS FOR LABELS ---
            roomRegions.push(
                { name: "RECEPTION & LOBBY", minX: -5, maxX: 5, minZ: 2, maxZ: 10 },
                { name: "OPEN OFFICE AREA", minX: -5, maxX: 5, minZ: -9, maxZ: 1 },
                { name: "MANAGER OFFICE", minX: -15, maxX: -5, minZ: -10, maxZ: -1 },
                { name: "MEETING ROOMS", minX: 5, maxX: 15, minZ: -10, maxZ: -1 },
                { name: "PANTRY & BREAK AREA", minX: 5, maxX: 15, minZ: 2, maxZ: 10 },
                { name: "HR, FINANCE & IT", minX: -15, maxX: -5, minZ: 2, maxZ: 10 }
            );

            // --- MAIN CONTROLLABLE AGENT (HUMAN AVATAR) ---
            const agentGroup = new THREE.Group();

            const headMesh = new THREE.Mesh(new THREE.SphereGeometry(0.24, 16, 16), materials.agentHead);
            headMesh.position.y = 1.52;
            headMesh.castShadow = true;
            agentGroup.add(headMesh);

            const torsoMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.24, 0.68, 12), materials.agentBody);
            torsoMesh.position.y = 0.98;
            torsoMesh.castShadow = true;
            agentGroup.add(torsoMesh);

            const legL = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.62, 0.11), materials.metalDark);
            legL.position.set(-0.09, 0.31, 0);
            const legR = legL.clone();
            legR.position.set(0.09, 0.31, 0);
            agentGroup.add(legL, legR);

            // "YOU" Selection Indicator
            const indicatorGeo = new THREE.ConeGeometry(0.12, 0.22, 4);
            const indicatorMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
            const indicator = new THREE.Mesh(indicatorGeo, indicatorMat);
            indicator.rotation.x = Math.PI;
            indicator.position.y = 1.95;
            agentGroup.add(indicator);

            // Start Position at Open Office / Lobby Threshold
            agentGroup.position.set(0, 0, 2.5);
            scene.add(agentGroup);

            // --- NAVIGATION & DUAL CAMERA MODES ---
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

            // Camera Mode: 0 = Architectural Cutaway View, 1 = Third Person Agent Follow
            let cameraMode = 0;
            function toggleCameraMode() {
                cameraMode = (cameraMode + 1) % 2;
            }

            function checkCollision(newX, newZ) {
                const radius = 0.35;
                for (let box of collisionBoxes) {
                    if (newX + radius > box.minX && newX - radius < box.maxX &&
                        newZ + radius > box.minZ && newZ - radius < box.maxZ) {
                        return true;
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

                    if (Math.abs(newX) < officeWidth / 2 - 0.5 && !checkCollision(newX, agentGroup.position.z)) {
                        agentGroup.position.x = newX;
                    }
                    if (Math.abs(newZ) < officeDepth / 2 - 0.5 && !checkCollision(agentGroup.position.x, newZ)) {
                        agentGroup.position.z = newZ;
                    }

                    agentGroup.rotation.y = Math.atan2(dx, dz);
                    indicator.position.y = 1.95 + Math.sin(Date.now() * 0.01) * 0.04;
                }

                // Camera Logic
                if (cameraMode === 0) {
                    // Architectural Cutaway Mode (Fixed Center Orbit)
                    controls.target.lerp(new THREE.Vector3(0, 0, 0), 0.05);
                } else {
                    // Agent View Mode (Follows Agent)
                    controls.target.lerp(agentGroup.position.clone().add(new THREE.Vector3(0, 1.2, 0)), 0.08);
                    const targetCamPos = agentGroup.position.clone().add(new THREE.Vector3(0, 3.5, 5.0));
                    camera.position.lerp(targetCamPos, 0.05);
                }

                // Update Room Label UI
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

            // --- MINI MAP DRAWING ---
            const minimapCanvas = document.getElementById('minimap');
            const mmCtx = minimapCanvas.getContext('2d');

            function drawMiniMap() {
                mmCtx.clearRect(0, 0, minimapCanvas.width, minimapCanvas.height);
                const scaleX = minimapCanvas.width / officeWidth;
                const scaleY = minimapCanvas.height / officeDepth;

                // Frame
                mmCtx.strokeStyle = "#475569";
                mmCtx.lineWidth = 1.5;
                mmCtx.strokeRect(0, 0, minimapCanvas.width, minimapCanvas.height);

                // Agent Marker
                const mmX = (agentGroup.position.x + officeWidth / 2) * scaleX;
                const mmY = (agentGroup.position.z + officeDepth / 2) * scaleY;

                mmCtx.fillStyle = "#10b981";
                mmCtx.beginPath();
                mmCtx.arc(mmX, mmY, 3.5, 0, Math.PI * 2);
                mmCtx.fill();
            }

            // --- ANIMATION LOOP ---
            function animate() {
                requestAnimationFrame(animate);
                updateAgentMovement();
                controls.update();
                renderer.render(scene, camera);
                drawMiniMap();
            }
            animate();

            // Window Resize Handler
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
