"""Модуль для работы с историей диалогов."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import HISTORY_FILE, MAX_HISTORY_ENTRIES


class HistoryManager:
    """Менеджер для работы с историей диалогов."""

    def __init__(self, history_file: Path = HISTORY_FILE) -> None:
        """
        Инициализирует менеджер истории.

        Args:
            history_file: Путь к файлу истории
        """
        self.history_file = history_file
        self.history: List[Dict[str, Any]] = []
        self._load_history()

    def _load_history(self) -> None:
        """Загружает историю из файла."""
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = [json.loads(line) for line in f if line.strip()]

                # Ограничиваем количество записей
                if len(self.history) > MAX_HISTORY_ENTRIES:
                    self.history = self.history[-MAX_HISTORY_ENTRIES:]

        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")
            self.history = []

    def save_history(self) -> None:
        """Сохраняет историю в файл."""
        try:
            # Создаем директорию если не существует
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.history_file, "w", encoding="utf-8") as f:
                for entry in self.history:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")

    def add_entry(
        self,
        question: str,
        answer: str,
        confidence: float,
        source: Optional[str] = None,
        similar_questions: Optional[List[str]] = None,
    ) -> None:
        """
        Добавляет запись в историю.

        Args:
            question: Вопрос пользователя
            answer: Ответ ассистента
            confidence: Уровень уверенности
            source: ID источника ответа
            similar_questions: Похожие вопросы
        """
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "source": source,
            "similar_questions": similar_questions or [],
        }

        self.history.append(entry)

        # Ограничиваем количество записей
        if len(self.history) > MAX_HISTORY_ENTRIES:
            self.history = self.history[-MAX_HISTORY_ENTRIES:]

        # Автосохранение
        self.save_history()

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Возвращает историю диалогов.

        Args:
            limit: Максимальное количество записей

        Returns:
            Список записей истории
        """
        if limit:
            return self.history[-limit:]
        return self.history

    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику по истории.

        Returns:
            Словарь со статистикой
        """
        if not self.history:
            return {
                "total_questions": 0,
                "average_confidence": 0.0,
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0,
            }

        total_questions = len(self.history)
        confidences = [entry["confidence"] for entry in self.history]
        average_confidence = sum(confidences) / len(confidences)

        high_confidence_count = sum(1 for c in confidences if c >= 0.8)
        medium_confidence_count = sum(1 for c in confidences if 0.6 <= c < 0.8)
        low_confidence_count = sum(1 for c in confidences if c < 0.6)

        return {
            "total_questions": total_questions,
            "average_confidence": average_confidence,
            "high_confidence_count": high_confidence_count,
            "medium_confidence_count": medium_confidence_count,
            "low_confidence_count": low_confidence_count,
        }

    def export_to_csv(self, output_file: Path) -> None:
        """
        Экспортирует историю в CSV файл.

        Args:
            output_file: Путь к выходному файлу
        """
        try:
            import pandas as pd

            if not self.history:
                print("История пуста, нечего экспортировать")
                return

            df = pd.DataFrame(self.history)
            df.to_csv(output_file, index=False, encoding="utf-8")
            print(f"История экспортирована в {output_file}")

        except ImportError:
            print("Для экспорта в CSV требуется pandas")
        except Exception as e:
            print(f"Ошибка экспорта: {e}")

    def clear_history(self) -> None:
        """Очищает историю."""
        self.history = []
        self.save_history()

    def search_history(self, query: str) -> List[Dict[str, Any]]:
        """
        Ищет в истории по запросу.

        Args:
            query: Поисковый запрос

        Returns:
            Список найденных записей
        """
        query_lower = query.lower()
        results = []

        for entry in self.history:
            if (
                query_lower in entry["question"].lower()
                or query_lower in entry["answer"].lower()
            ):
                results.append(entry)

        return results
