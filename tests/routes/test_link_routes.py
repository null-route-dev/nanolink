import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from fastapi import HTTPException

from main import app
from services.link_service import get_link_service
from services.click_log_service import get_click_log_service
from core.security import get_current_user
from schemas.link_schemas import LinkResponse
from schemas.user_schemas import UserResponse

@pytest.fixture
def mock_link_service():
    mock = AsyncMock()
    mock.create_short_link = AsyncMock()
    mock.get_original_url = AsyncMock()
    mock.get_user_links = AsyncMock()
    mock.update_link = AsyncMock()
    mock.delete_link = AsyncMock()
    return mock

@pytest.fixture
def mock_click_log_service():
    mock = AsyncMock()
    mock.create_click_log = AsyncMock()
    return mock

@pytest.fixture
def mock_current_user():
    return UserResponse(
        id=1,
        username="testuser",
        email="test@example.com",
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00"
    )

@pytest.fixture
def client(mock_link_service, mock_click_log_service, mock_current_user):
    app.dependency_overrides[get_link_service] = lambda: mock_link_service
    app.dependency_overrides[get_click_log_service] = lambda: mock_click_log_service
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_link_success(client, mock_link_service):
    link_data = {"original_url": "https://example.com"}
    expected_response = {
        "short_code": "ABC123",
        "original_url": "https://example.com/",
        "created_at": "2026-01-01T12:00:00",
        "owner_id": 1
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

def test_get_my_links_success(client, mock_link_service):
    expected_links = [
        {
            "short_code": "ABC123",
            "original_url": "https://example1.com",
            "created_at": "2026-01-01T12:00:00",
            "owner_id": 1
        },
        {
            "short_code": "DEF456",
            "original_url": "https://example2.com",
            "created_at": "2026-01-01T12:00:00",
            "owner_id": 1
        }
    ]
    mock_link_service.get_user_links.return_value = [LinkResponse(**link) for link in expected_links]

    response = client.get("/links/my")

    assert response.status_code == 200
    assert response.json() == expected_links
    mock_link_service.get_user_links.assert_called_once_with(1)

def test_get_my_links_empty(client, mock_link_service):
    mock_link_service.get_user_links.return_value = []

    response = client.get("/links/my")

    assert response.status_code == 200
    assert response.json() == []
    mock_link_service.get_user_links.assert_called_once_with(1)

def test_get_my_links_service_error(client, mock_link_service):
    mock_link_service.get_user_links.side_effect = Exception("Service error")

    with pytest.raises(Exception, match="Service error"):
        client.get("/links/my")

def test_update_link_success(client, mock_link_service):
    short_code = "ABC123"
    link_data = {"original_url": "https://newexample.com"}
    expected_response = {
        "short_code": "ABC123",
        "original_url": "https://newexample.com/",
        "created_at": "2026-01-01T12:00:00",
        "owner_id": 1
    }
    mock_link_service.update_link.return_value = LinkResponse(**expected_response)

    response = client.put(f"/links/{short_code}", json=link_data)

    assert response.status_code == 200
    assert response.json() == expected_response
    mock_link_service.update_link.assert_called_once_with(short_code, "https://newexample.com/", 1)

def test_update_link_not_found(client, mock_link_service):
    short_code = "NONEXIST"
    link_data = {"original_url": "https://newexample.com"}
    mock_link_service.update_link.side_effect = HTTPException(
        status_code=404, detail="Link not found or not owned by user"
    )

    response = client.put(f"/links/{short_code}", json=link_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found or not owned by user"

def test_update_link_service_error(client, mock_link_service):
    short_code = "ABC123"
    link_data = {"original_url": "https://newexample.com"}
    mock_link_service.update_link.side_effect = Exception("Service error")

    with pytest.raises(Exception, match="Service error"):
        client.put(f"/links/{short_code}", json=link_data)

def test_delete_link_success(client, mock_link_service):
    short_code = "ABC123"
    mock_link_service.delete_link.return_value = None

    response = client.delete(f"/links/{short_code}")

    assert response.status_code == 204
    assert response.text == ""
    mock_link_service.delete_link.assert_called_once_with(short_code, 1)

def test_delete_link_not_found(client, mock_link_service):
    short_code = "NONEXIST"
    mock_link_service.delete_link.side_effect = HTTPException(
        status_code=404, detail="Link not found or not owned by user"
    )

    response = client.delete(f"/links/{short_code}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found or not owned by user"

def test_delete_link_service_error(client, mock_link_service):
    short_code = "ABC123"
    mock_link_service.delete_link.side_effect = Exception("Service error")

    with pytest.raises(Exception, match="Service error"):
        client.delete(f"/links/{short_code}")

def test_create_link_with_custom_alias_success(client, mock_link_service):
    link_data = {
        "original_url": "https://example.com",
        "custom_alias": "mycustom"
    }
    expected_response = {
        "short_code": "mycustom",
        "original_url": "https://example.com/",
        "created_at": "2026-01-01T12:00:00",
        "owner_id": 1
    }
    mock_link_service.create_short_link.return_value = LinkResponse(**expected_response)

    response = client.post("/links/", json=link_data)

    assert response.status_code == 201
    assert response.json() == expected_response

def test_create_link_with_custom_alias_already_taken(client, mock_link_service):
    link_data = {
        "original_url": "https://example.com",
        "custom_alias": "taken"
    }
    mock_link_service.create_short_link.side_effect = HTTPException(
        status_code=400, detail="Alias already taken"
    )

    response = client.post("/links/", json=link_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Alias already taken"

def test_create_link_with_custom_alias_invalid_characters(client, mock_link_service):
    link_data = {
        "original_url": "https://example.com",
        "custom_alias": "invalid!"
    }
    mock_link_service.create_short_link.side_effect = HTTPException(
        status_code=400, detail="Alias must contain only letters, numbers, underscores and hyphens"
    )

    response = client.post("/links/", json=link_data)

    assert response.status_code == 400
    assert "Alias must contain only letters" in response.json()["detail"]