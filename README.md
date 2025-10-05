# FAQ Support Assistant

Intelligent FAQ search system for customer support chat automation using vector-based semantic search.

## Quick Start

### 1. Python Setup

```bash
# Clone repository
git clone <repository-url>
cd faq-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Docker Setup

```bash
# Build image
docker build -t faq-assistant .

# Run container
docker run -p 8000:8000 faq-assistant

# Or using docker-compose
docker-compose up -d
```

## API Endpoints

### Main Endpoints

- `POST /api/v1/ask` — FAQ search
- `POST /api/v1/feedback` — User feedback collection
- `GET /api/v1/health` — Health check
- `GET /docs` — Swagger documentation

## Configuration

### Environment Variables

```bash
# Server port (default: 8000)
PORT=8000

# Embedding model (default: BAAI/bge-m3)
MODEL_NAME=BAAI/bge-m3

# Knowledge base path
DATA_DIR=./data
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

## Project Structure

```
faq-assistant/
├── main.py                 # FastAPI server
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose
├── README.md              # Documentation
├── data/                  # Knowledge base
│   ├── faq.xlsx          # Source data
│   ├── faiss.index       # Vector index
│   └── kb.jsonl          # Knowledge base in JSON
├── utils/                 # Utilities
│   ├── search.py         # Search logic
│   └── excel_converter.py # Data converter
├── routers/               # API routes
│   └── ask.py            # FAQ endpoints
├── schemas/               # Pydantic models
│   └── ask.py            # Data schemas
└── tests/                 # Tests
```

## Knowledge Base Updates

### Adding New FAQs

1. **Update Excel file** `data/faq.xlsx`
2. **Rebuild index:**
   ```bash
   python build_index.py
   ```
3. **Restart server**

### Excel File Structure

| question | answer | id |
|----------|--------|-----|
| How to order a taxi? | Open the app... | q001 |
| What is the cost? | Rate depends on... | q002 |

## Troubleshooting

### Common Issues

**1. "Address already in use" error**
```bash
# Find process on port 8000
lsof -i :8000

# Stop process
kill -9 <PID>
```

**2. Model not loading**
```bash
# Check internet connection
# Model downloads on first run (~500MB)
```

**3. Knowledge base not found**
```bash
# Ensure files exist in data/
ls -la data/
```

## Performance

### Specifications

- **Response time:** < 3 seconds
- **Memory:** ~2GB (with model)
- **CPU:** 1-2 cores
- **Disk:** ~1GB (model + data)

### Scaling

- **Horizontal:** multiple instances behind load balancer
- **Vertical:** increase RAM for larger knowledge bases

## Security

### Recommendations

- Use HTTPS in production
- Configure rate limiting
- Restrict access by IP
- Regularly update dependencies

## Support

- **API Documentation:** http://localhost:8000/docs
- **Issues:** GitHub Issues
- **Email:** support@example.com

## License

MIT License
