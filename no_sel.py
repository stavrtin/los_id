from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from conf import USERNAME, PASSWORD

TARGET_URL = "https://los-files.sev-in.ru/"


def collect_links_js_hybrid():
    options = Options()
    # Укажите точный путь к вашему браузеру
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Увеличиваем лимит памяти для JS-выполнения
    options.add_argument("--js-flags=--max-old-space-size=4096")

    print("🔑 Авторизация через Selenium...")
    driver = webdriver.Chrome(options=options)

    try:
        safe_pass = quote(PASSWORD, safe='')
        auth_url = f"https://{USERNAME}:{safe_pass}@los-files.sev-in.ru/"
        driver.get(auth_url)

        # Ждем появления списка (гарантия успешной авторизации)
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list-group"))
        )

        print("✅ Авторизация прошла. Получаем HTML через JavaScript...")

        # 🔥 КЛЮЧЕВОЙ МОМЕНТ: Получаем outerHTML корневого элемента
        # Это избегает полной сериализации document.documentElement
        page_html = driver.execute_script("return document.documentElement.outerHTML;")

        if not page_html or len(page_html) < 1000:
            print("❌ Получен пустой или слишком короткий HTML. Возможно, авторизация не сработала.")
            return []

        print(f"📄 Получено {len(page_html)} символов HTML.")

    except Exception as e:
        print(f"❌ Ошибка в Selenium: {e}")
        return []
    finally:
        driver.quit()
        print("🛑 Браузер закрыт.")

    # Парсинг вне браузера
    print("🔍 Парсинг ссылок...")
    soup = BeautifulSoup(page_html, "lxml")
    raw_links = []

    for li in soup.select("ul.list-group > li.list-group-item"):
        a_tag = li.find("a", href=True)
        if a_tag:
            full_url = urljoin(TARGET_URL, a_tag["href"])
            raw_links.append(full_url)

    print(f"📂 Собрано ссылок: {len(raw_links)}")
    return raw_links


if __name__ == "__main__":
    links = collect_links_js_hybrid()

    if links:
        with open("links.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(links))
        print("💾 Ссылки сохранены в links.txt")

        print("\n--- Первые 5 ссылок ---")
        for link in links[:5]:
            print(link)
    else:
        print("❌ Не удалось собрать ссылки.")