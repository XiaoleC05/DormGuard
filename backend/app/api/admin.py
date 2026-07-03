"""管理配置 API（读写 .env）。"""
import logging
import subprocess
from typing import Dict, Set

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import get_current_user
from app.env_manager import mask_env_values, read_env_values, write_env_values

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(get_current_user)])

QQ_RELATED_KEYS: Set[str] = {
    "QQ_BOT_ENABLED",
    "QQ_BOT_API_URL",
    "QQ_BOT_GROUP_ID",
}


class SettingsResponse(BaseModel):
    settings: Dict[str, str]
    restart_required: bool = False


class SettingsUpdateRequest(BaseModel):
    settings: Dict[str, str]


def _restart_services(changed_keys: Set[str]) -> bool:
    services = ["dorm-backend"]
    if changed_keys & QQ_RELATED_KEYS:
        services.append("dorm-nonebot")
    try:
        for service in services:
            subprocess.run(
                ["systemctl", "restart", service],
                check=True,
                timeout=30,
            )
            logger.info("已重启服务: %s", service)
        return True
    except Exception as exc:
        logger.error("重启服务失败: %s", exc)
        return False


@router.get("/settings", response_model=SettingsResponse, summary="获取可管理配置")
async def get_settings():
    return SettingsResponse(settings=mask_env_values(read_env_values()))


@router.put("/settings", response_model=SettingsResponse, summary="更新可管理配置")
async def update_settings(body: SettingsUpdateRequest):
    current = read_env_values()
    merged = {**current, **body.settings}
    changed_keys: Set[str] = set()
    for key, value in list(merged.items()):
        if value == "******":
            merged[key] = current.get(key, "")
        elif merged.get(key) != current.get(key):
            changed_keys.add(key)
    write_env_values(merged)
    restarted = _restart_services(changed_keys) if changed_keys else True
    return SettingsResponse(
        settings=mask_env_values(read_env_values()),
        restart_required=not restarted,
    )
