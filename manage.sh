#!/bin/bash

# Скрипт управления FAQ Assistant
# Использование: ./manage.sh [start|stop|restart|status|logs|update]

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

# Функция показа помощи
show_help() {
    echo "Использование: $0 [команда]"
    echo ""
    echo "Команды:"
    echo "  start     - Запустить сервис"
    echo "  stop      - Остановить сервис"
    echo "  restart   - Перезапустить сервис"
    echo "  status    - Показать статус сервиса"
    echo "  logs      - Показать логи"
    echo "  update    - Обновить и перезапустить"
    echo "  health    - Проверить здоровье сервиса"
    echo "  backup    - Создать бэкап данных"
    echo "  restore   - Восстановить из бэкапа"
    echo ""
}

# Запуск сервиса
start_service() {
    log "Запускаем сервис..."
    docker-compose up -d
    success "Сервис запущен"
}

# Остановка сервиса
stop_service() {
    log "Останавливаем сервис..."
    docker-compose down
    success "Сервис остановлен"
}

# Перезапуск сервиса
restart_service() {
    log "Перезапускаем сервис..."
    docker-compose restart
    success "Сервис перезапущен"
}

# Показать статус
show_status() {
    log "Статус сервисов:"
    docker-compose ps

    echo ""
    log "Использование ресурсов:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Показать логи
show_logs() {
    log "Логи сервиса:"
    docker-compose logs --tail=50 -f
}

# Обновление сервиса
update_service() {
    log "Обновляем сервис..."

    # Останавливаем сервис
    docker-compose down

    # Пересобираем образ
    docker build -t faq-assistant:latest .

    # Запускаем сервис
    docker-compose up -d

    success "Сервис обновлен и перезапущен"
}

# Проверка здоровья
check_health() {
    log "Проверяем здоровье сервиса..."

    if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        success "Сервис здоров"

        # Показать детальную информацию
        echo ""
        log "Детальная информация:"
        curl -s http://localhost:8000/api/v1/health | jq '.' 2>/dev/null || curl -s http://localhost:8000/api/v1/health
    else
        error "Сервис не отвечает"
        return 1
    fi
}

# Создание бэкапа
create_backup() {
    log "Создаем бэкап данных..."

    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    if [ -d "data" ]; then
        cp -r data "$BACKUP_DIR/"
        success "Бэкап создан в $BACKUP_DIR"
    else
        warning "Директория data не найдена"
    fi
}

# Восстановление из бэкапа
restore_backup() {
    log "Доступные бэкапы:"
    ls -la backups/ 2>/dev/null || echo "Бэкапы не найдены"

    echo ""
    read -p "Введите имя директории бэкапа для восстановления: " backup_name

    if [ -d "backups/$backup_name" ]; then
        log "Восстанавливаем из бэкапа $backup_name..."
        cp -r "backups/$backup_name/data" ./
        success "Данные восстановлены"
    else
        error "Бэкап $backup_name не найден"
        return 1
    fi
}

# Основная функция
main() {
    case "${1:-help}" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        update)
            update_service
            ;;
        health)
            check_health
            ;;
        backup)
            create_backup
            ;;
        restore)
            restore_backup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Неизвестная команда: $1"
            show_help
            exit 1
            ;;
    esac
}

# Запуск
main "$@"
