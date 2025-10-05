"""Схемы для API вопросов и ответов."""

from typing import List, Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Схема запроса для поиска ответа."""

    query: str = Field(
        ..., min_length=1, max_length=1000, description="Вопрос пользователя"
    )


class AskResponse(BaseModel):
    """Схема ответа на вопрос."""

    reply: str = Field(..., description="Ответ ассистента")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Уровень уверенности (0-1)"
    )
    source: Optional[str] = Field(None, description="ID источника ответа")
    similar_questions: List[str] = Field(
        default_factory=list, description="Похожие вопросы"
    )


class FeedbackRequest(BaseModel):
    """Схема запроса обратной связи."""

    query: str = Field(
        ..., min_length=1, max_length=1000, description="Исходный вопрос"
    )
    answer_id: Optional[str] = Field(None, description="ID ответа")
    feedback: str = Field(..., pattern="^(👍|👎)$", description="Оценка ответа (👍 или 👎)")


class FeedbackResponse(BaseModel):
    """Схема ответа на обратную связь."""

    status: str = Field(..., description="Статус обработки")
    message: str = Field(..., description="Сообщение о результате")


class HealthResponse(BaseModel):
    """Схема ответа проверки здоровья."""

    status: str = Field(..., description="Статус сервиса")
    search_engine_ready: bool = Field(..., description="Готовность поискового движка")
