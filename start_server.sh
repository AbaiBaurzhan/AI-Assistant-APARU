#!/bin/bash

# Скрипт для запуска сервера FAQ-ассистента

echo "🚀 Запуск сервера FAQ-ассистента..."

# Переходим в директорию проекта
cd "/Users/abaibaurzhan/Desktop/ML Generation"

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем, что порт 8000 свободен
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Порт 8000 уже занят. Останавливаем процессы..."
    pkill -f uvicorn
    sleep 2
fi

# Запускаем сервер
echo "📡 Запуск сервера на http://localhost:8000"
echo "📚 Документация API: http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/api/v1/health"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo "────────────────────────────────────────────"

uvicorn main:app --host 0.0.0.0 --port 8000
