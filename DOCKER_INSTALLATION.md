# Установка Docker для macOS

## 🐳 Установка Docker Desktop

### Способ 1: Через официальный сайт (рекомендуется)

1. **Скачайте Docker Desktop для Mac:**

   - Перейдите на https://www.docker.com/products/docker-desktop/
   - Нажмите "Download for Mac"
   - Выберите версию для вашего процессора (Intel или Apple Silicon)

2. **Установите Docker Desktop:**

   - Откройте скачанный файл `.dmg`
   - Перетащите Docker в папку Applications
   - Запустите Docker из Applications

3. **Проверьте установку:**
   ```bash
   docker --version
   docker-compose --version
   ```

### Способ 2: Через Homebrew

```bash
# Установка Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установка Docker Desktop
brew install --cask docker

# Запуск Docker Desktop
open /Applications/Docker.app
```

### Способ 3: Через командную строку

```bash
# Установка Docker CLI
brew install docker

# Установка Docker Compose
brew install docker-compose

# Установка Docker Machine (опционально)
brew install docker-machine
```

## ⚙️ Настройка Docker

### Первоначальная настройка

1. **Запустите Docker Desktop**
2. **Примите лицензионное соглашение**
3. **Настройте ресурсы (опционально):**
   - CPU: 2-4 ядра
   - Memory: 4-8 GB
   - Disk: 60+ GB

### Проверка работы

```bash
# Проверка Docker
docker run hello-world

# Проверка Docker Compose
docker-compose --version

# Проверка доступности Docker daemon
docker info
```

## 🚀 Запуск FAQ Assistant с Docker

### После установки Docker

```bash
# Перейдите в директорию проекта
cd "/Users/abaibaurzhan/Desktop/ML Generation"

# Запустите деплой
./deploy.sh

# Или вручную
docker-compose up -d

# Проверьте статус
./manage.sh status
```

### Альтернативный запуск

```bash
# Сборка образа
docker build -t faq-assistant .

# Запуск контейнера
docker run -d \
  --name faq-assistant \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  faq-assistant

# Проверка
docker ps
curl http://localhost:8000/api/v1/health
```

## 🔧 Troubleshooting

### Проблемы с установкой

#### 1. Docker не запускается

```bash
# Перезапуск Docker Desktop
killall Docker
open /Applications/Docker.app

# Проверка логов
tail -f ~/Library/Containers/com.docker.docker/Data/log/vm/dockerd.log
```

#### 2. Ошибка "Docker daemon not running"

```bash
# Запуск Docker Desktop
open /Applications/Docker.app

# Или через командную строку
sudo /Applications/Docker.app/Contents/MacOS/Docker --unattended --install-privileges
```

#### 3. Проблемы с правами доступа

```bash
# Добавление пользователя в группу docker
sudo dseditgroup -o edit -a $(whoami) -t user docker

# Перезапуск терминала
```

### Проблемы с производительностью

#### 1. Медленная работа

```bash
# Увеличение ресурсов в Docker Desktop
# Settings -> Resources -> Advanced
# CPU: 4 cores
# Memory: 8 GB
# Disk: 100 GB
```

#### 2. Высокое потребление памяти

```bash
# Очистка неиспользуемых ресурсов
docker system prune -a

# Ограничение памяти для контейнера
docker run -m 2g faq-assistant
```

## 📊 Мониторинг Docker

### Полезные команды

```bash
# Статус контейнеров
docker ps -a

# Использование ресурсов
docker stats

# Логи контейнера
docker logs faq-assistant

# Информация о системе
docker system info

# Очистка системы
docker system prune
```

### Docker Compose команды

```bash
# Запуск сервисов
docker-compose up -d

# Остановка сервисов
docker-compose down

# Просмотр логов
docker-compose logs -f

# Пересборка образов
docker-compose up -d --build

# Масштабирование
docker-compose up -d --scale faq-assistant=3
```

## 🎯 Следующие шаги

После установки Docker:

1. **Запустите FAQ Assistant:**

   ```bash
   ./deploy.sh
   ```

2. **Проверьте работу:**

   ```bash
   ./manage.sh health
   ```

3. **Настройте мониторинг:**

   ```bash
   ./manage.sh status
   ```

4. **Создайте бэкап:**
   ```bash
   ./manage.sh backup
   ```

## 📚 Дополнительные ресурсы

- [Docker Desktop для Mac](https://docs.docker.com/desktop/mac/)
- [Docker Compose документация](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Troubleshooting Docker](https://docs.docker.com/desktop/troubleshoot/)
