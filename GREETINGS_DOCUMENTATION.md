# Документация по функциональности приветствий

## 📋 Содержание

1. [Обзор](#обзор)
2. [Архитектура](#архитектура)
3. [Конфигурация](#конфигурация)
4. [Основные функции](#основные-функции)
5. [Интеграция в API](#интеграция-в-api)
6. [Примеры использования](#примеры-использования)
7. [Тестирование](#тестирование)
8. [Настройка и кастомизация](#настройка-и-кастомизация)
9. [Восстановление функциональности](#восстановление-функциональности)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Обзор

Функциональность приветствий автоматически распознает приветственные сообщения пользователей и отвечает стандартным сообщением. Система поддерживает различные типы приветствий и может извлекать вопросы из сообщений, содержащих приветствие + вопрос.

### Основные возможности:

- ✅ Распознавание формальных и неформальных приветствий
- ✅ Автоматический ответ стандартным сообщением
- ✅ Извлечение вопросов из приветствий
- ✅ Поддержка различных языков
- ✅ Настраиваемые паттерны приветствий

---

## 🏗️ Архитектура

### Структура файлов:

```
utils/
├── greetings.py          # Основная логика обработки
├── greetings_config.py   # Конфигурация паттернов
└── __init__.py

routers/
└── ask.py               # Интеграция в API
```

### Компоненты системы:

1. **Конфигурация** - паттерны приветствий и стандартный ответ
2. **Нормализация** - приведение текста к стандартному виду
3. **Детекция** - определение приветствий в сообщениях
4. **Извлечение** - отделение вопроса от приветствия
5. **Интеграция** - подключение к API

---

## ⚙️ Конфигурация

### Файл: `utils/greetings_config.py`

#### Стандартный ответ на приветствие:

```python
STANDARD_GREETING_RESPONSE = (
    "Здравствуйте! Благодарим за ваше обращение. "
    "Напишите свои вопрос. Например: Какие преимущества АПАРУ ?"
)
```

#### Паттерны приветствий:

```python
GREETING_PATTERNS = [
    # Формальные приветствия
    "здравствуйте",
    "здравия желаю",
    "добрый день",
    "доброе утро",
    "добрый вечер",
    "доброго времени суток",
    "приветствую вас",
    "приветствую",

    # Неформальные приветствия
    "привет",
    "приветик",
    "хай",
    "хелло",
    "хей",
    "здрасьте",
    "здарова",
    "добреньки",

    # Вопросы-приветствия
    "как дела",
    "как поживаете",
    "все хорошо",
    "как настроение",
    "как жизнь",

    # Благодарности
    "спасибо за помощь",
    "благодарю",
    "спасибо большое",
    "спасибо",
]
```

#### Дополнительные паттерны:

```python
PARTIAL_GREETING_PATTERNS = [
    "добро пожаловать",
    "рад вас видеть",
    "добро пожаловать в службу поддержки",
]

# Английские приветствия (опционально)
ENGLISH_GREETINGS = [
    "hello", "hi", "good morning", "good afternoon",
    "good evening", "hey"
]

# Казахские приветствия (опционально)
KAZAKH_GREETINGS = [
    "сәлем", "қайырлы күн", "қайырлы таң", "қайырлы кеш"
]
```

---

## 🔧 Основные функции

### 1. `normalize_text(text: str) -> str`

**Назначение:** Приводит текст к стандартному виду для сравнения.

**Логика:**

- Приводит к нижнему регистру
- Убирает лишние пробелы
- Удаляет знаки препинания в конце

**Примеры:**

```python
normalize_text("Здравствуйте!") → "здравствуйте"
normalize_text("  Добрый день  ") → "добрый день"
normalize_text("Привет???") → "привет"
```

### 2. `is_greeting(message: str) -> Tuple[bool, Optional[str]]`

**Назначение:** Определяет, является ли сообщение приветствием.

**Возвращает:**

- `bool` - True если это приветствие, False иначе
- `Optional[str]` - найденный паттерн приветствия

**Логика проверки:**

1. **Точные совпадения:** полное соответствие паттерну
2. **Частичные совпадения:** сообщение начинается с паттерна
3. **Проверка первого слова:** первое слово совпадает с началом паттерна

**Примеры:**

```python
is_greeting("Здравствуйте") → (True, "здравствуйте")
is_greeting("Добрый день, как дела?") → (True, "добрый день")
is_greeting("Как заказать такси?") → (False, None)
```

### 3. `extract_main_content(message: str) -> str`

**Назначение:** Извлекает основное содержание, убирая приветствие.

**Логика:**

- Если только приветствие → возвращает пустую строку
- Если приветствие + текст → возвращает текст без приветствия
- Убирает знаки препинания после приветствия

**Примеры:**

```python
extract_main_content("Здравствуйте") → ""
extract_main_content("Здравствуйте, как заказать такси?") → "как заказать такси?"
extract_main_content("Добрый день! Сколько стоит поездка?") → "сколько стоит поездка?"
```

### 4. `get_greeting_response() -> str`

**Назначение:** Возвращает стандартный ответ на приветствие.

**Возвращает:** Строка с стандартным приветствием из конфигурации.

### 5. `process_greeting_message(message: str) -> Tuple[bool, Optional[str], Optional[str]]`

**Назначение:** Главная функция обработки приветствий.

**Возвращает:**

- `bool` - True если это приветствие, False если обычное сообщение
- `Optional[str]` - ответ системы (стандартный ответ или None)
- `Optional[str]` - основное содержание (вопрос без приветствия или исходное сообщение)

**Логика:**

1. Определяет, является ли сообщение приветствием
2. Если только приветствие → возвращает стандартный ответ
3. Если приветствие + вопрос → извлекает вопрос для поиска
4. Если обычное сообщение → возвращает исходное сообщение

**Примеры:**

```python
# Только приветствие
process_greeting_message("Здравствуйте") →
(True, "Здравствуйте! Благодарим за ваше обращение...", None)

# Приветствие + вопрос
process_greeting_message("Добрый день, как заказать такси?") →
(True, None, "как заказать такси?")

# Обычный вопрос
process_greeting_message("Как заказать такси?") →
(False, None, "Как заказать такси?")
```

---

## 🔗 Интеграция в API

### Файл: `routers/ask.py`

#### Импорт функции:

```python
from utils.greetings import process_greeting_message
```

#### Интеграция в endpoint `/api/v1/ask`:

```python
@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest) -> AskResponse:
    # Обрабатываем приветствие
    is_greeting_flag, greeting_response, main_content = process_greeting_message(
        request.query
    )

    # Если это только приветствие - возвращаем стандартный ответ
    if is_greeting_flag and greeting_response:
        logger.info(f"Обработано приветствие: {request.query[:50]}...")
        return AskResponse(
            reply=greeting_response,
            confidence=1.0,
            source="greeting",
            similar_questions=[],
        )

    # Определяем текст для поиска в FAQ
    search_query = main_content if main_content else request.query

    # Остальная логика поиска в FAQ...
```

#### Логика работы:

1. **Приветствие обрабатывается первым** - до поиска в FAQ
2. **Если только приветствие** - возвращается стандартный ответ с `confidence=1.0` и `source="greeting"`
3. **Если приветствие + вопрос** - извлекается вопрос и передается в поиск FAQ
4. **Если обычное сообщение** - передается в поиск FAQ как есть

---

## 📝 Примеры использования

### 1. Только приветствие

**Запрос:**

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Здравствуйте"}'
```

**Ответ:**

```json
{
  "reply": "Здравствуйте! Благодарим за ваше обращение. Напишите свои вопрос. Например: Какие преимущества АПАРУ ?",
  "confidence": 1.0,
  "source": "greeting",
  "similar_questions": []
}
```

### 2. Приветствие + вопрос

**Запрос:**

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Добрый день, какие преимущества АПАРУ?"}'
```

**Ответ:**

```json
{
  "reply": "Здравствуйте. Благодарим за ваше обращение. 1) Низкая фиксированная комиссия, а не процент от заработка водителя...",
  "confidence": 0.929,
  "source": "q001",
  "similar_questions": []
}
```

### 3. Обычный вопрос (без приветствия)

**Запрос:**

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Как заказать такси?"}'
```

**Ответ:**

```json
{
  "reply": "Уточните, пожалуйста, ваш вопрос. Возможно, вы имели в виду:",
  "confidence": 0.757,
  "source": null,
  "similar_questions": [
    "Запрос на такси с докуменами, развозка сотрудников",
    "Багаж в такси",
    "Предложение заказов"
  ]
}
```

---

## 🧪 Тестирование

### Автоматическое тестирование через curl:

```bash
#!/bin/bash

echo "=== ТЕСТ 1: Простое приветствие ==="
curl -s "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Здравствуйте"}' | jq .

echo -e "\n=== ТЕСТ 2: Неформальное приветствие ==="
curl -s "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Привет"}' | jq .

echo -e "\n=== ТЕСТ 3: Приветствие с вопросом ==="
curl -s "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Добрый день, какие преимущества АПАРУ?"}' | jq .

echo -e "\n=== ТЕСТ 4: Благодарность ==="
curl -s "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Спасибо"}' | jq .
```

### Тестирование через консольное приложение:

```bash
cd "/Users/abaibaurzhan/Desktop/ML Generation/test_console"
source ../venv/bin/activate
python main.py
```

**Команды для тестирования:**

```
ask Здравствуйте
ask Добрый день
ask Привет, как дела?
ask Спасибо за помощь
exit
```

### Unit тестирование (для разработчиков):

```python
import pytest
from utils.greetings import (
    normalize_text, is_greeting, extract_main_content,
    process_greeting_message
)

def test_normalize_text():
    assert normalize_text("Здравствуйте!") == "здравствуйте"
    assert normalize_text("  Добрый день  ") == "добрый день"

def test_is_greeting():
    assert is_greeting("Здравствуйте") == (True, "здравствуйте")
    assert is_greeting("Как дела?") == (True, "как дела")
    assert is_greeting("Обычный вопрос") == (False, None)

def test_extract_main_content():
    assert extract_main_content("Здравствуйте") == ""
    assert extract_main_content("Здравствуйте, вопрос") == "вопрос"

def test_process_greeting_message():
    # Только приветствие
    flag, response, content = process_greeting_message("Здравствуйте")
    assert flag is True
    assert response is not None
    assert content is None

    # Приветствие + вопрос
    flag, response, content = process_greeting_message("Привет, как дела?")
    assert flag is True
    assert response is None
    assert content == "как дела?"
```

---

## 🛠️ Настройка и кастомизация

### 1. Изменение стандартного ответа

**Файл:** `utils/greetings_config.py`

```python
STANDARD_GREETING_RESPONSE = (
    "Привет! Я готов помочь вам. "
    "Задайте ваш вопрос."
)
```

### 2. Добавление новых паттернов приветствий

```python
GREETING_PATTERNS = [
    # Существующие паттерны...
    "добро пожаловать",
    "рад вас видеть",
    "добро пожаловать в чат",
    # Ваши новые паттерны
    "хей",
    "приветики",
    "доброго здоровья",
]
```

### 3. Добавление поддержки других языков

```python
# Английские приветствия
ENGLISH_GREETINGS = [
    "hello", "hi", "good morning", "good afternoon",
    "good evening", "hey", "what's up"
]

# Объединение с основными паттернами
GREETING_PATTERNS.extend(ENGLISH_GREETINGS)
```

### 4. Настройка логирования

**Файл:** `utils/greetings.py`

```python
import logging

# Настройка уровня логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Для детального логирования

# Или отключить логирование
logger.setLevel(logging.WARNING)
```

---

## 🔄 Восстановление функциональности

### Полное восстановление пошагово:

#### 1. Создание файла конфигурации

**Создать файл:** `utils/greetings_config.py`

```python
"""Конфигурация для модуля обработки приветствий."""

# Стандартный ответ на приветствие
STANDARD_GREETING_RESPONSE = (
    "Здравствуйте! Благодарим за ваше обращение. "
    "Напишите свои вопрос. Например: Какие преимущества АПАРУ ?"
)

# Список паттернов приветствий
GREETING_PATTERNS = [
    # Формальные приветствия
    "здравствуйте",
    "здравия желаю",
    "добрый день",
    "доброе утро",
    "добрый вечер",
    "доброго времени суток",
    "приветствую вас",
    "приветствую",
    # Неформальные приветствия
    "привет",
    "приветик",
    "хай",
    "хелло",
    "хей",
    "здрасьте",
    "здарова",
    "добреньки",
    # Вопросы-приветствия
    "как дела",
    "как поживаете",
    "все хорошо",
    "как настроение",
    "как жизнь",
    # Благодарности
    "спасибо за помощь",
    "благодарю",
    "спасибо большое",
    "спасибо",
]

# Дополнительные паттерны для частичного совпадения
PARTIAL_GREETING_PATTERNS = [
    "добро пожаловать",
    "рад вас видеть",
    "добро пожаловать в службу поддержки",
]
```

#### 2. Создание основного модуля

**Создать файл:** `utils/greetings.py`

```python
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
            remaining = normalized_message[len(greeting_pattern):].strip()
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
    logger.info(f"Обработано приветствие с вопросом: '{greeting_pattern}' + '{main_content}'")
    return True, None, main_content
```

#### 3. Интеграция в API

**В файле:** `routers/ask.py`

**Добавить импорт:**

```python
from utils.greetings import process_greeting_message
```

**Модифицировать функцию `ask_question`:**

```python
@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest) -> AskResponse:
    try:
        # Обрабатываем приветствие
        is_greeting_flag, greeting_response, main_content = process_greeting_message(
            request.query
        )

        # Если это только приветствие - возвращаем стандартный ответ
        if is_greeting_flag and greeting_response:
            logger.info(f"Обработано приветствие: {request.query[:50]}...")
            return AskResponse(
                reply=greeting_response,
                confidence=1.0,
                source="greeting",
                similar_questions=[],
            )

        # Определяем текст для поиска в FAQ
        search_query = main_content if main_content else request.query

        # Остальная логика поиска в FAQ...
        if not search_engine._is_initialized:
            await search_engine.initialize()

        result = await search_engine.find_best_answer(search_query)

        return AskResponse(
            reply=result["reply"],
            confidence=result["confidence"],
            source=result.get("source"),
            similar_questions=result.get("similar_questions", []),
        )

    except Exception as e:
        logger.error(f"Ошибка обработки запроса: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
```

#### 4. Проверка работоспособности

**Перезапустить сервер:**

```bash
cd "/Users/abaibaurzhan/Desktop/ML Generation"
pkill -f uvicorn
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 &
```

**Тестирование:**

```bash
curl -s "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Здравствуйте"}' | jq .
```

---

## 🚨 Troubleshooting

### Проблема 1: Приветствия не распознаются

**Симптомы:**

- Сообщения "Здравствуйте" обрабатываются как обычные вопросы
- Возвращается поиск по FAQ вместо стандартного ответа

**Решения:**

1. Проверить импорт в `routers/ask.py`:

   ```python
   from utils.greetings import process_greeting_message
   ```

2. Проверить вызов функции:

   ```python
   is_greeting_flag, greeting_response, main_content = process_greeting_message(request.query)
   ```

3. Проверить логику обработки:
   ```python
   if is_greeting_flag and greeting_response:
       return AskResponse(...)
   ```

### Проблема 2: Неправильное извлечение вопросов

**Симптомы:**

- Приветствие + вопрос не извлекается корректно
- Возвращается полное сообщение вместо только вопроса

**Решения:**

1. Проверить функцию `extract_main_content`
2. Добавить логирование для отладки:
   ```python
   logger.debug(f"Исходное сообщение: {message}")
   logger.debug(f"Извлеченное содержание: {main_content}")
   ```

### Проблема 3: Новые паттерны не работают

**Симптомы:**

- Добавленные приветствия не распознаются
- Система не реагирует на новые паттерны

**Решения:**

1. Проверить синтаксис в `greetings_config.py`
2. Убедиться, что паттерны в нижнем регистре
3. Перезапустить сервер после изменений

### Проблема 4: Ошибки импорта

**Симптомы:**

```
ImportError: cannot import name 'process_greeting_message'
```

**Решения:**

1. Проверить существование файлов:

   ```bash
   ls -la utils/greetings.py
   ls -la utils/greetings_config.py
   ```

2. Проверить синтаксис Python:

   ```bash
   python -m py_compile utils/greetings.py
   python -m py_compile utils/greetings_config.py
   ```

3. Проверить `__init__.py` в папке `utils/`:
   ```python
   # utils/__init__.py должен быть пустым или содержать нужные импорты
   ```

### Проблема 5: Низкая производительность

**Симптомы:**

- Медленная обработка приветствий
- Задержки в ответах

**Решения:**

1. Оптимизировать список паттернов (убрать неиспользуемые)
2. Добавить кэширование для часто используемых приветствий
3. Уменьшить количество проверок в `is_greeting`

---

## 📊 Мониторинг и логирование

### Настройка логирования:

```python
import logging

# В main.py или в настройках
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Специальное логирование для приветствий
greeting_logger = logging.getLogger('greetings')
greeting_logger.setLevel(logging.DEBUG)
```

### Метрики для мониторинга:

1. **Количество приветствий** - сколько раз сработала функция
2. **Типы приветствий** - какие паттерны используются чаще
3. **Извлечение вопросов** - сколько раз извлекались вопросы
4. **Время обработки** - производительность функции

### Пример логирования:

```python
def process_greeting_message(message: str) -> Tuple[bool, Optional[str], Optional[str]]:
    start_time = time.time()

    is_greeting_flag, greeting_pattern = is_greeting(message)

    if is_greeting_flag:
        logger.info(f"Приветствие обнаружено: {greeting_pattern}")
        # Дополнительная логика...

    processing_time = time.time() - start_time
    logger.debug(f"Время обработки приветствия: {processing_time:.3f}s")

    return result
```

---

## 🎯 Заключение

Функциональность приветствий обеспечивает:

- ✅ **Автоматическое распознавание** различных типов приветствий
- ✅ **Стандартизированные ответы** для улучшения пользовательского опыта
- ✅ **Извлечение вопросов** из приветственных сообщений
- ✅ **Гибкую настройку** паттернов и ответов
- ✅ **Полную интеграцию** с существующей системой FAQ

Данная документация позволяет полностью восстановить и настроить функциональность приветствий в системе FAQ-ассистента.
