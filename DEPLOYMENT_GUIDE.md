# Руководство по развертыванию FAQ Assistant

## 🚀 Быстрый старт

### 1. Подготовка окружения

```bash
# Установка Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Клонирование и настройка

```bash
# Клонируем репозиторий
git clone <repository-url>
cd faq-assistant

# Создаем необходимые директории
mkdir -p data logs ssl backups

# Копируем данные (если есть)
cp your-faq-data.xlsx data/faq.xlsx
```

### 3. Первый запуск

```bash
# Запускаем деплой
./deploy.sh

# Проверяем статус
./manage.sh status

# Проверяем здоровье
./manage.sh health
```

## 📦 Варианты развертывания

### Вариант 1: Docker Compose (рекомендуется)

```bash
# Простой запуск
docker-compose up -d

# С пересборкой
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f
```

### Вариант 2: Только приложение

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
```

### Вариант 3: Нативный Python

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🔧 Конфигурация

### Переменные окружения

```bash
# Основные настройки
export FASTAPI_ENV=production
export LOG_LEVEL=INFO
export PYTHONPATH=/app

# Настройки сервера
export HOST=0.0.0.0
export PORT=8000
export WORKERS=1

# Настройки поисковой системы
export EMBEDDING_MODEL=BAAI/bge-m3
export FAISS_INDEX_PATH=data/faiss.index
export KNOWLEDGE_BASE_PATH=data/kb.jsonl
```

### Настройка данных

```bash
# Структура директории data/
data/
├── faq.xlsx          # База знаний в Excel
├── kb.jsonl          # База знаний в JSONL
├── faiss.index       # FAISS индекс
└── feedback.log      # Логи обратной связи
```

## 🌐 Настройка веб-сервера

### Nginx (рекомендуется)

```bash
# Установка Nginx
sudo apt update
sudo apt install nginx

# Копирование конфигурации
sudo cp nginx.conf /etc/nginx/sites-available/faq-assistant
sudo ln -s /etc/nginx/sites-available/faq-assistant /etc/nginx/sites-enabled/

# Перезапуск Nginx
sudo systemctl restart nginx
```

### Apache (альтернатива)

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    ProxyPreserveHost On
    ProxyPass /api/ http://localhost:8000/api/
    ProxyPassReverse /api/ http://localhost:8000/api/
</VirtualHost>
```

## 🔒 SSL сертификаты

### Let's Encrypt (рекомендуется)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Самоподписанный сертификат (для тестирования)

```bash
# Генерация сертификата
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Копирование в контейнер
docker cp ssl/ faq-assistant:/etc/nginx/ssl/
```

## 📊 Мониторинг

### Health Check

```bash
# Проверка здоровья
curl http://localhost:8000/api/v1/health

# Детальная информация
curl http://localhost:8000/api/v1/health | jq '.'
```

### Логирование

```bash
# Просмотр логов
docker-compose logs -f faq-assistant

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Prometheus + Grafana (опционально)

```bash
# Запуск с мониторингом
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Доступ к Grafana
open http://localhost:3000
# Логин: admin, Пароль: admin
```

## 🔄 Обновление

### Обновление кода

```bash
# Получение обновлений
git pull origin main

# Пересборка и перезапуск
./deploy.sh

# Или через manage.sh
./manage.sh update
```

### Обновление данных

```bash
# Добавление новых данных
cp new-faq-data.xlsx data/faq.xlsx

# Пересборка индекса
python build_index.py

# Перезапуск сервиса
./manage.sh restart
```

## 🛠️ Управление

### Основные команды

```bash
# Запуск
./manage.sh start

# Остановка
./manage.sh stop

# Перезапуск
./manage.sh restart

# Статус
./manage.sh status

# Логи
./manage.sh logs

# Обновление
./manage.sh update

# Проверка здоровья
./manage.sh health
```

### Резервное копирование

```bash
# Создание бэкапа
./manage.sh backup

# Восстановление
./manage.sh restore
```

## 🚨 Troubleshooting

### Частые проблемы

#### 1. Сервис не запускается

```bash
# Проверка логов
docker-compose logs faq-assistant

# Проверка портов
netstat -tlnp | grep 8000

# Проверка Docker
docker ps -a
```

#### 2. Модель не загружается

```bash
# Проверка интернета
ping huggingface.co

# Проверка места на диске
df -h

# Очистка Docker кэша
docker system prune -a
```

#### 3. Низкая производительность

```bash
# Мониторинг ресурсов
htop
docker stats

# Увеличение лимитов памяти
# В docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 4G
```

#### 4. Ошибки SSL

```bash
# Проверка сертификатов
openssl x509 -in ssl/cert.pem -text -noout

# Обновление сертификатов
sudo certbot renew
```

### Диагностика

```bash
# Полная диагностика
./manage.sh status
./manage.sh health
docker-compose logs --tail=100

# Проверка конфигурации
docker-compose config

# Тестирование API
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "тест"}'
```

## 📈 Масштабирование

### Горизонтальное масштабирование

```bash
# Увеличение количества воркеров
docker-compose up -d --scale faq-assistant=3

# Настройка load balancer в nginx.conf
upstream faq_backend {
    server faq-assistant_1:8000;
    server faq-assistant_2:8000;
    server faq-assistant_3:8000;
}
```

### Вертикальное масштабирование

```yaml
# В docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: "2.0"
    reservations:
      memory: 2G
      cpus: "1.0"
```

## 🔐 Безопасность

### Firewall

```bash
# UFW настройки
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Обновления безопасности

```bash
# Обновление системы
sudo apt update && sudo apt upgrade

# Обновление Docker
sudo apt install docker-ce docker-ce-cli containerd.io

# Обновление образов
docker-compose pull
docker-compose up -d
```

## 📋 Чеклист развертывания

### Перед развертыванием

- [ ] Docker и Docker Compose установлены
- [ ] Данные FAQ подготовлены
- [ ] Домен настроен (если нужен)
- [ ] SSL сертификаты готовы
- [ ] Firewall настроен

### После развертывания

- [ ] Сервис отвечает на health check
- [ ] API работает корректно
- [ ] Логи записываются
- [ ] Мониторинг настроен
- [ ] Бэкапы настроены
- [ ] Обновления автоматизированы

## 🆘 Поддержка

### Полезные команды

```bash
# Полная диагностика
./manage.sh status
./manage.sh health
./manage.sh logs

# Экстренный перезапуск
docker-compose down && docker-compose up -d

# Очистка системы
docker system prune -a
```

### Контакты

- Документация: `README.md`
- API документация: `http://your-domain.com/docs`
- Логи: `logs/app.log`
- Конфигурация: `CONFIGURATION.md`
