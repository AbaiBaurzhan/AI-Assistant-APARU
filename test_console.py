#!/usr/bin/env python3
"""Запуск консольного приложения для тестирования FAQ-ассистента."""

import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from test_console.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
