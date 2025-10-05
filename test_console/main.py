"""Главный файл консольного приложения для тестирования FAQ-ассистента."""

import asyncio
import sys
from pathlib import Path

from rich.console import Console

from .commands import CommandProcessor
from .config import DATA_DIR
from .display import print_header, print_info, print_separator, print_question_prompt
from .history import HistoryManager

# Создаем консоль для вывода
console = Console()


async def check_api_availability() -> bool:
    """Проверяет доступность API."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://localhost:8000/api/v1/health")
            return response.status_code == 200
    except Exception:
        return False


def check_data_files() -> bool:
    """Проверяет наличие необходимых файлов данных."""
    required_files = [
        DATA_DIR / "faq.xlsx",
        DATA_DIR / "faiss.index",
        DATA_DIR / "kb.jsonl",
    ]

    missing_files = [f for f in required_files if not f.exists()]

    if missing_files:
        print_info("Отсутствуют файлы данных:")
        for file in missing_files:
            print_info(f"  - {file}")
        print_info("Запустите 'python convert_excel.py' для создания базы знаний")
        return False

    return True


async def main() -> None:
    """Главная функция приложения."""
    try:
        # Проверяем файлы данных
        if not check_data_files():
            console.print("\n[bold red]❌ Не удается запустить приложение[/bold red]")
            sys.exit(1)

        # Проверяем API
        api_available = await check_api_availability()
        if not api_available:
            console.print("\n[bold yellow]⚠️ API недоступен. Запустите сервер: python main.py[/bold yellow]")
            console.print("[dim]Приложение будет работать в режиме демо[/dim]")

        # Инициализируем компоненты
        history_manager = HistoryManager()
        command_processor = CommandProcessor(history_manager)

        # Выводим заголовок
        print_header()

        # Показываем статистику
        if api_available:
            await command_processor.stats_command()

        print_separator()

        # Главный цикл
        while True:
            try:
                print_question_prompt()
                command = input().strip()

                if command:
                    await command_processor.process_command(command)
                    print_separator()

            except KeyboardInterrupt:
                console.print("\n[yellow]Прерывание пользователем[/yellow]")
                break
            except EOFError:
                console.print("\n[yellow]Конец ввода[/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]Ошибка: {e}[/red]")

    except Exception as e:
        console.print(f"\n[bold red]Критическая ошибка: {e}[/bold red]")
        sys.exit(1)

    finally:
        # Закрываем соединения
        if 'command_processor' in locals():
            await command_processor.close()


if __name__ == "__main__":
    # Запускаем приложение
    asyncio.run(main())
