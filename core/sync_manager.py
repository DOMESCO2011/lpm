import os
import json
import requests
from pathlib import Path

class SyncManager:
    def __init__(self):
        # A projekt gyökérkönyvtárának meghatározása (lpm/)
        self.root_dir = Path(__file__).parent.parent
        self.config_path = self.root_dir / "config.json"
        
        # A registry a projekt mappáján belül (lpm/registry)
        self.registry_dir = self.root_dir / "storage/registry"
        self.registry_dir.mkdir(parents=True, exist_ok=True)

    def load_mirrors(self):
        if not self.config_path.exists():
            print(f"[ERR] Config not found at {self.config_path}")
            return []
        
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                return config.get("mirror_servers", [])
        except json.JSONDecodeError:
            print("[ERR] config.json is corrupted.")
            return []

    def perform_sync(self):
        mirrors = self.load_mirrors()
        if not mirrors:
            print("[WARN] No mirrors to sync from.")
            return

        for mirror in mirrors:
            url = mirror if mirror.startswith("http") else f"http://{mirror}"
            sync_url = f"{url.rstrip('/')}/sync"
            
            print(f"[INFO] Connecting to: {sync_url}")

            try:
                response = requests.get(sync_url, timeout=5)
                response.raise_for_status()
                
                data = response.json()
                
                safe_name = mirror.replace(":", "_").replace(".", "_")
                save_path = self.registry_dir / f"{safe_name}.json"

                with open(save_path, "w") as f:
                    json.dump(data, f, indent=4)
                
                print(f"[OK] Synced! Metadata saved to: {save_path}")

            except requests.exceptions.RequestException as e:
                print(f"[ERR] Connection error ({mirror}): {e}")

if __name__ == "__main__":
    SyncManager().perform_sync()