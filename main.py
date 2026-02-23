import argparse
import sys
from core.sync_manager import SyncManager
from core.transaction_manager import TransactionManager
from core.launch_manager import LaunchManager
from core.file_manager import rm

def main():
    parser = argparse.ArgumentParser(
        description="LPM - Launchable Packet Manager",
        usage="lpm <command> [<args>]"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Core commands ---
    subparsers.add_parser("sync", help="Sync package list from the central server")
    subparsers.add_parser("trans", help="Transaction: Sync/Download newly listed packages")
    
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

    args = parser.parse_args()

    # --- Logic Routing ---
    if args.command == "sync":
        print("[INFO] Starting package index update...")
        syncer = SyncManager()
        syncer.perform_sync()
        
    elif args.command == "trans":
        print("[INFO] Processing transactions...")
        tm = TransactionManager()
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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()