import argparse
import sys
from core.sync_manager import SyncManager
from core.transaction_manager import TransactionManager
from core.launch_manager import LaunchManager
from core.file_manager import rm
from core.config_manager import int_main, logo_str
from core.list_manager import ListManager



def main():
    parser = argparse.ArgumentParser(
        description="LPM - Launchable Packet Manager",
        usage="lpm <command> [<args>]"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")


    # List parancs beállítása
    list_parser = subparsers.add_parser("list", help="List packages")
    list_group = list_parser.add_mutually_exclusive_group()
    list_group.add_argument("--all", action="store_true", help="Show all (default)")
    list_group.add_argument("--ins", action="store_true", help="Show only installed")
    list_group.add_argument("--upd", action="store_true", help="Show only up-to-date")


    # --- Core commands ---
    subparsers.add_parser("sync", help="Sync package list from the central server")
    subparsers.add_parser("config", help="Configuration interpreter")
    
    rem_parser = subparsers.add_parser("rem", help="Remove a package")
    rem_parser.add_argument("package", help="Name of the package to remove")
    
    launch_parser = subparsers.add_parser("launch", help="Run a package in an isolated environment")
    launch_parser.add_argument("package", help="Name of the package to launch")

    # --- OSM (Own Mirror System) commands ---
    osm_parser = subparsers.add_parser("osm", help="Manage your own mirror servers")
    osm_subparsers = osm_parser.add_subparsers(dest="osm_command")

    init_parser = osm_subparsers.add_parser("init", help="Initialize a custom server locally")
    init_parser.add_argument("name", help="Identifier name for the server")

    conf_parser = osm_subparsers.add_parser("conf", help="Configure server connection details")
    conf_parser.add_argument("name", help="Name of the server to configure")

    conn_parser = osm_subparsers.add_parser("connect", help="Connect to the server via SSH")
    conn_parser.add_argument("name", help="Name of the server")

    osm_sync_parser = osm_subparsers.add_parser("sync", help="Sync a package from a custom server")
    osm_sync_parser.add_argument("package", help="Package name")
    osm_sync_parser.add_argument("name", help="Server name")

    trans_parser = subparsers.add_parser("trans", help="Download packages")
    trans_parser.add_argument("package", nargs="?", help="Specific package ID to download (optional)")

    args = parser.parse_args()

    # --- Logic Routing ---
    if args.command == "sync":
        print("[INFO] Starting package index update...")
        syncer = SyncManager()
        syncer.perform_sync()
        
    elif args.command == "trans":
            tm = TransactionManager()
            if args.package:
                print(f"[INFO] Processing transaction for: {args.package}...")
                tm.process_downloads(target_package_id=args.package)
            else:
                print("[INFO] Processing all pending transactions...")
                tm.process_downloads()
        
    elif args.command == "rem":
        rm(args.package)
        
    elif args.command == "launch":
        # Itt hívjuk meg a launch_manager-t
        launcher = LaunchManager()
        launcher.launch_package(args.package)

    elif args.command == "osm":
        if args.osm_command == "init":
            print(f"[INFO] OSM: Initializing {args.name}...")
        elif args.osm_command == "conf":
            print(f"[INFO] OSM: Configuring {args.name}...")
        elif args.osm_command == "connect":
            print(f"[INFO] OSM: Connecting to {args.name}...")
        elif args.osm_command == "sync":
            print(f"[INFO] OSM: Syncing {args.package} from {args.name}...")
        else:
            osm_parser.print_help()

    elif args.command == "config":
        int_main()

    elif args.command == "list":
        lm = ListManager()
        mode = "all"
        if args.ins: mode = "ins"
        elif args.upd: mode = "upd"
        lm.list_packages(filter_mode=mode)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()