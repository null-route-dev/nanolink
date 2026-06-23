import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.click_log_crud import ClickLogRepository

@pytest.fixture
def mock_db_session() -> AsyncMock:
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    return mock_session

@pytest.fixture
def click_log_repository(mock_db_session: AsyncMock) -> ClickLogRepository:
    return ClickLogRepository(mock_db_session)

@pytest.mark.asyncio
async def test_create_click_log_by_short_code_success(
    click_log_repository: ClickLogRepository,
    mock_db_session: AsyncMock
) -> None:
    short_code = "abc123"
    ip_address = "192.168.1.1"
    user_agent = "Mozilla/5.0"
    
    mock_result = MagicMock()
    mock_result.inserted_primary_key = [1]
    mock_db_session.execute.return_value = mock_result
    
    result = await click_log_repository.create_click_log_by_short_code(
        short_code, ip_address, user_agent
    )
    
    mock_db_session.execute.assert_awaited_once()
    mock_db_session.commit.assert_awaited_once()
    assert result == mock_result
    assert result.inserted_primary_key == [1]

@pytest.mark.asyncio
async def test_create_click_log_by_short_code_commit_error(
    click_log_repository: ClickLogRepository,
    mock_db_session: AsyncMock
) -> None:
    short_code = "abc123"
    ip_address = "192.168.1.1"
    user_agent = "Mozilla/5.0"
    
    mock_result = MagicMock()
    mock_db_session.execute.return_value = mock_result
    
    mock_db_session.commit.side_effect = Exception("Database connection lost")
    
    with pytest.raises(Exception) as exc_info:
        await click_log_repository.create_click_log_by_short_code(
            short_code, ip_address, user_agent
        )
    
    assert "Database connection lost" in str(exc_info.value)
    mock_db_session.execute.assert_awaited_once()
    mock_db_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_click_log_stats_by_short_code_found(
    click_log_repository: ClickLogRepository,
    mock_db_session: AsyncMock
) -> None:
    short_code = "abc123"
    
    expected_data = {
        "short_code": "abc123",
        "original_url": "https://example.com",
        "created_at": "2024-01-01 12:00:00",
        "total_clicks": 42
    }
    
    mock_mapping = MagicMock()
    mock_mapping.first.return_value = expected_data
    
    mock_result = MagicMock()
    mock_result.mappings.return_value = mock_mapping
    mock_db_session.execute.return_value = mock_result
    
    result = await click_log_repository.get_click_log_stats_by_short_code(short_code)
    
    mock_db_session.execute.assert_awaited_once()
    assert result == expected_data
    assert result["short_code"] == "abc123"
    assert result["total_clicks"] == 42

@pytest.mark.asyncio
async def test_get_click_log_stats_by_short_code_not_found(
    click_log_repository: ClickLogRepository,
    mock_db_session: AsyncMock
) -> None:
    short_code = "nonexistent"
    
    mock_mapping = MagicMock()
    mock_mapping.first.return_value = None
    
    mock_result = MagicMock()
    mock_result.mappings.return_value = mock_mapping
    mock_db_session.execute.return_value = mock_result
    
    result = await click_log_repository.get_click_log_stats_by_short_code(short_code)
    
    mock_db_session.execute.assert_awaited_once()
    assert result is None

@pytest.mark.asyncio
async def test_get_click_log_stats_by_short_code_zero_clicks(
    click_log_repository: ClickLogRepository,
    mock_db_session: AsyncMock
) -> None:
    short_code = "abc123"
    
    expected_data = {
        "short_code": "abc123",
        "original_url": "https://example.com",
        "created_at": "2024-01-01 12:00:00",
        "total_clicks": 0
    }
    
    mock_mapping = MagicMock()
    mock_mapping.first.return_value = expected_data
    
    mock_result = MagicMock()
    mock_result.mappings.return_value = mock_mapping
    mock_db_session.execute.return_value = mock_result
    
    result = await click_log_repository.get_click_log_stats_by_short_code(short_code)
    
    mock_db_session.execute.assert_awaited_once()
    assert result == expected_data
    assert result["total_clicks"] == 0