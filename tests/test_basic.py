"""Базовые тесты для проверки работоспособности."""

from fastapi import status
import pytest


def test_health_check(client):
    """Тест проверки здоровья сервиса."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client):
    """Тест корневого эндпоинта."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_async_health_check(async_client):
    """Асинхронный тест проверки здоровья сервиса."""
    response = await async_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_sample_ride_data(sample_ride_data):
    """Тест фикстуры с данными поездки."""
    assert "passenger_id" in sample_ride_data
    assert "pickup_location" in sample_ride_data
    assert "dropoff_location" in sample_ride_data
    assert sample_ride_data["passenger_id"] == 12345


def test_sample_passenger_data(sample_passenger_data):
    """Тест фикстуры с данными пассажира."""
    assert "id" in sample_passenger_data
    assert "name" in sample_passenger_data
    assert "phone" in sample_passenger_data
    assert sample_passenger_data["id"] == 12345
