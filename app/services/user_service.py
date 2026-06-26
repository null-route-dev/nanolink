from fastapi import Depends, HTTPException, status
import bcrypt

from crud.user_crud import UserRepository, get_user_repository
from models.models import User
from schemas.user_schemas import CreateUser, LoginUser, UserResponse, Token
from core.jwt_utils import create_access_token

async def get_user_service(
    repo: UserRepository = Depends(get_user_repository)
) -> "UserService":
    return UserService(repo)

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def _hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        plain_bytes = plain_password.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_password.encode('utf-8'))
    
    async def register_user(self, user_data: CreateUser) -> UserResponse:
        existing = await self.repo.get_user_by_email(user_data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        hashed_password = self._hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )
        created = await self.repo.create_user(new_user)
        return UserResponse(
            id=created.id,
            username=created.username,
            email=created.email,
            created_at=created.created_at.isoformat() if created.created_at else None,
            updated_at=created.updated_at.isoformat() if created.updated_at else None
        )

    async def authenticate_user(self, login_data: LoginUser) -> Token:
        user = await self.repo.get_user_by_email(login_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not self._verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        access_token = create_access_token(data={"sub": user.email})
        return Token(access_token=access_token)

    async def get_user_by_email(self, email: str) -> UserResponse | None:
        user = await self.repo.get_user_by_email(email)
        if not user:
            return None
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None
        )