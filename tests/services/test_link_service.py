import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.services.link_service import LinkService
from app.crud.link_crud import LinkRepository
from app.models.models import Link
from app.schemas.link_schemas import LinkCreate

@pytest.fixture
def mock_link_repository() -> AsyncMock:
    repo = AsyncMock(spec=LinkRepository)
    repo.get_link_by_short_code = AsyncMock()
    repo.create_link = AsyncMock()
    return repo

@pytest.fixture
def link_service(mock_link_repository: AsyncMock) -> LinkService:
    return LinkService(mock_link_repository)

@pytest.mark.asyncio
async def test_create_short_link_success(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    original_url = "https://example.com/very/long/url"
    link_data = LinkCreate(original_url=original_url)
    user_id = 1
    
    mock_link_repository.get_link_by_short_code.return_value = None
    
    created_link = Link(
        short_code="ABC123",
        original_url=original_url,
        created_at=MagicMock()
    )
    created_link.created_at.isoformat.return_value = "2026-01-01T12:00:00"
    
    mock_link_repository.create_link.return_value = created_link
    
    result = await link_service.create_short_link(link_data, user_id)
    
    mock_link_repository.get_link_by_short_code.assert_called_once()
    mock_link_repository.create_link.assert_called_once()
    
    assert result.short_code == "ABC123"
    assert result.original_url == original_url
    assert result.created_at == "2026-01-01T12:00:00"
    assert mock_link_repository.create_link.call_args[0][0].user_id == user_id

@pytest.mark.asyncio
async def test_create_short_link_with_collision(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    original_url = "https://example.com/test"
    link_data = LinkCreate(original_url=original_url)
    user_id = 1
    
    existing_link = Link(short_code="ABC123", original_url="https://example.com/other")
    
    mock_link_repository.get_link_by_short_code.side_effect = [
        existing_link,
        None
    ]
    
    created_link = Link(
        short_code="DEF456",
        original_url=original_url,
        created_at=MagicMock()
    )
    created_link.created_at.isoformat.return_value = "2026-01-01T12:00:00"
    
    mock_link_repository.create_link.return_value = created_link
    
    result = await link_service.create_short_link(link_data, user_id)
    
    assert mock_link_repository.get_link_by_short_code.call_count == 2
    mock_link_repository.create_link.assert_called_once()
    assert result.short_code == "DEF456"

@pytest.mark.asyncio
async def test_create_short_link_repository_error(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    original_url = "https://example.com/test"
    link_data = LinkCreate(original_url=original_url)
    user_id = 1
    
    mock_link_repository.get_link_by_short_code.return_value = None
    mock_link_repository.create_link.side_effect = Exception("Database error")
    
    with pytest.raises(Exception) as exc_info:
        await link_service.create_short_link(link_data, user_id)
    
    assert "Database error" in str(exc_info.value)
    mock_link_repository.get_link_by_short_code.assert_called_once()
    mock_link_repository.create_link.assert_called_once()

@pytest.mark.asyncio
async def test_get_original_url_success(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    short_code = "ABC123"
    expected_url = "https://example.com/test"
    
    link = Link(short_code=short_code, original_url=expected_url)
    mock_link_repository.get_link_by_short_code.return_value = link
    
    with patch("app.services.link_service.cache_service.get", AsyncMock(return_value=None)):
        with patch("app.services.link_service.cache_service.set", AsyncMock()):
            result = await link_service.get_original_url(short_code)
    
    mock_link_repository.get_link_by_short_code.assert_called_once_with(short_code)
    assert result == expected_url

@pytest.mark.asyncio
async def test_get_original_url_not_found(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    short_code = "NONEXIST"
    mock_link_repository.get_link_by_short_code.return_value = None
    
    with patch("app.services.link_service.cache_service.get", AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc_info:
            await link_service.get_original_url(short_code)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Link not found"
    mock_link_repository.get_link_by_short_code.assert_called_once_with(short_code)

@pytest.mark.asyncio
async def test_get_original_url_repository_error(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    short_code = "ABC123"
    mock_link_repository.get_link_by_short_code.side_effect = Exception("Connection error")
    
    with patch("app.services.link_service.cache_service.get", AsyncMock(return_value=None)):
        with pytest.raises(Exception) as exc_info:
            await link_service.get_original_url(short_code)
    
    assert "Connection error" in str(exc_info.value)
    mock_link_repository.get_link_by_short_code.assert_called_once_with(short_code)

@pytest.mark.asyncio
async def test_create_short_link_with_special_characters_in_url(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    original_url = "https://example.com/path?param=value&foo=bar#anchor"
    link_data = LinkCreate(original_url=original_url)
    user_id = 1
    
    mock_link_repository.get_link_by_short_code.return_value = None
    
    created_link = Link(
        short_code="ABC123",
        original_url=original_url,
        created_at=MagicMock()
    )
    created_link.created_at.isoformat.return_value = "2026-01-01T12:00:00"
    
    mock_link_repository.create_link.return_value = created_link
    
    result = await link_service.create_short_link(link_data, user_id)
    
    assert result.original_url == original_url
    mock_link_repository.create_link.assert_called_once()

@pytest.mark.asyncio
async def test_create_short_link_with_multiple_collisions(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    original_url = "https://example.com/test"
    link_data = LinkCreate(original_url=original_url)
    user_id = 1
    
    existing_links = [
        Link(short_code=f"ABC{i}", original_url="https://example.com/other")
        for i in range(3)
    ]
    
    side_effects = existing_links + [None]
    mock_link_repository.get_link_by_short_code.side_effect = side_effects
    
    created_link = Link(
        short_code="XYZ789",
        original_url=original_url,
        created_at=MagicMock()
    )
    created_link.created_at.isoformat.return_value = "2026-01-01T12:00:00"
    
    mock_link_repository.create_link.return_value = created_link
    
    result = await link_service.create_short_link(link_data, user_id)
    
    assert mock_link_repository.get_link_by_short_code.call_count == 4
    assert result.short_code == "XYZ789"

@pytest.mark.asyncio
async def test_get_original_url_with_unicode_characters(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    short_code = "ABC123"
    expected_url = "https://example.com/hello_world"

    link = Link(short_code=short_code, original_url=expected_url)
    mock_link_repository.get_link_by_short_code.return_value = link

    with patch("app.services.link_service.cache_service.get", AsyncMock(return_value=None)):
        result = await link_service.get_original_url(short_code)

    assert result == expected_url