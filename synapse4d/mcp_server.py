"""
Synapse 4D - Native Model Context Protocol (MCP) Server (v2.5)
Enables Cursor, Claude Desktop, Antigravity, and VS Code to natively interface with Synapse 4D memory.
"""

from __future__ import annotations
import sys
import json
from pathlib import Path
from synapse4d.core import SynapseEngine


def run_mcp_server(vault_path: str = "."):
    engine = SynapseEngine(vault_path)

    # Standard MCP JSON-RPC 2.0 loop over stdio
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
                            "name": "synapse4d-mcp",
                            "version": "2.5.0",
                        },
                        "capabilities": {
                            "tools": {},
                        },
                    },
                }
            elif method == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": "synapse_get_working_memory",
                                "description": "Retrieve current active attention context, active project, and user profile.",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                            {
                                "name": "synapse_search_memory",
                                "description": "Search active facts, entities, and memories across SQLite relacional y embeddings.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string", "description": "Query concept or search term"}
                                    },
                                    "required": ["query"],
                                },
                            },
                            {
                                "name": "synapse_consolidate",
                                "description": "Execute the 4D consolidation cycle to absorb episodic logs into long-term facts.",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                            {
                                "name": "synapse_audit_vault",
                                "description": "Audit vault health score, broken wikilinks, needs_review count, and WAL status.",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                            {
                                "name": "synapse_undo_session",
                                "description": "Deterministically rollback a previous consolidation session.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "session_id": {"type": "string", "description": "Session ID to rollback"}
                                    },
                                    "required": ["session_id"],
                                },
                            },
                            {
                                "name": "synapse_review_facts",
                                "description": "List all provisional facts currently pending human or supervisor epistemic review.",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                        ]
                    },
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})

                if tool_name == "synapse_get_working_memory":
                    data = engine.get_working_context()
                    content = f"# Active Context\n{data.get('active_context', '')}\n\n# System Profile\n{data.get('system_profile', '')}"
                elif tool_name == "synapse_search_memory":
                    q = args.get("query", "")
                    facts = engine.db.get_active_facts()
                    matches = [f.model_dump() for f in facts if q.lower() in f.value.lower() or q.lower() in f.entity.lower()]
                    content = json.dumps(matches[:5], indent=2, ensure_ascii=False)
                elif tool_name == "synapse_consolidate":
                    data = engine.consolidate(recent_only=True)
                    content = json.dumps(data, indent=2, ensure_ascii=False)
                elif tool_name == "synapse_audit_vault":
                    data = engine.audit()
                    content = json.dumps(data, indent=2, ensure_ascii=False)
                elif tool_name == "synapse_undo_session":
                    s_id = args.get("session_id", "")
                    data = engine.undo(s_id)
                    content = json.dumps(data, indent=2, ensure_ascii=False)
                elif tool_name == "synapse_review_facts":
                    data = engine.review()
                    content = json.dumps(data, indent=2, ensure_ascii=False)
                else:
                    content = f"Unknown tool: {tool_name}"

                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": content}],
                    },
                }
            else:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}",
                    },
                }

            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal MCP server error: {str(e)}",
                },
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_mcp_server()
