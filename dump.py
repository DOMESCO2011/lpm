import os

OUTPUT_FILE = "tree_dump.txt"

TEXT_EXTENSIONS = {
    ".py", ".txt", ".c", ".h", ".ld", ".asm", ".json"
}

def write(line, file):
    print(line)
    file.write(line + "\n")

def is_text_file(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in TEXT_EXTENSIONS

def print_tree(path, file, prefix=""):
    items = sorted(os.listdir(path))
    for i, item in enumerate(items):
        item_path = os.path.join(path, item)
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        write(prefix + connector + item, file)

        if os.path.isdir(item_path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(item_path, file, new_prefix)
        else:
            # 🔒 csak engedélyezett szövegfájlok tartalma
            if not is_text_file(item):
                continue

            try:
                with open(item_path, "r", encoding="utf-8", errors="ignore") as f:
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    for line in f:
                        line = line.rstrip()
                        if not line:
                            continue
                        if len(line) > 120:
                            line = line[:117] + "..."
                        write(new_prefix + "| " + line, file)
            except Exception:
                continue

if __name__ == "__main__":
    root_folder = os.path.dirname(os.path.abspath(__file__))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        write(f"Directory tree of: {root_folder}\n", out)
        print_tree(root_folder, out)

    print(f"\n✔ Kimenet elmentve: {OUTPUT_FILE}")
