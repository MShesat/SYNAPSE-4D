"""
Synapse 4D - CLI Interface
Commands: init, consolidate, search, audit, serve.
"""

import argparse
import sys
import os
import shutil
from pathlib import Path
from synapse4d import __version__
from synapse4d.core import SynapseEngine

def main():
    parser = argparse.ArgumentParser(
        prog="synapse4d",
        description=f"Synapse 4D (v{__version__}) - SOTA Quad-Hybrid Memory Engine for AI Agents & Obsidian"
    )
    parser.add_argument("--version", action="version", version=f"synapse4d {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new Synapse 4D cognitive vault")
    init_parser.add_argument("path", help="Target directory for the new cognitive vault")

    # consolidate
    cons_parser = subparsers.add_parser("consolidate", help="Run the 4D consolidation cycle")
    cons_parser.add_argument("--vault", "-v", default=".", help="Path to the Obsidian vault (default: current dir)")
    cons_parser.add_argument("--all", action="store_true", help="Process all episodic logs, not just recent ones")

    # search
    search_parser = subparsers.add_parser("search", help="Semantic & temporal hybrid memory search")
    search_parser.add_argument("query", help="Query string")
    search_parser.add_argument("--vault", "-v", default=".", help="Path to the Obsidian vault")
    search_parser.add_argument("--limit", "-n", type=int, default=5, help="Number of results")

    # audit
    audit_parser = subparsers.add_parser("audit", help="Audit cognitive vault health, links, and orphans")
    audit_parser.add_argument("--vault", "-v", default=".", help="Path to the Obsidian vault")

    # serve (MCP Server)
    serve_parser = subparsers.add_parser("serve", help="Start the Synapse 4D MCP Server for Cursor/Claude/Antigravity")
    serve_parser.add_argument("--vault", "-v", default=".", help="Path to the Obsidian vault")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "init":
        target = Path(args.path).resolve()
        template_dir = Path(__file__).parent / "templates" / "starter_vault"
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
        if template_dir.exists():
            for item in template_dir.iterdir():
                dest = target / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            print(f"[OK] Cognitive vault initialized successfully at: {target}")
        else:
            print(f"[ERROR] Template directory not found at {template_dir}")

    elif args.command == "consolidate":
        engine = SynapseEngine(args.vault)
        print(f"[Synapse 4D] Consolidating vault: {engine.vault_path}...")
        res = engine.consolidate(recent_only=not args.all)
        print(f"[OK] Logs processed: {res['processed_logs']}")
        print(f"[OK] Facts extracted: {res['facts_extracted']} (+{res['facts_added']} added, ~{res['facts_updated']} updated, ={res['facts_noop']} duplicates skipped)")

    elif args.command == "search":
        engine = SynapseEngine(args.vault)
        res = engine.search(args.query, limit=args.limit)
        print(f"\n[Synapse 4D Results for: '{args.query}']\n")
        hits = res.get("vector_results", [])
        if not hits:
            print("No matching memories found.")
        for i, hit in enumerate(hits, 1):
            score = hit.get("score", 0.0)
            meta = hit.get("metadata", {})
            doc = hit.get("document", "").replace("\n", " ")[:150]
            print(f"[{i}] (Relevance: {score * 100:.1f}%) Source: {meta.get('source', 'Unknown')}")
            print(f"    Excerpt: {doc}...\n")

    elif args.command == "audit":
        engine = SynapseEngine(args.vault)
        report = engine.audit()
        print(f"\n=== Synapse 4D Vault Audit ===")
        print(f"Vault: {report['vault_path']}")
        print(f"Total Notes: {report['total_notes']}")
        print(f"Total Wikilinks: {report['total_wikilinks']}")
        print(f"Broken Links: {report['broken_links_count']}")
        print(f"Health Score: {report['health_score']}\n")
        if report['broken_links']:
            print("Detected Broken Links:")
            for b in report['broken_links']:
                print(f"  - In {b['file']}: [[{b['broken_target']}]]")

    elif args.command == "serve":
        from synapse4d.mcp_server import run_server
        run_server(args.vault)

if __name__ == "__main__":
    main()
