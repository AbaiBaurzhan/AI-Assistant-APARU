"""Модуль для fuzzy matching приветствий."""

import logging
from typing import Dict, List, Optional, Tuple

from rapidfuzz import fuzz

from .fuzzy_config import (
    ENABLE_FUZZY_CACHE,
    FUZZY_CACHE_SIZE,
    FUZZY_SCORER,
    GREETING_TYPES,
    LOG_FUZZY_MATCHES,
    LOG_FUZZY_THRESHOLD,
    MAX_FUZZY_LENGTH,
)

# Настройка логирования
logger = logging.getLogger(__name__)

# Простой кэш для результатов fuzzy matching
_fuzzy_cache: Dict[str, Tuple[bool, float, str]] = {}


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Вычисляет сходство между двумя текстами используя rapidfuzz.

    Args:
        text1: Первый текст для сравнения
        text2: Второй текст для сравнения

    Returns:
        float: Процент сходства (0-100)
    """
    if not text1 or not text2:
        return 0.0

    # Ограничиваем длину для производительности
    if len(text1) > MAX_FUZZY_LENGTH or len(text2) > MAX_FUZZY_LENGTH:
        text1 = text1[:MAX_FUZZY_LENGTH]
        text2 = text2[:MAX_FUZZY_LENGTH]

    # Используем выбранный scorer
    if FUZZY_SCORER == "ratio":
        similarity = fuzz.ratio(text1, text2)
    elif FUZZY_SCORER == "partial_ratio":
        similarity = fuzz.partial_ratio(text1, text2)
    elif FUZZY_SCORER == "token_sort_ratio":
        similarity = fuzz.token_sort_ratio(text1, text2)
    elif FUZZY_SCORER == "token_set_ratio":
        similarity = fuzz.token_set_ratio(text1, text2)
    else:
        similarity = fuzz.ratio(text1, text2)

    return float(similarity)


def get_best_match(message: str, patterns: List[str]) -> Tuple[str, float]:
    """
    Находит наиболее похожий паттерн из списка.

    Args:
        message: Сообщение для сравнения
        patterns: Список паттернов для сравнения

    Returns:
        Tuple[str, float]: (лучший_паттерн, сходство)
    """
    if not patterns:
        return "", 0.0

    best_pattern = ""
    best_similarity = 0.0

    for pattern in patterns:
        similarity = calculate_similarity(message, pattern)
        if similarity > best_similarity:
            best_similarity = similarity
            best_pattern = pattern

    return best_pattern, best_similarity


def determine_greeting_type(pattern: str) -> str:
    """
    Определяет тип приветствия по паттерну.

    Args:
        pattern: Паттерн приветствия

    Returns:
        str: Тип приветствия ("formal", "informal", "short", "question", "thanks")
    """
    pattern_lower = pattern.lower()

    for greeting_type, config in GREETING_TYPES.items():
        for type_pattern in config["patterns"]:
            if type_pattern in pattern_lower:
                return greeting_type

    return "informal"  # По умолчанию


def get_threshold_for_type(greeting_type: str) -> float:
    """
    Получает порог сходства для типа приветствия.

    Args:
        greeting_type: Тип приветствия

    Returns:
        float: Порог сходства
    """
    return GREETING_TYPES.get(greeting_type, {}).get("threshold", 85.0)


def fuzzy_greeting_match(
    message: str, patterns: List[str], threshold: Optional[float] = None
) -> Tuple[bool, float, str]:
    """
    Проверяет приветствие с помощью fuzzy matching.

    Args:
        message: Сообщение для проверки
        patterns: Список паттернов приветствий
        threshold: Порог сходства (если None, определяется автоматически)

    Returns:
        Tuple[bool, float, str]: (найдено, сходство, лучший_паттерн)
    """
    if not message or not patterns:
        return False, 0.0, ""

    # Проверяем кэш
    cache_key = f"{message.lower()}_{len(patterns)}"
    if ENABLE_FUZZY_CACHE and cache_key in _fuzzy_cache:
        logger.debug(f"Fuzzy match из кэша: '{message}'")
        return _fuzzy_cache[cache_key]

    # Находим лучший паттерн
    best_pattern, similarity = get_best_match(message, patterns)

    # Определяем порог
    if threshold is None:
        greeting_type = determine_greeting_type(best_pattern)
        threshold = get_threshold_for_type(greeting_type)

    # Проверяем, превышает ли сходство порог
    is_match = similarity >= threshold

    # Логируем результат
    if LOG_FUZZY_MATCHES and similarity >= LOG_FUZZY_THRESHOLD:
        logger.info(
            f"Fuzzy match: '{message}' -> '{best_pattern}' "
            f"(similarity: {similarity:.1f}%, threshold: {threshold:.1f}%, match: {is_match})"
        )

    result = (is_match, similarity, best_pattern)

    # Сохраняем в кэш
    if ENABLE_FUZZY_CACHE:
        if len(_fuzzy_cache) >= FUZZY_CACHE_SIZE:
            # Очищаем кэш при превышении размера
            _fuzzy_cache.clear()
        _fuzzy_cache[cache_key] = result

    return result


def clear_fuzzy_cache() -> None:
    """Очищает кэш fuzzy matching."""
    _fuzzy_cache.clear()
    logger.debug("Fuzzy cache очищен")


def get_fuzzy_cache_stats() -> Dict[str, int]:
    """
    Возвращает статистику кэша fuzzy matching.

    Returns:
        Dict[str, int]: Статистика кэша
    """
    return {
        "cache_size": len(_fuzzy_cache),
        "max_cache_size": FUZZY_CACHE_SIZE,
        "cache_usage_percent": int((len(_fuzzy_cache) / FUZZY_CACHE_SIZE) * 100),
    }
