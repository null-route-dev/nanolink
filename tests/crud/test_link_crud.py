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