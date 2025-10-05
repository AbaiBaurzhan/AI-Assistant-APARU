"""Конфигурация консольного приложения."""

import os
from pathlib import Path

# Пути к файлам
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
HISTORY_FILE = PROJECT_ROOT / "chat_history.jsonl"

# Пороги уверенности
CONFIDENCE_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.6,
    "low": 0.0,
}

# Настройки истории
MAX_HISTORY_ENTRIES = 1000
HISTORY_AUTO_SAVE = True

# Настройки отображения
COLORS = {
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "blue",
    "muted": "dim",
}

# Настройки API
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30

# Настройки прогресс-баров
PROGRESS_BAR_STYLE = "█"
PROGRESS_BAR_WIDTH = 50
