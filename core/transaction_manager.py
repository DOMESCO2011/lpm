import os
import json
import hashlib
import requests
from pathlib import Path

class TransactionManager:
    def __init__(self):
        # Elérési utak beállítása a struktúrád alapján
        self.root_dir = Path(__file__).parent.parent
        self.registry_dir = self.root_dir / "storage" / "registry"
        self.cache_dir = self.root_dir / "storage" / "cache"
        self.config_path = self.root_dir / "config.json"
        
        # Mappa létrehozása, ha még nincs
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_local_hash(self, file_path):
        if not file_path.exists():
            return None
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _load_mirrors(self):
        if not self.config_path.exists():
            print("[ERR] config.json not found")
            return []
        try:
            with open(self.config_path, "r") as f:
                return json.load(f).get("mirror_servers", [])
        except:
            return []

    def process_downloads(self):
        mirrors = self._load_mirrors()
        if not mirrors:
            print("[ERR] No mirrors configured")
            return

        # Végigmegyünk minden regisztrált JSON fájlon
        for reg_file in self.registry_dir.glob("*.json"):
            try:
                with open(reg_file, "r") as f:
                    data = json.load(f)
                    packages = data.get("packages", [])
            except:
                continue

            for pkg in packages:
                filename = pkg.get("filename")
                expected_hash = pkg.get("hash")
                target_path = self.cache_dir / filename

                # Ellenőrizzük, megvan-e már a fájl és jó-e a hash
                if target_path.exists():
                    if self._get_local_hash(target_path) == expected_hash:
                        print(f"[OK] {filename} is up to date")
                        continue

                # Letöltés megkísérlése a mirrorokról
                success = False
                for mirror in mirrors:
                    base_url = mirror if mirror.startswith("http") else f"http://{mirror}"
                    download_url = f"{base_url.rstrip('/')}/download/{filename}"
                    
                    print(f"[INFO] Downloading {filename} from {mirror}...")
                    try:
                        r = requests.get(download_url, stream=True, timeout=10)
                        r.raise_for_status()
                        
                        with open(target_path, "wb") as f_out:
                            for chunk in r.iter_content(chunk_size=8192):
                                f_out.write(chunk)
                        
                        # Futtathatóvá tétel (chmod +x)
                        os.chmod(target_path, 0o755)
                        
                        # Ellenőrzés letöltés után
                        if self._get_local_hash(target_path) == expected_hash:
                            print(f"[OK] {filename} downloaded and verified")
                            success = True
                            break
                        else:
                            print(f"[ERR] Hash mismatch for {filename}")
                    except Exception as e:
                        print(f"[WARN] Failed to download from {mirror}: {e}")
                
                if not success:
                    print(f"[ERR] Could not acquire {filename}")