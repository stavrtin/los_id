import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from conf import USERNAME, PASSWORD

# === НАСТРОЙКИ ===
BASE_URL = "https://los-files.sev-in.ru/"
TARGET_URL = "https://los-files.sev-in.ru/"
LINKS_FILE = "links_csv_17-09.txt"
DOWNLOAD_DIR = "downloads_csv"
CSV_FILES_TO_DOWNLOAD = 500  # Сколько именно CSV-файлов скачать (0 = все найденные)


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
        print(f" Ошибка при загрузке страницы: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    all_links = []
    csv_links = []

    for li in soup.select("ul.list-group > li.list-group-item"):
        a_tag = li.find("a", href=True)
        if a_tag:
            full_url = urljoin(BASE_URL, a_tag["href"])
            all_links.append(full_url)

            #  ФИЛЬТРАЦИЯ: проверяем расширение файла
            # unquote декодирует %2F в /, чтобы корректно проверить конец пути
            decoded_url = unquote(full_url)
            if decoded_url.lower().endswith(".csv"):
                csv_links.append(full_url)

    print(f"📊 Всего ссылок на странице: {len(all_links)}")
    print(f"📄 Найдено CSV-файлов: {len(csv_links)}")

    # Сохраняем ТОЛЬКО CSV-ссылки в файл
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(csv_links))

    print(f"💾 Список CSV сохранен в '{LINKS_FILE}'")
    return csv_links


def download_files(links):
    """Скачивает указанные CSV-файлы."""
    if not links:
        print("❌ CSV-файлы не найдены. Скачивание невозможно.")
        return

    # Определяем сколько качать
    to_download = links[:CSV_FILES_TO_DOWNLOAD] if CSV_FILES_TO_DOWNLOAD and CSV_FILES_TO_DOWNLOAD > 0 else links
    print(f"\n⬇️ Начинаю скачивание ({len(to_download)} из {len(links)} CSV-файлов)...")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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

            # Создаем все промежуточные папки
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            filename = os.path.basename(filepath)
            print(f"[{i}/{len(to_download)}] Скачиваю: {decoded_path}")

            with session.get(url, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            size_kb = os.path.getsize(filepath) / 1024
            print(f"    Сохранено: {filepath} ({size_kb:.2f} KB)\n")

        except Exception as e:
            print(f"   ❌ Ошибка при скачивании {url}: {e}\n")


if __name__ == "__main__":
    csv_links = get_csv_links()
    download_files(csv_links)
    print("🏁 Работа завершена.")