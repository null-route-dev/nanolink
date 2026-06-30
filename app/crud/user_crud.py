from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import User
from core.database import get_db

async def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> "UserRepository":
    return UserRepository(db)

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, id: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == id)
        )
        return result.scalar_one_or_none()

    async def update_password(self, user_id: int, new_hash: str) -> None:
        await self.db.execute(
            update(User).where(User.id == user_id).values(password_hash=new_hash)
        )
        await self.db.commit()