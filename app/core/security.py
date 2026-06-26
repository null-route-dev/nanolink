from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from services.user_service import UserService, get_user_service
from schemas.user_schemas import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login",
    auto_error=False
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_service.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_user_optional(
    token: str | None = Depends(optional_oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> UserResponse | None:
    if token is None:
        return None
    
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    user = await user_service.get_user_by_email(email)
    return user