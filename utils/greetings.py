"""Модуль для обработки приветствий в FAQ-ассистенте."""

import logging
import re
from typing import Optional, Tuple

from .fuzzy_greetings import fuzzy_greeting_match
from .greetings_config import (
    FALLBACK_CONFIDENCE_THRESHOLD,
    FALLBACK_GREETING_RESPONSE,
    GREETING_PATTERNS,
    PARTIAL_GREETING_PATTERNS,
    STANDARD_GREETING_RESPONSE,
)
from .smart_normalize import is_potential_greeting, smart_normalize_text

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


def hybrid_greeting_detection(message: str) -> Tuple[bool, Optional[str], str]:
    """
    Гибридная система распознавания приветствий.

    Алгоритм:
    1. Умная нормализация текста
    2. Быстрое сравнение с расширенными паттернами
    3. Если не найдено - fuzzy matching
    4. Логирование результата

    Args:
        message: Сообщение для проверки

    Returns:
        Tuple[bool, Optional[str], str]: (найдено, паттерн, метод)
    """
    if not message or not isinstance(message, str):
        return False, None, "invalid_input"

    # Этап 1: Умная нормализация
    normalized = smart_normalize_text(message)

    # Этап 2: Быстрое сравнение с расширенными паттернами
    exact_match = check_extended_patterns(normalized)
    if exact_match:
        logger.debug(f"Найдено точное приветствие: '{exact_match}'")
        return True, exact_match, "extended_patterns"

    # Этап 3: Проверка частичных совпадений
    partial_match = check_partial_patterns(normalized)
    if partial_match:
        logger.debug(f"Найдено частичное приветствие: '{partial_match}'")
        return True, partial_match, "partial_patterns"

    # Этап 4: Fuzzy matching для сложных случаев
    if is_potential_greeting(normalized):
        fuzzy_match, similarity, best_pattern = fuzzy_greeting_match(
            normalized, GREETING_PATTERNS
        )

        if fuzzy_match:
            logger.debug(
                f"Найдено fuzzy приветствие: '{best_pattern}' (similarity: {similarity:.1f}%)"
            )
            return True, best_pattern, f"fuzzy_{similarity:.1f}%"

    return False, None, "no_match"


def check_extended_patterns(normalized_message: str) -> Optional[str]:
    """
    Проверяет точные совпадения с расширенными паттернами.

    Args:
        normalized_message: Нормализованное сообщение

    Returns:
        Optional[str]: Найденный паттерн или None
    """
    # Проверяем точные совпадения с паттернами
    for pattern in GREETING_PATTERNS:
        if normalized_message == pattern:
            return pattern

    return None


def check_partial_patterns(normalized_message: str) -> Optional[str]:
    """
    Проверяет частичные совпадения в начале сообщения.

    Args:
        normalized_message: Нормализованное сообщение

    Returns:
        Optional[str]: Найденный паттерн или None
    """
    # Проверяем частичные совпадения в начале сообщения
    for pattern in PARTIAL_GREETING_PATTERNS:
        if normalized_message.startswith(pattern):
            return pattern

    # Проверяем, начинается ли сообщение с приветствия
    words = normalized_message.split()
    if words:
        first_word = words[0]
        for pattern in GREETING_PATTERNS:
            if first_word == pattern.split()[0]:
                return pattern

    return None


def is_greeting(message: str) -> Tuple[bool, Optional[str]]:
    """
    Проверяет, является ли сообщение приветствием.
    Использует гибридную систему распознавания.

    Args:
        message: Сообщение для проверки

    Returns:
        Tuple[bool, Optional[str]]: (найдено, паттерн)
    """
    is_greeting_flag, greeting_pattern, method = hybrid_greeting_detection(message)

    if is_greeting_flag:
        logger.info(f"Приветствие распознано: '{greeting_pattern}' (method: {method})")
        return True, greeting_pattern

    return False, None


def extract_main_content(message: str) -> str:
    """
    Извлекает основное содержание сообщения, убирая приветствие.
    Использует гибридную систему для более точного извлечения.

    Args:
        message: Исходное сообщение пользователя

    Returns:
        str: Сообщение без приветствия, только основное содержание
    """
    if not message or not isinstance(message, str):
        return ""

    # Используем умную нормализацию
    normalized_message = smart_normalize_text(message)
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


def get_fallback_greeting() -> str:
    """
    Возвращает fallback приветствие для случаев с низкой уверенностью.

    Returns:
        str: Fallback приветствие с предложением помощи
    """
    return FALLBACK_GREETING_RESPONSE


def should_use_fallback_greeting(confidence: float) -> bool:
    """
    Проверяет, нужно ли использовать fallback приветствие.

    Args:
        confidence: Уровень уверенности системы (0.0 - 1.0)

    Returns:
        bool: True если нужно использовать fallback приветствие
    """
    return confidence < FALLBACK_CONFIDENCE_THRESHOLD


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
