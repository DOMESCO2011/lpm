import os
import json
import hashlib
import requests
from pathlib import Path
from tqdm import tqdm

class TransactionManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.registry_dir = self.root_dir / "storage" / "registry"
        self.cache_dir = self.root_dir / "storage" / "cache"
        self.config_path = self.root_dir / "config.json"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_local_hash(self, file_path):
        if not file_path.exists():
            return None
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return None

    def _load_mirrors(self):
        if not self.config_path.exists():
            print("[ERR] config.json not found")
            return []
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("mirror_servers", [])
        except Exception as e:
            print(f"[ERR] Failed to load config: {e}")
            return []

    def process_downloads(self, target_package_id=None):
        mirrors = self._load_mirrors()
        if not mirrors:
            print("[ERR] No mirrors configured")
            return

        for reg_file in self.registry_dir.glob("*.json"):
            try:
                with open(reg_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    packages = data.get("packages", [])
            except Exception:
                continue

            for pkg in packages:
                pkg_id = pkg.get("id")
                filename = pkg.get("filename")
                expected_hash = pkg.get("hash")
                total_size = pkg.get("size_bytes", 0) # JSON-ból kinyert méret
                
                if target_package_id and pkg_id != target_package_id:
                    continue

                target_path = self.cache_dir / filename

                # 1. Integritás ellenőrzés
                if target_path.exists():
                    if self._get_local_hash(target_path) == expected_hash:
                        if target_package_id:
                            print(f"[OK] {pkg_id} is already up to date")
                        continue

                # 2. Letöltés mirrorokról
                success = False
                for mirror in mirrors:
                    host = mirror.get("host")
                    port = mirror.get("https_port", 5000)
                    if not host: continue

                    download_url = f"http://{host}:{port}/download/{filename}"
                    
                    try:
                        response = requests.get(download_url, stream=True, timeout=10)
                        response.raise_for_status()
                        
                        # Ha a szerver nem küld Content-Length-et, a JSON-ből vesszük
                        content_length = int(response.headers.get('content-length', total_size))

                        # Progress Bar inicializálása
                        progress_bar = tqdm(
                            total=content_length,
                            unit='B',
                            unit_scale=True,
                            desc=f"[DOWNLOAD] {filename}",
                            ascii=True
                        )

                        with open(target_path, "wb") as f_out:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f_out.write(chunk)
                                    progress_bar.update(len(chunk))
                        
                        progress_bar.close()

                        # Jogosultság és Hash ellenőrzés
                        os.chmod(target_path, 0o755)
                        if self._get_local_hash(target_path) == expected_hash:
                            print(f"[OK] {filename} verified.")
                            success = True
                            break
                        else:
                            print(f"[ERR] Hash mismatch for {filename}")
                            if target_path.exists(): target_path.unlink()

                    except Exception as e:
                        print(f"[WARN] Mirror {host} failed: {e}")
                
                if not success:
                    print(f"[ERR] Could not acquire {filename}")