from pathlib import Path


def build_tree(paths):
    """Строит вложенный словарь-дерево из списка путей (только папки)."""
    tree = {}
    for raw_path in paths:
        raw_path = raw_path.strip()
        if not raw_path:
            continue

        # Нормализуем разделители (на случай Windows-путей)
        parts = raw_path.replace("\\", "/").split("/")
        parts = [p for p in parts if p]

        # Последний элемент — имя файла, его пропускаем
        folders = parts[:-1]

        node = tree
        for folder in folders:
            node = node.setdefault(folder, {})
    return tree


def render_tree(tree, prefix="", is_last=True, is_root=True):
    """Рекурсивно рисует дерево каталогов в виде псевдографики."""
    lines = []
    items = sorted(tree.items())

    for i, (name, subtree) in enumerate(items):
        last = (i == len(items) - 1)

        if is_root:
            # Корневые элементы без соединителей
            lines.append(name)
            lines.extend(render_tree(subtree, prefix="", is_last=last, is_root=False))
        else:
            connector = "└── " if last else "├── "
            lines.append(prefix + connector + name)
            extension = "    " if last else "│   "
            lines.extend(render_tree(subtree, prefix + extension, is_last=last, is_root=False))

    return lines


def main():
    input_file = "paths_only.txt"
    output_file = "folder_tree.txt"

    with open(input_file, "r", encoding="utf-8") as f:
        paths = f.readlines()

    tree = build_tree(paths)
    lines = render_tree(tree)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Дублируем вывод в консоль
    print("\n".join(lines))
    print(f"\nРезультат сохранён в {output_file}")


if __name__ == "__main__":
    main()