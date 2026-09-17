import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from conf import USERNAME, PASSWORD

# === НАСТРОЙКИ ===
BASE_URL = "https://los-files.sev-in.ru/"
TARGET_URL = "https://los-files.sev-in.ru/"
LINKS_FILE = "links_csv_17-09.txt"
DOWNLOAD_DIR = "downloads_csv_all"  # Единая общая папка для всех CSV
CSV_FILES_TO_DOWNLOAD = 0  # 0 = скачать ВСЕ найденные CSV-файлы


def get_unique_filepath(base_dir, filename):
    """
    Проверяет наличие файла и добавляет постфикс _v2, _v3... при дубликатах.
    Возвращает гарантированно уникальный путь.
    """
    filepath = os.path.join(base_dir, filename)

    if not os.path.exists(filepath):
        return filepath

    name, ext = os.path.splitext(filename)
    counter = 2

    while True:
        new_filename = f"{name}_v{counter}{ext}"
        new_filepath = os.path.join(base_dir, new_filename)

        if not os.path.exists(new_filepath):
            return new_filepath

        counter += 1


def get_csv_links():
    """Собирает ВСЕ ссылки, но возвращает только те, что заканчиваются на .csv"""
    print("🔑 Авторизация и поиск CSV-файлов...")

    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        response = session.get(TARGET_URL, timeout=300)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Ошибка при загрузке страницы: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    all_links = []
    csv_links = []

    for li in soup.select("ul.list-group > li.list-group-item"):
        a_tag = li.find("a", href=True)
        if a_tag:
            full_url = urljoin(BASE_URL, a_tag["href"])
            all_links.append(full_url)

            # Фильтрация по расширению .csv
            decoded_url = unquote(full_url)
            if decoded_url.lower().endswith(".csv"):
                csv_links.append(full_url)

    print(f" Всего ссылок на странице: {len(all_links)}")
    print(f"📄 Найдено CSV-файлов: {len(csv_links)}")

    # Сохраняем ТОЛЬКО CSV-ссылки в файл
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(csv_links))

    print(f"💾 Список CSV сохранен в '{LINKS_FILE}'")
    return csv_links


def download_files(links):
    """Скачивает CSV-файлы в общую папку с обработкой дубликатов."""
    if not links:
        print("❌ CSV-файлы не найдены. Скачивание невозможно.")
        return

    # Определяем сколько качать
    to_download = links[:CSV_FILES_TO_DOWNLOAD] if CSV_FILES_TO_DOWNLOAD and CSV_FILES_TO_DOWNLOAD > 0 else links
    print(f"\n⬇️ Начинаю скачивание ({len(to_download)} из {len(links)} CSV-файлов)...")

    # Создаем ЕДИНУЮ общую папку
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    for i, url in enumerate(to_download, 1):
        try:
            # Декодируем URL и берем только имя файла (без пути к папкам)
            decoded_path = unquote(url.split("file=")[-1])
            filename = os.path.basename(decoded_path)

            # 🔥 Получаем уникальный путь (добавит _v2, _v3 если нужно)
            save_path = get_unique_filepath(DOWNLOAD_DIR, filename)

            # Если имя изменилось из-за дубликата, выводим уведомление
            display_name = os.path.basename(save_path)
            if display_name != filename:
                print(f"[{i}/{len(to_download)}] Дубликат! Сохраняю как: {display_name}")
            else:
                print(f"[{i}/{len(to_download)}] Скачиваю: {filename}")

            with session.get(url, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            size_kb = os.path.getsize(save_path) / 1024
            print(f"    💾 Сохранено: {save_path} ({size_kb:.2f} KB)\n")

        except Exception as e:
            print(f"   ❌ Ошибка при скачивании {url}: {e}\n")


if __name__ == "__main__":
    csv_links = get_csv_links()
    download_files(csv_links)
    print("🏁 Работа завершена.")