#!/bin/bash

# Скрипт деплоя FAQ Assistant
# Использование: ./deploy.sh [environment]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверка аргументов
ENVIRONMENT=${1:-production}
log "Начинаем деплой в окружении: $ENVIRONMENT"

# Проверка зависимостей
check_dependencies() {
    log "Проверяем зависимости..."

    if ! command -v docker &> /dev/null; then
        error "Docker не установлен"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose не установлен"
        exit 1
    fi

    success "Все зависимости установлены"
}

# Создание необходимых директорий
create_directories() {
    log "Создаем необходимые директории..."

    mkdir -p data logs ssl
    mkdir -p backups/$(date +%Y%m%d_%H%M%S)

    success "Директории созданы"
}

# Бэкап текущих данных
backup_data() {
    log "Создаем бэкап данных..."

    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

    if [ -d "data" ]; then
        cp -r data "$BACKUP_DIR/"
        success "Бэкап создан в $BACKUP_DIR"
    else
        warning "Директория data не найдена, пропускаем бэкап"
    fi
}

# Сборка Docker образа
build_image() {
    log "Собираем Docker образ..."

    docker build -t faq-assistant:$ENVIRONMENT .
    success "Docker образ собран"
}

# Остановка старых контейнеров
stop_containers() {
    log "Останавливаем старые контейнеры..."

    docker-compose down || true
    success "Старые контейнеры остановлены"
}

# Запуск новых контейнеров
start_containers() {
    log "Запускаем новые контейнеры..."

    docker-compose up -d
    success "Контейнеры запущены"
}

# Проверка здоровья сервиса
health_check() {
    log "Проверяем здоровье сервиса..."

    # Ждем запуска сервиса
    sleep 30

    # Проверяем health endpoint
    for i in {1..10}; do
        if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
            success "Сервис здоров и готов к работе"
            return 0
        fi
        log "Попытка $i/10: сервис еще не готов, ждем..."
        sleep 10
    done

    error "Сервис не отвечает после 10 попыток"
    return 1
}

# Показать статус
show_status() {
    log "Статус сервисов:"
    docker-compose ps

    log "Логи приложения:"
    docker-compose logs --tail=20 faq-assistant
}

# Основная функция
main() {
    log "=== Начинаем деплой FAQ Assistant ==="

    check_dependencies
    create_directories
    backup_data
    build_image
    stop_containers
    start_containers

    if health_check; then
        success "=== Деплой успешно завершен ==="
        show_status
    else
        error "=== Деплой завершился с ошибкой ==="
        show_status
        exit 1
    fi
}

# Обработка сигналов
trap 'error "Деплой прерван пользователем"; exit 1' INT TERM

# Запуск
main "$@"
