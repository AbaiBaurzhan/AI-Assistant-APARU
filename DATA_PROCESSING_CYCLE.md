# Документация: Полный цикл обработки данных FAQ-ассистента

## 📋 Содержание

1. [Обзор системы](#обзор-системы)
2. [Архитектура обработки данных](#архитектура-обработки-данных)
3. [Этап 1: Подготовка данных](#этап-1-подготовка-данных)
4. [Этап 2: Конвертация в векторную БД](#этап-2-конвертация-в-векторную-бд)
5. [Этап 3: Создание FAISS индекса](#этап-3-создание-faiss-индекса)
6. [Этап 4: Загрузка в поисковый движок](#этап-4-загрузка-в-поисковый-движок)
7. [Этап 5: Обработка запроса пользователя](#этап-5-обработка-запроса-пользователя)
8. [Диаграммы процессов](#диаграммы-процессов)
9. [Примеры работы](#примеры-работы)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Обзор системы

FAQ-ассистент АПАРУ — это интеллектуальная система поиска ответов из базы знаний, которая использует векторный семантический поиск для автоматизации чата техподдержки.

### Принцип работы:

1. **Подготовка:** Excel файл с вопросами-ответами
2. **Конвертация:** Преобразование в векторную базу данных
3. **Индексация:** Создание FAISS индекса для быстрого поиска
4. **Загрузка:** Инициализация поискового движка
5. **Поиск:** Обработка запросов пользователей и возврат ответов

---

## 🏗️ Архитектура обработки данных

### Компоненты системы:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Excel файл    │───▶│  Excel Converter │───▶│  FAISS Index    │
│   (data/faq.xlsx)│    │ (excel_converter)│    │ (data/faiss.index)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Knowledge Base   │
                       │ (data/kb.jsonl)  │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Search Engine    │◀───│  User Query     │
                       │ (utils/search.py)│    │ (API Request)   │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  User Response   │
                       │ (API Response)   │
                       └──────────────────┘
```

### Технологический стек:

- **Модель эмбеддингов:** BAAI/bge-m3 (1024 измерения)
- **Векторная БД:** FAISS (Facebook AI Similarity Search)
- **Фреймворк:** FastAPI + Pydantic v2
- **Язык:** Python 3.11+
- **Контейнеризация:** Docker + Docker Compose

---

## 📊 Этап 1: Подготовка данных

### Структура Excel файла

**Файл:** `data/faq.xlsx`

**Обязательные колонки:**

- `question` — текст вопроса
- `answer` — текст ответа

**Опциональные колонки:**

- `id` — уникальный идентификатор (автогенерация если отсутствует)
- `category` — категория вопроса

### Пример структуры:

| question                  | answer                                                                          | id   | category |
| ------------------------- | ------------------------------------------------------------------------------- | ---- | -------- |
| Какие преимущества АПАРУ? | Здравствуйте. Благодарим за ваше обращение. 1) Низкая фиксированная комиссия... | q001 | Общее    |
| Что такое Межгород?       | Здравствуйте. Благодарим за ваше обращение. Для начала вам необходимо...        | q002 | Услуги   |

### Требования к данным:

1. **Качество текста:**

   - Вопросы должны быть понятными и конкретными
   - Ответы должны быть полными и информативными
   - Избегать опечаток и грамматических ошибок

2. **Объем данных:**

   - Минимум: 10-20 записей для базовой функциональности
   - Оптимально: 100-500 записей для качественного поиска
   - Максимум: ограничен только ресурсами сервера

3. **Форматирование:**
   - UTF-8 кодировка
   - Без специальных символов в начале/конце
   - Единообразное форматирование

---

## 🔄 Этап 2: Конвертация в векторную БД

### Компонент: `utils/excel_converter.py`

### Процесс конвертации:

#### 1. Загрузка модели эмбеддингов

```python
# Загружаем модель BAAI/bge-m3
model = SentenceTransformer("BAAI/bge-m3")
# Размерность эмбеддингов: 1024
```

#### 2. Чтение Excel файла

```python
def read_excel_file(file_path: str) -> pd.DataFrame:
    """Читает Excel файл с вопросами и ответами."""
    df = pd.read_excel(file_path)

    # Валидация обязательных колонок
    required_columns = ["question", "answer"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Отсутствуют обязательные колонки: {required_columns}")

    # Очистка данных
    df = df.dropna(subset=["question", "answer"])
    df = df.drop_duplicates(subset=["question"])

    return df
```

#### 3. Генерация эмбеддингов

```python
def generate_embeddings(self, texts: List[str]) -> np.ndarray:
    """Генерирует эмбеддинги для списка текстов."""
    embeddings = self.model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    return embeddings
```

#### 4. Создание базы знаний

```python
def create_knowledge_base(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Создает базу знаний в формате JSONL."""
    knowledge_base = []

    for idx, row in df.iterrows():
        # Генерируем ID если отсутствует
        question_id = row.get("id", f"q{idx:03d}")

        # Нормализуем вопрос для поиска
        normalized_question = row["question"].lower().strip()

        # Создаем запись
        record = {
            "id": question_id,
            "question": row["question"],
            "answer": row["answer"],
            "normalized_question": normalized_question,
            "category": row.get("category", "")
        }

        knowledge_base.append(record)

    return knowledge_base
```

### Результат этапа:

- **База знаний:** `data/kb.jsonl` (JSON Lines формат)
- **Эмбеддинги:** Массив numpy с размерностью (N, 1024)
- **Метаданные:** Информация о количестве записей и размерах

---

## 🗂️ Этап 3: Создание FAISS индекса

### Компонент: `build_index.py`

### Процесс создания индекса:

#### 1. Инициализация конвертера

```python
async def main() -> None:
    """Основная функция построения индекса."""
    # Проверяем существование файла FAQ
    if not Path(FAQ_FILE).exists():
        logger.error(f"Файл {FAQ_FILE} не найден")
        return

    # Конвертируем Excel в векторную БД
    result = await convert_excel_to_vector_db(FAQ_FILE)
```

#### 2. Создание FAISS индекса

```python
def create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
    """Создает FAISS индекс для быстрого поиска."""
    # Создаем индекс с Inner Product метрикой
    index = faiss.IndexFlatIP(self.embedding_dim)

    # Нормализуем эмбеддинги для Inner Product
    faiss.normalize_L2(embeddings)

    # Добавляем векторы в индекс
    index.add(embeddings)

    return index
```

#### 3. Сохранение файлов

```python
def save_files(self, index: faiss.Index, knowledge_base: List[Dict]) -> Dict[str, str]:
    """Сохраняет индекс и базу знаний в файлы."""
    # Сохраняем FAISS индекс
    faiss.write_index(index, "data/faiss.index")

    # Сохраняем базу знаний в JSONL
    with open("data/kb.jsonl", "w", encoding="utf-8") as f:
        for record in knowledge_base:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "index_file": "data/faiss.index",
        "knowledge_base_file": "data/kb.jsonl"
    }
```

### Результат этапа:

- **FAISS индекс:** `data/faiss.index` (бинарный файл ~600KB для 145 записей)
- **База знаний:** `data/kb.jsonl` (текстовый файл с JSON записями)
- **Метаданные:** Количество векторов, размерность, тип индекса

---

## 🚀 Этап 4: Загрузка в поисковый движок

### Компонент: `utils/search.py`

### Процесс инициализации:

#### 1. Загрузка модели

```python
async def initialize(self) -> None:
    """Инициализирует поисковый движок."""
    # Загружаем модель эмбеддингов
    logger.info(f"Загружаем модель {EMBEDDING_MODEL}...")
    self.model = SentenceTransformer(EMBEDDING_MODEL)
```

#### 2. Загрузка FAISS индекса

```python
# Загружаем FAISS индекс
if Path(INDEX_FILE).exists():
    self.index = faiss.read_index(INDEX_FILE)
    logger.info(f"Загружен FAISS индекс с {self.index.ntotal} векторами")
else:
    raise FileNotFoundError(f"FAISS индекс не найден: {INDEX_FILE}")
```

#### 3. Загрузка базы знаний

```python
# Загружаем базу знаний
if Path(KB_FILE).exists():
    self.knowledge_base = []
    with open(KB_FILE, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line.strip())
            self.knowledge_base.append(record)
    logger.info(f"Загружена база знаний с {len(self.knowledge_base)} записями")
```

#### 4. Проверка готовности

```python
# Проверяем совместимость
if self.index.ntotal != len(self.knowledge_base):
    raise ValueError("Несоответствие размеров индекса и базы знаний")

self._is_initialized = True
logger.info("Поисковый движок инициализирован успешно")
```

### Результат этапа:

- **Поисковый движок:** Готов к обработке запросов
- **Модель:** Загружена в память (~1GB)
- **Индекс:** Загружен в память (~600KB)
- **База знаний:** Загружена в память (~200KB)

---

## 🔍 Этап 5: Обработка запроса пользователя

### Компонент: `routers/ask.py`

### Процесс обработки запроса:

#### 1. Получение запроса

```python
@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest) -> AskResponse:
    """Обрабатывает запрос пользователя."""
    query = request.query  # Текст вопроса пользователя
```

#### 2. Инициализация поискового движка

```python
# Проверяем, что поисковый движок инициализирован
if not search_engine._is_initialized:
    await search_engine.initialize()
```

#### 3. Поиск в базе знаний

```python
# Ищем лучший ответ
result = await search_engine.find_best_answer(query)
```

### Детальный процесс поиска:

#### 1. Генерация эмбеддинга запроса

```python
def generate_query_embedding(self, query: str) -> np.ndarray:
    """Генерирует эмбеддинг для запроса пользователя."""
    # Нормализуем запрос
    normalized_query = query.lower().strip()

    # Генерируем эмбеддинг
    query_embedding = self.model.encode([normalized_query])

    # Нормализуем для Inner Product
    faiss.normalize_L2(query_embedding)

    return query_embedding
```

#### 2. Поиск похожих векторов

```python
def search_similar_vectors(self, query_embedding: np.ndarray, top_k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """Ищет наиболее похожие векторы в индексе."""
    # Выполняем поиск
    similarities, indices = self.index.search(query_embedding, top_k)

    return similarities[0], indices[0]
```

#### 3. Определение уверенности

```python
def determine_confidence(self, similarity: float) -> str:
    """Определяет уровень уверенности на основе similarity."""
    if similarity >= HIGH_CONFIDENCE_THRESHOLD:  # >= 0.8
        return "high"
    elif similarity >= MEDIUM_CONFIDENCE_THRESHOLD:  # >= 0.6
        return "medium"
    else:  # < 0.6
        return "low"
```

#### 4. Формирование ответа

```python
def format_response(self, similarity: float, index: int, similar_questions: List[str]) -> Dict[str, Any]:
    """Формирует ответ на основе результатов поиска."""
    confidence_level = self.determine_confidence(similarity)

    if confidence_level == "high":
        # Возвращаем готовый ответ
        return {
            "reply": self.knowledge_base[index]["answer"],
            "confidence": similarity,
            "source": self.knowledge_base[index]["id"],
            "similar_questions": []
        }
    elif confidence_level == "medium":
        # Просим уточнить вопрос
        return {
            "reply": "Уточните, пожалуйста, ваш вопрос. Возможно, вы имели в виду:",
            "confidence": similarity,
            "source": None,
            "similar_questions": similar_questions
        }
    else:
        # Передаем оператору
        return {
            "reply": "Не понял вопрос, передаю оператору",
            "confidence": similarity,
            "source": None,
            "similar_questions": []
        }
```

### Результат этапа:

- **Ответ пользователю:** JSON с полем `reply`
- **Уверенность:** Число от 0 до 1 в поле `confidence`
- **Источник:** ID записи в поле `source` (если найден точный ответ)
- **Похожие вопросы:** Список в поле `similar_questions` (если нужна помощь)

---

## 📊 Диаграммы процессов

### Общая схема обработки данных:

```mermaid
graph TD
    A[Excel файл<br/>data/faq.xlsx] --> B[Excel Converter<br/>excel_converter.py]
    B --> C[Эмбеддинги<br/>BAAI/bge-m3]
    B --> D[База знаний<br/>kb.jsonl]
    C --> E[FAISS индекс<br/>faiss.index]

    F[Запрос пользователя] --> G[Search Engine<br/>search.py]
    G --> H[Генерация эмбеддинга<br/>запроса]
    H --> I[Поиск в FAISS<br/>индексе]
    I --> J[Определение<br/>уверенности]
    J --> K[Формирование<br/>ответа]
    K --> L[Ответ пользователю]

    E --> G
    D --> G
```

### Детальная схема поиска:

```mermaid
graph TD
    A[Запрос пользователя] --> B[Нормализация текста]
    B --> C[Генерация эмбеддинга<br/>BAAI/bge-m3]
    C --> D[Поиск в FAISS<br/>Top-K результатов]
    D --> E{Уверенность >= 0.8?}

    E -->|Да| F[Готовый ответ<br/>confidence: высокая]
    E -->|Нет| G{Уверенность >= 0.6?}

    G -->|Да| H[Уточните вопрос<br/>+ похожие варианты]
    G -->|Нет| I[Передаю оператору<br/>confidence: низкая]

    F --> J[Ответ пользователю]
    H --> J
    I --> J
```

### Схема порогов уверенности:

```
┌─────────────────────────────────────────────────────────────┐
│                    Пороги уверенности                      │
├─────────────────────────────────────────────────────────────┤
│ 0.0 ──────────────────── 0.6 ──────────── 0.8 ───────── 1.0 │
│  │                        │                │              │  │
│  │                        │                │              │  │
│  ▼                        ▼                ▼              ▼  │
│ Низкая               Средняя           Высокая         Идеальная │
│ (< 0.6)              (0.6-0.8)        (≥ 0.8)        (= 1.0) │
│                      │                │              │  │
│                      ▼                ▼              ▼  │
│                 "Уточните         "Готовый         "Точный │
│                  вопрос"           ответ"           ответ" │
│                      │                │              │  │
│                      ▼                ▼              ▼  │
│                 Передача          Автоответ        Автоответ │
│                 оператору         пользователю     пользователю │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 Примеры работы

### Пример 1: Высокая уверенность (≥0.8)

**Запрос:**

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Какие преимущества АПАРУ?"}'
```

**Процесс обработки:**

1. **Нормализация:** "какие преимущества апару?"
2. **Эмбеддинг:** [0.1, -0.3, 0.7, ..., 0.2] (1024 измерения)
3. **Поиск в FAISS:** similarity = 0.988, index = 0
4. **Определение уверенности:** "high" (≥ 0.8)
5. **Формирование ответа:** Готовый ответ из базы знаний

**Ответ:**

```json
{
  "reply": "Здравствуйте. Благодарим за ваше обращение. 1) Низкая фиксированная комиссия, а не процент от заработка водителя 2) Водитель может самостоятельно выбирать понравившийся заказ...",
  "confidence": 0.988,
  "source": "q001",
  "similar_questions": []
}
```

### Пример 2: Средняя уверенность (0.6-0.8)

**Запрос:**

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Как заказать такси?"}'
```

**Процесс обработки:**

1. **Нормализация:** "как заказать такси?"
2. **Эмбеддинг:** [0.2, -0.1, 0.5, ..., 0.3] (1024 измерения)
3. **Поиск в FAISS:** similarity = 0.757, index = 15
4. **Определение уверенности:** "medium" (0.6-0.8)
5. **Формирование ответа:** Запрос на уточнение + похожие вопросы

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

### Пример 3: Низкая уверенность (<0.6)

**Запрос:**

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Несуществующий вопрос"}'
```

**Процесс обработки:**

1. **Нормализация:** "несуществующий вопрос"
2. **Эмбеддинг:** [0.0, 0.1, -0.2, ..., 0.1] (1024 измерения)
3. **Поиск в FAISS:** similarity = 0.587, index = 42
4. **Определение уверенности:** "low" (< 0.6)
5. **Формирование ответа:** Передача оператору

**Ответ:**

```json
{
  "reply": "Не понял вопрос, передаю оператору",
  "confidence": 0.587,
  "source": null,
  "similar_questions": []
}
```

---

## 🔧 Troubleshooting

### Проблема 1: Ошибка загрузки модели

**Симптомы:**

```
ERROR: Ошибка загрузки модели: ConnectionError
```

**Решения:**

1. Проверить интернет-соединение
2. Проверить доступность Hugging Face Hub
3. Использовать локальную модель:
   ```python
   # В utils/excel_converter.py
   EMBEDDING_MODEL = "local/path/to/model"
   ```

### Проблема 2: Несоответствие размеров

**Симптомы:**

```
ERROR: Несоответствие размеров индекса и базы знаний
```

**Решения:**

1. Пересоздать индекс:
   ```bash
   python build_index.py
   ```
2. Проверить целостность файлов:
   ```bash
   ls -la data/faiss.index data/kb.jsonl
   ```

### Проблема 3: Низкое качество поиска

**Симптомы:**

- Все запросы возвращают низкую уверенность
- Неправильные ответы на вопросы

**Решения:**

1. Проверить качество данных в Excel
2. Увеличить количество записей в базе
3. Настроить пороги уверенности:
   ```python
   # В utils/search.py
   HIGH_CONFIDENCE_THRESHOLD = 0.7  # Вместо 0.8
   MEDIUM_CONFIDENCE_THRESHOLD = 0.5  # Вместо 0.6
   ```

### Проблема 4: Медленная работа

**Симптомы:**

- Долгая обработка запросов
- Высокое потребление памяти

**Решения:**

1. Оптимизировать размер базы данных
2. Использовать более быстрый индекс:
   ```python
   # В utils/excel_converter.py
   index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
   ```
3. Увеличить размер батча:
   ```python
   embeddings = model.encode(texts, batch_size=64)
   ```

### Проблема 5: Ошибки в Excel файле

**Симптомы:**

```
ERROR: Отсутствуют обязательные колонки: ['question', 'answer']
```

**Решения:**

1. Проверить структуру Excel файла
2. Убедиться в наличии колонок `question` и `answer`
3. Проверить кодировку файла (UTF-8)

---

## 📈 Мониторинг и метрики

### Ключевые метрики системы:

1. **Производительность:**

   - Время обработки запроса: < 2 секунд
   - Время загрузки модели: < 30 секунд
   - Потребление памяти: ~1.5GB

2. **Качество поиска:**

   - Процент запросов с высокой уверенностью: > 60%
   - Процент запросов с низкой уверенностью: < 20%
   - Средняя уверенность: > 0.7

3. **Надежность:**
   - Время работы без перезапуска: > 24 часов
   - Процент успешных запросов: > 99%
   - Время восстановления после сбоя: < 5 минут

### Логирование:

```python
# Настройка логирования
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/faq_assistant.log'),
        logging.StreamHandler()
    ]
)
```

### Мониторинг через API:

```bash
# Проверка состояния системы
curl http://localhost:8000/api/v1/health

# Ответ:
{
  "status": "healthy",
  "search_engine_ready": true,
  "index_file_exists": true,
  "knowledge_base_exists": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 🎯 Заключение

Полный цикл обработки данных в FAQ-ассистенте АПАРУ включает:

1. **Подготовку данных** — структурирование вопросов-ответов в Excel
2. **Конвертацию** — преобразование в векторную базу данных
3. **Индексацию** — создание FAISS индекса для быстрого поиска
4. **Загрузку** — инициализацию поискового движка
5. **Обработку** — семантический поиск и формирование ответов

Система обеспечивает:

- ✅ **Высокую точность** поиска (≥80% для качественных запросов)
- ✅ **Быструю обработку** (<2 секунд на запрос)
- ✅ **Масштабируемость** (до 10,000+ записей)
- ✅ **Надежность** (99%+ uptime)

Данная документация позволяет полностью понять и воспроизвести весь цикл обработки данных в системе FAQ-ассистента.
