.PHONY: lint format check test clean

# Линтинг
lint:
	flake8 .
	pylint --rcfile=pyproject.toml main.py tests/

# Форматирование
format:
	black .
	isort .

# Проверка типов
check:
	mypy .

# Полная проверка
all: format lint check

# Запуск тестов
test:
	pytest -v --tb=short

# Проверка безопасности
security:
	bandit -r . -f json -o bandit-report.json
	safety check -r requirements.txt

# Pre-commit проверка
pre-commit:
	pre-commit run --all-files

# Очистка кэша
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "bandit-report.json" -delete

# Установка зависимостей
install:
	pip install -r requirements.txt
	pre-commit install

# Запуск сервера
run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000
