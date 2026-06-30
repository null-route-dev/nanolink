import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_crud import UserRepository
from app.models.models import User

@pytest.fixture
def mock_db_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def user_repository(mock_db_session: AsyncMock) -> UserRepository:
    return UserRepository(mock_db_session)

@pytest.mark.asyncio
async def test_create_user(
    user_repository: UserRepository,
    mock_db_session: AsyncMock
) -> None:
    test_user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password123"
    )

    mock_db_session.refresh.return_value = None

    result = await user_repository.create_user(test_user)

    mock_db_session.add.assert_called_once_with(test_user)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(test_user)
    assert result == test_user

@pytest.mark.asyncio
async def test_get_user_by_email_found(
    user_repository: UserRepository,
    mock_db_session: AsyncMock
) -> None:
    expected_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password123"
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_db_session.execute.return_value = mock_result

    result = await user_repository.get_user_by_email("test@example.com")

    mock_db_session.execute.assert_called_once()
    assert result == expected_user
    assert result.email == "test@example.com"
    assert result.username == "testuser"

@pytest.mark.asyncio
async def test_get_user_by_email_not_found(
    user_repository: UserRepository,
    mock_db_session: AsyncMock
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    result = await user_repository.get_user_by_email("nonexistent@example.com")

    mock_db_session.execute.assert_called_once()
    assert result is None

@pytest.mark.asyncio
async def test_get_user_by_id_found(
    user_repository: UserRepository,
    mock_db_session: AsyncMock
) -> None:
    expected_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_db_session.execute.return_value = mock_result

    result = await user_repository.get_user_by_id(1)

    mock_db_session.execute.assert_called_once()
    assert result == expected_user
    assert result.id == 1
    assert result.username == "testuser"
    assert result.email == "test@example.com"

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    user_repository: UserRepository,
    mock_db_session: AsyncMock
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    result = await user_repository.get_user_by_id(999)

    mock_db_session.execute.assert_called_once()
    assert result is None

@pytest.mark.asyncio
async def test_update_password_success(
    user_repository: UserRepository,
    mock_db_session: AsyncMock
) -> None:
    user_id = 1
    new_hash = "new_hashed_password"

    mock_db_session.execute.return_value = None

    await user_repository.update_password(user_id, new_hash)

    mock_db_session.execute.assert_called_once()
    mock_db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_password_repository_error(
    user_repository: UserRepository,
    mock_db_session: AsyncMock
) -> None:
    user_id = 1
    new_hash = "new_hashed_password"

    mock_db_session.execute.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc_info:
        await user_repository.update_password(user_id, new_hash)

    assert "Database error" in str(exc_info.value)
    mock_db_session.execute.assert_called_once()
    mock_db_session.commit.assert_not_called()