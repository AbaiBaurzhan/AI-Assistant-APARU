"""Скрипт для конвертации Excel файла в векторную базу знаний."""

import asyncio
import logging
import sys
from pathlib import Path

from utils.excel_converter import convert_excel_to_vector_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Основная функция для конвертации Excel файла."""
    try:
        # Путь к Excel файлу
        excel_file = "data/faq.xlsx"

        # Проверяем существование файла
        if not Path(excel_file).exists():
            logger.error(f"Файл {excel_file} не найден!")
            logger.info("Создайте Excel файл с колонками 'question' и 'answer'")
            sys.exit(1)

        logger.info(f"Начинаем конвертацию файла: {excel_file}")

        # Конвертируем Excel в векторную БД
        result = await convert_excel_to_vector_db(excel_file)

        if result["status"] == "success":
            logger.info("✅ Конвертация завершена успешно!")
            logger.info(f"📊 Обработано записей: {result['records_processed']}")
            logger.info(f"📁 Индекс сохранен: {result['index_file']}")
            logger.info(f"📁 База знаний: {result['knowledge_base_file']}")
            logger.info(f"🤖 Модель: {result['model_used']}")
            logger.info(f"📐 Размерность эмбеддингов: {result['embedding_dimension']}")
        else:
            logger.error(f"❌ Ошибка конвертации: {result['error']}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

