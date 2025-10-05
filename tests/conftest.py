"""Конфигурация pytest для тестов."""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


@pytest.fixture
def client():
    """Фикстура для синхронного тестового клиента."""
    # Импортируем app здесь, чтобы избежать циклических импортов
    from main import app

    return TestClient(app)


@pytest.fixture
async def async_client():
    """Фикстура для асинхронного тестового клиента."""
    from main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_ride_data():
    """Фикстура с тестовыми данными поездки."""
    return {
        "passenger_id": 12345,
        "pickup_location": "ул. Абая, 1",
        "dropoff_location": "ул. Сатпаева, 10",
        "ride_type": "economy",
    }


@pytest.fixture
def sample_passenger_data():
    """Фикстура с тестовыми данными пассажира."""
    return {
        "id": 12345,
        "name": "Иван Иванов",
        "phone": "+7 777 123 45 67",
        "rating": 4.8,
    }
