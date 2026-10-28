"""
Synapse 4D - Neural Matrix Visualizer & Master HUD (Pro Owner Edition)
Inspired by NeuralT / Cybernetic Neural Core: Multi-layer neural network visualization
with glowing bezier synapses, animated electrical impulse firings, Hebbian weight telemetry,
and real-time 4D state synchronization.
"""

import http.server
import socketserver
import json
import urllib.parse
from pathlib import Path
from typing import Dict, Any

from synapse4d.core import SynapseEngine

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synapse 4D — Cybernetic Neural Core HUD</title>
    <style>
        :root {
            --bg-void: #030509;
            --bg-panel: rgba(7, 11, 20, 0.88);
            --border-glow: rgba(0, 240, 255, 0.25);
            --neon-cyan: #00f0ff;
            --neon-magenta: #ff007f;
            --neon-violet: #8b5cf6;
            --neon-emerald: #10b981;
            --text-primary: #e6edf3;
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
            background: rgba(3, 5, 9, 0.95);
            border-bottom: 1px solid var(--border-glow);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
            box-shadow: 0 4px 30px rgba(0, 240, 255, 0.08);
        }
        .brand { display: flex; align-items: center; gap: 14px; }
        .brand-badge {
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-magenta));
            color: #000;
            font-weight: 900;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 13px;
            letter-spacing: 1.5px;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
        }
        .brand-title { font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 1px; }
        .version-tag {
            border: 1px solid var(--neon-cyan);
            color: var(--neon-cyan);
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 10px;
            background: rgba(0, 240, 255, 0.1);
        }

        .hud-stats { display: flex; gap: 24px; font-size: 12px; }
        .hud-stat-item { display: flex; flex-direction: column; align-items: flex-end; }
        .hud-stat-val { font-weight: 800; color: var(--neon-cyan); font-size: 14px; text-shadow: 0 0 8px rgba(0, 240, 255, 0.6); }
        .hud-stat-lbl { color: var(--text-dim); font-size: 10px; text-transform: uppercase; }

        .btn-toggle-hud {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(0, 240, 255, 0.3);
            color: var(--neon-cyan);
            padding: 8px 14px;
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
            padding: 8px 18px;
            border-radius: 6px;
            font-weight: 800;
            font-size: 12px;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 0 20px rgba(255, 0, 127, 0.4);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .btn-pulse:hover { transform: scale(1.03); box-shadow: 0 0 30px rgba(0, 240, 255, 0.8); }

        /* Main Workspace */
        #workspace {
            position: relative;
            flex: 1;
            display: flex;
            width: 100vw;
            height: calc(100vh - 60px);
            overflow: hidden;
        }

        /* Neural Canvas */
        #neural-canvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }

        /* Floating HUD Side Panels */
        .hud-panel {
            position: absolute;
            z-index: 10;
            background: var(--bg-panel);
            border: 1px solid var(--border-glow);
            border-radius: 10px;
            backdrop-filter: blur(14px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
            pointer-events: auto;
        }

        /* Left Panel: Telemetry & D1 Scratchpad */
        #panel-left {
            top: 20px;
            left: 20px;
            width: 340px;
            max-height: calc(100vh - 100px);
            padding: 16px;
            gap: 14px;
        }
        .panel-title {
            font-size: 12px;
            font-weight: 800;
            color: var(--neon-cyan);
            text-transform: uppercase;
            letter-spacing: 1px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 240, 255, 0.15);
            padding-bottom: 8px;
        }
        textarea.hud-text {
            width: 100%;
            height: 160px;
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            padding: 10px;
            color: #d1d5db;
            font-size: 11px;
            line-height: 1.4;
            resize: none;
            outline: none;
        }
        textarea.hud-text:focus { border-color: var(--neon-cyan); box-shadow: 0 0 10px rgba(0, 240, 255, 0.3); }

        /* Right Panel: Inspector & Semantic Recall */
        #panel-right {
            top: 20px;
            right: 20px;
            width: 360px;
            max-height: calc(100vh - 100px);
            padding: 16px;
            gap: 12px;
        }
        .search-row { display: flex; gap: 8px; }
        .search-input {
            flex: 1;
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 8px 12px;
            border-radius: 6px;
            color: #fff;
            font-size: 12px;
            outline: none;
        }
        .search-input:focus { border-color: var(--neon-magenta); }
        .results-box {
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-height: 240px;
            overflow-y: auto;
        }
        .result-entry {
            background: rgba(255, 255, 255, 0.03);
            border-left: 2px solid var(--neon-cyan);
            padding: 8px 10px;
            font-size: 11px;
            border-radius: 0 6px 6px 0;
        }
        .result-entry.alt { border-left-color: var(--neon-magenta); }

        /* Neuron Inspector Card */
        #neuron-detail {
            background: rgba(0, 240, 255, 0.05);
            border: 1px solid rgba(0, 240, 255, 0.2);
            padding: 10px;
            border-radius: 6px;
            font-size: 11px;
            display: none;
        }

        /* Toast Feedback */
        #toast {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--neon-magenta);
            color: #fff;
            padding: 10px 24px;
            border-radius: 8px;
            font-weight: 800;
            font-size: 13px;
            display: none;
            box-shadow: 0 0 25px rgba(255, 0, 127, 0.7);
            z-index: 200;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <span class="brand-badge">SYNAPSE 4D</span>
            <span class="brand-title">CYBERNETIC NEURAL CORE</span>
            <span class="version-tag">OWNER EDITION v1.0</span>
        </div>
        
        <div class="hud-stats">
            <div class="hud-stat-item">
                <span id="stat-nodes" class="hud-stat-val">28</span>
                <span class="hud-stat-lbl">Neuronas Activas</span>
            </div>
            <div class="hud-stat-item">
                <span id="stat-synapses" class="hud-stat-val">124</span>
                <span class="hud-stat-lbl">Sinapsis Fibras</span>
            </div>
            <div class="hud-stat-item">
                <span id="stat-health" class="hud-stat-val" style="color:var(--neon-emerald)">100%</span>
                <span class="hud-stat-lbl">Topología Coherente</span>
            </div>
            <div class="hud-stat-item">
                <span id="stat-freq" class="hud-stat-val">60 Hz</span>
                <span class="hud-stat-lbl">Frecuencia Sináptica</span>
            </div>
        </div>

        <div style="display:flex; gap:12px; align-items:center;">
            <button class="btn-toggle-hud" onclick="toggleHUD()">
                👁️ MODO NEURONAL PURO
            </button>
            <button class="btn-pulse" onclick="triggerConsolidation()">
                ⚡ SINCRONIZAR COGNICIÓN
            </button>
        </div>
    </header>

    <div id="workspace">
        <!-- Canvas de Neuronas y Fibras Eléctricas -->
        <canvas id="neural-canvas"></canvas>

        <!-- Panel Izquierdo: Foco D1 -->
        <div id="panel-left" class="hud-panel">
            <div class="panel-title">
                <span>D1: Buffer de Atención</span>
                <button onclick="saveFocus()" style="background:none; border:1px solid var(--neon-cyan); color:var(--neon-cyan); border-radius:4px; padding:2px 6px; font-size:10px; cursor:pointer;">GUARDAR</button>
            </div>
            <textarea id="scratchpad" class="hud-text" spellcheck="false" placeholder="Cargando foco de trabajo..."></textarea>
            
            <div class="panel-title">
                <span>Jerarquía de Verdad (D2)</span>
            </div>
            <div style="font-size:11px; display:flex; flex-direction:column; gap:6px; color:var(--text-dim);">
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#fff;">Axiomas del Sistema:</span>
                    <span style="color:var(--neon-cyan); font-weight:800;">Nivel 1.0 (Inmutable)</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#fff;">Preferencias Usuario:</span>
                    <span style="color:var(--neon-magenta); font-weight:800;">Nivel 0.8 (Prioritario)</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#fff;">Observaciones Empíricas:</span>
                    <span style="color:var(--neon-emerald); font-weight:800;">Nivel 0.5 (Dinámico)</span>
                </div>
            </div>
        </div>

        <!-- Panel Derecho: Telemetría y Búsqueda -->
        <div id="panel-right" class="hud-panel">
            <div class="panel-title">
                <span>Sonda de Recuerdos (Vector & Chronos)</span>
            </div>
            <div class="search-row">
                <input id="search-query" class="search-input" type="text" placeholder="Consultar cerebro..." onkeydown="if(event.key==='Enter') executeSearch()">
                <button onclick="executeSearch()" style="background:var(--neon-magenta); color:#fff; border:none; padding:0 12px; border-radius:6px; font-weight:800; cursor:pointer;">SONDA</button>
            </div>
            <div id="search-results" class="results-box">
                <div style="color:var(--text-dim); font-size:11px; text-align:center; padding:15px;">Escribe una consulta para activar sinapsis resonantes.</div>
            </div>

            <div class="panel-title" style="margin-top:6px;">
                <span>Inspector Neuronal (D3/D4)</span>
            </div>
            <div id="neuron-detail">
                <div id="detail-title" style="font-weight:800; color:var(--neon-cyan); margin-bottom:4px;">Selecciona una neurona</div>
                <div id="detail-desc" style="color:#d1d5db; line-height:1.4;">Haz clic en cualquier nodo para inspeccionar sus conexiones.</div>
            </div>
        </div>
    </div>

    <div id="toast"></div>

    <script>
        const canvas = document.getElementById("neural-canvas");
        const ctx = canvas.getContext("2d");

        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight - 60;

        window.addEventListener("resize", () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight - 60;
            initNeuralLayout();
        });

        // 4 Columns: D1 Focus, D2 Distiller, D3 Chronos Central Spine, D4 Associative Mesh
        let layers = [[], [], [], []];
        let synapses = [];
        let pulses = [];
        let selectedNode = null;
        let hoveredNode = null;

        function showToast(msg) {
            const t = document.getElementById("toast");
            t.innerText = msg;
            t.style.display = "block";
            setTimeout(() => { t.style.display = "none"; }, 3200);
        }

        async function loadState() {
            try {
                const res = await fetch("/api/state");
                const data = await res.json();
                
                document.getElementById("scratchpad").value = data.working_context.active_context || "";
                document.getElementById("stat-nodes").innerText = data.audit.total_nodes;
                document.getElementById("stat-health").innerText = data.audit.health_score;

                buildNeuralNetwork(data.graph_nodes, data.graph_edges);
            } catch (err) {
                console.error("Error loading state:", err);
            }
        }

        function buildNeuralNetwork(nodes, edges) {
            layers = [[], [], [], []];
            synapses = [];
            pulses = [];

            // Partition nodes into the 4 Dimensions
            nodes.forEach((n, idx) => {
                let layerIdx = 3; // Default D4 Associative Mesh
                if (n.id.includes("contexto") || n.id.includes("perfil") || n.id.includes("Inicio")) layerIdx = 0; // D1 Focus
                else if (n.id.includes("regla") || n.id.includes("antipatron") || n.id.includes("exito")) layerIdx = 1; // D2 Distiller
                else if (idx % 3 === 0) layerIdx = 2; // D3 Chronos Spine

                layers[layerIdx].push({
                    id: n.id,
                    label: n.label,
                    layer: layerIdx,
                    x: 0,
                    y: 0,
                    radius: layerIdx === 2 ? 6.5 : 5,
                    color: layerIdx === 0 ? "#00f0ff" : (layerIdx === 1 ? "#10b981" : (layerIdx === 2 ? "#ff007f" : "#8b5cf6")),
                    firing: 0
                });
            });

            // Ensure vertical spine (layer 2) has a dense stack (like NeuralT)
            initNeuralLayout();

            // Generate dense synapic connections between layers
            for (let l = 0; l < 3; l++) {
                const curr = layers[l];
                const next = layers[l + 1];

                curr.forEach((fromNode, i) => {
                    next.forEach((toNode, j) => {
                        // High density synaptic mesh (like NeuralT)
                        if (Math.random() < 0.65 || (l === 1 && l + 1 === 2)) {
                            const syn = {
                                from: fromNode,
                                to: toNode,
                                weight: Math.random() * 0.8 + 0.2,
                                color: l % 2 === 0 ? "cyan-to-magenta" : "magenta-to-cyan"
                            };
                            synapses.push(syn);
                        }
                    });
                });
            }

            document.getElementById("stat-synapses").innerText = synapses.length;

            // Seed initial electrical impulse particles
            for (let p = 0; p < 80; p++) {
                spawnPulse();
            }
        }

        let hudVisible = true;
        function toggleHUD() {
            hudVisible = !hudVisible;
            document.getElementById("panel-left").style.display = hudVisible ? "flex" : "none";
            document.getElementById("panel-right").style.display = hudVisible ? "flex" : "none";
            initNeuralLayout();
        }

        function initNeuralLayout() {
            const colX = hudVisible ? [
                width * 0.35,  // D1 Input Layer
                width * 0.46,  // D2 Distiller Layer
                width * 0.57,  // D3 Chronos Central Spine (vertical dense column)
                width * 0.69   // D4 Associative Mesh
            ] : [
                width * 0.15,
                width * 0.38,
                width * 0.62,
                width * 0.85
            ];

            layers.forEach((layerNodes, lIdx) => {
                const x = colX[lIdx];
                const count = layerNodes.length;
                const spacing = (height - 120) / Math.max(count, 1);
                const startY = 60;

                layerNodes.forEach((node, nIdx) => {
                    node.x = x;
                    node.y = startY + (nIdx + 0.5) * spacing;
                });
            });
        }

        function spawnPulse(forceFromNode = null) {
            if (synapses.length === 0) return;
            const valid = forceFromNode 
                ? synapses.filter(s => s.from === forceFromNode) 
                : synapses;
            if (valid.length === 0) return;

            const s = valid[Math.floor(Math.random() * valid.length)];
            pulses.push({
                synapse: s,
                progress: 0,
                speed: 0.008 + Math.random() * 0.012,
                color: Math.random() > 0.5 ? "#00f0ff" : "#ff007f"
            });
        }

        // Animation Loop (60 FPS Cybernetic Render)
        function animate() {
            ctx.fillStyle = "rgba(3, 5, 9, 0.25)"; // Motion blur decay
            ctx.fillRect(0, 0, width, height);

            // Layer Column Background Guides
            const colNames = ["D1: FOCUS ATTENTION", "D2: FACT DISTILLER", "D3: CHRONOS LATTICE (SPINE)", "D4: ASSOCIATIVE MESH"];
            const colX = [width * 0.30, width * 0.44, width * 0.58, width * 0.72];

            ctx.font = "10px monospace";
            ctx.fillStyle = "rgba(0, 240, 255, 0.4)";
            colX.forEach((x, i) => {
                ctx.fillText(colNames[i], x - 65, 30);
                ctx.strokeStyle = "rgba(255, 255, 255, 0.03)";
                ctx.beginPath();
                ctx.moveTo(x, 40);
                ctx.lineTo(x, height - 20);
                ctx.stroke();
            });

            // 1. Draw Synaptic Strands (Glowing Bezier Curves)
            ctx.lineWidth = 0.8;
            synapses.forEach(s => {
                const isHovered = hoveredNode && (s.from === hoveredNode || s.to === hoveredNode);
                const alpha = isHovered ? 0.9 : (hoveredNode ? 0.04 : 0.18 * s.weight);

                const grad = ctx.createLinearGradient(s.from.x, s.from.y, s.to.x, s.to.y);
                if (s.color === "cyan-to-magenta") {
                    grad.addColorStop(0, `rgba(0, 240, 255, ${alpha})`);
                    grad.addColorStop(1, `rgba(255, 0, 127, ${alpha})`);
                } else {
                    grad.addColorStop(0, `rgba(255, 0, 127, ${alpha})`);
                    grad.addColorStop(1, `rgba(0, 240, 255, ${alpha})`);
                }

                ctx.strokeStyle = grad;
                ctx.beginPath();
                ctx.moveTo(s.from.x, s.from.y);
                const cp1x = s.from.x + (s.to.x - s.from.x) * 0.5;
                const cp2x = s.from.x + (s.to.x - s.from.x) * 0.5;
                ctx.bezierCurveTo(cp1x, s.from.y, cp2x, s.to.y, s.to.x, s.to.y);
                ctx.stroke();
            });

            // 2. Draw Electrical Impulses (Traveling Photons)
            for (let i = pulses.length - 1; i >= 0; i--) {
                const p = pulses[i];
                p.progress += p.speed;

                if (p.progress >= 1.0) {
                    p.synapse.to.firing = 1.0;
                    pulses.splice(i, 1);
                    if (Math.random() < 0.6) spawnPulse(p.synapse.to);
                    continue;
                }

                // Calculate Cubic Bezier position
                const s = p.synapse;
                const cp1x = s.from.x + (s.to.x - s.from.x) * 0.5;
                const cp2x = s.from.x + (s.to.x - s.from.x) * 0.5;
                const t = p.progress;

                const px = Math.pow(1 - t, 3) * s.from.x + 3 * Math.pow(1 - t, 2) * t * cp1x + 3 * (1 - t) * Math.pow(t, 2) * cp2x + Math.pow(t, 3) * s.to.x;
                const py = Math.pow(1 - t, 3) * s.from.y + 3 * Math.pow(1 - t, 2) * t * s.from.y + 3 * (1 - t) * Math.pow(t, 2) * s.to.y + Math.pow(t, 3) * s.to.y;

                ctx.fillStyle = p.color;
                ctx.shadowColor = p.color;
                ctx.shadowBlur = 10;
                ctx.beginPath();
                ctx.arc(px, py, 2.2, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
            }

            // 3. Draw Neurons
            layers.forEach(layer => {
                layer.forEach(n => {
                    const isHovered = (n === hoveredNode);
                    const isSelected = (n === selectedNode);

                    // Decay firing glow
                    if (n.firing > 0) n.firing -= 0.04;

                    ctx.shadowColor = n.color;
                    ctx.shadowBlur = (isHovered || isSelected || n.firing > 0) ? 18 : 6;

                    ctx.fillStyle = n.firing > 0 ? "#ffffff" : n.color;
                    ctx.beginPath();
                    ctx.arc(n.x, n.y, isHovered ? n.radius * 1.5 : n.radius, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;

                    // Outlines for Central Spine
                    if (n.layer === 2) {
                        ctx.strokeStyle = "rgba(255, 255, 255, 0.6)";
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.arc(n.x, n.y, n.radius + 2, 0, Math.PI * 2);
                        ctx.stroke();
                    }

                    // Label on hover or select
                    if (isHovered || isSelected) {
                        ctx.font = "11px monospace";
                        ctx.fillStyle = "#ffffff";
                        ctx.fillText(n.label, n.x + 12, n.y + 4);
                    }
                });
            });

            requestAnimationFrame(animate);
        }

        // Mouse Interactivity
        canvas.addEventListener("mousemove", (e) => {
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            hoveredNode = null;
            layers.forEach(layer => {
                layer.forEach(n => {
                    const dist = Math.hypot(n.x - mx, n.y - my);
                    if (dist < 14) {
                        hoveredNode = n;
                    }
                });
            });
        });

        canvas.addEventListener("click", (e) => {
            if (hoveredNode) {
                selectedNode = hoveredNode;
                // Burst pulses from clicked neuron
                for (let k = 0; k < 6; k++) spawnPulse(selectedNode);

                // Show details in inspector
                const detailBox = document.getElementById("neuron-detail");
                detailBox.style.display = "block";
                document.getElementById("detail-title").innerText = selectedNode.label;
                document.getElementById("detail-desc").innerText = `Capa: Dimensión ${selectedNode.layer + 1} | ID: ${selectedNode.id} | Estado: Activo en Chronos Lattice.`;
            }
        });

        async function triggerConsolidation() {
            showToast("⚡ INICIANDO REPETICIÓN SINÁPTICA 4D...");
            // Blast pulses everywhere
            for (let k = 0; k < 80; k++) spawnPulse();

            const res = await fetch("/api/consolidate", { method: "POST" });
            const data = await res.json();
            showToast(`¡CONSOLIDACIÓN COMPLETA! (${data.facts_distilled} hechos destilados)`);
            loadState();
        }

        async function saveFocus() {
            const text = document.getElementById("scratchpad").value;
            await fetch("/api/update_focus", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content: text })
            });
            showToast("FOCO DE ATENCIÓN ACTUALIZADO");
        }

        async function executeSearch() {
            const q = document.getElementById("search-query").value.trim();
            if (!q) return;
            const container = document.getElementById("search-results");
            container.innerHTML = "<div style='color:var(--text-dim); text-align:center; padding:10px;'>Activando sinapsis...</div>";

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
                    <div style="color:#d1d5db;">${h.document.substring(0, 110)}...</div>
                `;
                container.appendChild(card);
            });

            // Burst pulses on search
            for (let k = 0; k < 25; k++) spawnPulse();
        }

        loadState();
        requestAnimationFrame(animate);
    </script>
</body>
</html>
"""

class SynapseHUDHandler(http.server.BaseHTTPRequestHandler):
    engine: SynapseEngine = None

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
                color = "#00f0ff" if "00_" in str(md) else ("#10b981" if "20_" in str(md) else "#8b5cf6")
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

    # Enable socket reuse to prevent WinError 10048 if recently restarted
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), SynapseHUDHandler) as httpd:
        print(f"\n[SYNAPSE 4D] Cybernetic Neural Core iniciado con exito!")
        print(f"-> Abre tu panel visual en: http://localhost:{port}")
        print(f"Boveda activa: {engine.vault_path}")
        print("Presiona Ctrl+C para detener el servidor.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SYNAPSE 4D] Servidor detenido.")
