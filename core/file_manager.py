import os

def rm(package):
    if input(f"Do you want to remove {package} N/y ") == "y":
        print(f"[INFO] Deleting package: {package}")
        try:
            os.system(f"rm storage/cache/{package}")
            print("Packet has been removed")
        except Exception as e:
            print(f"[ERR] Error while deleting package: {e}")
    else:
        pass