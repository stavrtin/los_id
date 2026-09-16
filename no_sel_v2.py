import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from conf import USERNAME, PASSWORD

# === НАСТРОЙКИ ===
BASE_URL = "https://los-files.sev-in.ru/"
TARGET_URL = "https://los-files.sev-in.ru/"
DOWNLOAD_DIR = "downloads"
FILES_TO_DOWNLOAD = 8


def download_files():
    # Создаем корневую папку загрузок
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    print(" Получаем список ссылок...")
    response = session.get(TARGET_URL, timeout=300)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    links = []

    for li in soup.select("ul.list-group > li.list-group-item"):
        a_tag = li.find("a", href=True)
        if a_tag:
            full_url = urljoin(BASE_URL, a_tag["href"])
            links.append(full_url)
            if len(links) >= FILES_TO_DOWNLOAD:
                break

    if not links:
        print("❌ Ссылки не найдены.")
        return

    print(f"✅ Найдено {len(links)} ссылок. Начинаю скачивание...\n")

    for i, url in enumerate(links, 1):
        try:
            # Декодируем URL и извлекаем относительный путь файла
            decoded_url = unquote(url.split("file=")[-1])

            # 🔥 КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Собираем полный путь к файлу
            # os.path.join корректно обрабатывает слэши на Windows
            filepath = os.path.join(DOWNLOAD_DIR, decoded_url)

            # Создаем ВСЕ промежуточные папки (TrailCams/Отработано/...)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            filename = os.path.basename(filepath)
            print(f"[{i}/{len(links)}] Скачиваю: {decoded_url}")

            with session.get(url, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"   💾 Сохранено: {filepath} ({size_mb:.2f} MB)\n")

        except Exception as e:
            print(f"   ❌ Ошибка: {e}\n")


if __name__ == "__main__":
    download_files()