import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from fastapi import HTTPException

from main import app
from services.click_log_service import get_click_log_service
from schemas.click_log_schemas import ClickLogStats

@pytest.fixture
def mock_click_log_service():
    mock = AsyncMock()
    mock.get_log_stats = AsyncMock()
    return mock

@pytest.fixture
def client(mock_click_log_service):
    app.dependency_overrides[get_click_log_service] = lambda: mock_click_log_service
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_get_link_stats_success(client, mock_click_log_service):
    short_code = "ABC123"
    expected_response = {
        "short_code": "ABC123",
        "original_url": "https://example.com",
        "created_at": "2024-01-01T12:00:00",
        "total_clicks": 42
    }

    mock_click_log_service.get_log_stats.return_value = ClickLogStats(**expected_response)

    response = client.get(f"/stats/{short_code}")

    assert response.status_code == 200
    assert response.json() == expected_response
    mock_click_log_service.get_log_stats.assert_called_once_with(short_code)

def test_get_link_stats_not_found(client, mock_click_log_service):
    short_code = "NONEXIST"
    mock_click_log_service.get_log_stats.side_effect = HTTPException(
        status_code=404, detail="Link not found"
    )

    response = client.get(f"/stats/{short_code}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found"
    mock_click_log_service.get_log_stats.assert_called_once_with(short_code)

def test_get_link_stats_service_error(client, mock_click_log_service):
    short_code = "ABC123"
    mock_click_log_service.get_log_stats.side_effect = Exception("Database error")

    with pytest.raises(Exception, match="Database error"):
        client.get(f"/stats/{short_code}")