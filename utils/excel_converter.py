"""Утилиты для конвертации Excel файлов в векторную базу знаний."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
HIGH_CONFIDENCE_THRESHOLD = 0.8
MEDIUM_CONFIDENCE_THRESHOLD = 0.6


class ExcelToVectorDBConverter:
    """Класс для конвертации Excel файлов в векторную базу знаний."""

    def __init__(self, model_name: str = EMBEDDING_MODEL) -> None:
        """
        Инициализирует конвертер.

        Args:
            model_name: Название модели для генерации эмбеддингов
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.embedding_dim = EMBEDDING_DIM

    async def load_model(self) -> None:
        """Загружает модель для генерации эмбеддингов."""
        try:
            logger.info(f"Загружаем модель {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Модель успешно загружена")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            raise

    def read_excel_file(self, file_path: str) -> pd.DataFrame:
        """
        Читает Excel файл с вопросами и ответами.

        Args:
            file_path: Путь к Excel файлу

        Returns:
            DataFrame с данными

        Raises:
            ValueError: Если файл не содержит нужные колонки
        """
        try:
            # Проверяем существование файла
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Файл не найден: {file_path}")

            # Читаем Excel файл
            df = pd.read_excel(file_path)
            logger.info(f"Прочитан файл {file_path}, строк: {len(df)}")

            # Проверяем наличие нужных колонок
            required_columns = ["question", "answer"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValueError(
                    f"Файл должен содержать колонки: {required_columns}. "
                    f"Отсутствуют: {missing_columns}"
                )

            # Удаляем пустые строки
            initial_count = len(df)
            df = df.dropna(subset=required_columns)
            final_count = len(df)

            if initial_count != final_count:
                logger.warning(f"Удалено {initial_count - final_count} пустых строк")

            # Удаляем дубликаты по вопросу
            initial_count = len(df)
            df = df.drop_duplicates(subset=["question"])
            final_count = len(df)

            if initial_count != final_count:
                logger.warning(f"Удалено {initial_count - final_count} дубликатов")

            logger.info(f"Готово к обработке {len(df)} записей")
            return df

        except Exception as e:
            logger.error(f"Ошибка чтения файла {file_path}: {e}")
            raise

    def normalize_text(self, text: str) -> str:
        """
        Нормализует текст для лучшего поиска.

        Args:
            text: Исходный текст

        Returns:
            Нормализованный текст
        """
        if not isinstance(text, str):
            return ""

        # Базовая нормализация
        text = text.strip().lower()

        # Удаляем лишние пробелы
        text = " ".join(text.split())

        return text

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Генерирует эмбеддинги для списка текстов.

        Args:
            texts: Список текстов для обработки

        Returns:
            Массив эмбеддингов
        """
        if not self.model:
            raise RuntimeError("Модель не загружена. Вызовите load_model()")

        try:
            # Нормализуем тексты
            normalized_texts = [self.normalize_text(text) for text in texts]

            # Генерируем эмбеддинги
            embeddings = self.model.encode(
                normalized_texts,
                batch_size=32,
                show_progress_bar=True,
                convert_to_numpy=True,
            )

            logger.info(f"Сгенерированы эмбеддинги для {len(texts)} текстов")
            return embeddings

        except Exception as e:
            logger.error(f"Ошибка генерации эмбеддингов: {e}")
            raise

    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Строит FAISS индекс из эмбеддингов.

        Args:
            embeddings: Массив эмбеддингов

        Returns:
            FAISS индекс
        """
        try:
            # Создаем индекс для косинусного сходства
            index = faiss.IndexFlatIP(embeddings.shape[1])

            # Нормализуем эмбеддинги для косинусного сходства
            faiss.normalize_L2(embeddings)

            # Добавляем эмбеддинги в индекс
            index.add(embeddings.astype("float32"))

            logger.info(f"Построен FAISS индекс с {index.ntotal} векторами")
            return index

        except Exception as e:
            logger.error(f"Ошибка построения FAISS индекса: {e}")
            raise

    def save_knowledge_base(self, df: pd.DataFrame, output_file: str) -> None:
        """
        Сохраняет базу знаний в JSONL формате.

        Args:
            df: DataFrame с данными
            output_file: Путь к выходному файлу
        """
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for idx, row in df.iterrows():
                    kb_entry = {
                        "id": f"q{idx:03d}",
                        "question": row["question"],
                        "answer": row["answer"],
                        "normalized_question": self.normalize_text(row["question"]),
                    }
                    f.write(json.dumps(kb_entry, ensure_ascii=False) + "\n")

            logger.info(f"База знаний сохранена в {output_file}")

        except Exception as e:
            logger.error(f"Ошибка сохранения базы знаний: {e}")
            raise

    async def convert_excel_to_vector_db(
        self,
        excel_file: str,
        output_dir: str = "data",
        index_filename: str = "faiss.index",
        kb_filename: str = "kb.jsonl",
    ) -> Dict[str, Any]:
        """
        Конвертирует Excel файл в векторную базу знаний.

        Args:
            excel_file: Путь к Excel файлу
            output_dir: Директория для сохранения результатов
            index_filename: Имя файла FAISS индекса
            kb_filename: Имя файла базы знаний

        Returns:
            Словарь с информацией о результате
        """
        try:
            # Создаем выходную директорию
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)

            # Загружаем модель
            await self.load_model()

            # Читаем Excel файл
            df = self.read_excel_file(excel_file)

            # Генерируем эмбеддинги для вопросов
            questions = df["question"].tolist()
            embeddings = self.generate_embeddings(questions)

            # Строим FAISS индекс
            index = self.build_faiss_index(embeddings)

            # Сохраняем индекс
            index_file = output_path / index_filename
            faiss.write_index(index, str(index_file))
            logger.info(f"FAISS индекс сохранен в {index_file}")

            # Сохраняем базу знаний
            kb_file = output_path / kb_filename
            self.save_knowledge_base(df, str(kb_file))

            # Возвращаем информацию о результате
            result = {
                "status": "success",
                "records_processed": len(df),
                "index_file": str(index_file),
                "knowledge_base_file": str(kb_file),
                "embedding_dimension": embeddings.shape[1],
                "model_used": self.model_name,
            }

            logger.info("Конвертация завершена успешно!")
            return result

        except Exception as e:
            logger.error(f"Ошибка конвертации: {e}")
            return {
                "status": "error",
                "error": str(e),
                "records_processed": 0,
            }


# Функция для быстрого использования
async def convert_excel_to_vector_db(
    excel_file: str,
    output_dir: str = "data",
    model_name: str = EMBEDDING_MODEL,
) -> Dict[str, Any]:
    """
    Быстрая функция для конвертации Excel в векторную БД.

    Args:
        excel_file: Путь к Excel файлу
        output_dir: Директория для сохранения
        model_name: Модель для эмбеддингов

    Returns:
        Результат конвертации
    """
    converter = ExcelToVectorDBConverter(model_name)
    return await converter.convert_excel_to_vector_db(excel_file, output_dir)

