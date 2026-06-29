import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.link_crud import LinkRepository
from app.models.models import Link

@pytest.fixture
def mock_db_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def link_repository(mock_db_session: AsyncMock) -> LinkRepository:
    return LinkRepository(mock_db_session)

@pytest.mark.asyncio
async def test_create_link(
    link_repository: LinkRepository,
    mock_db_session: AsyncMock
) -> None:
    test_link = Link(
        original_url="https://example.com",
        short_code="abc123"
    )

    mock_db_session.refresh.return_value = None
    
    result = await link_repository.create_link(test_link)
    
    mock_db_session.add.assert_called_once_with(test_link)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(test_link)
    assert result == test_link

@pytest.mark.asyncio
async def test_get_links_by_user_id_success(
    link_repository: LinkRepository,
    mock_db_session: AsyncMock
) -> None:
    user_id = 1
    expected_links = [
        Link(short_code="abc123", original_url="https://example1.com", user_id=user_id),
        Link(short_code="def456", original_url="https://example2.com", user_id=user_id)
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = expected_links
    mock_db_session.execute.return_value = mock_result

    result = await link_repository.get_links_by_user_id(user_id)

    mock_db_session.execute.assert_called_once()
    assert result == expected_links
    assert len(result) == 2

@pytest.mark.asyncio
async def test_get_links_by_user_id_empty(
    link_repository: LinkRepository,
    mock_db_session: AsyncMock
) -> None:
    user_id = 1

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db_session.execute.return_value = mock_result

    result = await link_repository.get_links_by_user_id(user_id)

    mock_db_session.execute.assert_called_once()
    assert result == []

@pytest.mark.asyncio
async def test_update_link_url_success(
    link_repository: LinkRepository,
    mock_db_session: AsyncMock
) -> None:
    short_code = "abc123"
    new_url = "https://newexample.com"
    user_id = 1

    updated_link = Link(
        short_code=short_code,
        original_url=new_url,
        user_id=user_id
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = updated_link
    mock_db_session.execute.return_value = mock_result
    mock_db_session.refresh = AsyncMock()

    result = await link_repository.update_link_url(short_code, new_url, user_id)

    mock_db_session.execute.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(updated_link)
    assert result == updated_link
    assert result.original_url == new_url

@pytest.mark.asyncio
async def test_update_link_url_not_found(
    link_repository: LinkRepository,
    mock_db_session: AsyncMock
) -> None:
    short_code = "nonexistent"
    new_url = "https://newexample.com"
    user_id = 1

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    result = await link_repository.update_link_url(short_code, new_url, user_id)

    mock_db_session.execute.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_not_called()
    assert result is None

@pytest.mark.asyncio
async def test_update_link_url_wrong_user(
    link_repository: LinkRepository,
    mock_db_session: AsyncMock
) -> None:
    short_code = "abc123"
    new_url = "https://newexample.com"
    user_id = 2

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    result = await link_repository.update_link_url(short_code, new_url, user_id)

    mock_db_session.execute.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_not_called()
    assert result is None

@pytest.mark.asyncio
async def test_delete_link_success(
    link_repository: LinkRepository,
    mock_db_session: AsyncMock
) -> None:
    short_code = "abc123"
    user_id = 1

    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_db_session.execute.return_value = mock_result

    result = await link_repository.delete_link(short_code, user_id)

    mock_db_session.execute.assert_called_once()
    mock_db_session.commit.assert_called_once()
    assert result is True

@pytest.mark.asyncio
async def test_delete_link_not_found(
    link_repository: LinkRepository,
    mock_db_session: AsyncMock
) -> None:
    short_code = "nonexistent"
    user_id = 1

    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_db_session.execute.return_value = mock_result

    result = await link_repository.delete_link(short_code, user_id)

    mock_db_session.execute.assert_called_once()
    mock_db_session.commit.assert_called_once()
    assert result is False

@pytest.mark.asyncio
async def test_get_link_by_short_code_found(
    link_repository: LinkRepository,
    mock_db_session: AsyncMock
) -> None:
    expected_link = Link(
        original_url="https://example.com",
        short_code="abc123"
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_link
    mock_db_session.execute.return_value = mock_result
    
    result = await link_repository.get_link_by_short_code("abc123")
    
    mock_db_session.execute.assert_called_once()
    assert result == expected_link
    assert result.short_code == "abc123"

@pytest.mark.asyncio
async def test_get_link_by_short_code_not_found(
    link_repository: LinkRepository,
    mock_db_session: AsyncMock
) -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result
    
    result = await link_repository.get_link_by_short_code("nonexistent")
    
    mock_db_session.execute.assert_called_once()
    assert result is None