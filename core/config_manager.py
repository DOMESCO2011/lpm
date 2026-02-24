import os

logo_str = r"""
$$\       $$$$$$$\  $$\      $$\ 
$$ |      $$  __$$\ $$$\    $$$ |
$$ |      $$ |  $$ |$$$$\  $$$$ |
$$ |      $$$$$$$  |$$\$$\$$ $$ |
$$ |      $$  ____/ $$ \$$$  $$ |
$$ |      $$ |      $$ |\$  /$$ |
$$$$$$$$\ $$ |      $$ | \_/ $$ |
\________|\__|      \__|     \__|
"""

def int_main():
    print(logo_str)
    print("LPM configuration interpreter -- type help to the help message")
    while True:
        command = input("lpm:interpreter> ")
        if command == "exit":
            break
        elif command == "config":
            config()
        elif command == "dev":
            dev()
        else:
            print("Command not found")


def config():
    print("Config")

import os
import glob

def dev():
    print("dev mode")
    while True:
        coma = input("dev>")
        if coma == "clean":
            print("cleaning everything...")
            
            folders_to_empty = ["storage/cache", "storage/registry"]
            
            for folder in folders_to_empty:
                try:
                    files = glob.glob(f"{folder}/*")
                    for f in files:
                        if os.path.isfile(f) or os.path.islink(f):
                            os.unlink(f)
                        elif os.path.isdir(f):
                            import shutil
                            shutil.rmtree(f)
                    
                    print(f"[INFO] {folder} tartalma ürítve.")
                except Exception as e:
                    print(f"[ERR] Hiba a(z) {folder} ürítése közben: {e}")
        elif coma == "exit":
            break