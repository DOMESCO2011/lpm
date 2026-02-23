import subprocess

def ping_isactive(addr):
    """
    Megpingeli a megadott címet Linux alatt.
    Visszatérési érték: True (él) / False (nem elérhető)
    """
    try:

        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", addr],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        

        return result.returncode == 0
    except Exception:
        return False
