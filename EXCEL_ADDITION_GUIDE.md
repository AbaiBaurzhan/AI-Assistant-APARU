# Процесс добавления Excel файла в систему FAQ Assistant

## 📥 Способы добавления Excel файла

### 1. 🖱️ Простое добавление (замена существующего)

#### Шаги:

1. **Подготовьте Excel файл** с правильной структурой
2. **Скопируйте файл** в директорию `data/`
3. **Переименуйте** в `faq.xlsx`
4. **Запустите обработку**

```bash
# 1. Скопировать файл
cp your_new_faq.xlsx data/faq.xlsx

# 2. Запустить обработку
python build_index.py
```

### 2. 🔄 Добавление к существующим данным (слияние)

#### Подготовка файлов:

```bash
# Создаем директорию для новых файлов
mkdir -p incoming

# Копируем новые Excel файлы
cp new_questions.xlsx incoming/
cp additional_faq.xlsx incoming/
```

#### Процесс слияния:

```python
# Скрипт для слияния Excel файлов
import pandas as pd
from pathlib import Path

def merge_excel_files():
    # Читаем существующий файл
    existing_df = pd.read_excel('data/faq.xlsx')

    # Читаем новые файлы
    new_files = list(Path('incoming').glob('*.xlsx'))

    all_dataframes = [existing_df]

    for file in new_files:
        df = pd.read_excel(file)
        all_dataframes.append(df)

    # Объединяем все данные
    merged_df = pd.concat(all_dataframes, ignore_index=True)

    # Удаляем дубликаты
    merged_df = merged_df.drop_duplicates(subset=['question'])

    # Сохраняем объединенный файл
    merged_df.to_excel('data/faq_merged.xlsx', index=False)

    return merged_df
```

## 🔍 Требования к Excel файлу

### Обязательная структура:

```excel
| question                    | answer                        |
|----------------------------|-------------------------------|
| Как заказать такси?        | Откройте приложение и нажмите |
| Сколько стоит поездка?     | Тариф зависит от расстояния   |
| Как отменить заказ?        | Заказ можно отменить в приложении |
```

### Дополнительные требования:

- **Формат**: `.xlsx` или `.xls`
- **Кодировка**: UTF-8
- **Колонки**: `question` (обязательно), `answer` (обязательно)
- **Размер**: до 10MB (рекомендуется)
- **Количество строк**: до 10,000 (рекомендуется)

### Пример правильного файла:

```python
# Проверка структуры файла
import pandas as pd

def validate_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)

        # Проверяем обязательные колонки
        required_columns = ['question', 'answer']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"❌ Отсутствуют колонки: {missing_columns}")
            return False

        # Проверяем наличие данных
        if len(df) == 0:
            print("❌ Файл пустой")
            return False

        # Проверяем пустые значения
        empty_questions = df['question'].isna().sum()
        empty_answers = df['answer'].isna().sum()

        if empty_questions > 0 or empty_answers > 0:
            print(f"⚠️ Найдены пустые значения: вопросов={empty_questions}, ответов={empty_answers}")

        print(f"✅ Файл валиден: {len(df)} записей")
        return True

    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return False
```

## 🔄 Процесс обработки Excel файла

### Этап 1: Валидация файла

```python
def read_excel_file(self, file_path: str) -> pd.DataFrame:
    # 1. Проверка существования файла
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    # 2. Чтение Excel файла
    df = pd.read_excel(file_path)
    logger.info(f"Прочитан файл {file_path}, строк: {len(df)}")

    # 3. Проверка обязательных колонок
    required_columns = ["question", "answer"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Файл должен содержать колонки: {required_columns}")

    # 4. Удаление пустых строк
    initial_count = len(df)
    df = df.dropna(subset=required_columns)
    final_count = len(df)

    if initial_count != final_count:
        logger.warning(f"Удалено {initial_count - final_count} пустых строк")

    # 5. Удаление дубликатов
    initial_count = len(df)
    df = df.drop_duplicates(subset=["question"])
    final_count = len(df)

    if initial_count != final_count:
        logger.warning(f"Удалено {initial_count - final_count} дубликатов")

    return df
```

### Этап 2: Нормализация данных

```python
def normalize_text(self, text: str) -> str:
    if not isinstance(text, str):
        return ""

    # Базовая нормализация
    text = text.strip().lower()

    # Удаляем лишние пробелы
    text = " ".join(text.split())

    return text
```

### Этап 3: Генерация эмбеддингов

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

    logger.info(f"Сгенерированы эмбеддинги для {len(texts)} текстов")
    return embeddings
```

### Этап 4: Построение FAISS индекса

```python
def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
    # 1. Создание индекса для косинусного сходства
    index = faiss.IndexFlatIP(embeddings.shape[1])

    # 2. Нормализация эмбеддингов
    faiss.normalize_L2(embeddings)

    # 3. Добавление эмбеддингов в индекс
    index.add(embeddings.astype("float32"))

    logger.info(f"Построен FAISS индекс с {index.ntotal} векторами")
    return index
```

### Этап 5: Сохранение результатов

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

    logger.info(f"База знаний сохранена в {output_file}")
```

## 🚀 Команды для добавления и обработки

### Простое добавление:

```bash
# 1. Остановить сервер (если запущен)
pkill -f uvicorn

# 2. Заменить Excel файл
cp new_faq.xlsx data/faq.xlsx

# 3. Перестроить индекс
python build_index.py

# 4. Запустить сервер
uvicorn main:app --host 0.0.0.0 --port 8000 &
```

### Слияние файлов:

```bash
# 1. Создать скрипт слияния
cat > merge_excel.py << 'EOF'
import pandas as pd
from pathlib import Path

def merge_excel_files():
    # Читаем существующий файл
    existing_df = pd.read_excel('data/faq.xlsx')

    # Читаем новые файлы
    new_files = list(Path('incoming').glob('*.xlsx'))

    all_dataframes = [existing_df]

    for file in new_files:
        df = pd.read_excel(file)
        all_dataframes.append(df)

    # Объединяем все данные
    merged_df = pd.concat(all_dataframes, ignore_index=True)

    # Удаляем дубликаты
    merged_df = merged_df.drop_duplicates(subset=['question'])

    # Сохраняем объединенный файл
    merged_df.to_excel('data/faq_merged.xlsx', index=False)

    print(f"Объединено {len(merged_df)} записей")
    return merged_df

if __name__ == "__main__":
    merge_excel_files()
EOF

# 2. Запустить слияние
python merge_excel.py

# 3. Заменить основной файл
cp data/faq_merged.xlsx data/faq.xlsx

# 4. Перестроить индекс
python build_index.py
```

### Автоматизированный процесс:

```bash
#!/bin/bash
# add_excel.sh - Скрипт для добавления Excel файла

set -e

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Добавление Excel файла в систему FAQ${NC}"

# Проверяем аргументы
if [ $# -eq 0 ]; then
    echo -e "${RED}Использование: $0 <путь_к_excel_файлу>${NC}"
    exit 1
fi

EXCEL_FILE=$1

# Проверяем существование файла
if [ ! -f "$EXCEL_FILE" ]; then
    echo -e "${RED}Файл не найден: $EXCEL_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}1. Останавливаем сервер...${NC}"
pkill -f uvicorn || true

echo -e "${YELLOW}2. Создаем бэкап текущего файла...${NC}"
if [ -f "data/faq.xlsx" ]; then
    cp data/faq.xlsx "data/faq_backup_$(date +%Y%m%d_%H%M%S).xlsx"
fi

echo -e "${YELLOW}3. Копируем новый файл...${NC}"
cp "$EXCEL_FILE" data/faq.xlsx

echo -e "${YELLOW}4. Валидируем файл...${NC}"
python3 -c "
import pandas as pd
try:
    df = pd.read_excel('data/faq.xlsx')
    required_columns = ['question', 'answer']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print(f'❌ Отсутствуют колонки: {missing_columns}')
        exit(1)

    print(f'✅ Файл валиден: {len(df)} записей')
except Exception as e:
    print(f'❌ Ошибка валидации: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}Валидация не прошла!${NC}"
    exit 1
fi

echo -e "${YELLOW}5. Перестраиваем индекс...${NC}"
python build_index.py

if [ $? -ne 0 ]; then
    echo -e "${RED}Ошибка построения индекса!${NC}"
    exit 1
fi

echo -e "${YELLOW}6. Запускаем сервер...${NC}"
uvicorn main:app --host 0.0.0.0 --port 8000 &

echo -e "${GREEN}✅ Excel файл успешно добавлен и обработан!${NC}"
echo -e "${GREEN}Сервер запущен на http://localhost:8000${NC}"
```

## 📊 Мониторинг процесса обработки

### Логи обработки:

```python
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Примеры логов при обработке
INFO - Прочитан файл data/faq.xlsx, строк: 200
INFO - Удалено 5 пустых строк
INFO - Удалено 3 дубликатов
INFO - Готово к обработке 192 записей
INFO - Загружаем модель BAAI/bge-m3...
INFO - Модель успешно загружена
INFO - Сгенерированы эмбеддинги для 192 текстов
INFO - Построен FAISS индекс с 192 векторами
INFO - FAISS индекс сохранен в data/faiss.index
INFO - База знаний сохранена в data/kb.jsonl
```

### Проверка результатов:

```bash
# Проверка количества записей
python3 -c "
import pandas as pd
import json
import faiss

# Excel файл
df = pd.read_excel('data/faq.xlsx')
print(f'Excel записей: {len(df)}')

# JSONL файл
with open('data/kb.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(f'JSONL записей: {len(lines)}')

# FAISS индекс
index = faiss.read_index('data/faiss.index')
print(f'FAISS векторов: {index.ntotal}')
"
```

## 🚨 Обработка ошибок

### Частые ошибки и решения:

#### 1. Файл не найден

```python
FileNotFoundError: Файл не найден: data/faq.xlsx
```

**Решение**: Убедитесь, что файл существует в директории `data/`

#### 2. Неправильная структура

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

#### 5. Недостаточно памяти

```python
MemoryError: Недостаточно памяти
```

**Решение**: Уменьшите размер файла или увеличьте память

## 🎯 Лучшие практики

### Подготовка данных:

1. **Проверьте качество** вопросов и ответов
2. **Удалите дубликаты** перед добавлением
3. **Нормализуйте текст** (уберите лишние пробелы)
4. **Проверьте кодировку** (UTF-8)

### Процесс добавления:

1. **Создайте бэкап** существующих данных
2. **Валидируйте файл** перед обработкой
3. **Мониторьте логи** во время обработки
4. **Проверьте результаты** после обработки

### Оптимизация:

1. **Используйте пакетную обработку** для больших файлов
2. **Мониторьте использование памяти**
3. **Создавайте инкрементальные обновления**
4. **Тестируйте на небольшом наборе данных**

## 🚀 Заключение

Процесс добавления Excel файла включает:

1. **📥 Подготовку** файла с правильной структурой
2. **🔍 Валидацию** данных и формата
3. **🔄 Обработку** через конвертер
4. **🤖 Генерацию** эмбеддингов
5. **🗂️ Построение** FAISS индекса
6. **💾 Сохранение** результатов
7. **🚀 Запуск** обновленной системы

**Система готова к добавлению новых данных и автоматической обработке!** 🎉
