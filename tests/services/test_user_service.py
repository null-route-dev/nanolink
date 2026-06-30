import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
import bcrypt

from app.services.user_service import UserService
from app.crud.user_crud import UserRepository
from app.models.models import User
from app.schemas.user_schemas import CreateUser, LoginUser

@pytest.fixture
def mock_user_repository() -> AsyncMock:
    repo = AsyncMock(spec=UserRepository)
    repo.get_user_by_email = AsyncMock()
    repo.create_user = AsyncMock()
    return repo

@pytest.fixture
def user_service(mock_user_repository: AsyncMock) -> UserService:
    return UserService(mock_user_repository)

@pytest.mark.asyncio
async def test_register_user_success(
    user_service: UserService,
    mock_user_repository: AsyncMock
) -> None:
    user_data = CreateUser(
        username="testuser",
        email="test@example.com",
        password="secret123"
    )

    mock_user_repository.get_user_by_email.return_value = None

    created_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    created_user.created_at = MagicMock()
    created_user.created_at.isoformat.return_value = "2026-01-01T12:00:00"
    created_user.updated_at = MagicMock()
    created_user.updated_at.isoformat.return_value = "2026-01-01T12:00:00"

    mock_user_repository.create_user.return_value = created_user

    result = await user_service.register_user(user_data)

    mock_user_repository.get_user_by_email.assert_called_once_with("test@example.com")
    mock_user_repository.create_user.assert_called_once()

    assert result.id == 1
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    assert result.created_at == "2026-01-01T12:00:00"
    assert result.updated_at == "2026-01-01T12:00:00"

@pytest.mark.asyncio
async def test_register_user_email_already_exists(
    user_service: UserService,
    mock_user_repository: AsyncMock
) -> None:
    user_data = CreateUser(
        username="testuser",
        email="test@example.com",
        password="secret123"
    )

    existing_user = User(email="test@example.com")
    mock_user_repository.get_user_by_email.return_value = existing_user

    with pytest.raises(HTTPException) as exc_info:
        await user_service.register_user(user_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered"
    mock_user_repository.get_user_by_email.assert_called_once_with("test@example.com")
    mock_user_repository.create_user.assert_not_called()

@pytest.mark.asyncio
async def test_authenticate_user_success(
    user_service: UserService,
    mock_user_repository: AsyncMock
) -> None:
    login_data = LoginUser(email="test@example.com", password="secret123")
    password = "secret123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash=hashed
    )
    mock_user_repository.get_user_by_email.return_value = user

    result = await user_service.authenticate_user(login_data)

    mock_user_repository.get_user_by_email.assert_called_once_with("test@example.com")
    assert result.access_token is not None
    assert result.token_type == "bearer"

@pytest.mark.asyncio
async def test_authenticate_user_invalid_email(
    user_service: UserService,
    mock_user_repository: AsyncMock
) -> None:
    login_data = LoginUser(email="wrong@example.com", password="secret123")

    mock_user_repository.get_user_by_email.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await user_service.authenticate_user(login_data)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid email or password"
    mock_user_repository.get_user_by_email.assert_called_once_with("wrong@example.com")

@pytest.mark.asyncio
async def test_authenticate_user_invalid_password(
    user_service: UserService,
    mock_user_repository: AsyncMock
) -> None:
    login_data = LoginUser(email="test@example.com", password="wrongpass")
    password = "secret123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash=hashed
    )
    mock_user_repository.get_user_by_email.return_value = user

    with pytest.raises(HTTPException) as exc_info:
        await user_service.authenticate_user(login_data)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid email or password"
    mock_user_repository.get_user_by_email.assert_called_once_with("test@example.com")

@pytest.mark.asyncio
async def test_get_user_by_email_found(
    user_service: UserService,
    mock_user_repository: AsyncMock
) -> None:
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed"
    )
    user.created_at = MagicMock()
    user.created_at.isoformat.return_value = "2026-01-01T12:00:00"
    user.updated_at = MagicMock()
    user.updated_at.isoformat.return_value = "2026-01-01T12:00:00"
    mock_user_repository.get_user_by_email.return_value = user

    result = await user_service.get_user_by_email("test@example.com")

    mock_user_repository.get_user_by_email.assert_called_once_with("test@example.com")
    assert result.id == 1
    assert result.username == "testuser"
    assert result.email == "test@example.com"

@pytest.mark.asyncio
async def test_get_user_by_email_not_found(
    user_service: UserService,
    mock_user_repository: AsyncMock
) -> None:
    mock_user_repository.get_user_by_email.return_value = None

    result = await user_service.get_user_by_email("notfound@example.com")

    mock_user_repository.get_user_by_email.assert_called_once_with("notfound@example.com")
    assert result is None

@pytest.mark.asyncio
async def test_change_password_success(
    user_service: UserService,
    mock_user_repository: AsyncMock
) -> None:
    user_id = 1
    old_password = "oldpass123"
    new_password = "newpass456"

    user = User(id=user_id, password_hash="hashed_old")
    mock_user_repository.get_user_by_id.return_value = user

    with patch.object(user_service, "_verify_password") as mock_verify:
        mock_verify.return_value = True
        with patch.object(user_service, "_hash_password") as mock_hash:
            mock_hash.return_value = "hashed_new"
            await user_service.change_password(user_id, old_password, new_password)

    mock_user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_verify.assert_called_once_with(old_password, "hashed_old")
    mock_hash.assert_called_once_with(new_password)
    mock_user_repository.update_password.assert_called_once_with(user_id, "hashed_new")

@pytest.mark.asyncio
async def test_change_password_user_not_found(
    user_service: UserService,
    mock_user_repository: AsyncMock
) -> None:
    user_id = 999
    old_password = "oldpass123"
    new_password = "newpass456"

    mock_user_repository.get_user_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await user_service.change_password(user_id, old_password, new_password)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
    mock_user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_user_repository.update_password.assert_not_called()

@pytest.mark.asyncio
async def test_change_password_invalid_old_password(
    user_service: UserService,
    mock_user_repository: AsyncMock
) -> None:
    user_id = 1
    old_password = "wrongpass"
    new_password = "newpass456"

    user = User(id=user_id, password_hash="hashed_old")
    mock_user_repository.get_user_by_id.return_value = user

    with patch.object(user_service, "_verify_password") as mock_verify:
        mock_verify.return_value = False
        with pytest.raises(HTTPException) as exc_info:
            await user_service.change_password(user_id, old_password, new_password)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid old password"
    mock_user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_verify.assert_called_once_with(old_password, "hashed_old")
    mock_user_repository.update_password.assert_not_called()

@pytest.mark.asyncio
async def test_change_password_repository_error(
    user_service: UserService,
    mock_user_repository: AsyncMock
) -> None:
    user_id = 1
    old_password = "oldpass123"
    new_password = "newpass456"

    user = User(id=user_id, password_hash="hashed_old")
    mock_user_repository.get_user_by_id.return_value = user
    mock_user_repository.update_password.side_effect = Exception("Database error")

    with patch.object(user_service, "_verify_password") as mock_verify:
        mock_verify.return_value = True
        with patch.object(user_service, "_hash_password") as mock_hash:
            mock_hash.return_value = "hashed_new"
            with pytest.raises(Exception) as exc_info:
                await user_service.change_password(user_id, old_password, new_password)

    assert "Database error" in str(exc_info.value)
    mock_user_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_verify.assert_called_once_with(old_password, "hashed_old")
    mock_hash.assert_called_once_with(new_password)
    mock_user_repository.update_password.assert_called_once_with(user_id, "hashed_new")