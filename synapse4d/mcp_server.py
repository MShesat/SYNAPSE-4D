"""
Synapse 4D - Native Model Context Protocol (MCP) Server
Allows Cursor, Claude Desktop, Antigravity, and VS Code to natively use Synapse 4D memory.
"""

import sys
import json
from pathlib import Path
from synapse4d.core import SynapseEngine

def run_server(vault_path: str = "."):
    engine = SynapseEngine(vault_path)

    # Simple JSON-RPC loop over stdio
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {
                            "name": "synapse4d",
                            "version": "1.0.0"
                        },
                        "capabilities": {
                            "tools": {}
                        }
                    }
                }
            elif method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": "synapse_get_working_memory",
                                "description": "Retrieve current active working memory, user profile, and active project state.",
                                "inputSchema": {"type": "object", "properties": {}}
                            },
                            {
                                "name": "synapse_search_memory",
                                "description": "Semantic and temporal hybrid search across all cognitive memory layers.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string", "description": "Natural language query"}
                                    },
                                    "required": ["query"]
                                }
                            },
                            {
                                "name": "synapse_consolidate",
                                "description": "Trigger the 4D consolidation cycle to absorb recent session logs into long-term facts.",
                                "inputSchema": {"type": "object", "properties": {}}
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})

                if tool_name == "synapse_get_working_memory":
                    data = engine.get_working_context()
                    content = f"# Active Context\n{data['active_context']}\n\n# System Profile\n{data['system_profile']}"
                elif tool_name == "synapse_search_memory":
                    q = args.get("query", "")
                    data = engine.search(q, limit=5)
                    content = json.dumps(data, indent=2, ensure_ascii=False)
                elif tool_name == "synapse_consolidate":
                    data = engine.consolidate(recent_only=True)
                    content = json.dumps(data, indent=2, ensure_ascii=False)
                else:
                    content = f"Unknown tool: {tool_name}"

                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": content}]
                    }
                }
            else:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {}
                }

            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32000, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()
