# ИИ Ассистент АПАРУ

Интеллектуальная система поиска ответов из базы знаний для автоматизации чата техподдержки на основе векторного семантического поиска.

## Быстрый старт

### 1. Установка через Python

```bash
# Клонируем репозиторий
git clone <repository-url>
cd faq-assistant

# Создаем виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Устанавливаем зависимости
pip install -r requirements.txt

# Запускаем сервер
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Установка через Docker

```bash
# Сборка образа
docker build -t faq-assistant .

# Запуск контейнера
docker run -p 8000:8000 faq-assistant

# Или через docker-compose
docker-compose up -d
```

## API Endpoints

### Основные эндпоинты

- `POST /api/v1/ask` — Поиск ответов в FAQ
- `POST /api/v1/feedback` — Сбор обратной связи пользователей
- `GET /api/v1/health` — Проверка состояния сервиса
- `GET /docs` — Swagger документация

## Конфигурация

### Переменные окружения

```bash
# Порт сервера (по умолчанию: 8000)
PORT=8000

# Модель эмбеддингов (по умолчанию: BAAI/bge-m3)
MODEL_NAME=BAAI/bge-m3

# Путь к базе знаний
DATA_DIR=./data
```

## Мониторинг

### Проверка состояния

```bash
curl http://localhost:8000/api/v1/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

## Структура проекта

```
faq-assistant/
├── main.py                 # FastAPI сервер
├── requirements.txt        # Python зависимости
├── Dockerfile             # Docker конфигурация
├── docker-compose.yml     # Docker Compose
├── README.md              # Документация
├── data/                  # База знаний
│   ├── faq.xlsx          # Исходные данные
│   ├── faiss.index       # Векторный индекс
│   └── kb.jsonl          # База в JSON
├── utils/                 # Утилиты
│   ├── search.py         # Логика поиска
│   └── excel_converter.py # Конвертер данных
├── routers/               # API маршруты
│   └── ask.py            # Эндпоинты FAQ
├── schemas/               # Pydantic модели
│   └── ask.py            # Схемы данных
└── tests/                 # Тесты
```

## Обновление базы знаний

### Добавление новых FAQ

1. **Обновите Excel файл** `data/faq.xlsx`
2. **Пересоберите индекс:**
   ```bash
   python build_index.py
   ```
3. **Перезапустите сервер**

### Структура Excel файла

| question | answer | id |
|----------|--------|-----|
| Как заказать такси? | Откройте приложение... | q001 |
| Сколько стоит поездка? | Тариф зависит от... | q002 |

## Устранение неполадок

### Частые проблемы

**1. Ошибка "Address already in use"**
```bash
# Найдите процесс на порту 8000
lsof -i :8000

# Остановите процесс
kill -9 <PID>
```

**2. Модель не загружается**
```bash
# Проверьте подключение к интернету
# Модель загружается при первом запуске (~500MB)
```

**3. База знаний не найдена**
```bash
# Убедитесь, что файлы в data/ присутствуют
ls -la data/
```

## Производительность

### Характеристики

- **Время ответа:** < 3 секунд
- **Память:** ~2GB (с моделью)
- **CPU:** 1-2 ядра
- **Диск:** ~1GB (модель + данные)

### Масштабирование

- **Горизонтальное:** несколько инстансов за load balancer
- **Вертикальное:** увеличение RAM для больших баз

## Безопасность

### Рекомендации

- Используйте HTTPS в продакшене
- Настройте rate limiting
- Ограничьте доступ по IP
- Регулярно обновляйте зависимости

## Поддержка

- **Документация API:** http://localhost:8000/docs
- **Issues:** GitHub Issues
- **Email:** support@example.com

## Лицензия

MIT License
