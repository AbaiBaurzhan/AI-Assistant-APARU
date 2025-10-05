"""Главный файл FastAPI приложения для FAQ-ассистента."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.ask import router as ask_router
from utils.search import search_engine

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Инициализация при запуске
    try:
        logger.info("Инициализация поискового движка...")
        await search_engine.initialize()
        logger.info("Приложение готово к работе")
    except Exception as e:
        logger.error(f"Ошибка инициализации: {e}")
        # Приложение может работать без поискового движка,
        # но с ограниченной функциональностью

    yield

    # Очистка при завершении
    logger.info("Приложение завершает работу")


# Создаем экземпляр FastAPI
app = FastAPI(
    title="FAQ Support Assistant",
    description="ИИ-ассистент техподдержки на основе FAQ с векторным поиском",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(ask_router)


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "FAQ Support Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
