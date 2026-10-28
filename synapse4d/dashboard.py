"""
Synapse 4D - Master HUD & Web Visualizer (Pro Owner Edition)
Zero-dependency, standalone local web server providing real-time 4D state inspection,
interactive neural graph visualization, semantic vector search, and 1-click consolidation.
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
    <title>Synapse 4D — Master Cognitive HUD</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        :root {
            --bg-base: #0a0d14;
            --bg-card: rgba(18, 24, 38, 0.85);
            --border-card: rgba(45, 212, 191, 0.2);
            --accent-green: #10b981;
            --accent-cyan: #06b6d4;
            --accent-violet: #8b5cf6;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
        body { background: var(--bg-base); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; overflow-x: hidden; }
        
        /* Top Navigation Header */
        header {
            background: rgba(10, 13, 20, 0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-card);
            padding: 16px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .logo-area { display: flex; align-items: center; gap: 14px; }
        .logo-badge {
            background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan));
            color: #000;
            font-weight: 800;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 14px;
            letter-spacing: 1px;
        }
        .header-title { font-size: 20px; font-weight: 700; color: #fff; letter-spacing: 0.5px; }
        .owner-badge {
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid var(--accent-violet);
            color: #c4b5fd;
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: 600;
        }
        .btn-consolidate {
            background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan));
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .btn-consolidate:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4); }

        /* Main Grid */
        main {
            padding: 24px 32px;
            display: grid;
            grid-template-columns: 360px 1fr 380px;
            gap: 24px;
            flex: 1;
        }

        .panel {
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 14px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        .panel-header { display: flex; justify-content: space-between; align-items: center; }
        .panel-title { font-size: 15px; font-weight: 700; color: var(--accent-cyan); display: flex; align-items: center; gap: 8px; text-transform: uppercase; letter-spacing: 1px; }

        /* D1: Focus Scratchpad */
        textarea.scratchpad {
            width: 100%;
            height: 220px;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 12px;
            color: #e5e7eb;
            font-size: 13px;
            resize: none;
            outline: none;
            line-height: 1.5;
        }
        textarea.scratchpad:focus { border-color: var(--accent-green); }

        /* D3: Interactive Graph */
        #network-graph {
            width: 100%;
            height: 520px;
            background: rgba(0, 0, 0, 0.6);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* Search Section */
        .search-box {
            display: flex;
            gap: 10px;
        }
        .search-input {
            flex: 1;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 10px 14px;
            border-radius: 8px;
            color: #fff;
            outline: none;
        }
        .search-input:focus { border-color: var(--accent-cyan); }
        .search-results {
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-height: 280px;
            overflow-y: auto;
        }
        .result-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 12px;
            border-radius: 8px;
            font-size: 12px;
            line-height: 1.4;
        }
        .result-meta { color: var(--accent-green); font-weight: 700; margin-bottom: 4px; display: flex; justify-content: space-between; }

        /* Metrics HUD */
        .metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .metric-card {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 14px;
            border-radius: 10px;
            text-align: center;
        }
        .metric-val { font-size: 24px; font-weight: 800; color: #fff; }
        .metric-lbl { font-size: 11px; color: var(--text-muted); margin-top: 4px; text-transform: uppercase; }

        /* Notification Toast */
        #toast {
            position: fixed;
            bottom: 24px;
            right: 32px;
            background: var(--accent-green);
            color: #000;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 700;
            display: none;
            box-shadow: 0 4px 20px rgba(16, 185, 129, 0.5);
            z-index: 1000;
        }
    </style>
</head>
<body>

    <header>
        <div class="logo-area">
            <span class="logo-badge">SYNAPSE 4D</span>
            <span class="header-title">Master Cognitive HUD</span>
            <span class="owner-badge">👑 OWNER PRO EDITION</span>
        </div>
        <button class="btn-consolidate" onclick="triggerConsolidation()">
            ⚡ Consolidar 4D Ahora
        </button>
    </header>

    <main>
        <!-- Panel Izquierdo: D1 Focus & Estado -->
        <div class="panel">
            <div class="panel-header">
                <span class="panel-title">🧠 D1: Focus Engine</span>
                <button onclick="saveFocus()" style="background:none; border:1px solid var(--accent-green); color:var(--accent-green); border-radius:6px; padding:4px 8px; cursor:pointer; font-size:11px;">Guardar</button>
            </div>
            <textarea id="scratchpad" class="scratchpad" placeholder="Cargando memoria activa..."></textarea>
            
            <div class="panel-header" style="margin-top:10px;">
                <span class="panel-title">📊 Métricas del Cerebro</span>
            </div>
            <div class="metric-grid">
                <div class="metric-card">
                    <div id="stat-nodes" class="metric-val">-</div>
                    <div class="metric-lbl">Nodos Activos</div>
                </div>
                <div class="metric-card">
                    <div id="stat-health" class="metric-val" style="color:var(--accent-green);">-</div>
                    <div class="metric-lbl">Salud Topológica</div>
                </div>
                <div class="metric-card">
                    <div id="stat-edges" class="metric-val">-</div>
                    <div class="metric-lbl">Sinapsis Chronos</div>
                </div>
                <div class="metric-card">
                    <div id="stat-vectors" class="metric-val">-</div>
                    <div class="metric-lbl">Vectores Semánticos</div>
                </div>
            </div>
        </div>

        <!-- Panel Central: D3 Chronos Lattice & D4 Malla Topológica -->
        <div class="panel">
            <div class="panel-header">
                <span class="panel-title">🌐 D3 & D4: Matriz Neuronal Bi-Temporal</span>
                <span id="vault-display" style="font-size:12px; color:var(--text-muted); font-family:monospace;"></span>
            </div>
            <div id="network-graph"></div>
        </div>

        <!-- Panel Derecho: Búsqueda Semántica Vectorial -->
        <div class="panel">
            <div class="panel-header">
                <span class="panel-title">🔍 Recuperación Semántica</span>
            </div>
            <div class="search-box">
                <input id="search-query" class="search-input" type="text" placeholder="Consultar recuerdos en lenguaje natural..." onkeydown="if(event.key==='Enter') executeSearch()">
                <button onclick="executeSearch()" style="background:var(--accent-cyan); color:#000; border:none; padding:0 14px; border-radius:8px; font-weight:700; cursor:pointer;">Buscar</button>
            </div>
            <div id="search-results" class="search-results">
                <div style="color:var(--text-muted); font-size:12px; text-align:center; padding:20px;">Escribe una consulta para buscar en vectores y grafos.</div>
            </div>
        </div>
    </main>

    <div id="toast"></div>

    <script>
        let network = null;

        function showToast(msg) {
            const t = document.getElementById("toast");
            t.innerText = msg;
            t.style.display = "block";
            setTimeout(() => { t.style.display = "none"; }, 3000);
        }

        async function loadState() {
            try {
                const res = await fetch("/api/state");
                const data = await res.json();
                
                document.getElementById("scratchpad").value = data.working_context.active_context || "";
                document.getElementById("vault-display").innerText = data.vault_path;
                document.getElementById("stat-nodes").innerText = data.audit.total_nodes;
                document.getElementById("stat-health").innerText = data.audit.health_score;
                document.getElementById("stat-edges").innerText = data.active_lattice_edges;
                document.getElementById("stat-vectors").innerText = data.total_indexed_chunks;

                renderGraph(data.graph_nodes, data.graph_edges);
            } catch (err) {
                console.error("Error loading state:", err);
            }
        }

        function renderGraph(nodesData, edgesData) {
            const container = document.getElementById("network-graph");
            const nodes = new vis.DataSet(nodesData);
            const edges = new vis.DataSet(edgesData);

            const data = { nodes: nodes, edges: edges };
            const options = {
                nodes: {
                    shape: "dot",
                    size: 16,
                    font: { color: "#f3f4f6", size: 12, face: "monospace" },
                    borderWidth: 2,
                    shadow: true
                },
                edges: {
                    width: 2,
                    color: { color: "rgba(6, 182, 212, 0.4)", highlight: "#10b981" },
                    arrows: { to: { enabled: true, scaleFactor: 0.6 } },
                    smooth: { type: "continuous" }
                },
                physics: {
                    stabilization: false,
                    barnesHut: { gravitationalConstant: -3000, springLength: 95 }
                }
            };
            if (network) network.destroy();
            network = new vis.Network(container, data, options);
        }

        async function triggerConsolidation() {
            showToast("Ejecutando consolidación 4D...");
            const res = await fetch("/api/consolidate", { method: "POST" });
            const data = await res.json();
            showToast(`¡Consolidación exitosa! (${data.facts_distilled} hechos procesados)`);
            loadState();
        }

        async function saveFocus() {
            const text = document.getElementById("scratchpad").value;
            await fetch("/api/update_focus", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content: text })
            });
            showToast("Memoria de trabajo actualizada");
        }

        async function executeSearch() {
            const q = document.getElementById("search-query").value.trim();
            if (!q) return;
            const container = document.getElementById("search-results");
            container.innerHTML = "<div style='color:#9ca3af; text-align:center; padding:15px;'>Buscando...</div>";

            const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            
            container.innerHTML = "";
            const hits = data.vector_results || [];
            if (hits.length === 0) {
                container.innerHTML = "<div style='color:#9ca3af; text-align:center; padding:15px;'>Sin resultados.</div>";
                return;
            }

            hits.forEach(h => {
                const card = document.createElement("div");
                card.className = "result-card";
                const score = (h.score * 100).toFixed(1);
                const source = h.metadata.source || "Episodio";
                card.innerHTML = `
                    <div class="result-meta">
                        <span>${source}</span>
                        <span>${score}%</span>
                    </div>
                    <div>${h.document.substring(0, 140)}...</div>
                `;
                container.appendChild(card);
            });
        }

        loadState();
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

            # Format graph nodes & edges for Vis.js
            nodes = []
            edges = []
            node_set = set()

            # Add all markdown vault files as nodes
            all_mds = list(self.engine.vault_path.rglob("*.md"))
            for md in all_mds:
                if ".synapse" in str(md):
                    continue
                name = md.stem
                node_set.add(name)
                color = "#10b981" if "00_" in str(md) else ("#06b6d4" if "20_" in str(md) else "#8b5cf6")
                nodes.append({
                    "id": name,
                    "label": name,
                    "color": {"background": color, "border": "#fff"}
                })

            for e in active_lattice:
                s = e["source"]
                t = e["target"]
                if s not in node_set:
                    nodes.append({"id": s, "label": s, "color": {"background": "#ec4899", "border": "#fff"}})
                    node_set.add(s)
                if t not in node_set:
                    nodes.append({"id": t, "label": t, "color": {"background": "#ec4899", "border": "#fff"}})
                    node_set.add(t)

                edges.append({
                    "from": s,
                    "to": t,
                    "label": e.get("relation", "rel")
                })

            payload = {
                "vault_path": str(self.engine.vault_path),
                "working_context": context,
                "audit": audit,
                "active_lattice_edges": len(active_lattice),
                "total_indexed_chunks": self.engine.vector_store.count(),
                "graph_nodes": nodes[:80],
                "graph_edges": edges[:120]
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

    with socketserver.TCPServer(("", port), SynapseHUDHandler) as httpd:
        print(f"\n🧠 [SYNAPSE 4D] Master HUD iniciado con éxito!")
        print(f"👉 Abre tu panel visual en: http://localhost:{port}")
        print(f"Bóveda activa: {engine.vault_path}")
        print("Presiona Ctrl+C para detener el servidor.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SYNAPSE 4D] Servidor detenido.")
