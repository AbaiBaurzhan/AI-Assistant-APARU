#!/bin/bash

# Скрипт для запуска консольного приложения

echo "🤖 Запуск консольного приложения FAQ-ассистента..."

# Переходим в директорию проекта
cd "/Users/abaibaurzhan/Desktop/ML Generation"

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем, что сервер запущен
echo "🔍 Проверка сервера..."
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "✅ Сервер доступен"
else
    echo "❌ Сервер недоступен. Запустите сервер: ./start_server.sh"
    echo "   Или в отдельном терминале: cd '/Users/abaibaurzhan/Desktop/ML Generation' && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000"
    exit 1
fi

echo ""
echo "🎯 Консольное приложение готово к работе!"
echo "📖 Введите 'help' для списка команд"
echo "────────────────────────────────────────────"

# Запускаем консольное приложение
python test_console.py
