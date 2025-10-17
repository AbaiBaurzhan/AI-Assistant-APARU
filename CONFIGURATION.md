# Конфигурация системы

## 🔧 Основные настройки

### Переменные окружения

```bash
# Основные настройки
FASTAPI_ENV=production
LOG_LEVEL=INFO

# Настройки поисковой системы
EMBEDDING_MODEL=BAAI/bge-m3
FAISS_INDEX_PATH=data/faiss.index
KNOWLEDGE_BASE_PATH=data/kb.jsonl

# Настройки сервера
HOST=0.0.0.0
PORT=8000
```

## 🤖 Настройки обработки приветствий

### Конфигурация в `utils/greetings_config.py`

```python
# Fallback приветствие для случаев с низкой уверенностью
FALLBACK_GREETING_RESPONSE = (
    "Здравствуйте! Благодарим за ваше обращение. "
    "Напишите свои вопрос. Например: Какие преимущества АПАРУ ?"
)

# Порог confidence для fallback приветствия
FALLBACK_CONFIDENCE_THRESHOLD = 0.6

# Стандартный ответ на приветствие
STANDARD_GREETING_RESPONSE = (
    "Здравствуйте! Благодарим за ваше обращение. "
    "Напишите свои вопрос. Например: Какие преимущества АПАРУ ?"
)
```

### Настройка паттернов приветствий

```python
# Список паттернов приветствий
GREETING_PATTERNS = [
    # Формальные приветствия (правильные)
    "здравствуйте",
    "добрый день",
    "доброе утро",
    "добрый вечер",

    # Формальные приветствия с опечатками
    "здраствуйте",  # пропуск "в"
    "добрый ден",   # пропуск мягкого знака

    # Неформальные приветствия
    "привет",
    "хай",
    "хелло",

    # Неформальные приветствия с опечатками
    "приветт",      # удвоение "т"
]
```

## 🔍 Настройки Fuzzy Matching

### Конфигурация в `utils/fuzzy_config.py`

```python
# Пороги сходства для разных типов приветствий
FORMAL_GREETING_THRESHOLD = 90    # "здравствуйте", "добрый день"
INFORMAL_GREETING_THRESHOLD = 85  # "привет", "хай"
SHORT_GREETING_THRESHOLD = 80     # "привет", "хай"
QUESTION_GREETING_THRESHOLD = 85  # "как дела", "как поживаете"
THANKS_GREETING_THRESHOLD = 85    # "спасибо", "благодарю"

# Максимальная длина текста для fuzzy сравнения
MAX_FUZZY_LENGTH = 50

# Настройки для rapidfuzz
FUZZY_SCORER = "ratio"  # "ratio", "partial_ratio", "token_sort_ratio", "token_set_ratio"

# Кэширование результатов fuzzy matching
ENABLE_FUZZY_CACHE = True
FUZZY_CACHE_SIZE = 1000

# Логирование fuzzy matching
LOG_FUZZY_MATCHES = True
LOG_FUZZY_THRESHOLD = 70  # Логировать только если сходство >= этого порога
```

## 📊 Настройки поисковой системы

### Пороги уверенности

```python
# В utils/search.py
HIGH_CONFIDENCE_THRESHOLD = 0.8   # Высокая уверенность
MEDIUM_CONFIDENCE_THRESHOLD = 0.6 # Средняя уверенность
LOW_CONFIDENCE_THRESHOLD = 0.4    # Низкая уверенность
```

### Логика ответов

- **confidence ≥ 0.8**: Возвращается точный ответ
- **0.6 ≤ confidence < 0.8**: Возвращается уточнение с похожими вопросами
- **confidence < 0.6**: Возвращается fallback приветствие

## 🎯 Настройка производительности

### Кэширование

```python
# В utils/fuzzy_greetings.py
ENABLE_FUZZY_CACHE = True
FUZZY_CACHE_SIZE = 1000

# В utils/search.py
ENABLE_SEARCH_CACHE = True
SEARCH_CACHE_SIZE = 500
```

### Оптимизация

```python
# Максимальная длина для обработки
MAX_QUERY_LENGTH = 500
MAX_RESPONSE_LENGTH = 2000

# Таймауты
SEARCH_TIMEOUT = 5.0  # секунд
EMBEDDING_TIMEOUT = 10.0  # секунд
```

## 📝 Логирование

### Уровни логирования

```python
# В main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Файлы логов

- `logs/app.log` - Основные логи приложения
- `data/feedback.log` - Логи обратной связи
- `logs/greetings.log` - Логи обработки приветствий
- `logs/fuzzy.log` - Логи fuzzy matching

## 🔄 Обновление конфигурации

### Без перезапуска сервера

```python
# Динамическое обновление порогов
from utils.greetings_config import FALLBACK_CONFIDENCE_THRESHOLD
FALLBACK_CONFIDENCE_THRESHOLD = 0.7  # Новый порог
```

### С перезапуском сервера

```bash
# Перезапуск для применения изменений
pkill -f uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 &
```

## 🧪 Тестирование конфигурации

### Проверка настроек

```bash
# Проверка health endpoint
curl http://localhost:8000/api/v1/health

# Тестирование приветствий
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "здравствуйте"}'

# Тестирование fuzzy matching
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "добрй ден"}'
```

### Мониторинг

```bash
# Просмотр логов
tail -f logs/app.log

# Мониторинг производительности
htop
```
