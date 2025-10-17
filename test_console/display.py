"""Модуль для цветного вывода и форматирования."""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from .config import COLORS, CONFIDENCE_THRESHOLDS

# Создаем консоль для вывода
console = Console()


def print_header() -> None:
    """Выводит заголовок приложения."""
    header = Panel.fit(
        "[bold blue]🤖 FAQ Assistant Console v1.0[/bold blue]\n"
        "[dim]Интерактивное тестирование ассистента техподдержки[/dim]\n"
        "[green]💡 Просто введите ваш вопрос - команда 'ask' не нужна![/green]",
        border_style="blue",
    )
    console.print(header)


def print_stats(stats: Dict[str, Any]) -> None:
    """Выводит статистику базы знаний."""
    table = Table(title="📊 Статистика базы знаний")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")

    table.add_row("Записей в базе", str(stats.get("records", 0)))
    table.add_row("Модель", stats.get("model", "BAAI/bge-m3"))
    table.add_row("Размерность эмбеддингов", str(stats.get("embedding_dim", 1024)))
    table.add_row(
        "Индекс FAISS", "✅ Готов" if stats.get("index_ready") else "❌ Не готов"
    )

    console.print(table)


def print_question_prompt() -> None:
    """Выводит приглашение для ввода вопроса."""
    console.print("\n[bold cyan]> [/bold cyan]", end="")


def print_answer(
    question: str,
    answer: str,
    confidence: float,
    source: Optional[str] = None,
    similar_questions: Optional[List[str]] = None,
) -> None:
    """Выводит ответ ассистента с цветовой индикацией."""
    # Определяем цвет по уверенности
    if confidence >= CONFIDENCE_THRESHOLDS["high"]:
        color = "green"
        icon = "✅"
        status = "Высокая уверенность"
    elif confidence >= CONFIDENCE_THRESHOLDS["medium"]:
        color = "yellow"
        icon = "⚠️"
        status = "Средняя уверенность"
    else:
        color = "red"
        icon = "❌"
        status = "Низкая уверенность"

    # Выводим вопрос
    console.print(f"\n[bold]{icon} Ответ найден ({status})[/bold]")
    console.print(f"[dim]Вопрос: {question}[/dim]")

    # Выводим ответ
    console.print(f"[{color}]{answer}[/{color}]")

    # Выводим метаданные
    if source:
        console.print(f"[dim]🆔 Источник: {source}[/dim]")
    console.print(f"[dim]📊 Уверенность: {confidence:.3f}[/dim]")

    # Выводим похожие вопросы если есть
    if similar_questions:
        console.print("\n[bold yellow]🔍 Похожие вопросы:[/bold yellow]")
        for i, similar_q in enumerate(similar_questions[:3], 1):
            console.print(f"[dim]{i}. {similar_q}[/dim]")


def print_error(message: str) -> None:
    """Выводит сообщение об ошибке."""
    console.print(f"\n[bold red]❌ Ошибка: {message}[/bold red]")


def print_info(message: str) -> None:
    """Выводит информационное сообщение."""
    console.print(f"\n[blue]ℹ️ {message}[/blue]")


def print_success(message: str) -> None:
    """Выводит сообщение об успехе."""
    console.print(f"\n[green]✅ {message}[/green]")


def print_help() -> None:
    """Выводит справку по командам."""
    help_text = """
[bold cyan]Режим работы:[/bold cyan]
[green]Просто введите ваш вопрос - команда 'ask' не нужна![/green]

[bold cyan]Доступные команды:[/bold cyan]

[bold]stats[/bold]            - Показать статистику базы знаний
[bold]history[/bold]          - Показать историю диалогов
[bold]clear[/bold]            - Очистить экран
[bold]help[/bold]             - Показать эту справку
[bold]exit[/bold]             - Выйти из приложения

[bold yellow]Примеры:[/bold yellow]
  Как заказать такси?        [dim](автоматически: ask Как заказать такси?)[/dim]
  Сколько стоит поездка?     [dim](автоматически: ask Сколько стоит поездка?)[/dim]
  stats
  history
  exit
"""
    console.print(Panel(help_text, title="📖 Справка", border_style="green"))


def print_history(history: List[Dict[str, Any]], limit: int = 10) -> None:
    """Выводит историю диалогов."""
    if not history:
        console.print("[yellow]📝 История пуста[/yellow]")
        return

    table = Table(title=f"📝 История диалогов (последние {min(limit, len(history))})")
    table.add_column("Время", style="dim", width=12)
    table.add_column("Вопрос", style="cyan", width=30)
    table.add_column("Уверенность", style="green", width=12)
    table.add_column("Источник", style="blue", width=10)

    for entry in history[-limit:]:
        timestamp = entry.get("timestamp", "")
        question = (
            entry.get("question", "")[:27] + "..."
            if len(entry.get("question", "")) > 30
            else entry.get("question", "")
        )
        confidence = f"{entry.get('confidence', 0):.3f}"
        source = entry.get("source", "N/A")

        table.add_row(timestamp, question, confidence, source)

    console.print(table)


def show_progress(message: str) -> Progress:
    """Показывает прогресс-бар для длительных операций."""
    progress = Progress(
        SpinnerColumn(),
        TextColumn(f"[blue]{message}[/blue]"),
        console=console,
    )
    return progress


def print_goodbye() -> None:
    """Выводит прощальное сообщение."""
    console.print(
        "\n[bold blue]👋 До свидания! Спасибо за использование FAQ Assistant Console![/bold blue]"
    )


def clear_screen() -> None:
    """Очищает экран."""
    console.clear()


def print_separator() -> None:
    """Выводит разделитель."""
    console.print("[dim]" + "─" * 60 + "[/dim]")
