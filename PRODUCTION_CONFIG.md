# Конфигурация для продакшена

## Переменные окружения

```bash
# Основные настройки
FASTAPI_ENV=production
LOG_LEVEL=INFO
PYTHONPATH=/app

# Настройки сервера
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Настройки поисковой системы
EMBEDDING_MODEL=BAAI/bge-m3
FAISS_INDEX_PATH=data/faiss.index
KNOWLEDGE_BASE_PATH=data/kb.jsonl

# Настройки безопасности
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Настройки логирования
LOG_FILE=logs/app.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5

# Настройки кэширования
ENABLE_CACHE=true
CACHE_SIZE=1000
CACHE_TTL=3600

# Настройки мониторинга
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Docker Compose для продакшена

```yaml
version: "3.8"

services:
  faq-assistant:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FASTAPI_ENV=production
      - LOG_LEVEL=INFO
      - PYTHONPATH=/app
      - WORKERS=1
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - faq-network
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: "1.0"
        reservations:
          memory: 1G
          cpus: "0.5"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - faq-assistant
    restart: unless-stopped
    networks:
      - faq-network

  # Мониторинг (опционально)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    restart: unless-stopped
    networks:
      - faq-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped
    networks:
      - faq-network

networks:
  faq-network:
    driver: bridge

volumes:
  data:
  logs:
  grafana-data:
```

## Nginx конфигурация для продакшена

```nginx
events {
    worker_connections 1024;
}

http {
    # Основные настройки
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Логирование
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    upstream faq_backend {
        server faq-assistant:8000;
        keepalive 32;
    }

    # HTTP сервер (редирект на HTTPS)
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS сервер
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL сертификаты
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # SSL настройки
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Безопасность
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Rate limiting
        limit_req zone=api burst=20 nodelay;

        # API endpoints
        location /api/ {
            proxy_pass http://faq_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            proxy_http_version 1.1;

            # Таймауты
            proxy_connect_timeout 5s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Swagger документация
        location /docs {
            proxy_pass http://faq_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://faq_backend/api/v1/health;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Статичные файлы
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Безопасность
        location / {
            return 404;
        }
    }
}
```

## Мониторинг и логирование

### Prometheus конфигурация

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "faq-assistant"
    static_configs:
      - targets: ["faq-assistant:8000"]
    metrics_path: "/metrics"
    scrape_interval: 30s
```

### Логирование

```python
# В main.py
import logging
from logging.handlers import RotatingFileHandler

# Настройка логирования для продакшена
if FASTAPI_ENV == "production":
    # Файловое логирование с ротацией
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Добавляем обработчик
    logger.addHandler(file_handler)

    # Уровень логирования
    logger.setLevel(logging.INFO)
```

## Безопасность

### SSL сертификаты

```bash
# Генерация самоподписанного сертификата для тестирования
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Для продакшена используйте Let's Encrypt
certbot --nginx -d your-domain.com
```

### Firewall настройки

```bash
# UFW настройки
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Резервное копирование

### Автоматический бэкап

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Бэкап данных
cp -r data "$BACKUP_DIR/"

# Бэкап логов
cp -r logs "$BACKUP_DIR/"

# Сжатие
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

# Удаление старых бэкапов (старше 30 дней)
find /backups -name "*.tar.gz" -mtime +30 -delete
```

### Cron задача

```bash
# Добавить в crontab
0 2 * * * /path/to/backup.sh
```

## Обновление

### Zero-downtime обновление

```bash
#!/bin/bash
# rolling-update.sh

# Создаем новый образ
docker build -t faq-assistant:new .

# Запускаем новый контейнер
docker-compose up -d --scale faq-assistant=2

# Ждем готовности
sleep 30

# Проверяем здоровье
curl -f http://localhost:8000/api/v1/health

# Останавливаем старый контейнер
docker-compose up -d --scale faq-assistant=1

# Удаляем старый образ
docker rmi faq-assistant:old
docker tag faq-assistant:new faq-assistant:latest
```
