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
    repo.get_links_by_user_id = AsyncMock()
    repo.update_link_url = AsyncMock()
    repo.delete_link = AsyncMock()
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
        created_at=MagicMock(),
        user_id=user_id
    )
    created_link.created_at.isoformat.return_value = "2026-01-01T12:00:00"
    
    mock_link_repository.create_link.return_value = created_link
    
    result = await link_service.create_short_link(link_data, user_id)
    
    mock_link_repository.get_link_by_short_code.assert_called_once()
    mock_link_repository.create_link.assert_called_once()
    
    assert result.short_code == "ABC123"
    assert result.original_url == original_url
    assert result.created_at == "2026-01-01T12:00:00"
    assert result.owner_id == user_id

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
        created_at=MagicMock(),
        user_id=user_id
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
        created_at=MagicMock(),
        user_id=user_id
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
        created_at=MagicMock(),
        user_id=user_id
    )
    created_link.created_at.isoformat.return_value = "2026-01-01T12:00:00"

    mock_link_repository.create_link.return_value = created_link

    result = await link_service.create_short_link(link_data, user_id)

    assert mock_link_repository.get_link_by_short_code.call_count == 4
    assert result.short_code == "XYZ789"

@pytest.mark.asyncio
async def test_get_user_links_success(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    user_id = 1
    links = [
        Link(short_code="ABC123", original_url="https://example1.com", user_id=user_id),
        Link(short_code="DEF456", original_url="https://example2.com", user_id=user_id)
    ]
    for link in links:
        link.created_at = MagicMock()
        link.created_at.isoformat.return_value = "2026-01-01T12:00:00"

    mock_link_repository.get_links_by_user_id.return_value = links

    result = await link_service.get_user_links(user_id)

    mock_link_repository.get_links_by_user_id.assert_called_once_with(user_id)
    assert len(result) == 2
    assert result[0].short_code == "ABC123"
    assert result[0].owner_id == user_id

@pytest.mark.asyncio
async def test_get_user_links_empty(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    user_id = 1
    mock_link_repository.get_links_by_user_id.return_value = []

    result = await link_service.get_user_links(user_id)

    mock_link_repository.get_links_by_user_id.assert_called_once_with(user_id)
    assert result == []

@pytest.mark.asyncio
async def test_update_link_success(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    short_code = "ABC123"
    new_url = "https://newexample.com"
    user_id = 1

    updated_link = Link(
        short_code=short_code,
        original_url=new_url,
        user_id=user_id
    )
    updated_link.created_at = MagicMock()
    updated_link.created_at.isoformat.return_value = "2026-01-01T12:00:00"

    mock_link_repository.update_link_url.return_value = updated_link

    with patch("app.services.link_service.cache_service.delete", AsyncMock()):
        result = await link_service.update_link(short_code, new_url, user_id)

    mock_link_repository.update_link_url.assert_called_once_with(short_code, new_url, user_id)
    assert result.short_code == short_code
    assert result.original_url == new_url
    assert result.owner_id == user_id

@pytest.mark.asyncio
async def test_update_link_not_found(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    short_code = "NONEXIST"
    new_url = "https://newexample.com"
    user_id = 1

    mock_link_repository.update_link_url.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await link_service.update_link(short_code, new_url, user_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Link not found or not owned by user"
    mock_link_repository.update_link_url.assert_called_once_with(short_code, new_url, user_id)

@pytest.mark.asyncio
async def test_delete_link_success(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    short_code = "ABC123"
    user_id = 1

    mock_link_repository.delete_link.return_value = True

    with patch("app.services.link_service.cache_service.delete", AsyncMock()):
        await link_service.delete_link(short_code, user_id)

    mock_link_repository.delete_link.assert_called_once_with(short_code, user_id)

@pytest.mark.asyncio
async def test_delete_link_not_found(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    short_code = "NONEXIST"
    user_id = 1

    mock_link_repository.delete_link.return_value = False

    with pytest.raises(HTTPException) as exc_info:
        await link_service.delete_link(short_code, user_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Link not found or not owned by user"
    mock_link_repository.delete_link.assert_called_once_with(short_code, user_id)

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
async def test_get_original_url_from_cache(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    short_code = "ABC123"
    expected_url = "https://example.com/test"

    with patch("app.services.link_service.cache_service.get", AsyncMock(return_value=expected_url)):
        result = await link_service.get_original_url(short_code)

    mock_link_repository.get_link_by_short_code.assert_not_called()
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

@pytest.mark.asyncio
async def test_create_short_link_with_custom_alias_success(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    original_url = "https://example.com"
    custom_alias = "mycustom"
    link_data = LinkCreate(original_url=original_url, custom_alias=custom_alias)
    user_id = 1

    mock_link_repository.get_link_by_short_code.return_value = None

    created_link = Link(
        short_code=custom_alias,
        original_url=original_url,
        created_at=MagicMock(),
        user_id=user_id
    )
    created_link.created_at.isoformat.return_value = "2026-01-01T12:00:00"

    mock_link_repository.create_link.return_value = created_link

    result = await link_service.create_short_link(link_data, user_id)

    mock_link_repository.get_link_by_short_code.assert_called_once_with(custom_alias)
    mock_link_repository.create_link.assert_called_once()
    assert result.short_code == custom_alias

@pytest.mark.asyncio
async def test_create_short_link_with_custom_alias_already_taken(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    original_url = "https://example.com"
    custom_alias = "taken"
    link_data = LinkCreate(original_url=original_url, custom_alias=custom_alias)
    user_id = 1

    existing_link = Link(short_code=custom_alias, original_url="https://other.com")
    mock_link_repository.get_link_by_short_code.return_value = existing_link

    with pytest.raises(HTTPException) as exc_info:
        await link_service.create_short_link(link_data, user_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Alias already taken"
    mock_link_repository.get_link_by_short_code.assert_called_once_with(custom_alias)
    mock_link_repository.create_link.assert_not_called()

@pytest.mark.asyncio
async def test_create_short_link_with_custom_alias_invalid_characters(
    link_service: LinkService,
    mock_link_repository: AsyncMock
) -> None:
    original_url = "https://example.com"
    custom_alias = "invalid!"
    link_data = LinkCreate(original_url=original_url, custom_alias=custom_alias)
    user_id = 1

    with pytest.raises(HTTPException) as exc_info:
        await link_service.create_short_link(link_data, user_id)

    assert exc_info.value.status_code == 400