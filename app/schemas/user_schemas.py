from pydantic import BaseModel

class CreateUser(BaseModel):
    username: str
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str
    updated_at: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"