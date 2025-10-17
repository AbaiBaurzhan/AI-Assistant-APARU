"""Модуль для умной нормализации текста приветствий."""

import re
from typing import Dict, List


def smart_normalize_text(text: str) -> str:
    """
    Умная нормализация текста для лучшего распознавания опечаток.

    Args:
        text: Исходный текст

    Returns:
        str: Нормализованный текст
    """
    if not text:
        return ""

    # Базовая нормализация
    normalized = text.lower().strip()

    # Убираем знаки препинания в конце
    normalized = re.sub(r"[.!?]+$", "", normalized)

    # Убираем лишние пробелы
    normalized = re.sub(r"\s+", " ", normalized).strip()

    # Удаляем повторяющиеся символы (приветт -> привет)
    normalized = re.sub(r"(.)\1+", r"\1", normalized)

    # Стандартизация частых опечаток
    normalized = apply_common_fixes(normalized)

    return normalized


def apply_common_fixes(text: str) -> str:
    """
    Применяет исправления для частых опечаток.

    Args:
        text: Текст для исправления

    Returns:
        str: Исправленный текст
    """
    # Словарь частых исправлений (только неправильные -> правильные)
    common_fixes: Dict[str, str] = {
        # Формальные приветствия с опечатками
        "здраствуйте": "здравствуйте",  # пропуск "в"
        "здравствуйте": "здравствуйте",  # замена "в" на "в"
        "добрый ден": "добрый день",  # пропуск мягкого знака
        # Неформальные приветствия с опечатками
        "приветт": "привет",  # удвоение "т"
        "привет": "привет",  # замена "т" на "т"
        # Остальные паттерны оставляем как есть
    }

    # Применяем исправления только для неправильных вариантов
    for wrong, correct in common_fixes.items():
        if text == wrong:  # Точное совпадение с неправильным вариантом
            text = correct
            break

    return text


def extract_greeting_words(text: str) -> List[str]:
    """
    Извлекает слова, которые могут быть приветствиями.

    Args:
        text: Текст для анализа

    Returns:
        List[str]: Список потенциальных приветствий
    """
    words = text.split()
    greeting_words = []

    # Список слов-приветствий
    greeting_word_list = [
        "здравствуйте",
        "здраствуйте",
        "здравствуйте",
        "добрый",
        "доброе",
        "доброго",
        "добрй",  # опечатка в "добрый"
        "ден",  # опечатка в "день"
        "привет",
        "приветт",
        "привет",
        "хай",
        "хелло",
        "хей",
        "здрасьте",
        "здарова",
        "добреньки",
        "как",
        "все",
        "спасибо",
        "благодарю",
    ]

    for word in words:
        if word.lower() in greeting_word_list:
            greeting_words.append(word.lower())

    return greeting_words


def is_potential_greeting(text: str) -> bool:
    """
    Проверяет, может ли текст быть приветствием.

    Args:
        text: Текст для проверки

    Returns:
        bool: True если текст может быть приветствием
    """
    if not text:
        return False

    normalized = smart_normalize_text(text)

    # Проверяем длину (приветствия обычно короткие)
    if len(normalized) > 100:
        return False

    # Проверяем наличие слов-приветствий
    greeting_words = extract_greeting_words(normalized)
    if not greeting_words:
        return False

    # Проверяем, что текст не содержит явно не-приветственных слов
    non_greeting_words = [
        "вопрос",
        "проблема",
        "ошибка",
        "помощь",
        "заказ",
        "оплата",
        "доставка",
        "возврат",
        "жалоба",
        "претензия",
    ]

    for word in non_greeting_words:
        if word in normalized:
            return False

    return True


def normalize_for_fuzzy_matching(text: str) -> str:
    """
    Специальная нормализация для fuzzy matching.

    Args:
        text: Текст для нормализации

    Returns:
        str: Текст, оптимизированный для fuzzy matching
    """
    if not text:
        return ""

    # Применяем умную нормализацию
    normalized = smart_normalize_text(text)

    # Дополнительные оптимизации для fuzzy matching
    # Убираем очень короткие слова (предлоги, союзы)
    words = normalized.split()
    filtered_words = [word for word in words if len(word) > 2]

    return " ".join(filtered_words)
