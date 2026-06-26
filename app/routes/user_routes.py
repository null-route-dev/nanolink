from fastapi import APIRouter, Depends

from services.user_service import UserService, get_user_service
from schemas.user_schemas import CreateUser, LoginUser, UserResponse

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
    user_data: CreateUser,
    service: UserService = Depends(get_user_service)
):
    return await service.register_user(user_data)

@user_router.post("/login", response_model=UserResponse, status_code=200)
async def authenticate_user(
    user_data: LoginUser,
    service: UserService = Depends(get_user_service)
):
    return await service.authenticate_user(user_data)