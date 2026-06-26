import pytest
from unittest.mock import AsyncMock
from datetime import datetime
from fastapi import HTTPException

from app.services.click_log_service import ClickLogService
from app.crud.click_log_crud import ClickLogRepository

@pytest.fixture
def mock_click_log_repository() -> AsyncMock:
    repo = AsyncMock(spec=ClickLogRepository)
    repo.get_click_log_stats_by_short_code = AsyncMock()
    repo.create_click_log_by_short_code = AsyncMock()
    return repo

@pytest.fixture
def click_log_service(mock_click_log_repository: AsyncMock) -> ClickLogService:
    return ClickLogService(mock_click_log_repository)

@pytest.mark.asyncio
async def test_get_log_stats_success(
    click_log_service: ClickLogService,
    mock_click_log_repository: AsyncMock
) -> None:
    short_code = "ABC123"
    user_id = 1
    created_at = datetime(2026, 6, 23, 17, 0, 0)
    
    stats_data = {
        "short_code": "ABC123",
        "original_url": "https://example.com",
        "created_at": created_at,
        "total_clicks": 42
    }
    
    mock_click_log_repository.get_click_log_stats_by_short_code.return_value = stats_data
    
    result = await click_log_service.get_log_stats(short_code, user_id)
    
    mock_click_log_repository.get_click_log_stats_by_short_code.assert_called_once_with(short_code, user_id)
    
    assert hasattr(result, "short_code")
    assert hasattr(result, "original_url")
    assert hasattr(result, "created_at")
    assert hasattr(result, "total_clicks")
    assert result.short_code == "ABC123"
    assert result.original_url == "https://example.com"
    assert result.created_at == "2026-06-23 17:00:00"
    assert result.total_clicks == 42

@pytest.mark.asyncio
async def test_get_log_stats_link_not_found(
    click_log_service: ClickLogService,
    mock_click_log_repository: AsyncMock
) -> None:
    short_code = "NONEXIST"
    user_id = 1
    
    mock_click_log_repository.get_click_log_stats_by_short_code.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await click_log_service.get_log_stats(short_code, user_id)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Link not found"
    mock_click_log_repository.get_click_log_stats_by_short_code.assert_called_once_with(short_code, user_id)

@pytest.mark.asyncio
async def test_get_log_stats_repository_error(
    click_log_service: ClickLogService,
    mock_click_log_repository: AsyncMock
) -> None:
    short_code = "ABC123"
    user_id = 1
    
    mock_click_log_repository.get_click_log_stats_by_short_code.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info:
        await click_log_service.get_log_stats(short_code, user_id)
    
    assert "Database error" in str(exc_info.value)
    mock_click_log_repository.get_click_log_stats_by_short_code.assert_called_once_with(short_code, user_id)

@pytest.mark.asyncio
async def test_create_click_log_success(
    click_log_service: ClickLogService,
    mock_click_log_repository: AsyncMock
) -> None:
    short_code = "ABC123"
    ip = "192.168.1.1"
    user_agent = "Mozilla/5.0"
    
    mock_click_log_repository.create_click_log_by_short_code.return_value = None
    
    result = await click_log_service.create_click_log(short_code, ip, user_agent)
    
    mock_click_log_repository.create_click_log_by_short_code.assert_called_once_with(
        short_code, ip, user_agent
    )
    assert result is None

@pytest.mark.asyncio
async def test_create_click_log_repository_error(
    click_log_service: ClickLogService,
    mock_click_log_repository: AsyncMock
) -> None:
    short_code = "ABC123"
    ip = "192.168.1.1"
    user_agent = "Mozilla/5.0"
    
    mock_click_log_repository.create_click_log_by_short_code.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info:
        await click_log_service.create_click_log(short_code, ip, user_agent)
    
    assert "Database error" in str(exc_info.value)
    mock_click_log_repository.create_click_log_by_short_code.assert_called_once_with(
        short_code, ip, user_agent
    )