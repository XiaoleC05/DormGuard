"""单用户鉴权（root），无注册、无改密；支持 Oxelia51 网关模式（ADR-007）。"""
import base64
import hashlib
import hmac
import ipaddress
import json
import logging
import secrets
import time
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

logger = logging.getLogger(__name__)

_bearer = HTTPBearer(auto_error=False)

# 可配置的 .env 键（供管理页读写）
MANAGEABLE_ENV_KEYS = [
    "CRAWLER_DORM_NUMBER",
    "CRAWLER_ROOM_ID",
    "CRAWLER_OPENID",
    "CRAWLER_JSESSIONID",
    "SCHEDULER_INTERVAL_HOURS",
    "ALERT_COOLDOWN_HOURS",
    "QQ_ALERT_PAUSE_UNTIL",
    "QQ_BOT_ENABLED",
    "QQ_BOT_API_URL",
    "QQ_BOT_GROUP_ID",
]

SENSITIVE_ENV_KEYS = {
    "CRAWLER_JSESSIONID",
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
    # DormGuard 自研 token 格式为 {payload_b64}.{hmac_signature}（2 段）。
    # 拒绝标准 JWT 格式（3 段 {header}.{payload}.{signature}），
    # 防止未来误用标准 JWT 库时 alg=none 攻击绕过签名校验。
    parts = token.split(".")
    if len(parts) != 2:
        return None
    try:
        payload_b64, signature = parts
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


def _is_trusted_gateway_client(host: str) -> bool:
    if not host:
        return False
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _gateway_username(request: Request) -> Optional[str]:
    """平台网关 loopback 请求：信任 X-Oxelia51-* 头，跳过 DormGuard JWT。"""
    if not settings.OXELIA_GATEWAY_MODE:
        return None

    client_host = request.client.host if request.client else ""
    if not _is_trusted_gateway_client(client_host):
        logger.warning("gateway reject host=%r", client_host)
        return None

    user_id = request.headers.get("X-Oxelia51-User-Id", "").strip()
    username = request.headers.get("X-Oxelia51-Username", "").strip()
    role = request.headers.get("X-Oxelia51-Role", "").strip()
    if not user_id or not username or role not in ("admin", "user"):
        logger.warning(
            "gateway reject headers uid=%r username=%r role=%r host=%r",
            user_id, username, role, client_host,
        )
        return None

    secret = settings.OXELIA_GATEWAY_SECRET.strip()
    if secret:
        got = request.headers.get("X-Oxelia51-Gateway-Secret", "")
        if not got or not secrets.compare_digest(got, secret):
            return None

    return username


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> str:
    gateway_user = _gateway_username(request)
    if gateway_user:
        return gateway_user

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
