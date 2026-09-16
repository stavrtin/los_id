import requests
from base64 import b64encode
from conf import USERNAME, PASSWORD

BASE_URL = "https://los-files.sev-in.ru/"


def debug_auth():
    print("=== ДИАГНОСТИКА АВТОРИЗАЦИИ ===")
    print(f"Логин из конфига: '{USERNAME}'")
    print(f"Пароль из конфига: '{PASSWORD}'")
    print(f"Длина пароля: {len(PASSWORD)}")

    # Тест 1: Стандартный Basic Auth через requests
    print("\n1️⃣ Тест: requests.auth (стандартный)")
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)
    resp = session.get(BASE_URL, timeout=30)
    print(f"   Статус: {resp.status_code}")

    # Тест 2: Ручное формирование заголовка Authorization
    print("\n2️⃣ Тест: Ручной заголовок Authorization")
    creds = f"{USERNAME}:{PASSWORD}"
    encoded = b64encode(creds.encode('utf-8')).decode('ascii')
    headers = {'Authorization': f'Basic {encoded}'}
    resp2 = requests.get(BASE_URL, headers=headers, timeout=30)
    print(f"   Статус: {resp2.status_code}")

    # Тест 3: Формат DOMAIN\User (если применимо)
    # Раскомментируйте и подставьте свой домен, если есть
    # domain_user = r"SEV-IN\user_login"
    # print(f"\n3️⃣ Тест: Формат DOMAIN\\User")
    # session3 = requests.Session()
    # session3.auth = (domain_user, PASSWORD)
    # resp3 = session3.get(BASE_URL, timeout=30)
    # print(f"   Статус: {resp3.status_code}")


if __name__ == "__main__":
    debug_auth()