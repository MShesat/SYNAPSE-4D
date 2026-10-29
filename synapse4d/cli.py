"""
Synapse 4D - CLI Interface (v2.5)
Commands: init, consolidate, search, audit, undo, review, migrate, serve, dashboard.
"""

import argparse
import sys
import os
import shutil
from pathlib import Path
from synapse4d import __version__
from synapse4d.core import SynapseEngine
from synapse4d.storage.migration import VaultMigrator


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(
        prog="synapse4d",
        description=f"Synapse 4D (v{__version__}) - Arquitectura de Memoria Persistente 4D para Agentes de IA y Obsidian"
    )
    parser.add_argument("--version", action="version", version=f"synapse4d {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # init
    init_parser = subparsers.add_parser("init", help="Inicializar una nueva bóveda cognitiva CoALA")
    init_parser.add_argument("path", help="Directorio destino para la bóveda cognitiva")

    # consolidate
    cons_parser = subparsers.add_parser("consolidate", help="Ejecutar ciclo de consolidación 4D")
    cons_parser.add_argument("--vault", "-v", default=".", help="Ruta a la bóveda de Obsidian (default: directorio actual)")
    cons_parser.add_argument("--all", action="store_true", help="Procesar todas las bitácoras episódicas, no solo las recientes")

    # search
    search_parser = subparsers.add_parser("search", help="Búsqueda híbrida semántica y temporal")
    search_parser.add_argument("query", help="Texto o concepto a buscar")
    search_parser.add_argument("--vault", "-v", default=".", help="Ruta a la bóveda de Obsidian")
    search_parser.add_argument("--limit", "-n", type=int, default=5, help="Número de resultados")

    # audit
    audit_parser = subparsers.add_parser("audit", help="Auditar salud de la bóveda, enlaces rotos y hechos pendientes")
    audit_parser.add_argument("--vault", "-v", default=".", help="Ruta a la bóveda de Obsidian")

    # undo
    undo_parser = subparsers.add_parser("undo", help="Revertir de forma determinista una sesión de consolidación previa")
    undo_parser.add_argument("session_id", help="ID de la sesión de consolidación a revertir")
    undo_parser.add_argument("--vault", "-v", default=".", help="Ruta a la bóveda de Obsidian")

    # review
    review_parser = subparsers.add_parser("review", help="Auditar, promover o descartar hechos provisionales")
    review_parser.add_argument("--vault", "-v", default=".", help="Ruta a la bóveda de Obsidian")
    review_parser.add_argument("--promote", help="ID del hecho provisional a promover a axioma activo")
    review_parser.add_argument("--demote", help="ID del hecho a degradar o invalidar")

    # migrate
    migrate_parser = subparsers.add_parser("migrate", help="Migrar bóveda legacy v1.0 a esquema relacional SQLite v2.0")
    migrate_parser.add_argument("--vault", "-v", default=".", help="Ruta a la bóveda de Obsidian")
    migrate_parser.add_argument("--no-backup", action="store_true", help="Omitir respaldo automático preventivo")

    # dashboard (Open Core notice)
    dash_parser = subparsers.add_parser("dashboard", help="Lanzar el Master Cognitive HUD (Pro Edition)")
    dash_parser.add_argument("--vault", "-v", default=".", help="Ruta a la bóveda de Obsidian")
    dash_parser.add_argument("--port", "-p", type=int, default=5000, help="Puerto web (default: 5000)")

    # serve (MCP Server)
    serve_parser = subparsers.add_parser("serve", help="Iniciar el servidor MCP de Synapse 4D para Antigravity/Cursor/Claude")
    serve_parser.add_argument("--vault", "-v", default=".", help="Ruta a la bóveda de Obsidian")

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
            print(f"[OK] Bóveda cognitiva inicializada exitosamente en: {target}")
        else:
            print(f"[ERROR] Directorio de plantillas no encontrado en {template_dir}")

    elif args.command == "consolidate":
        engine = SynapseEngine(args.vault)
        print(f"[Synapse 4D] Consolidando bóveda: {engine.vault_path}...")
        res = engine.consolidate(recent_only=not args.all)
        print(f"[OK] Sesión: {res['session_id']}")
        print(f"[OK] Bitácoras procesadas: {res['processed_streams']}")
        print(f"[OK] Hechos destilados: {res['facts_distilled']} (+{res['facts_retained']} retenidos, ~{res['facts_superseded']} invalidados, ={res['facts_redundant']} redundantes)")
        print(f"[OK] Stubs de clausura D4 creados: {res['stubs_created']}")

    elif args.command == "search":
        engine = SynapseEngine(args.vault)
        results = engine.search(args.query, limit=args.limit)
        print(f"\n[Synapse 4D - Búsqueda Híbrida Semántica para: '{args.query}']\n")
        if not results:
            print("No se encontraron hechos activos coincidentes.")
        for i, hit in enumerate(results, 1):
            rev_tag = " [PENDIENTE DE REVISIÓN]" if hit.get("needs_review") else ""
            sim = hit.get("similarity", 0.0)
            score = hit.get("score", 0.0)
            print(f"[{i}] ({hit['entity']} -> {hit['attribute']}): {hit['value']}{rev_tag} | Score: {score:.3f} (Sim: {sim:.3f}, Conf: {hit['confidence']})")
        print()

    elif args.command == "audit":
        engine = SynapseEngine(args.vault)
        report = engine.audit()
        print(f"\n=======================================================")
        print(f"            SYNAPSE 4D - AUDITORÍA COGNITIVA           ")
        print(f"=======================================================")
        print(f"Bóveda: {report['vault_path']}")
        print(f"Nodos totales: {report['total_nodes']}")
        print(f"Hechos activos (SQLite): {report['active_facts_count']}")
        print(f"Aristas activas (D4 Mesh): {report['active_edges_count']}")
        print(f"Enlaces totales: {report['total_bindings']}")
        print(f"Enlaces rotos: {report['broken_bindings_count']}")
        print(f"Score de salud: {report['health_score']}")
        print(f"Recuperación post-crash: {report['recovery_status']}")

        if report["needs_review_alert"]:
            print(f"\n[ALERTA ROJA] {report['needs_review_count']} hechos pendientes de revisión (>20).")
            print("Ejecuta 'synapse4d review' para auditar o promover hechos provisionales.")
        elif report["needs_review_count"] > 0:
            print(f"\n[INFO] {report['needs_review_count']} hechos provisionales pendientes de revisión.")

        if report["broken_bindings"]:
            print("\nPrimeros enlaces rotos detectados:")
            for b in report["broken_bindings"]:
                print(f"  - {b['file']} -> [[{b['target']}]]")
        print(f"=======================================================\n")

    elif args.command == "undo":
        engine = SynapseEngine(args.vault)
        print(f"[Synapse 4D] Revirtiendo sesión: {args.session_id}...")
        res = engine.undo(args.session_id)
        print(f"[OK] Hechos restaurados: {res['facts_restored']}")
        print(f"[OK] Hechos revocados: {res['facts_rolled_back']}")

    elif args.command == "review":
        engine = SynapseEngine(args.vault)
        if args.promote:
            engine.promote_fact(args.promote)
            print(f"[OK] Hecho {args.promote} promovido a axioma activo con confianza 1.0.")
        elif args.demote:
            engine.demote_fact(args.demote)
            print(f"[OK] Hecho {args.demote} invalidado/degradado.")
        else:
            pending = engine.review()
            print(f"\n=== Hechos Pendientes de Revisión ({len(pending)}) ===")
            if not pending:
                print("Todos los hechos están consolidados y confirmados. Cero deuda técnica.")
            for p in pending:
                print(f"[{p['id']}] {p['entity']} -> {p['attribute']}: {p['value']} (Conf: {p['confidence']})")
                print(f"       Para promover: synapse4d review --promote {p['id']}")
            print()

    elif args.command == "migrate":
        migrator = VaultMigrator(args.vault)
        print(f"[Synapse 4D] Iniciando migración a SQLite relacional en: {migrator.vault_path}...")
        res = migrator.migrate(create_backup=not args.no_backup)
        if res.get("success"):
            print(f"[OK] Migración exitosa.")
            print(f"     Sesión: {res['session_id']}")
            print(f"     Aristas migradas: {res['edges_migrated']}")
            print(f"     Hechos migrados: {res['facts_migrated']}")
            if res.get("backup_path"):
                print(f"     Copia de respaldo en: {res['backup_path']}")
        else:
            print(f"[ERROR] Error durante migración: {res.get('error')}")

    elif args.command == "dashboard":
        print("\n[Synapse 4D Open Core]")
        print("El HUD interactivo 2D/3D es parte de Synapse 4D Pro Edition.")
        print("Para lanzarlo con interfaz visual nativa y soporte para Obsidian:")
        print("  1. Adquiere o activa Synapse 4D Pro Edition.")
        print("  2. Consulta: https://synapse4d.lemonsqueezy.com/buy\n")

    elif args.command == "serve":
        from synapse4d.mcp_server import run_mcp_server
        run_mcp_server(vault_path=args.vault)


if __name__ == "__main__":
    main()
