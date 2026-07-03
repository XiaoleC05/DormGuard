"""登录接口（唯一用户 root，无注册/改密）。"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.auth import create_access_token, verify_password

router = APIRouter()


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


@router.post("/login", response_model=LoginResponse, summary="管理员登录")
async def login(body: LoginRequest):
    if not verify_password(body.username, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    return LoginResponse(
        access_token=create_access_token(body.username),
        username=body.username,
    )
