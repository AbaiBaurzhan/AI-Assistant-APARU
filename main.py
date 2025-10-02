"""Главный файл FastAPI приложения."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Создаем экземпляр FastAPI
app = FastAPI(
    title="ML Generation Support Assistant",
    description="ИИ-ассистент техподдержки для ML Generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": "ML Generation Support Assistant API"}


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

