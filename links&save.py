import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from conf import USERNAME, PASSWORD

# === НАСТРОЙКИ ===
BASE_URL = "https://los-files.sev-in.ru/"
TARGET_URL = "https://los-files.sev-in.ru/"
LINKS_FILE = "links_17-09.txt"
DOWNLOAD_DIR = "downloads_17"
FILES_TO_DOWNLOAD = 20  # Установите 0 или None, если нужно скачать ВСЕ файлы


def get_all_links():
    """Собирает все ссылки со страницы и сохраняет в файл."""
    print("🔑 Авторизация и сбор списка ссылок...")

    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        response = session.get(TARGET_URL, timeout=300)
        response.raise_for_status()
    except Exception as e:
        print(f" Ошибка при загрузке страницы: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    links = []

    for li in soup.select("ul.list-group > li.list-group-item"):
        a_tag = li.find("a", href=True)
        if a_tag:
            full_url = urljoin(BASE_URL, a_tag["href"])
            links.append(full_url)

    # Сохраняем список в файл
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(links))

    print(f"✅ Собрано ссылок: {len(links)}")
    print(f"💾 Список сохранен в '{LINKS_FILE}'")
    return links


def download_files(links):
    """Скачивает файлы по списку ссылок."""
    if not links:
        print("❌ Список ссылок пуст. Скачивание невозможно.")
        return

    # Определяем сколько качать
    to_download = links[:FILES_TO_DOWNLOAD] if FILES_TO_DOWNLOAD and FILES_TO_DOWNLOAD > 0 else links
    print(f"\n⬇️ Начинаю скачивание ({len(to_download)} из {len(links)} файлов)...")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Создаем новую сессию (или можно переиспользовать, но лучше отдельную для загрузки)
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    for i, url in enumerate(to_download, 1):
        try:
            # Декодируем URL для получения правильного пути с кириллицей
            decoded_path = unquote(url.split("file=")[-1])

            # Формируем полный путь сохранения
            filepath = os.path.join(DOWNLOAD_DIR, decoded_path)

            #  Создаем все промежуточные папки
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            filename = os.path.basename(filepath)
            print(f"[{i}/{len(to_download)}] Скачиваю: {decoded_path}")

            with session.get(url, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"   💾 Сохранено: {filepath} ({size_mb:.2f} MB)\n")

        except Exception as e:
            print(f"   ❌ Ошибка при скачивании {url}: {e}\n")


if __name__ == "__main__":
    all_links = get_all_links()
    download_files(all_links)
    print("🏁 Работа завершена.")