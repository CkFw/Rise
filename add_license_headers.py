#!/usr/bin/env python
"""
Скрипт для автоматического добавления лицензионного заголовка GPLv3
в начало всех .py файлов проекта, исключая сторонние библиотеки.
"""

import os
import sys

# --- Конфигурация ---
AUTHOR = "Ваше Имя"          # Замените на своё имя
YEAR = "2025"                # Год создания/публикации
PROJECT_NAME = "Rise Browser"  # Название проекта

# Папки, которые нужно исключить (можно добавить свои)
EXCLUDE_DIRS = {
    'venv', 'env', '.venv', '.env', '__pycache__', '.git', 'build', 'dist',
    'data', 'I2P', 'assets', 'icons', '.idea', '.vscode'
}

# Расширения файлов для обработки
EXTENSIONS = ('.py',)

# Заголовок лицензии (без первой строки с комментариями, её добавим отдельно)
LICENSE_HEADER = f"""# Этот файл является частью {PROJECT_NAME}.
# Copyright (C) {"2026"} {"Clark Flow (Егор)"}
# 
# {PROJECT_NAME} is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# {PROJECT_NAME} is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


def should_skip_file(filepath):
    """Проверяет, нужно ли пропустить файл."""
    # Проверяем расширение
    if not filepath.endswith(EXTENSIONS):
        return True
    # Проверяем, находится ли файл в исключённой папке
    for part in filepath.split(os.sep):
        if part in EXCLUDE_DIRS:
            return True
    return False


def has_license(filepath):
    """Проверяет, содержит ли файл уже лицензионный заголовок."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Читаем первые 30 строк, обычно заголовок помещается туда
            first_lines = ''.join(f.readline() for _ in range(30))
            # Ищем характерные фразы
            if 'GNU General Public License' in first_lines or 'Copyright (C)' in first_lines:
                return True
    except Exception as e:
        print(f"Ошибка чтения {filepath}: {e}")
    return False


def add_license(filepath):
    """Добавляет лицензионный заголовок в начало файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Не удалось прочитать {filepath}: {e}")
        return False

    # Проверяем наличие shebang
    lines = content.splitlines(keepends=True)
    new_content = []
    if lines and lines[0].startswith('#!'):
        # Сохраняем shebang
        new_content.append(lines[0])
        # Если после shebang пустая строка, оставляем её
        if len(lines) > 1 and lines[1].strip() == '':
            new_content.append(lines[1])
            start_idx = 2
        else:
            start_idx = 1
        # Добавляем заголовок
        new_content.append(LICENSE_HEADER + '\n')
        # Добавляем остальной код
        new_content.extend(lines[start_idx:])
    else:
        # Просто вставляем заголовок в начало
        new_content = [LICENSE_HEADER + '\n'] + lines

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
        print(f"✅ Добавлен заголовок: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Ошибка записи {filepath}: {e}")
        return False


def main():
    # Запрашиваем корневую директорию (по умолчанию текущая)
    root_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    root_dir = os.path.abspath(root_dir)

    if not os.path.isdir(root_dir):
        print(f"Ошибка: {root_dir} не является директорией")
        sys.exit(1)

    print(f"Сканируем {root_dir} ...")
    count_processed = 0
    count_skipped = 0
    count_already = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Удаляем из обхода исключённые папки на лету, чтобы не заходить в них
        for d in list(dirnames):
            if d in EXCLUDE_DIRS:
                dirnames.remove(d)

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if should_skip_file(filepath):
                continue

            if has_license(filepath):
                # print(f"⏩ Уже есть лицензия: {filepath}")
                count_already += 1
                continue

            if add_license(filepath):
                count_processed += 1
            else:
                count_skipped += 1

    print("\n--- Результат ---")
    print(f"Добавлено заголовков: {count_processed}")
    print(f"Уже были: {count_already}")
    print(f"Пропущено (ошибки): {count_skipped}")


if __name__ == '__main__':
    main()