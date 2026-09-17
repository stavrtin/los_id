import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from conf import USERNAME, PASSWORD

# === НАСТРОЙКИ ===
BASE_URL = "https://los-files.sev-in.ru/"
TARGET_URL = "https://los-files.sev-in.ru/"
LINKS_FILE = "links_17-09.txt"
DOWNLOAD_DIR = "downloads_17"
FILES_TO_DOWNLOAD = 20 # 0 или None — скачать все файлы


def ts():
    """Быстрая метка времени для логов."""
    return datetime.now().strftime("%H:%M:%S")


def get_all_links():
    """Собирает все ссылки со страницы и сохраняет в файл."""
    print(f"[{ts()}] 🔑 Авторизация и сбор списка ссылок...")

    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        response = session.get(TARGET_URL, timeout=300)
        response.raise_for_status()
    except Exception as e:
        print(f"[{ts()}]  Ошибка при загрузке страницы: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    links = []

    for li in soup.select("ul.list-group > li.list-group-item"):
        a_tag = li.find("a", href=True)
        if a_tag:
            full_url = urljoin(BASE_URL, a_tag["href"])
            links.append(full_url)

    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(links))

    print(f"[{ts()}] ✅ Собрано ссылок: {len(links)}")
    print(f"[{ts()}] 💾 Список сохранен в '{LINKS_FILE}'")
    return links


def download_files(links):
    """Скачивает файлы по списку ссылок."""
    if not links:
        print(f"[{ts()}] ❌ Список ссылок пуст. Скачивание невозможно.")
        return

    to_download = links[:FILES_TO_DOWNLOAD] if FILES_TO_DOWNLOAD and FILES_TO_DOWNLOAD > 0 else links
    print(f"[{ts()}] ⬇️ Начинаю скачивание ({len(to_download)} из {len(links)} файлов)...")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    total_start = time.monotonic()          # общий таймер, см. ниже

    for i, url in enumerate(to_download, 1):
        try:
            decoded_path = unquote(url.split("file=")[-1])
            filepath = os.path.join(DOWNLOAD_DIR, decoded_path)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            print(f"[{ts()}] [{i}/{len(to_download)}] Скачиваю: {decoded_path}")

            file_start = time.monotonic()
            with session.get(url, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            elapsed = time.monotonic() - file_start

            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"[{ts()}]    💾 Сохранено: {filepath} "
                  f"({size_mb:.2f} MB, {elapsed:.1f} с)\n")

        except Exception as e:
            print(f"[{ts()}]    ❌ Ошибка при скачивании {url}: {e}\n")

    total = time.monotonic() - total_start
    print(f"[{ts()}] 🏁 Работа завершена. Общее время: {total/60:.1f} мин")


if __name__ == "__main__":
    all_links = get_all_links()
    download_files(all_links)