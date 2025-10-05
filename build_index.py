"""Скрипт для построения FAISS индекса из базы знаний FAQ."""

import asyncio
import logging
from pathlib import Path

from utils.excel_converter import convert_excel_to_vector_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы
FAQ_FILE = "data/faq.xlsx"


async def main() -> None:
    """Основная функция построения индекса."""
    try:
        # Проверяем существование файла FAQ
        if not Path(FAQ_FILE).exists():
            logger.error(f"Файл {FAQ_FILE} не найден")
            logger.info("Создайте Excel файл с колонками 'question' и 'answer'")
            return

        logger.info(f"Начинаем построение индекса из файла: {FAQ_FILE}")

        # Конвертируем Excel в векторную БД
        result = await convert_excel_to_vector_db(FAQ_FILE)

        if result["status"] == "success":
            logger.info("✅ Построение индекса завершено успешно!")
            logger.info(f"📊 Обработано записей: {result['records_processed']}")
            logger.info(f"📁 Индекс сохранен: {result['index_file']}")
            logger.info(f"📁 База знаний: {result['knowledge_base_file']}")
        else:
            logger.error(f"❌ Ошибка построения индекса: {result['error']}")

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
