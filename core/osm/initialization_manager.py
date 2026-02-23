import json
import os
import sys
import paramiko

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)


from crypto.encrypt import encrypt
from crypto.encrypt import decrypt

def save_to_config(username, password_hash):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "..", "config.json")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("[ERR] config.json not found")

    data["ssh-username"] = username
    data["ssh-hash"] = password_hash

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def ssh_cliinit():
    usrname = input("Enter your osm ssh server username: ")
    hashpass = encrypt(input("Enter your osm ssh server password: "))
    save_to_config(usrname, hashpass)

def sshserverinit():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # A projekt gyökerében lévő config.json elérése
    config_path = os.path.normpath(os.path.join(current_dir, "..", "..", "config.json"))

    try:
        # 1. Adatok betöltése a config.json-ból
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        user = data.get("ssh-username")
        encrypted_pass = data.get("ssh-hash")
        
        # A mirror_servers listából vesszük az első szerver objektumot
        servers = data.get("mirror_servers", [])
        if not servers:
            print("[ERR] No mirror servers found in config.json")
            return

        server = servers[0]
        host = server.get("host")
        ssh_port = server.get("ssh_port", 22)  # Alapértelmezett 22, ha nincs megadva
        https_port = server.get("https_port", 5000) # Későbbi API hívásokhoz jól jöhet

        if not host or not user or not encrypted_pass:
            print("[ERR] Missing host, user, or encrypted password in config.json")
            return

        # Jelszó visszafejtése
        password = decrypt(encrypted_pass)

        # 2. SSH kliens inicializálása
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Itt már a dedikált ssh_port-ot használjuk!
        print(f"Connecting to {host} via SSH on port {ssh_port} (User: {user})...")
        
        ssh.connect(
            hostname=host, 
            port=ssh_port, 
            username=user, 
            password=password,
            timeout=10 # Érdemes egy timeout-ot megadni a lefagyás ellen
        )

        print("[OK] SSH connection established.")

        # 3. SFTP munkamenet nyitása
        sftp = ssh.open_sftp()
        print("[OK] SFTP session opened.")

        return ssh, sftp # Érdemes visszaadni őket, hogy tudj velük dolgozni

    except Exception as e:
        print(f"Hiba történt: {e}")
        return None, None


sshserverinit()