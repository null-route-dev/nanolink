import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from fastapi import HTTPException

from main import app
from services.link_service import get_link_service
from services.click_log_service import get_click_log_service
from schemas.link_schemas import LinkResponse

@pytest.fixture
def mock_link_service():
    mock = AsyncMock()
    mock.create_short_link = AsyncMock()
    mock.get_original_url = AsyncMock()
    return mock

@pytest.fixture
def mock_click_log_service():
    mock = AsyncMock()
    mock.create_click_log = AsyncMock()
    return mock

@pytest.fixture
def client(mock_link_service, mock_click_log_service):
    app.dependency_overrides[get_link_service] = lambda: mock_link_service
    app.dependency_overrides[get_click_log_service] = lambda: mock_click_log_service
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_link_success(client, mock_link_service):
    link_data = {"original_url": "https://example.com"}
    expected_response = {
        "short_code": "ABC123",
        "original_url": "https://example.com/",
        "created_at": "2024-01-01T12:00:00"
    }

    mock_link_service.create_short_link.return_value = LinkResponse(**expected_response)

    response = client.post("/links/", json=link_data)

    assert response.status_code == 201
    assert response.json() == expected_response

def test_create_link_service_error(client, mock_link_service):
    link_data = {"original_url": "https://example.com"}
    mock_link_service.create_short_link.side_effect = Exception("Service error")

    with pytest.raises(Exception, match="Service error"):
        client.post("/links/", json=link_data)

def test_redirect_to_url_success(client, mock_link_service, mock_click_log_service):
    short_code = "ABC123"
    original_url = "https://example.com"
    mock_link_service.get_original_url.return_value = original_url
    mock_click_log_service.create_click_log.return_value = None

    response = client.get(
        f"/links/{short_code}",
        headers={"user-agent": "TestAgent"},
        follow_redirects=False
    )

    assert response.status_code == 307
    assert response.headers["location"] == original_url
    mock_link_service.get_original_url.assert_called_once_with(short_code)
    mock_click_log_service.create_click_log.assert_called_once_with(
        short_code, "testclient", "TestAgent"
    )

def test_redirect_to_url_not_found(client, mock_link_service, mock_click_log_service):
    short_code = "NONEXIST"
    mock_link_service.get_original_url.side_effect = HTTPException(
        status_code=404, detail="Link not found"
    )

    response = client.get(f"/links/{short_code}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found"
    mock_click_log_service.create_click_log.assert_not_called()

def test_redirect_to_url_service_error(client, mock_link_service, mock_click_log_service):
    short_code = "ABC123"
    mock_link_service.get_original_url.side_effect = Exception("DB error")

    with pytest.raises(Exception, match="DB error"):
        client.get(f"/links/{short_code}")

    mock_click_log_service.create_click_log.assert_not_called()