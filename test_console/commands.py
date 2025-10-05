"""Модуль с командами консольного приложения."""

import asyncio
import sys
from typing import Any, Dict, List, Optional

import httpx

from .config import API_BASE_URL, API_TIMEOUT
from .display import (
    print_answer,
    print_error,
    print_goodbye,
    print_help,
    print_history,
    print_info,
    print_separator,
    print_stats,
    show_progress,
)
from .history import HistoryManager


class CommandProcessor:
    """Процессор команд консольного приложения."""

    def __init__(self, history_manager: HistoryManager) -> None:
        """
        Инициализирует процессор команд.

        Args:
            history_manager: Менеджер истории
        """
        self.history_manager = history_manager
        self.client = httpx.AsyncClient(timeout=API_TIMEOUT)

    async def ask_command(self, question: str) -> None:
        """
        Обрабатывает команду ask.

        Args:
            question: Вопрос пользователя
        """
        if not question.strip():
            print_error("Вопрос не может быть пустым")
            return

        try:
            # Показываем прогресс
            with show_progress("Поиск ответа..."):
                # Отправляем запрос к API
                response = await self.client.post(
                    f"{API_BASE_URL}/api/v1/ask",
                    json={"query": question}
                )
                response.raise_for_status()
                result = response.json()

            # Выводим ответ
            print_answer(
                question=question,
                answer=result["reply"],
                confidence=result["confidence"],
                source=result.get("source"),
                similar_questions=result.get("similar_questions", [])
            )

            # Сохраняем в историю
            self.history_manager.add_entry(
                question=question,
                answer=result["reply"],
                confidence=result["confidence"],
                source=result.get("source"),
                similar_questions=result.get("similar_questions", [])
            )

        except httpx.ConnectError:
            print_error("Не удается подключиться к API. Убедитесь, что сервер запущен.")
        except httpx.HTTPStatusError as e:
            print_error(f"Ошибка API: {e.response.status_code}")
        except Exception as e:
            print_error(f"Неожиданная ошибка: {e}")

    async def stats_command(self) -> None:
        """Обрабатывает команду stats."""
        try:
            # Получаем статистику из истории
            history_stats = self.history_manager.get_stats()

            # Базовая статистика
            stats = {
                "records": 145,  # Из базы знаний
                "model": "BAAI/bge-m3",
                "embedding_dim": 1024,
                "index_ready": True,
            }

            # Добавляем статистику из истории
            stats.update(history_stats)

            print_stats(stats)

        except Exception as e:
            print_error(f"Ошибка получения статистики: {e}")

    def history_command(self, limit: int = 10) -> None:
        """
        Обрабатывает команду history.

        Args:
            limit: Количество записей для показа
        """
        try:
            history = self.history_manager.get_history(limit)
            print_history(history, limit)

        except Exception as e:
            print_error(f"Ошибка получения истории: {e}")

    def help_command(self) -> None:
        """Обрабатывает команду help."""
        print_help()

    def clear_command(self) -> None:
        """Обрабатывает команду clear."""
        import os
        os.system("clear" if os.name == "posix" else "cls")

    def exit_command(self) -> None:
        """Обрабатывает команду exit."""
        print_goodbye()
        sys.exit(0)

    async def process_command(self, command: str) -> None:
        """
        Обрабатывает введенную команду.

        Args:
            command: Команда для обработки
        """
        command = command.strip()

        if not command:
            return

        # Парсим команду
        parts = command.split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Обрабатываем команды
        if cmd == "ask":
            if not args:
                print_error("Использование: ask <вопрос>")
                return
            await self.ask_command(args)

        elif cmd == "stats":
            await self.stats_command()

        elif cmd == "history":
            try:
                limit = int(args) if args else 10
                self.history_command(limit)
            except ValueError:
                print_error("Лимит должен быть числом")

        elif cmd == "help":
            self.help_command()

        elif cmd == "clear":
            self.clear_command()

        elif cmd == "exit":
            self.exit_command()

        else:
            print_error(f"Неизвестная команда: {cmd}")
            print_info("Введите 'help' для списка команд")

    async def close(self) -> None:
        """Закрывает соединения."""
        await self.client.aclose()
