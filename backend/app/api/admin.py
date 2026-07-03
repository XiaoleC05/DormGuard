"""管理配置 API（读写 .env）。"""
from typing import Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import get_current_user
from app.env_manager import mask_env_values, read_env_values, write_env_values

router = APIRouter(dependencies=[Depends(get_current_user)])


class SettingsResponse(BaseModel):
    settings: Dict[str, str]
    restart_required: bool = True


class SettingsUpdateRequest(BaseModel):
    settings: Dict[str, str]


@router.get("/settings", response_model=SettingsResponse, summary="获取可管理配置")
async def get_settings():
    return SettingsResponse(settings=mask_env_values(read_env_values()))


@router.put("/settings", response_model=SettingsResponse, summary="更新可管理配置")
async def update_settings(body: SettingsUpdateRequest):
    current = read_env_values()
    merged = {**current, **body.settings}
    # 敏感字段传 ****** 表示不修改
    for key, value in list(merged.items()):
        if value == "******":
            merged[key] = current.get(key, "")
    write_env_values(merged)
    return SettingsResponse(
        settings=mask_env_values(read_env_values()),
        restart_required=True,
    )
