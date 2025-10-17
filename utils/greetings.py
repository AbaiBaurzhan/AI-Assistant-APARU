"""Модуль для обработки приветствий в FAQ-ассистенте."""

import logging
import re
from typing import Optional, Tuple

from .greetings_config import (
    GREETING_PATTERNS,
    PARTIAL_GREETING_PATTERNS,
    STANDARD_GREETING_RESPONSE,
)

# Настройка логирования
logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """Нормализует текст для сравнения с паттернами приветствий."""
    if not text:
        return ""

    # Приводим к нижнему регистру и убираем лишние пробелы
    normalized = text.lower().strip()

    # Убираем знаки препинания в конце
    normalized = re.sub(r"[.!?]+$", "", normalized)

    return normalized


def is_greeting(message: str) -> Tuple[bool, Optional[str]]:
    """Проверяет, является ли сообщение приветствием."""
    if not message or not isinstance(message, str):
        return False, None

    normalized_message = normalize_text(message)

    # Проверяем точные совпадения с паттернами
    for pattern in GREETING_PATTERNS:
        if normalized_message == pattern:
            logger.debug(f"Найдено точное приветствие: '{pattern}'")
            return True, pattern

    # Проверяем частичные совпадения в начале сообщения
    for pattern in PARTIAL_GREETING_PATTERNS:
        if normalized_message.startswith(pattern):
            logger.debug(f"Найдено частичное приветствие: '{pattern}'")
            return True, pattern

    # Проверяем, начинается ли сообщение с приветствия
    words = normalized_message.split()
    if words:
        first_word = words[0]
        for pattern in GREETING_PATTERNS:
            if first_word == pattern.split()[0]:
                logger.debug(f"Найдено приветствие в начале: '{first_word}'")
                return True, pattern

    return False, None


def extract_main_content(message: str) -> str:
    """Извлекает основное содержание сообщения, убирая приветствие."""
    if not message or not isinstance(message, str):
        return ""

    normalized_message = normalize_text(message)
    is_greeting_flag, greeting_pattern = is_greeting(message)

    if not is_greeting_flag:
        return message.strip()

    # Убираем найденное приветствие из начала сообщения
    if greeting_pattern:
        # Убираем точное совпадение
        if normalized_message == greeting_pattern:
            return ""

        # Убираем частичное совпадение в начале
        if normalized_message.startswith(greeting_pattern):
            remaining = normalized_message[len(greeting_pattern) :].strip()
            # Убираем запятые и другие знаки препинания после приветствия
            remaining = re.sub(r"^[,.\-:;]+", "", remaining).strip()
            return remaining

    # Если не удалось точно определить, пробуем убрать первое слово
    words = normalized_message.split()
    if len(words) > 1:
        # Проверяем, является ли первое слово приветствием
        first_word = words[0]
        for pattern in GREETING_PATTERNS:
            if first_word == pattern.split()[0]:
                remaining_words = words[1:]
                remaining_text = " ".join(remaining_words)
                # Убираем знаки препинания после приветствия
                remaining_text = re.sub(r"^[,.\-:;]+", "", remaining_text).strip()
                return remaining_text

    return ""


def get_greeting_response() -> str:
    """Возвращает стандартный ответ на приветствие."""
    return STANDARD_GREETING_RESPONSE


def process_greeting_message(message: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Обрабатывает сообщение на предмет приветствия."""
    is_greeting_flag, greeting_pattern = is_greeting(message)

    if not is_greeting_flag:
        return False, None, message

    # Если это только приветствие
    main_content = extract_main_content(message)
    if not main_content:
        logger.info(f"Обработано приветствие: '{greeting_pattern}'")
        return True, get_greeting_response(), None

    # Если приветствие + вопрос
    logger.info(
        f"Обработано приветствие с вопросом: '{greeting_pattern}' + '{main_content}'"
    )
    return True, None, main_content
