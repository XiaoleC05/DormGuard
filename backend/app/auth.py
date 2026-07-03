"""单用户鉴权（root），无注册、无改密。"""
import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

_bearer = HTTPBearer(auto_error=False)

# 可配置的 .env 键（供管理页读写）
MANAGEABLE_ENV_KEYS = [
    "CRAWLER_DORM_NUMBER",
    "CRAWLER_ROOM_ID",
    "CRAWLER_OPENID",
    "CRAWLER_JSESSIONID",
    "CRAWLER_TOKEN",
    "SCHEDULER_INTERVAL_HOURS",
    "ALERT_COOLDOWN_HOURS",
    "QQ_ALERT_PAUSE_UNTIL",
    "EMAIL_ENABLED",
    "EMAIL_SMTP_HOST",
    "EMAIL_SMTP_PORT",
    "EMAIL_SMTP_USER",
    "EMAIL_SMTP_PASSWORD",
    "EMAIL_FROM",
    "EMAIL_TO",
    "QQ_BOT_ENABLED",
    "QQ_BOT_API_URL",
    "QQ_BOT_GROUP_ID",
    "QQ_BOT_USER_ID",
    "QQ_BOT_ACCESS_TOKEN",
]

SENSITIVE_ENV_KEYS = {
    "CRAWLER_OPENID",
    "CRAWLER_JSESSIONID",
    "CRAWLER_TOKEN",
    "EMAIL_SMTP_PASSWORD",
    "QQ_BOT_ACCESS_TOKEN",
    "DB_PASSWORD",
    "ADMIN_PASSWORD",
}


def _sign_payload(payload_b64: str) -> str:
    return hmac.new(
        settings.ADMIN_JWT_SECRET.encode(),
        payload_b64.encode(),
        hashlib.sha256,
    ).hexdigest()


def create_access_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": int(time.time()) + settings.ADMIN_TOKEN_EXPIRE_HOURS * 3600,
    }
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode()
    return f"{payload_b64}.{_sign_payload(payload_b64)}"


def verify_access_token(token: str) -> Optional[str]:
    try:
        payload_b64, signature = token.rsplit(".", 1)
    except ValueError:
        return None
    if not hmac.compare_digest(_sign_payload(payload_b64), signature):
        return None
    try:
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode()))
    except (json.JSONDecodeError, ValueError):
        return None
    if payload.get("exp", 0) < int(time.time()):
        return None
    username = payload.get("sub")
    if username != settings.ADMIN_USERNAME:
        return None
    return username


def verify_password(username: str, password: str) -> bool:
    if username != settings.ADMIN_USERNAME:
        return False
    return secrets.compare_digest(password, settings.ADMIN_PASSWORD)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期",
        )
    username = verify_access_token(credentials.credentials)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期",
        )
    return username
