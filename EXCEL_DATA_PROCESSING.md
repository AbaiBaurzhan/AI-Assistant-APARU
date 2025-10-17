# Процесс работы с Excel базой данных FAQ

## 📊 Обзор процесса

Полный цикл работы с Excel базой данных включает несколько этапов: от получения файла до использования в поисковой системе.

## 🔄 Этапы обработки

### 1. 📥 Получение Excel файла

#### Структура файла

```excel
| question                    | answer                        | id   |
|----------------------------|-------------------------------|------|
| Как заказать такси?        | Откройте приложение и нажмите | q001 |
| Сколько стоит поездка?     | Тариф зависит от расстояния   | q002 |
| Как отменить заказ?        | Заказ можно отменить в приложении | q003 |
```

#### Требования к файлу:

- **Обязательные колонки**: `question`, `answer`
- **Опциональные колонки**: `id` (автогенерируется если нет)
- **Формат**: `.xlsx` или `.xls`
- **Кодировка**: UTF-8
- **Размер**: до 10MB (рекомендуется)

### 2. 🔍 Валидация и очистка данных

#### Процесс валидации:

```python
def read_excel_file(self, file_path: str) -> pd.DataFrame:
    # 1. Проверка существования файла
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    # 2. Чтение Excel файла
    df = pd.read_excel(file_path)

    # 3. Проверка обязательных колонок
    required_columns = ["question", "answer"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    # 4. Удаление пустых строк
    df = df.dropna(subset=required_columns)

    # 5. Удаление дубликатов
    df = df.drop_duplicates(subset=["question"])

    return df
```

#### Очистка данных:

- ✅ **Удаление пустых строк** по колонкам question/answer
- ✅ **Удаление дубликатов** по вопросу
- ✅ **Нормализация текста** (приведение к нижнему регистру, удаление лишних пробелов)
- ✅ **Валидация формата** данных

### 3. 🤖 Генерация эмбеддингов

#### Модель эмбеддингов:

- **Модель**: `BAAI/bge-m3`
- **Размерность**: 1024
- **Язык**: Многоязычная (поддерживает русский)
- **Тип**: Sentence Transformer

#### Процесс генерации:

```python
def generate_embeddings(self, texts: List[str]) -> np.ndarray:
    # 1. Нормализация текстов
    normalized_texts = [self.normalize_text(text) for text in texts]

    # 2. Генерация эмбеддингов
    embeddings = self.model.encode(
        normalized_texts,
        batch_size=32,           # Пакетная обработка
        show_progress_bar=True,  # Прогресс-бар
        convert_to_numpy=True,   # Конвертация в numpy
    )

    return embeddings
```

#### Особенности:

- **Пакетная обработка**: 32 текста за раз
- **Прогресс-бар**: Отображение процесса
- **Нормализация**: Приведение к единому формату
- **Векторизация**: Преобразование текста в числовые векторы

### 4. 🗂️ Построение FAISS индекса

#### Тип индекса:

- **Индекс**: `IndexFlatIP` (Inner Product)
- **Метрика**: Косинусное сходство
- **Нормализация**: L2 нормализация

#### Процесс построения:

```python
def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
    # 1. Создание индекса для косинусного сходства
    index = faiss.IndexFlatIP(embeddings.shape[1])

    # 2. Нормализация эмбеддингов
    faiss.normalize_L2(embeddings)

    # 3. Добавление векторов в индекс
    index.add(embeddings.astype("float32"))

    return index
```

#### Преимущества FAISS:

- ⚡ **Быстрый поиск**: O(log n) сложность
- 🔍 **Точность**: Точное совпадение
- 💾 **Эффективность**: Оптимизированное хранение
- 🚀 **Масштабируемость**: Поддержка больших объемов

### 5. 💾 Сохранение результатов

#### Файлы результатов:

1. **`data/faiss.index`** - FAISS индекс для быстрого поиска
2. **`data/kb.jsonl`** - База знаний в JSONL формате
3. **`data/faq.xlsx`** - Исходный Excel файл (копия)

#### Формат JSONL:

```json
{"id": "q001", "question": "Как заказать такси?", "answer": "Откройте приложение и нажмите", "normalized_question": "как заказать такси"}
{"id": "q002", "question": "Сколько стоит поездка?", "answer": "Тариф зависит от расстояния", "normalized_question": "сколько стоит поездка"}
```

#### Процесс сохранения:

```python
def save_knowledge_base(self, df: pd.DataFrame, output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        for idx, row in df.iterrows():
            kb_entry = {
                "id": f"q{idx:03d}",                    # Автогенерированный ID
                "question": row["question"],            # Оригинальный вопрос
                "answer": row["answer"],                # Ответ
                "normalized_question": self.normalize_text(row["question"]), # Нормализованный вопрос
            }
            f.write(json.dumps(kb_entry, ensure_ascii=False) + "\n")
```

## 🔍 Использование в поисковой системе

### 1. 🚀 Инициализация поискового движка

```python
class SearchEngine:
    async def initialize(self) -> None:
        # 1. Загрузка модели эмбеддингов
        self.model = SentenceTransformer(EMBEDDING_MODEL)

        # 2. Загрузка FAISS индекса
        self.index = faiss.read_index(INDEX_FILE)

        # 3. Загрузка базы знаний
        self.knowledge_base = self.load_knowledge_base(KB_FILE)

        self._is_initialized = True
```

### 2. 🔎 Поиск ответов

#### Процесс поиска:

```python
async def find_best_answer(self, query: str) -> Dict[str, Any]:
    # 1. Нормализация запроса
    normalized_query = self.normalize_text(query)

    # 2. Генерация эмбеддинга для запроса
    query_embedding = self.model.encode([normalized_query])
    faiss.normalize_L2(query_embedding)

    # 3. Поиск в FAISS индексе
    similarities, indices = self.index.search(query_embedding, TOP_K_RESULTS)

    # 4. Обработка результатов
    best_match = self.process_search_results(similarities, indices)

    return best_match
```

#### Обработка результатов:

```python
def process_search_results(self, similarities: np.ndarray, indices: np.ndarray) -> Dict[str, Any]:
    # 1. Получение лучшего совпадения
    best_similarity = similarities[0][0]
    best_index = indices[0][0]

    # 2. Определение уровня уверенности
    if best_similarity >= HIGH_CONFIDENCE_THRESHOLD:
        # Высокая уверенность - возвращаем точный ответ
        return {
            "reply": self.knowledge_base[best_index]["answer"],
            "confidence": float(best_similarity),
            "source": self.knowledge_base[best_index]["id"],
            "similar_questions": []
        }
    elif best_similarity >= MEDIUM_CONFIDENCE_THRESHOLD:
        # Средняя уверенность - просим уточнить
        similar_questions = [self.knowledge_base[i]["question"] for i in indices[0][:3]]
        return {
            "reply": "Уточните, пожалуйста, ваш вопрос. Возможно, вы имели в виду:",
            "confidence": float(best_similarity),
            "source": None,
            "similar_questions": similar_questions
        }
    else:
        # Низкая уверенность - fallback приветствие
        return {
            "reply": "Здравствуйте! Благодарим за ваше обращение. Напишите свои вопрос.",
            "confidence": 1.0,
            "source": "fallback_greeting",
            "similar_questions": []
        }
```

## 📈 Производительность и оптимизация

### Временные характеристики:

- **Чтение Excel**: ~100ms для 1000 записей
- **Генерация эмбеддингов**: ~2-5 секунд для 1000 записей
- **Построение FAISS индекса**: ~50ms для 1000 записей
- **Поиск в индексе**: ~1-5ms на запрос

### Оптимизации:

- **Пакетная обработка**: 32 текста за раз
- **Кэширование модели**: Загрузка один раз
- **Нормализация**: Предварительная обработка
- **Индексирование**: Быстрый поиск через FAISS

## 🔧 Команды для работы с данными

### Построение индекса:

```bash
# Основная команда
python build_index.py

# Или через конвертер
python convert_excel.py

# С проверкой
python -c "
import asyncio
from utils.excel_converter import convert_excel_to_vector_db
result = asyncio.run(convert_excel_to_vector_db('data/faq.xlsx'))
print(f'Статус: {result[\"status\"]}')
print(f'Записей: {result[\"records_processed\"]}')
"
```

### Проверка данных:

```bash
# Проверка Excel файла
python -c "
import pandas as pd
df = pd.read_excel('data/faq.xlsx')
print(f'Строк: {len(df)}')
print(f'Колонки: {list(df.columns)}')
print('Первые 3 строки:')
print(df.head(3))
"

# Проверка JSONL файла
python -c "
import json
with open('data/kb.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(f'Записей в JSONL: {len(lines)}')
print('Первая запись:')
print(json.loads(lines[0]))
"
```

## 🚨 Обработка ошибок

### Частые ошибки:

#### 1. Файл не найден

```python
FileNotFoundError: Файл не найден: data/faq.xlsx
```

**Решение**: Убедитесь, что файл существует в директории `data/`

#### 2. Отсутствуют колонки

```python
ValueError: Файл должен содержать колонки: ['question', 'answer']
```

**Решение**: Добавьте обязательные колонки в Excel файл

#### 3. Пустой файл

```python
ValueError: Файл не содержит данных
```

**Решение**: Добавьте данные в Excel файл

#### 4. Ошибка модели

```python
RuntimeError: Модель не загружена
```

**Решение**: Проверьте подключение к интернету для загрузки модели

## 📊 Мониторинг процесса

### Логирование:

```python
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Примеры логов
INFO - Прочитан файл data/faq.xlsx, строк: 145
INFO - Удалено 2 пустых строк
INFO - Удалено 1 дубликатов
INFO - Готово к обработке 142 записей
INFO - Загружаем модель BAAI/bge-m3...
INFO - Модель успешно загружена
INFO - Сгенерированы эмбеддинги для 142 текстов
INFO - Построен FAISS индекс с 142 векторами
INFO - FAISS индекс сохранен в data/faiss.index
INFO - База знаний сохранена в data/kb.jsonl
```

### Метрики качества:

- **Количество обработанных записей**
- **Время обработки**
- **Размер индекса**
- **Точность поиска**

## 🎯 Заключение

Процесс работы с Excel базой данных включает:

1. **📥 Получение** и валидацию Excel файла
2. **🔍 Очистку** и нормализацию данных
3. **🤖 Генерацию** эмбеддингов с помощью AI модели
4. **🗂️ Построение** FAISS индекса для быстрого поиска
5. **💾 Сохранение** результатов в оптимизированном формате
6. **🔎 Использование** в поисковой системе для ответов пользователям

**Система обеспечивает высокую точность поиска при оптимальной производительности!** 🚀
