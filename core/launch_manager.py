import os
import subprocess
from pathlib import Path

class LaunchManager:
    def __init__(self):
        # A struktúra alapján a storage/cache mappát használjuk
        self.root_dir = Path(__file__).parent.parent
        self.cache_dir = self.root_dir / "storage" / "cache"

    def launch_package(self, package_name):
        """Megkeresi és futtatja a csomagot a cache-ből."""
        
        # Megkeressük a fájlt (lehet .AppImage kiterjesztése vagy anélkül)
        # Először pontos egyezést nézünk, aztán .AppImage kiterjesztéssel
        target_path = self.cache_dir / package_name
        if not target_path.exists():
            target_path = self.cache_dir / f"{package_name}.AppImage"

        if not target_path.exists():
            print(f"[ERR] Package '{package_name}' not found in cache. Run 'lpm trans' first.")
            return False

        # Ellenőrizzük, hogy futtatható-e (Linuxon ez kritikus)
        if not os.access(target_path, os.X_OK):
            print(f"[WARN] Package '{package_name}' is not executable. Fixing permissions...")
            try:
                os.chmod(target_path, 0o755)
            except Exception as e:
                print(f"[ERR] Failed to set executable permission: {e}")
                return False

        print(f"[INFO] Launching {target_path.name}...")
        
        try:
            # Popen-t használunk, hogy a fő folyamat ne fagyjon be, amíg a szoftver fut
            # A stderr és stdout az aktuális terminálra lesz irányítva
            subprocess.run([str(target_path)], check=True)
            return True
        except KeyboardInterrupt:
            print(f"\n[INFO] Package '{package_name}' stopped by user.")
            return True
        except Exception as e:
            print(f"[ERR] An error occurred while running the package: {e}")
            return False