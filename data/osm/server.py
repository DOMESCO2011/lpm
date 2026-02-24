from flask import Flask, send_from_directory, jsonify, abort
import os
import hashlib

app = Flask(__name__)

# Konfiguráció
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_DIR = os.path.join(BASE_DIR, "manifest")
PORT = 5000

def get_sha256(file_path):
    """Kiszámolja a fájl SHA256 hash-ét az integritás ellenőrzéshez."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@app.route('/sync', methods=['GET'])
def sync_manifest():
    """
    Dinamikusan legenerálja a csomaglistát. 
    Jelenleg csak a test.AppImage fájlt keresi.
    """
    target_file = "test.AppImage"
    file_path = os.path.join(MANIFEST_DIR, target_file)

    if not os.path.exists(file_path):
        return jsonify({"error": f"File '{target_file}' not found in manifest directory."}), 404

    # Itt épül fel a JSON válasz
    package_info = {
        "packages": [
            {
                "id": "test-app",
                "name": "Test Application",
                "filename": target_file,
                "version": "1.0.0",
                "hash": get_sha256(file_path),
                "size_bytes": os.path.getsize(file_path),
                "launch_command": f"./{target_file}"
            }
        ]
    }
    return jsonify(package_info)

@app.route('/download/<filename>', methods=['GET'])
def download_package(filename):
    """Kiszolgálja a tényleges fájlt letöltésre."""
    if not os.path.exists(os.path.join(MANIFEST_DIR, filename)):
        abort(404)
    return send_from_directory(MANIFEST_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    # Mappa ellenőrzése
    if not os.path.exists(MANIFEST_DIR):
        os.makedirs(MANIFEST_DIR)
        print(f"[*] Created missing directory: {MANIFEST_DIR}")
        print("[!] Please drop a 'test.AppImage' file into it.")

    print(f"🚀 LPM Official Server running on http://0.0.0.0:{PORT}")
    print(f"🔗 Sync URL: http://localhost:{PORT}/sync")
    app.run(host='0.0.0.0', port=PORT, debug=False)
