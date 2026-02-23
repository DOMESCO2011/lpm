import os
import json
import requests
from pathlib import Path

class SyncManager:
    def __init__(self):
        # 1. Resolve the absolute path of the current script
        current_path = Path(__file__).resolve()
        
        # 2. Find the 'lpm' root directory
        self.root_dir = None
        for parent in [current_path] + list(current_path.parents):
            if parent.name == "lpm":
                self.root_dir = parent
                break
        
        if not self.root_dir:
            # Fallback to 2 levels up if 'lpm' name isn't found
            self.root_dir = current_path.parent.parent

        self.config_path = self.root_dir / "config.json"
        self.registry_dir = self.root_dir / "storage" / "registry"
        
        # Ensure the storage directory exists
        self.registry_dir.mkdir(parents=True, exist_ok=True)

    def load_mirrors(self):
        """Loads the mirror server list from the config.json file."""
        if not self.config_path.exists():
            print(f"[ERR] Config file not found at: {self.config_path}")
            return []
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                mirrors = config.get("mirror_servers", [])
                
                if not isinstance(mirrors, list):
                    print("[ERR] 'mirror_servers' in config.json must be a list.")
                    return []
                return mirrors
        except (json.JSONDecodeError, IOError) as e:
            print(f"[ERR] Failed to read config.json: {e}")
            return []

    def perform_sync(self):
        """Connects to mirrors and saves registry metadata."""
        mirrors = self.load_mirrors()
        
        if not mirrors:
            print("[WARN] No mirror servers found in configuration.")
            return

        for mirror in mirrors:
            # Handle both string and dictionary formats from config.json
            if isinstance(mirror, dict):
                host = mirror.get("host")
                # Use https_port if available, otherwise default to 5000 as requested
                port = mirror.get("https_port") or mirror.get("port") or 5000
                mirror_str = f"{host}:{port}" if host else None
            else:
                mirror_str = str(mirror).strip()

            if not mirror_str:
                print(f"[ERR] Skipping invalid mirror entry: {mirror}")
                continue
            
            # Construct the final URL
            url_base = mirror_str if mirror_str.startswith("http") else f"http://{mirror_str}"
            sync_url = f"{url_base.rstrip('/')}/sync"
            
            print(f"[INFO] Connecting to: {sync_url}")

            try:
                # Request the sync data
                response = requests.get(sync_url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # Sanitize filename for Linux filesystem
                safe_name = mirror_str.replace(":", "_").replace(".", "_")
                save_path = self.registry_dir / f"{safe_name}.json"

                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                print(f"[OK] Sync complete! Data saved to: {save_path.name}")

            except requests.exceptions.RequestException as e:
                print(f"[ERR] Connection failed for {mirror_str}: {e}")

if __name__ == "__main__":
    # Test execution
    manager = SyncManager()
    manager.perform_sync()