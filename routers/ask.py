"""Роутер для обработки вопросов и обратной связи."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, status

from schemas.ask import AskRequest, AskResponse, FeedbackRequest, FeedbackResponse
from utils.greetings import process_greeting_message
from utils.search import search_engine

# Настройка логирования
logger = logging.getLogger(__name__)

# Создаем роутер
router = APIRouter(prefix="/api/v1", tags=["FAQ Assistant"])

# Файл для логирования обратной связи
FEEDBACK_LOG_FILE = "data/feedback.log"


async def log_feedback(feedback_data: Dict[str, Any]) -> None:
    """Логирует обратную связь в файл."""
    try:
        # Создаем директорию data если не существует
        Path("data").mkdir(exist_ok=True)

        # Формируем запись лога
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": feedback_data["query"],
            "answer_id": feedback_data.get("answer_id"),
            "feedback": feedback_data["feedback"],
        }

        # Записываем в файл
        with open(FEEDBACK_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{log_entry}\n")

        logger.info(f"Обратная связь записана: {feedback_data['feedback']}")

    except Exception as e:
        logger.error(f"Ошибка записи обратной связи: {e}")


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest) -> AskResponse:
    """
    Обрабатывает вопрос пользователя и возвращает ответ.

    Args:
        request: Запрос с вопросом пользователя

    Returns:
        Ответ ассистента с уровнем уверенности

    Raises:
        HTTPException: При ошибках обработки
    """
    try:
        # Обрабатываем приветствие
        is_greeting_flag, greeting_response, main_content = process_greeting_message(
            request.query
        )

        # Если это только приветствие - возвращаем стандартный ответ
        if is_greeting_flag and greeting_response:
            logger.info(f"Обработано приветствие: {request.query[:50]}...")
            return AskResponse(
                reply=greeting_response,
                confidence=1.0,
                source="greeting",
                similar_questions=[],
            )

        # Определяем текст для поиска в FAQ
        search_query = main_content if main_content else request.query

        # Проверяем, что поисковый движок инициализирован
        if not search_engine._is_initialized:
            await search_engine.initialize()

        # Ищем лучший ответ
        result = await search_engine.find_best_answer(search_query)

        # Логируем запрос
        logger.info(
            f"Обработан вопрос: {request.query[:50]}... "
            f"(confidence: {result['confidence']:.3f})"
        )

        return AskResponse(
            reply=result["reply"],
            confidence=result["confidence"],
            source=result["source"],
            similar_questions=result["similar_questions"],
        )

    except Exception as e:
        logger.error(f"Ошибка обработки вопроса: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при обработке вопроса",
        )


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """
    Принимает обратную связь от пользователя.

    Args:
        request: Запрос с обратной связью

    Returns:
        Статус обработки обратной связи

    Raises:
        HTTPException: При ошибках обработки
    """
    try:
        # Логируем обратную связь
        feedback_data = {
            "query": request.query,
            "answer_id": request.answer_id,
            "feedback": request.feedback,
        }

        await log_feedback(feedback_data)

        # Логируем в систему
        logger.info(
            f"Получена обратная связь: {request.feedback} "
            f"для вопроса: {request.query[:50]}..."
        )

        return FeedbackResponse(
            status="success", message="Обратная связь успешно сохранена"
        )

    except Exception as e:
        logger.error(f"Ошибка обработки обратной связи: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при обработке обратной связи",
        )


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Проверяет состояние сервиса.

    Returns:
        Статус сервиса и компонентов
    """
    try:
        # Проверяем готовность поискового движка
        search_engine_ready = search_engine._is_initialized

        # Проверяем существование файлов
        index_exists = Path("data/faiss.index").exists()
        kb_exists = Path("data/kb.jsonl").exists()

        overall_status = (
            "healthy"
            if (search_engine_ready and index_exists and kb_exists)
            else "degraded"
        )

        return {
            "status": overall_status,
            "search_engine_ready": search_engine_ready,
            "index_file_exists": index_exists,
            "knowledge_base_exists": kb_exists,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
