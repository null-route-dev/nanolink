from fastapi import APIRouter, Depends

from services.user_service import UserService, get_user_service
from schemas.user_schemas import CreateUser, LoginUser, UserResponse, ChangePassword, Token
from core.security import get_current_user

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
    user_data: CreateUser,
    service: UserService = Depends(get_user_service)
):
    return await service.register_user(user_data)

@user_router.post("/login", response_model=Token, status_code=200)
async def authenticate_user(
    user_data: LoginUser,
    service: UserService = Depends(get_user_service)
):
    return await service.authenticate_user(user_data)

@user_router.post("/change-password", status_code=204)
async def change_password(
    data: ChangePassword,
    service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(get_current_user)
):
    await service.change_password(current_user.id, data.old_password, data.new_password)