"""读写 backend/.env，供管理页更新配置。"""
import fcntl
from pathlib import Path
from typing import Dict

from app.auth import MANAGEABLE_ENV_KEYS, SENSITIVE_ENV_KEYS

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
_LOCK_PATH = Path(__file__).resolve().parent.parent / ".env.lock"


def _acquire_lock():
    """获取文件排他锁，防止并发写 .env 导致数据损坏。"""
    lock_file = open(_LOCK_PATH, "w")
    fcntl.flock(lock_file, fcntl.LOCK_EX)
    return lock_file


def _parse_env_lines(text: str) -> list[str]:
    return text.splitlines()


def read_env_values() -> Dict[str, str]:
    if not ENV_PATH.exists():
        return {key: "" for key in MANAGEABLE_ENV_KEYS}

    values = {key: "" for key in MANAGEABLE_ENV_KEYS}
    for line in _parse_env_lines(ENV_PATH.read_text(encoding="utf-8")):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if key in values:
            values[key] = value.strip()
    return values


def mask_env_values(values: Dict[str, str]) -> Dict[str, str]:
    masked = {}
    for key, value in values.items():
        if key in SENSITIVE_ENV_KEYS and value:
            masked[key] = "******"
        else:
            masked[key] = value
    return masked


def write_env_values(updates: Dict[str, str]) -> None:
    allowed = set(MANAGEABLE_ENV_KEYS)
    filtered = {
        key: str(value).strip()
        for key, value in updates.items()
        if key in allowed
    }
    if not filtered:
        return

    lock = _acquire_lock()
    try:
        lines: list[str] = []
        if ENV_PATH.exists():
            lines = _parse_env_lines(ENV_PATH.read_text(encoding="utf-8"))

        existing_keys = set()
        new_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                new_lines.append(line)
                continue
            key, _ = stripped.split("=", 1)
            key = key.strip()
            if key in filtered:
                new_lines.append(f"{key}={filtered[key]}")
                existing_keys.add(key)
            else:
                new_lines.append(line)

        for key, value in filtered.items():
            if key not in existing_keys:
                new_lines.append(f"{key}={value}")

        ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
