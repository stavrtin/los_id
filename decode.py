#!/usr/bin/env python3
"""
Скрипт для декодирования percent-encoding (URL-encoding) в кириллицу.
Читает файл со списком URL, декодирует параметр file= и сохраняет результат.
"""

import sys
import re
from urllib.parse import unquote, urlparse, parse_qs, urlencode, urlunparse
from pathlib import Path


def decode_url(url: str) -> str:
    """
    Декодирует URL: percent-encoding → кириллица, '+' → пробел.
    Корректно обрабатывает параметр file= с вложенными путями.
    """
    # urllib.parse.unquote декодирует %XX, но НЕ трогает '+'
    # В query-строках '+' означает пробел, поэтому сначала заменим '+' на '%20'
    # ВНИМАНИЕ: делаем это только для параметров, не для всего URL целиком

    parsed = urlparse(url.strip())

    if not parsed.query:
        # Нет query — декодируем путь целиком
        return unquote(url)

    # Разбираем query на параметры
    # parse_qs автоматически декодирует %, но '+' превращает в пробел —
    # это как раз то, что нам нужно для кириллицы (пробелы кодируются как '+' или %20)
    params = parse_qs(parsed.query, keep_blank_values=True)

    # Собираем query обратно, но с декодированными значениями
    # parse_qs уже сделал unquote, поэтому теперь просто склеиваем
    decoded_query_parts = []
    for key, values in params.items():
        for value in values:
            decoded_query_parts.append(f"{key}={value}")

    decoded_query = "&".join(decoded_query_parts)

    # Собираем URL обратно
    # path тоже может содержать %XX — декодируем
    decoded_path = unquote(parsed.path)

    result = urlunparse((
        parsed.scheme,
        parsed.netloc,
        decoded_path,
        parsed.params,
        decoded_query,
        parsed.fragment,
    ))

    return result


def decode_file_path_only(url: str) -> str:
    """
    Альтернативный вариант: декодирует ТОЛЬКО значение параметра file=,
    оставляя остальной URL в исходном виде. Подходит для случая,
    когда нужны "нормальные" пути к файлам.
    """
    parsed = urlparse(url.strip())
    params = parse_qs(parsed.query, keep_blank_values=True)

    if "file" in params:
        # parse_qs уже декодировал значение
        file_value = params["file"][0]
        return file_value

    return url


def process_file(input_path: str, output_path: str, mode: str = "url"):
    """
    Обрабатывает файл построчно.

    mode:
        'url'  — полностью декодированный URL
        'path' — только путь из параметра file=
    """
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        print(f"Ошибка: файл '{input_path}' не найден", file=sys.stderr)
        sys.exit(1)

    lines = input_file.read_text(encoding="utf-8").splitlines()
    results = []

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        try:
            if mode == "path":
                decoded = decode_file_path_only(line)
            else:
                decoded = decode_url(line)
            results.append(decoded)
        except Exception as e:
            print(f"Строка {i}: ошибка декодирования — {e}", file=sys.stderr)
            results.append(line)  # оставляем как есть

    output_file.write_text("\n".join(results) + "\n", encoding="utf-8")
    print(f"Готово! Обработано строк: {len(results)}")
    print(f"Результат сохранён в: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование:")
        print(f"  {sys.argv[0]} <входной_файл> <выходной_файл> [url|path]")
        print()
        print("  url  — полностью декодированный URL (по умолчанию)")
        print("  path — только путь из параметра file= (без https://...)")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "url"

    if mode not in ("url", "path"):
        print(f"Неизвестный режим: {mode}", file=sys.stderr)
        sys.exit(1)

    process_file(input_file, output_file, mode)