import re

def extract_camera_names(filename: str) -> list[str]:
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    # Заглавная латинская буква + 1-2 цифры (возможен ведущий ноль).
    # Слева — не буква/цифра (чтобы не поймать "KDSP1"), справа — не буква/цифра
    # (чтобы поймать имена перед "_", "-", ".", концом строки и т.п.).
    pattern = re.compile(r"(?<![A-Za-z0-9])([A-Z]\d{1,2})(?![0-9A-Za-z])")

    names = set(pattern.findall(text))
    return sorted(names, key=lambda x: (x[0], int(x[1:])))

if __name__ == "__main__":
    # cameras = extract_camera_names("folder_tree.txt")
    cameras = extract_camera_names("paths_only.txt")
    print(cameras)
    print(f"Всего уникальных ловушек: {len(cameras)}")