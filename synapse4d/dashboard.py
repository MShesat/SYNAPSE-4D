"""
Synapse 4D - Community Edition Dashboard (Lite Inspector)
Note: The full 3D Holographic Neural Core, Real-Time Oscilloscope, and Interactive
Bezier Matrix are exclusive to the Synapse 4D Pro Edition.
"""

import http.server
import socketserver
import json
from pathlib import Path
from synapse4d.core import SynapseEngine

COMMUNITY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Synapse 4D — Community Inspector</title>
    <style>
        body { background: #050811; color: #e6edf3; font-family: monospace; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 24px; }
        .card { background: rgba(13, 19, 33, 0.9); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 12px; padding: 32px; max-width: 680px; width: 100%; box-shadow: 0 10px 40px rgba(0,0,0,0.8); text-align: center; }
        .badge { background: linear-gradient(135deg, #00f0ff, #ff007f); color: #000; font-weight: 900; padding: 4px 12px; border-radius: 6px; font-size: 12px; display: inline-block; margin-bottom: 12px; }
        h1 { font-size: 22px; margin-bottom: 8px; color: #fff; }
        p { color: #8b949e; font-size: 13px; line-height: 1.5; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }
        .stat-box { background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.08); padding: 14px; border-radius: 8px; }
        .stat-val { font-size: 22px; font-weight: 800; color: #00f0ff; }
        .stat-lbl { font-size: 10px; color: #8b949e; text-transform: uppercase; margin-top: 4px; }
        .pro-banner { background: linear-gradient(135deg, rgba(0, 240, 255, 0.1), rgba(255, 0, 127, 0.15)); border: 1px solid #ff007f; border-radius: 10px; padding: 20px; margin-top: 16px; }
        .btn-pro { display: inline-block; background: linear-gradient(135deg, #00f0ff, #ff007f); color: #000; font-weight: 900; text-decoration: none; padding: 10px 24px; border-radius: 6px; margin-top: 12px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="card">
        <span class="badge">SYNAPSE 4D COMMUNITY</span>
        <h1>Local Cognitive State Inspector</h1>
        <p>Your 4D CLI & MCP Server are active and healthy.</p>
        <div class="stats">
            <div class="stat-box"><div id="nodes" class="stat-val">-</div><div class="stat-lbl">Active Nodes</div></div>
            <div class="stat-box"><div id="bindings" class="stat-val">-</div><div class="stat-lbl">Wikilink Bindings</div></div>
            <div class="stat-box"><div id="health" class="stat-val" style="color:#00f59b;">-</div><div class="stat-lbl">Graph Health</div></div>
        </div>
        <div class="pro-banner">
            <h3 style="color:#ff007f; margin-bottom:6px;">⚡ Upgrade to Synapse 4D Pro</h3>
            <p style="margin-bottom:8px;">Unlock the <b>3D Holographic Neural Core HUD</b>, Real-Time Gamma Oscilloscope, Interactive 3D Bezier Synapses, and Single-File SQLite Engine.</p>
            <a class="btn-pro" href="https://github.com/MShesat/SYNAPSE-4D" target="_blank">Get Synapse 4D Pro Edition</a>
        </div>
    </div>
    <script>
        fetch('/api/state').then(r => r.json()).then(d => {
            document.getElementById('nodes').innerText = d.audit.total_nodes;
            document.getElementById('bindings').innerText = d.audit.total_bindings;
            document.getElementById('health').innerText = d.audit.health_score;
        });
    </script>
</body>
</html>
"""

class CommunityHUDHandler(http.server.BaseHTTPRequestHandler):
    engine: SynapseEngine = None
    def log_message(self, format, *args): pass
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(COMMUNITY_HTML.encode("utf-8"))
        elif self.path == "/api/state":
            payload = {"audit": self.engine.audit()}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_dashboard(vault_path: str = ".", port: int = 5000):
    engine = SynapseEngine(vault_path)
    CommunityHUDHandler.engine = engine
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), CommunityHUDHandler) as httpd:
        print(f"\n[SYNAPSE 4D] Community Inspector started at http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
