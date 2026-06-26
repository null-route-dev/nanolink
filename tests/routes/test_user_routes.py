import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from fastapi import HTTPException

from main import app
from services.user_service import get_user_service
from schemas.user_schemas import CreateUser, LoginUser, UserResponse, Token

@pytest.fixture
def mock_user_service():
    mock = AsyncMock()
    mock.register_user = AsyncMock()
    mock.authenticate_user = AsyncMock()
    return mock

@pytest.fixture
def client(mock_user_service):
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_register_user_success(client, mock_user_service):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret123"
    }
    expected_response = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "created_at": "2024-01-01T12:00:00",
        "updated_at": "2024-01-01T12:00:00"
    }
    mock_user_service.register_user.return_value = UserResponse(**expected_response)

    response = client.post("/users/register", json=user_data)

    assert response.status_code == 201
    assert response.json() == expected_response
    mock_user_service.register_user.assert_called_once_with(CreateUser(**user_data))

def test_register_user_email_already_exists(client, mock_user_service):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret123"
    }
    mock_user_service.register_user.side_effect = HTTPException(
        status_code=400, detail="Email already registered"
    )

    response = client.post("/users/register", json=user_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
    mock_user_service.register_user.assert_called_once_with(CreateUser(**user_data))

def test_login_user_success(client, mock_user_service):
    login_data = {
        "email": "test@example.com",
        "password": "secret123"
    }
    expected_token = {
        "access_token": "jwt_token",
        "token_type": "bearer"
    }
    mock_user_service.authenticate_user.return_value = Token(**expected_token)

    response = client.post("/users/login", json=login_data)

    assert response.status_code == 200
    assert response.json() == expected_token
    mock_user_service.authenticate_user.assert_called_once_with(LoginUser(**login_data))

def test_login_user_invalid_credentials(client, mock_user_service):
    login_data = {
        "email": "wrong@example.com",
        "password": "wrongpass"
    }
    mock_user_service.authenticate_user.side_effect = HTTPException(
        status_code=401, detail="Invalid email or password"
    )

    response = client.post("/users/login", json=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
    mock_user_service.authenticate_user.assert_called_once_with(LoginUser(**login_data))