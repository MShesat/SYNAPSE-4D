"""
Synapse 4D - 3D Holographic Neural Core & Real-Time Cognitive Pipeline HUD
Features:
  - 3D Perspective Projection Engine (rotatable camera, depth-of-field, helical spine, orbital rings)
  - Real-time animated 4-stage cognitive processing wave (D1 -> D2 -> D3 -> D4)
  - Floating 3D epistemic telemetry labels (Hebbian delta weights, Truth Hierarchy checks)
  - Live Neural Oscilloscope & Real-Time Cognitive Stream log
"""

import http.server
import socketserver
import json
import urllib.parse
import time
from pathlib import Path
from typing import Dict, Any

from synapse4d.core import SynapseEngine

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synapse 4D — 3D Holographic Neural Core</title>
    <style>
        :root {
            --bg-void: #020307;
            --bg-panel: rgba(6, 10, 19, 0.84);
            --border-glow: rgba(0, 240, 255, 0.28);
            --neon-cyan: #00f0ff;
            --neon-magenta: #ff007f;
            --neon-violet: #9d4edd;
            --neon-emerald: #00f59b;
            --neon-amber: #ffb703;
            --text-primary: #eef2f6;
            --text-dim: #7d8590;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: "JetBrains Mono", "SF Mono", Consolas, monospace; }
        body {
            background: var(--bg-void);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            user-select: none;
        }

        /* Top HUD Bar */
        header {
            background: rgba(2, 4, 8, 0.92);
            border-bottom: 1px solid var(--border-glow);
            padding: 10px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
            box-shadow: 0 4px 35px rgba(0, 240, 255, 0.12);
        }
        .brand { display: flex; align-items: center; gap: 12px; }
        .brand-badge {
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-magenta));
            color: #000;
            font-weight: 900;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 13px;
            letter-spacing: 1.5px;
            box-shadow: 0 0 18px rgba(0, 240, 255, 0.6);
        }
        .brand-title { font-size: 15px; font-weight: 800; color: #fff; letter-spacing: 1px; }
        .version-tag {
            border: 1px solid var(--neon-cyan);
            color: var(--neon-cyan);
            font-size: 10px;
            padding: 2px 8px;
            border-radius: 10px;
            background: rgba(0, 240, 255, 0.1);
        }

        .hud-stats { display: flex; gap: 22px; font-size: 12px; }
        .hud-stat-item { display: flex; flex-direction: column; align-items: flex-end; }
        .hud-stat-val { font-weight: 800; color: var(--neon-cyan); font-size: 14px; text-shadow: 0 0 8px rgba(0, 240, 255, 0.6); }
        .hud-stat-lbl { color: var(--text-dim); font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; }

        .btn-toggle-hud {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(0, 240, 255, 0.35);
            color: var(--neon-cyan);
            padding: 7px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-toggle-hud:hover {
            background: rgba(0, 240, 255, 0.2);
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
        }

        .btn-pulse {
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-magenta));
            color: #000;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 900;
            font-size: 11px;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 0 20px rgba(255, 0, 127, 0.5);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .btn-pulse:hover { transform: scale(1.04); box-shadow: 0 0 30px rgba(0, 240, 255, 0.9); }

        /* Main Workspace */
        #workspace {
            position: relative;
            flex: 1;
            display: flex;
            width: 100vw;
            height: calc(100vh - 54px);
            overflow: hidden;
        }

        #neural-canvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
            cursor: grab;
        }
        #neural-canvas:active { cursor: grabbing; }

        /* Floating HUD Side Panels */
        .hud-panel {
            position: absolute;
            z-index: 10;
            background: var(--bg-panel);
            border: 1px solid var(--border-glow);
            border-radius: 10px;
            backdrop-filter: blur(16px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.75);
            display: flex;
            flex-direction: column;
            pointer-events: auto;
        }

        /* Left Panel */
        #panel-left {
            top: 16px;
            left: 16px;
            width: 330px;
            max-height: calc(100vh - 140px);
            padding: 14px;
            gap: 12px;
        }
        .panel-title {
            font-size: 11px;
            font-weight: 800;
            color: var(--neon-cyan);
            text-transform: uppercase;
            letter-spacing: 1px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 240, 255, 0.15);
            padding-bottom: 6px;
        }
        textarea.hud-text {
            width: 100%;
            height: 130px;
            background: rgba(0, 0, 0, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            padding: 8px;
            color: #d1d5db;
            font-size: 11px;
            line-height: 1.4;
            resize: none;
            outline: none;
        }
        textarea.hud-text:focus { border-color: var(--neon-cyan); box-shadow: 0 0 10px rgba(0, 240, 255, 0.3); }

        /* Oscilloscope & Live Stream */
        #oscilloscope {
            width: 100%;
            height: 54px;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(0, 240, 255, 0.2);
            border-radius: 6px;
        }
        #live-stream {
            height: 115px;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 6px;
            padding: 8px;
            font-size: 10px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .stream-line { color: #9ca3af; line-height: 1.3; }
        .stream-line span.ts { color: var(--neon-cyan); font-weight: 700; margin-right: 4px; }
        .stream-line span.tag { color: var(--neon-magenta); font-weight: 700; }

        /* Right Panel */
        #panel-right {
            top: 16px;
            right: 16px;
            width: 340px;
            max-height: calc(100vh - 140px);
            padding: 14px;
            gap: 12px;
        }
        .search-row { display: flex; gap: 6px; }
        .search-input {
            flex: 1;
            background: rgba(0, 0, 0, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 7px 10px;
            border-radius: 6px;
            color: #fff;
            font-size: 11px;
            outline: none;
        }
        .search-input:focus { border-color: var(--neon-magenta); }
        .results-box {
            display: flex;
            flex-direction: column;
            gap: 6px;
            max-height: 190px;
            overflow-y: auto;
        }
        .result-entry {
            background: rgba(255, 255, 255, 0.03);
            border-left: 2px solid var(--neon-cyan);
            padding: 7px 9px;
            font-size: 10px;
            border-radius: 0 5px 5px 0;
        }
        .result-entry.alt { border-left-color: var(--neon-magenta); }

        #neuron-detail {
            background: rgba(0, 240, 255, 0.06);
            border: 1px solid rgba(0, 240, 255, 0.25);
            padding: 10px;
            border-radius: 6px;
            font-size: 11px;
            display: block;
        }

        /* Bottom Real-Time Cognitive Pipeline Bar */
        #pipeline-bar {
            position: absolute;
            bottom: 16px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 20;
            background: rgba(5, 9, 18, 0.9);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 10px 20px;
            display: flex;
            align-items: center;
            gap: 14px;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8);
        }
        .stage-pill {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            font-size: 11px;
            font-weight: 700;
            color: var(--text-dim);
            transition: all 0.25s;
        }
        .stage-pill.active {
            color: #fff;
            border-color: var(--neon-cyan);
            background: rgba(0, 240, 255, 0.16);
            box-shadow: 0 0 18px rgba(0, 240, 255, 0.45);
            transform: translateY(-2px);
        }
        .stage-pill.active-magenta {
            color: #fff;
            border-color: var(--neon-magenta);
            background: rgba(255, 0, 127, 0.2);
            box-shadow: 0 0 18px rgba(255, 0, 127, 0.5);
            transform: translateY(-2px);
        }
        .stage-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--text-dim);
        }
        .stage-pill.active .stage-dot {
            background: var(--neon-cyan);
            box-shadow: 0 0 8px var(--neon-cyan);
        }
        .stage-pill.active-magenta .stage-dot {
            background: var(--neon-magenta);
            box-shadow: 0 0 8px var(--neon-magenta);
        }
        .stage-arrow { color: rgba(0, 240, 255, 0.35); font-size: 12px; font-weight: 900; }

        /* 3D Camera Controls Hint */
        #cam-controls {
            position: absolute;
            bottom: 72px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 15;
            font-size: 10px;
            color: rgba(0, 240, 255, 0.65);
            background: rgba(0, 0, 0, 0.5);
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid rgba(0, 240, 255, 0.15);
            pointer-events: none;
        }

        #toast {
            position: fixed;
            top: 70px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, var(--neon-magenta), var(--neon-violet));
            color: #fff;
            padding: 10px 24px;
            border-radius: 8px;
            font-weight: 800;
            font-size: 12px;
            display: none;
            box-shadow: 0 0 25px rgba(255, 0, 127, 0.8);
            z-index: 200;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <span class="brand-badge">SYNAPSE 4D</span>
            <span class="brand-title">3D HOLOGRAPHIC NEURAL CORE</span>
            <span class="version-tag">OWNER PRO v1.5</span>
        </div>
        
        <div class="hud-stats">
            <div class="hud-stat-item">
                <span id="stat-nodes" class="hud-stat-val">28</span>
                <span class="hud-stat-lbl">Neuronas 3D</span>
            </div>
            <div class="hud-stat-item">
                <span id="stat-synapses" class="hud-stat-val">136</span>
                <span class="hud-stat-lbl">Sinapsis Activas</span>
            </div>
            <div class="hud-stat-item">
                <span id="stat-ops" class="hud-stat-val" style="color:var(--neon-magenta)">240/s</span>
                <span class="hud-stat-lbl">Impulsos / Seg</span>
            </div>
            <div class="hud-stat-item">
                <span id="stat-health" class="hud-stat-val" style="color:var(--neon-emerald)">100%</span>
                <span class="hud-stat-lbl">Integridad 4D</span>
            </div>
        </div>

        <div style="display:flex; gap:10px; align-items:center;">
            <button class="btn-toggle-hud" onclick="toggleAutoRotate()" id="btn-rot">
                🔄 ÓRBITA 3D: ON
            </button>
            <button class="btn-toggle-hud" onclick="toggleHUD()">
                👁️ MODO HOLOGRAMA PURO
            </button>
            <button class="btn-pulse" onclick="triggerConsolidation()">
                ⚡ PROCESAR Y CONSOLIDAR 4D
            </button>
        </div>
    </header>

    <div id="workspace">
        <canvas id="neural-canvas"></canvas>

        <!-- Panel Izquierdo: Foco D1 + Osciloscopio en Tiempo Real -->
        <div id="panel-left" class="hud-panel">
            <div class="panel-title">
                <span>D1: Buffer de Atención Activa</span>
                <button onclick="saveFocus()" style="background:none; border:1px solid var(--neon-cyan); color:var(--neon-cyan); border-radius:4px; padding:2px 6px; font-size:9px; cursor:pointer;">GUARDAR</button>
            </div>
            <textarea id="scratchpad" class="hud-text" spellcheck="false" placeholder="Cargando foco de trabajo..."></textarea>
            
            <div class="panel-title">
                <span>Osciloscopio Sináptico (Tiempo Real)</span>
                <span id="osc-state" style="color:var(--neon-emerald); font-size:9px;">● GAMMA 60Hz</span>
            </div>
            <canvas id="oscilloscope" width="300" height="54"></canvas>

            <div class="panel-title">
                <span>Flujo de Procesamiento en Vivo</span>
            </div>
            <div id="live-stream"></div>
        </div>

        <!-- Panel Derecho: Sonda Semántica & Inspector 3D -->
        <div id="panel-right" class="hud-panel">
            <div class="panel-title">
                <span>Sonda de Resonancia Semántica</span>
            </div>
            <div class="search-row">
                <input id="search-query" class="search-input" type="text" placeholder="Consultar recuerdo o concepto..." onkeydown="if(event.key==='Enter') executeSearch()">
                <button onclick="executeSearch()" style="background:var(--neon-magenta); color:#fff; border:none; padding:0 12px; border-radius:6px; font-weight:800; font-size:11px; cursor:pointer;">SONDA</button>
            </div>
            <div id="search-results" class="results-box">
                <div style="color:var(--text-dim); font-size:10px; text-align:center; padding:12px;">Escribe una consulta para excitar la matriz 3D.</div>
            </div>

            <div class="panel-title" style="margin-top:4px;">
                <span>Telemetría de Neurona Seleccionada</span>
            </div>
            <div id="neuron-detail">
                <div id="detail-title" style="font-weight:800; color:var(--neon-cyan); margin-bottom:4px;">Núcleo Chronos Activo</div>
                <div id="detail-desc" style="color:#d1d5db; line-height:1.4; font-size:10px;">Arrastra con el mouse para rotar el cerebro en 3D o haz clic en cualquier neurona para disparar potenciales de acción.</div>
            </div>
        </div>

        <div id="cam-controls">
            🖱️ Arrastra para rotar en 3D  |  🔍 Rueda del mouse para Zoom  |  ⚡ Clic en neurona para excitar
        </div>

        <!-- Barra Inferior: Pipeline de Procesamiento en Tiempo Real -->
        <div id="pipeline-bar">
            <div id="stage-0" class="stage-pill active">
                <span class="stage-dot"></span>
                <span>D1: INGESTA DE ATENCIÓN</span>
            </div>
            <span class="stage-arrow">➔</span>
            <div id="stage-1" class="stage-pill">
                <span class="stage-dot"></span>
                <span>D2: DESTILACIÓN & VERDAD</span>
            </div>
            <span class="stage-arrow">➔</span>
            <div id="stage-2" class="stage-pill">
                <span class="stage-dot"></span>
                <span>D3: ESPINA CHRONOS (HEBB)</span>
            </div>
            <span class="stage-arrow">➔</span>
            <div id="stage-3" class="stage-pill">
                <span class="stage-dot"></span>
                <span>D4: MALLA HIPERGRAFO</span>
            </div>
        </div>
    </div>

    <div id="toast"></div>

    <script>
        const canvas = document.getElementById("neural-canvas");
        const ctx = canvas.getContext("2d");
        const oscCanvas = document.getElementById("oscilloscope");
        const oscCtx = oscCanvas.getContext("2d");

        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight - 54;

        window.addEventListener("resize", () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight - 54;
        });

        // 3D Camera & Perspective State
        let rotY = 0.22;
        let rotX = 0.08;
        let autoRotate = true;
        let cameraZ = 920;
        const fov = 720;

        let isDragging = false;
        let lastMouseX = 0;
        let lastMouseY = 0;

        // Neural 3D Structures
        let layers = [[], [], [], []];
        let allNodes = [];
        let synapses = [];
        let pulses = [];
        let floatingTelemetry = [];
        let selectedNode = null;
        let hoveredNode = null;

        // Real-Time Processing Wave State
        let activeStage = 0;
        let stageTimer = 0;
        let hyperProcessing = 0; // Boosted during consolidation/search
        let oscHistory = new Array(100).fill(0);
        let timeTick = 0;

        const TELEMETRY_TAGS = [
            "Δw +0.20 LTP", "AXIOM OK", "O(1) PAGE", "[[RECIPROCAL]]",
            "HEBB POTENTIATED", "CHRONOS VALID", "SIM > 0.85", "ZERO-ORPHAN"
        ];

        function logStream(tag, msg) {
            const box = document.getElementById("live-stream");
            const now = new Date().toLocaleTimeString("es-PE", { hour12: false });
            const line = document.createElement("div");
            line.className = "stream-line";
            line.innerHTML = `<span class="ts">[${now}]</span><span class="tag">[${tag}]</span> ${msg}`;
            box.prepend(line);
            if (box.children.length > 35) box.removeChild(box.lastChild);
        }

        function showToast(msg) {
            const t = document.getElementById("toast");
            t.innerText = msg;
            t.style.display = "block";
            setTimeout(() => { t.style.display = "none"; }, 3200);
        }

        function toggleAutoRotate() {
            autoRotate = !autoRotate;
            document.getElementById("btn-rot").innerText = autoRotate ? "🔄 ÓRBITA 3D: ON" : "⏸️ ÓRBITA 3D: OFF";
        }

        let hudVisible = true;
        function toggleHUD() {
            hudVisible = !hudVisible;
            document.getElementById("panel-left").style.display = hudVisible ? "flex" : "none";
            document.getElementById("panel-right").style.display = hudVisible ? "flex" : "none";
        }

        // 3D Projection Math
        function project3D(x, y, z) {
            // Rotate around Y axis
            const cosY = Math.cos(rotY);
            const sinY = Math.sin(rotY);
            const x1 = x * cosY - z * sinY;
            const z1 = z * cosY + x * sinY;

            // Rotate around X axis
            const cosX = Math.cos(rotX);
            const sinX = Math.sin(rotX);
            const y2 = y * cosX - z1 * sinX;
            const z2 = z1 * cosX + y * sinX;

            const depth = cameraZ + z2;
            const scale = fov / Math.max(depth, 80);

            return {
                sx: width * 0.5 + x1 * scale,
                sy: height * 0.48 + y2 * scale,
                scale: scale,
                depth: depth,
                z2: z2
            };
        }

        async function loadState() {
            try {
                const res = await fetch("/api/state");
                const data = await res.json();
                
                document.getElementById("scratchpad").value = data.working_context.active_context || "";
                document.getElementById("stat-nodes").innerText = data.audit.total_nodes;
                document.getElementById("stat-health").innerText = data.audit.health_score;

                build3DNeuralNetwork(data.graph_nodes, data.graph_edges);
                logStream("CORE", `Matriz 3D sincronizada: ${data.audit.total_nodes} neuronas en línea.`);
            } catch (err) {
                console.error("Error loading state:", err);
            }
        }

        function build3DNeuralNetwork(nodes, edges) {
            layers = [[], [], [], []];
            allNodes = [];
            synapses = [];
            pulses = [];

            nodes.forEach((n, idx) => {
                let layerIdx = 3;
                if (n.id.includes("contexto") || n.id.includes("perfil") || n.id.includes("Inicio")) layerIdx = 0;
                else if (n.id.includes("regla") || n.id.includes("antipatron") || n.id.includes("exito")) layerIdx = 1;
                else if (idx % 2 === 0) layerIdx = 2; // Dense D3 Chronos Spine

                const nodeObj = {
                    id: n.id,
                    label: n.label,
                    layer: layerIdx,
                    x3d: 0, y3d: 0, z3d: 0,
                    sx: 0, sy: 0, scale: 1, depth: 0,
                    baseRadius: layerIdx === 2 ? 7.2 : 5.5,
                    color: layerIdx === 0 ? "#00f0ff" : (layerIdx === 1 ? "#00f59b" : (layerIdx === 2 ? "#ff007f" : "#9d4edd")),
                    firing: 0,
                    weight: (1.0 + Math.random() * 1.4).toFixed(2)
                };
                layers[layerIdx].push(nodeObj);
                allNodes.push(nodeObj);
            });

            // Assign 3D Volumetric Coordinates
            const layerX = [-310, -110, 60, 290];

            layers.forEach((layerNodes, lIdx) => {
                const count = layerNodes.length;
                layerNodes.forEach((node, nIdx) => {
                    const norm = count > 1 ? (nIdx / (count - 1)) - 0.5 : 0;
                    node.y3d = norm * 440;

                    if (lIdx === 2) {
                        // D3 Chronos Spine: 3D Double Helix / Cylindrical Core
                        const angle = nIdx * 0.65;
                        node.x3d = layerX[lIdx] + Math.cos(angle) * 28;
                        node.z3d = Math.sin(angle) * 65;
                    } else {
                        // Curved 3D Cerebral Hemisphere Arcs
                        const archAngle = norm * Math.PI * 0.85;
                        node.x3d = layerX[lIdx] + Math.cos(archAngle) * 35;
                        node.z3d = Math.sin(archAngle) * 160;
                    }
                });
            });

            // Build Dense 3D Synaptic Mesh
            for (let l = 0; l < 3; l++) {
                const curr = layers[l];
                const next = layers[l + 1];

                curr.forEach(fromNode => {
                    next.forEach(toNode => {
                        if (Math.random() < 0.68 || (l === 1 && l + 1 === 2)) {
                            synapses.push({
                                from: fromNode,
                                to: toNode,
                                stage: l,
                                weight: Math.random() * 0.85 + 0.25,
                                colorMode: l % 2 === 0 ? "cyan-magenta" : "magenta-cyan"
                            });
                        }
                    });
                });
            }

            document.getElementById("stat-synapses").innerText = synapses.length;

            for (let p = 0; p < 95; p++) {
                spawnPulse();
            }
        }

        function spawnPulse(forceFromNode = null, targetStage = null) {
            if (synapses.length === 0) return;
            let pool = synapses;
            if (forceFromNode) {
                pool = synapses.filter(s => s.from === forceFromNode);
            } else if (targetStage !== null) {
                pool = synapses.filter(s => s.stage === targetStage);
            }
            if (pool.length === 0) pool = synapses;

            const s = pool[Math.floor(Math.random() * pool.length)];
            const speedBoost = hyperProcessing > 0 ? 2.4 : 1.0;
            pulses.push({
                synapse: s,
                progress: 0,
                speed: (0.009 + Math.random() * 0.014) * speedBoost,
                color: s.stage === 1 ? "#ff007f" : (Math.random() > 0.45 ? "#00f0ff" : "#00f59b")
            });
        }

        function spawnTelemetry(node, customText = null) {
            if (floatingTelemetry.length > 18) return;
            const text = customText || TELEMETRY_TAGS[Math.floor(Math.random() * TELEMETRY_TAGS.length)];
            floatingTelemetry.push({
                node: node,
                text: text,
                life: 1.0,
                offsetY: 0
            });
        }

        function updatePipelineUI(stage) {
            for (let i = 0; i < 4; i++) {
                const el = document.getElementById(`stage-${i}`);
                el.className = "stage-pill";
                if (i === stage) {
                    el.classList.add(i === 2 ? "active-magenta" : "active");
                }
            }
        }

        function drawOscilloscope() {
            const w = oscCanvas.width;
            const h = oscCanvas.height;
            oscCtx.fillStyle = "rgba(0, 0, 0, 0.35)";
            oscCtx.fillRect(0, 0, w, h);

            // Calculate current synaptic excitation energy
            const activePulses = pulses.length;
            const amp = hyperProcessing > 0 ? 22 : 10;
            const val = Math.sin(timeTick * 0.35) * Math.cos(timeTick * 0.12) * amp + (Math.random() - 0.5) * 6;
            oscHistory.push(val);
            if (oscHistory.length > 100) oscHistory.shift();

            oscCtx.strokeStyle = hyperProcessing > 0 ? "#ff007f" : "#00f0ff";
            oscCtx.lineWidth = 1.6;
            oscCtx.beginPath();
            oscHistory.forEach((v, i) => {
                const x = (i / 100) * w;
                const y = h * 0.5 + v;
                if (i === 0) oscCtx.moveTo(x, y);
                else oscCtx.lineTo(x, y);
            });
            oscCtx.stroke();
        }

        // Main 3D Render & Real-Time Processing Loop
        function animate() {
            timeTick++;

            // 1. Update Real-Time Processing Stage Wave
            stageTimer++;
            const cycleThreshold = hyperProcessing > 0 ? 28 : 85;
            if (stageTimer >= cycleThreshold) {
                stageTimer = 0;
                activeStage = (activeStage + 1) % 4;
                updatePipelineUI(activeStage);

                // Excite neurons in the currently active processing stage
                const stageNodes = layers[activeStage];
                if (stageNodes.length > 0) {
                    const pick = stageNodes[Math.floor(Math.random() * stageNodes.length)];
                    pick.firing = 1.0;
                    spawnTelemetry(pick);
                    for (let k = 0; k < (hyperProcessing > 0 ? 12 : 4); k++) {
                        spawnPulse(pick, activeStage);
                    }
                    if (Math.random() < 0.45 || hyperProcessing > 0) {
                        const stageNames = ["D1-FOCUS", "D2-DISTILL", "D3-CHRONOS", "D4-MESH"];
                        logStream(stageNames[activeStage], `Procesando nodo [[${pick.label}]] (w=${pick.weight})`);
                    }
                }
            }

            if (hyperProcessing > 0) {
                hyperProcessing--;
                document.getElementById("osc-state").innerText = "⚡ HIPER-SINAPSIS 140Hz";
                document.getElementById("osc-state").style.color = "#ff007f";
            } else {
                document.getElementById("osc-state").innerText = "● GAMMA 60Hz";
                document.getElementById("osc-state").style.color = "#00f59b";
            }

            document.getElementById("stat-ops").innerText = `${pulses.length * 4}/s`;

            // 2. Smooth 3D Orbital Camera Rotation
            if (autoRotate && !isDragging) {
                rotY += 0.0032;
                rotX = 0.08 + Math.sin(timeTick * 0.01) * 0.04;
            }

            // Clear Canvas with subtle motion trail
            ctx.fillStyle = "rgba(2, 3, 7, 0.32)";
            ctx.fillRect(0, 0, width, height);

            // 3. Project all 3D nodes into 2D Perspective Space
            allNodes.forEach((n, idx) => {
                // Subtle 3D breathing oscillation on D3 Spine
                let dynZ = n.z3d;
                if (n.layer === 2) {
                    dynZ += Math.sin(timeTick * 0.03 + idx) * 12;
                }
                const p = project3D(n.x3d, n.y3d, dynZ);
                n.sx = p.sx;
                n.sy = p.sy;
                n.scale = p.scale;
                n.depth = p.depth;
            });

            // 4. Draw 3D Holographic Orbital Rings around the D3 Spine
            ctx.save();
            for (let r = -180; r <= 180; r += 120) {
                ctx.beginPath();
                for (let a = 0; a <= Math.PI * 2; a += 0.2) {
                    const rx = 60 + Math.cos(a + timeTick * 0.02) * 85;
                    const rz = Math.sin(a + timeTick * 0.02) * 85;
                    const rp = project3D(rx, r, rz);
                    if (a === 0) ctx.moveTo(rp.sx, rp.sy);
                    else ctx.lineTo(rp.sx, rp.sy);
                }
                ctx.closePath();
                ctx.strokeStyle = activeStage === 2 ? "rgba(255, 0, 127, 0.22)" : "rgba(0, 240, 255, 0.09)";
                ctx.lineWidth = 1;
                ctx.stroke();
            }
            ctx.restore();

            // 5. Draw 3D Synaptic Filaments (Curved Bezier Strands with Depth Scaling)
            synapses.forEach(s => {
                const isHovered = hoveredNode && (s.from === hoveredNode || s.to === hoveredNode);
                const isActiveStage = (s.stage === activeStage);
                const depthAlpha = Math.min(1.0, Math.max(0.15, (s.from.scale + s.to.scale) * 0.55));
                
                let alpha = 0.16 * s.weight * depthAlpha;
                if (isActiveStage) alpha *= 1.8;
                if (isHovered) alpha = 0.92;
                else if (hoveredNode) alpha = 0.03;

                const grad = ctx.createLinearGradient(s.from.sx, s.from.sy, s.to.sx, s.to.sy);
                if (s.colorMode === "cyan-magenta") {
                    grad.addColorStop(0, `rgba(0, 240, 255, ${alpha})`);
                    grad.addColorStop(1, `rgba(255, 0, 127, ${alpha})`);
                } else {
                    grad.addColorStop(0, `rgba(255, 0, 127, ${alpha})`);
                    grad.addColorStop(1, `rgba(0, 240, 255, ${alpha})`);
                }

                ctx.strokeStyle = grad;
                ctx.lineWidth = isHovered ? 1.8 : Math.max(0.5, 0.9 * s.from.scale);
                ctx.beginPath();
                ctx.moveTo(s.from.sx, s.from.sy);
                const midX = (s.from.sx + s.to.sx) * 0.5;
                ctx.bezierCurveTo(midX, s.from.sy, midX, s.to.sy, s.to.sx, s.to.sy);
                ctx.stroke();
            });

            // 6. Draw Traveling 3D Electrical Impulses
            for (let i = pulses.length - 1; i >= 0; i--) {
                const p = pulses[i];
                p.progress += p.speed;

                if (p.progress >= 1.0) {
                    p.synapse.to.firing = 1.0;
                    pulses.splice(i, 1);
                    if (Math.random() < 0.72) spawnPulse(p.synapse.to);
                    continue;
                }

                const s = p.synapse;
                const midX = (s.from.sx + s.to.sx) * 0.5;
                const t = p.progress;

                const px = Math.pow(1 - t, 3) * s.from.sx + 3 * Math.pow(1 - t, 2) * t * midX + 3 * (1 - t) * Math.pow(t, 2) * midX + Math.pow(t, 3) * s.to.sx;
                const py = Math.pow(1 - t, 3) * s.from.sy + 3 * Math.pow(1 - t, 2) * t * s.from.sy + 3 * (1 - t) * Math.pow(t, 2) * s.to.sy + Math.pow(t, 3) * s.to.sy;
                const pScale = s.from.scale * (1 - t) + s.to.scale * t;

                ctx.fillStyle = p.color;
                ctx.shadowColor = p.color;
                ctx.shadowBlur = 12;
                ctx.beginPath();
                ctx.arc(px, py, Math.max(1.4, 2.6 * pScale), 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
            }

            // 7. Sort Neurons by 3D Depth (Painter's Algorithm: Back to Front)
            const sortedNodes = [...allNodes].sort((a, b) => b.depth - a.depth);

            sortedNodes.forEach(n => {
                const isHovered = (n === hoveredNode);
                const isSelected = (n === selectedNode);
                const isStageActive = (n.layer === activeStage);

                if (n.firing > 0) n.firing -= 0.035;

                const r = Math.max(2.5, n.baseRadius * n.scale * (isHovered ? 1.55 : 1.0));

                ctx.shadowColor = n.color;
                ctx.shadowBlur = (isHovered || isSelected || n.firing > 0.2 || isStageActive) ? 20 : 6;

                ctx.fillStyle = n.firing > 0.3 ? "#ffffff" : n.color;
                ctx.beginPath();
                ctx.arc(n.sx, n.sy, r, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;

                // Holographic Outer Ring on D3 Spine or Active Stage
                if (n.layer === 2 || isStageActive || isHovered) {
                    ctx.strokeStyle = isStageActive ? "rgba(0, 240, 255, 0.85)" : "rgba(255, 255, 255, 0.55)";
                    ctx.lineWidth = 1.1 * n.scale;
                    ctx.beginPath();
                    ctx.arc(n.sx, n.sy, r + 2.5 * n.scale, 0, Math.PI * 2);
                    ctx.stroke();
                }

                if (isHovered || isSelected) {
                    ctx.font = "bold 11px monospace";
                    ctx.fillStyle = "#ffffff";
                    ctx.fillText(`${n.label} [w:${n.weight}]`, n.sx + 12, n.sy + 4);
                }
            });

            // 8. Draw Floating 3D Processing Telemetry Labels
            for (let i = floatingTelemetry.length - 1; i >= 0; i--) {
                const ft = floatingTelemetry[i];
                ft.life -= 0.018;
                ft.offsetY -= 0.65;
                if (ft.life <= 0) {
                    floatingTelemetry.splice(i, 1);
                    continue;
                }
                ctx.font = "bold 9px monospace";
                ctx.fillStyle = `rgba(0, 245, 155, ${ft.life})`;
                ctx.fillText(ft.text, ft.node.sx + 10, ft.node.sy - 8 + ft.offsetY);
            }

            drawOscilloscope();
            requestAnimationFrame(animate);
        }

        // 3D Mouse Drag & Zoom Controls
        canvas.addEventListener("mousedown", (e) => {
            isDragging = true;
            lastMouseX = e.clientX;
            lastMouseY = e.clientY;
        });

        window.addEventListener("mouseup", () => {
            isDragging = false;
        });

        canvas.addEventListener("mousemove", (e) => {
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            if (isDragging) {
                const dx = e.clientX - lastMouseX;
                const dy = e.clientY - lastMouseY;
                rotY += dx * 0.0055;
                rotX = Math.max(-0.8, Math.min(0.8, rotX + dy * 0.0055));
                lastMouseX = e.clientX;
                lastMouseY = e.clientY;
                return;
            }

            hoveredNode = null;
            allNodes.forEach(n => {
                const dist = Math.hypot(n.sx - mx, n.sy - my);
                if (dist < 14 * n.scale) {
                    hoveredNode = n;
                }
            });
        });

        canvas.addEventListener("wheel", (e) => {
            e.preventDefault();
            cameraZ = Math.max(420, Math.min(1600, cameraZ + e.deltaY * 0.6));
        }, { passive: false });

        canvas.addEventListener("click", () => {
            if (hoveredNode) {
                selectedNode = hoveredNode;
                selectedNode.firing = 1.0;
                spawnTelemetry(selectedNode, "ACTION POTENTIAL FIRED");
                for (let k = 0; k < 10; k++) spawnPulse(selectedNode);

                document.getElementById("detail-title").innerText = `${selectedNode.label} (Peso w=${selectedNode.weight})`;
                document.getElementById("detail-desc").innerText = `Dimensión: D${selectedNode.layer + 1} | Coordenadas 3D: (${Math.round(selectedNode.x3d)}, ${Math.round(selectedNode.y3d)}, ${Math.round(selectedNode.z3d)}) | Sinapsis Hebbiana Activa.`;
                logStream("NEURON", `Excitación manual en [[${selectedNode.label}]]`);
            }
        });

        async function triggerConsolidation() {
            hyperProcessing = 180; // 3 seconds of intense 4D visual processing
            showToast("⚡ PROCESANDO LAS 4 DIMENSIONES EN TIEMPO REAL...");
            logStream("SYNC", "Iniciando ciclo de consolidación 4D...");

            for (let k = 0; k < 90; k++) spawnPulse();
            allNodes.forEach(n => {
                if (Math.random() < 0.4) spawnTelemetry(n);
            });

            const res = await fetch("/api/consolidate", { method: "POST" });
            const data = await res.json();
            logStream("DISTILL", `${data.facts_distilled} hechos destilados (+${data.facts_retained} retenidos, ~${data.facts_superseded} actualizados)`);
            showToast(`¡CONSOLIDACIÓN 4D COMPLETADA! (${data.facts_distilled} hechos procesados)`);
            loadState();
        }

        async function saveFocus() {
            const text = document.getElementById("scratchpad").value;
            await fetch("/api/update_focus", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content: text })
            });
            logStream("D1-FOCUS", "Buffer de memoria de trabajo guardado.");
            showToast("MEMORIA DE TRABAJO ACTUALIZADA");
        }

        async function executeSearch() {
            const q = document.getElementById("search-query").value.trim();
            if (!q) return;
            hyperProcessing = 90;
            logStream("PROBE", `Sonda vectorial lanzada: "${q}"`);

            const container = document.getElementById("search-results");
            container.innerHTML = "<div style='color:var(--text-dim); text-align:center; padding:10px;'>Excitando sinapsis en 3D...</div>";

            const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            
            container.innerHTML = "";
            const hits = data.vector_results || [];
            if (hits.length === 0) {
                container.innerHTML = "<div style='color:var(--text-dim); text-align:center; padding:10px;'>Sin resonancia encontrada.</div>";
                return;
            }

            hits.forEach((h, idx) => {
                const card = document.createElement("div");
                card.className = "result-entry" + (idx % 2 === 1 ? " alt" : "");
                const score = (h.score * 100).toFixed(1);
                const source = h.metadata.source || "Recuerdo";
                card.innerHTML = `
                    <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                        <span style="font-weight:800; color:var(--neon-cyan);">${source}</span>
                        <span style="color:var(--neon-magenta); font-weight:800;">${score}%</span>
                    </div>
                    <div style="color:#d1d5db;">${h.document.substring(0, 100)}...</div>
                `;
                container.appendChild(card);
            });

            logStream("RECALL", `${hits.length} nodos resonantes recuperados.`);
            for (let k = 0; k < 35; k++) spawnPulse();
        }

        loadState();
        requestAnimationFrame(animate);
    </script>
</body>
</html>
"""

class SynapseHUDHandler(http.server.BaseHTTPRequestHandler):
    engine: SynapseEngine = None

    def log_message(self, format, *args):
        pass  # Keep console clean

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))

        elif path == "/api/state":
            audit = self.engine.audit()
            context = self.engine.get_working_context()
            active_lattice = self.engine.chronos.get_active_lattice()

            nodes = []
            edges = []
            node_set = set()

            all_mds = list(self.engine.vault_path.rglob("*.md"))
            for md in all_mds:
                if ".synapse" in str(md):
                    continue
                name = md.stem
                node_set.add(name)
                color = "#00f0ff" if "00_" in str(md) else ("#00f59b" if "20_" in str(md) else "#9d4edd")
                nodes.append({
                    "id": name,
                    "label": name,
                    "color": color
                })

            for e in active_lattice:
                s = e["source"]
                t = e["target"]
                if s not in node_set:
                    nodes.append({"id": s, "label": s, "color": "#ff007f"})
                    node_set.add(s)
                if t not in node_set:
                    nodes.append({"id": t, "label": t, "color": "#ff007f"})
                    node_set.add(t)

                edges.append({
                    "from": s,
                    "to": t,
                    "relation": e.get("relation", "superseded_by")
                })

            payload = {
                "vault_path": str(self.engine.vault_path),
                "working_context": context,
                "audit": audit,
                "active_lattice_edges": len(active_lattice),
                "total_indexed_chunks": self.engine.vector_store.count(),
                "graph_nodes": nodes[:90],
                "graph_edges": edges[:150]
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

        elif path == "/api/search":
            qs = urllib.parse.parse_qs(parsed.query)
            q = qs.get("q", [""])[0]
            results = self.engine.search(q, limit=5)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(results, ensure_ascii=False).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/consolidate":
            stats = self.engine.consolidate(recent_only=True)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode("utf-8"))

        elif path == "/api/update_focus":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)
            data = json.loads(post_body.decode("utf-8"))
            self.engine.focus.context_file.write_text(data.get("content", ""), encoding="utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "updated"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_dashboard(vault_path: str = ".", port: int = 5000):
    engine = SynapseEngine(vault_path)
    SynapseHUDHandler.engine = engine

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), SynapseHUDHandler) as httpd:
        print(f"\n[SYNAPSE 4D] 3D Holographic Neural Core iniciado con exito!")
        print(f"-> Abre tu panel visual en: http://localhost:{port}")
        print(f"Boveda activa: {engine.vault_path}")
        print("Presiona Ctrl+C para detener el servidor.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SYNAPSE 4D] Servidor detenido.")
