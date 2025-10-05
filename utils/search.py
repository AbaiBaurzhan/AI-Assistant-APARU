"""Утилиты для поиска и работы с эмбеддингами."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы
EMBEDDING_MODEL = "BAAI/bge-m3"
INDEX_FILE = "data/faiss.index"
KB_FILE = "data/kb.jsonl"
EMBEDDING_DIM = 1024

# Пороги для принятия решений
HIGH_CONFIDENCE_THRESHOLD = 0.8
MEDIUM_CONFIDENCE_THRESHOLD = 0.6
TOP_K_RESULTS = 5


class SearchEngine:
    """Класс для поиска в базе знаний FAQ."""

    def __init__(self) -> None:
        """Инициализирует поисковый движок."""
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.knowledge_base: List[Dict[str, Any]] = []
        self._is_initialized = False

    async def initialize(self) -> None:
        """Инициализирует поисковый движок."""
        try:
            # Загружаем модель эмбеддингов
            logger.info(f"Загружаем модель {EMBEDDING_MODEL}...")
            self.model = SentenceTransformer(EMBEDDING_MODEL)

            # Загружаем FAISS индекс
            if Path(INDEX_FILE).exists():
                self.index = faiss.read_index(INDEX_FILE)
                logger.info(f"Загружен FAISS индекс с {self.index.ntotal} векторами")
            else:
                raise FileNotFoundError(f"FAISS индекс не найден: {INDEX_FILE}")

            # Загружаем базу знаний
            if Path(KB_FILE).exists():
                with open(KB_FILE, "r", encoding="utf-8") as f:
                    self.knowledge_base = [json.loads(line) for line in f]
                logger.info(
                    f"Загружена база знаний с {len(self.knowledge_base)} записями"
                )
            else:
                raise FileNotFoundError(f"База знаний не найдена: {KB_FILE}")

            self._is_initialized = True
            logger.info("Поисковый движок инициализирован успешно")

        except Exception as e:
            logger.error(f"Ошибка инициализации поискового движка: {e}")
            raise

    def _ensure_initialized(self) -> None:
        """Проверяет, что движок инициализирован."""
        if not self._is_initialized:
            raise RuntimeError("Поисковый движок не инициализирован")

    def normalize_text(self, text: str) -> str:
        """Нормализует текст для лучшего поиска."""
        if not isinstance(text, str):
            return ""

        # Базовая нормализация
        text = text.strip().lower()

        # Удаляем лишние пробелы
        text = " ".join(text.split())

        return text

    async def generate_embedding(self, text: str) -> np.ndarray:
        """Генерирует эмбеддинг для текста."""
        self._ensure_initialized()

        try:
            normalized_text = self.normalize_text(text)
            embedding = self.model.encode([normalized_text], convert_to_numpy=True)

            # Нормализуем для косинусного сходства
            faiss.normalize_L2(embedding)

            return embedding.astype("float32")

        except Exception as e:
            logger.error(f"Ошибка генерации эмбеддинга: {e}")
            raise

    async def search_similar(
        self, query: str, top_k: int = TOP_K_RESULTS
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Ищет похожие вопросы в базе знаний."""
        self._ensure_initialized()

        try:
            # Генерируем эмбеддинг для запроса
            query_embedding = await self.generate_embedding(query)

            # Ищем похожие векторы
            similarities, indices = self.index.search(query_embedding, top_k)

            # Формируем результаты
            results = []
            for similarity, idx in zip(similarities[0], indices[0]):
                if idx < len(self.knowledge_base):
                    kb_entry = self.knowledge_base[idx]
                    results.append((kb_entry, float(similarity)))

            logger.info(
                f"Найдено {len(results)} похожих вопросов "
                f"для запроса: {query[:50]}..."
            )
            return results

        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            raise

    def get_confidence_level(self, similarity: float) -> str:
        """Определяет уровень уверенности по сходству."""
        if similarity >= HIGH_CONFIDENCE_THRESHOLD:
            return "high"
        elif similarity >= MEDIUM_CONFIDENCE_THRESHOLD:
            return "medium"
        else:
            return "low"

    async def find_best_answer(self, query: str) -> Dict[str, Any]:
        """Находит лучший ответ на вопрос пользователя."""
        try:
            # Ищем похожие вопросы
            similar_results = await self.search_similar(query, top_k=3)

            if not similar_results:
                return {
                    "reply": "Не понял вопрос, передаю оператору",
                    "confidence": 0.0,
                    "source": None,
                    "similar_questions": [],
                }

            # Берем лучший результат
            best_match, best_similarity = similar_results[0]
            confidence_level = self.get_confidence_level(best_similarity)

            if confidence_level == "high":
                # Высокая уверенность - возвращаем готовый ответ
                return {
                    "reply": best_match["answer"],
                    "confidence": min(best_similarity, 1.0),  # Ограничиваем до 1.0
                    "source": best_match["id"],
                    "similar_questions": [],
                }

            elif confidence_level == "medium":
                # Средняя уверенность - просим уточнить
                similar_questions = [
                    result[0]["question"] for result in similar_results[:3]
                ]
                return {
                    "reply": "Уточните, пожалуйста, ваш вопрос. Возможно, вы имели в виду:",
                    "confidence": min(best_similarity, 1.0),  # Ограничиваем до 1.0
                    "source": None,
                    "similar_questions": similar_questions,
                }

            else:
                # Низкая уверенность - передаем оператору
                return {
                    "reply": "Не понял вопрос, передаю оператору",
                    "confidence": min(best_similarity, 1.0),  # Ограничиваем до 1.0
                    "source": None,
                    "similar_questions": [],
                }

        except Exception as e:
            logger.error(f"Ошибка поиска ответа: {e}")
            return {
                "reply": "Произошла ошибка при обработке запроса",
                "confidence": 0.0,
                "source": None,
                "similar_questions": [],
            }


# Глобальный экземпляр поискового движка
search_engine = SearchEngine()
