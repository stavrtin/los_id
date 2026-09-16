import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from conf import USERNAME, PASSWORD

# === НАСТРОЙКИ ===
TARGET_URL = "https://los-files.sev-in.ru/"


def collect_links_selenium():
    options = Options()

    # ⚠️ ВАЖНО: Укажите точный путь к вашему браузеру
    # Если у вас Google Chrome:
    CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    # Если у вас Microsoft Edge (раскомментируйте строку ниже):
    # CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    options.binary_location = CHROME_PATH

    # Опции для стабильной работы в фоне
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    print("🚀 Запуск браузера через Selenium Manager...")
    try:
        # Selenium Manager автоматически найдет/скачает chromedriver
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"❌ Не удалось запустить браузер: {e}")
        print("💡 Проверьте, что путь в CHROME_PATH верный и файл существует.")
        return []

    try:
        # Кодирование пароля на случай спецсимволов (@, :, / и т.д.)
        safe_password = quote(PASSWORD, safe='')
        auth_url = f"https://{USERNAME}:{safe_password}@los-files.sev-in.ru/"

        print("🔑 Выполняется авторизация...")
        driver.get(auth_url)

        # Ждем появления списка файлов.
        # Для 54k файлов может потребоваться больше времени, чем стандартные 10 сек.
        print("⏳ Ожидаем загрузки страницы (это может занять время)...")
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list-group"))
        )

        page_source = driver.page_source

        print("✅ Страница загружена. Парсинг ссылок...")
        soup = BeautifulSoup(page_source, "lxml")
        raw_links = []

        for li in soup.select("ul.list-group > li.list-group-item"):
            a_tag = li.find("a", href=True)
            if a_tag:
                full_url = urljoin(TARGET_URL, a_tag["href"])
                raw_links.append(full_url)

        print(f"📂 Собрано ссылок: {len(raw_links)}")
        return raw_links

    except Exception as e:
        print(f"❌ Ошибка при сборе данных: {e}")
        return []
    finally:
        driver.quit()
        print("🛑 Браузер закрыт.")


if __name__ == "__main__":
    links = collect_links_selenium()

    if links:
        print("\n--- Первые 5 ссылок ---")
        for link in links[:5]:
            print(link)

        with open("links.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(links))
        print("💾 Ссылки сохранены в links.txt")
    else:
        print("Ссылки не собраны.")