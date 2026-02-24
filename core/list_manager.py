import os
import json
import hashlib
from pathlib import Path

class ListManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.registry_dir = self.root_dir / "storage" / "registry"
        self.cache_dir = self.root_dir / "storage" / "cache"

    def _get_local_hash(self, file_path):
        """Kiszámolja a helyi fájl SHA256 hash-ét."""
        if not file_path.exists():
            return None
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except:
            return None

    def list_packages(self, filter_mode="all"):
        """
        Csomagok kilistázása.
        filter_mode: 'all', 'ins' (telepített), 'upd' (naprakész)
        """
        all_packages = []

        # Registry fájlok beolvasása
        if not self.registry_dir.exists():
            print("[ERR] Registry directory missing!")
            return

        for reg_file in self.registry_dir.glob("*.json"):
            try:
                with open(reg_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for p in data.get("packages", []):
                        all_packages.append(p)
            except:
                continue

        if not all_packages:
            print("[!] No packages found in registry. Try 'lpm sync' first.")
            return

        print(f"\n{'ID':<15} {'NAME':<20} {'VERSION':<10} {'STATUS':<15}")
        print("-" * 65)

        for pkg in all_packages:
            p_id = pkg.get("id", "n/a")
            p_name = pkg.get("name", "n/a")
            p_ver = pkg.get("version", "n/a")
            filename = pkg.get("filename", "")
            remote_hash = pkg.get("hash", "")

            target_path = self.cache_dir / filename
            is_installed = target_path.exists()
            
            status = "Not Installed"
            is_up_to_date = False

            if is_installed:
                local_hash = self._get_local_hash(target_path)
                if local_hash == remote_hash:
                    status = "Installed"
                    is_up_to_date = True
                else:
                    status = "Update Avail"

            # Szűrési logika
            if filter_mode == "ins" and not is_installed:
                continue
            if filter_mode == "upd" and not is_up_to_date:
                continue

            print(f"{p_id:<15} {p_name:<20} {p_ver:<10} {status:<15}")

        print("-" * 65 + "\n")