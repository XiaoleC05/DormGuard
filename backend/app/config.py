"""
奥泽莉亚工具箱 - 配置文件
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import field_validator


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "dorm_power_guard"
    
    # 爬虫配置
    CRAWLER_BASE_URL: Optional[str] = None
    CRAWLER_API_BASE_URL: Optional[str] = None
    CRAWLER_TOKEN: Optional[str] = None
    CRAWLER_USERNAME: Optional[str] = None
    CRAWLER_PASSWORD: Optional[str] = None
    CRAWLER_DORM_NUMBER: Optional[str] = None
    CRAWLER_TOKEN_REFRESH_URL: Optional[str] = None
    
    # 西华大学电费系统特定配置
    CRAWLER_OPENID: Optional[str] = None
    CRAWLER_JSESSIONID: Optional[str] = None
    CRAWLER_ROOM_ID: Optional[str] = None
    CRAWLER_AREA_ID: Optional[str] = "1"
    CRAWLER_YQ_ID: Optional[str] = "3"
    CRAWLER_BUILDING_ID: Optional[str] = "40-1"
    CRAWLER_FLOOR_ID: Optional[str] = "3"
    CRAWLER_FACTORY_CODE: Optional[str] = "E014"
    CRAWLER_SIGN: Optional[str] = "qt"
    CRAWLER_ORG_ID: Optional[str] = "2"
    
    # 定时任务配置
    SCHEDULER_INTERVAL_HOURS: int = 2  # 爬虫与告警检测间隔（小时）
    ALERT_COOLDOWN_HOURS: int = 2  # 同类告警最短间隔（小时），建议与检测间隔一致
    QQ_ALERT_PAUSE_UNTIL: Optional[str] = None  # QQ告警暂停至该日期（不含），格式 YYYY-MM-DD，到达当日恢复
    SCHEDULER_HOURS: str = "8,12,18,22"  # 已废弃
    
    # 邮件配置
    EMAIL_ENABLED: bool = False
    EMAIL_SMTP_HOST: Optional[str] = None
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SMTP_USER: Optional[str] = None
    EMAIL_SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    EMAIL_TO: Optional[str] = None
    
    # QQ机器人（NoneBot + NapCat，仅群消息）
    QQ_BOT_ENABLED: bool = False
    QQ_BOT_API_URL: Optional[str] = None
    QQ_BOT_ID: str = "1270667498"  # 机器人登录QQ号，固定不可改
    QQ_BOT_GROUP_ID: Optional[str] = "6011223303"  # 告警消息发送目标群号，可修改
    QQ_BOT_ACCESS_TOKEN: Optional[str] = None    
    # QQ直推配置（QMsg）
    QQ_NOTIFY_API_KEY: Optional[str] = None

    # 默认告警阈值
    DEFAULT_ALERT_THRESHOLD: float = 20.0

    # 管理登录（唯一用户，无注册/改密）
    ADMIN_USERNAME: str = "root"
    ADMIN_PASSWORD: str = "783688"
    ADMIN_JWT_SECRET: str = "dorm-power-guard-masterc-secret"
    ADMIN_TOKEN_EXPIRE_HOURS: int = 168

    @field_validator("DEFAULT_ALERT_THRESHOLD", mode="before")
    @classmethod
    def handle_empty_threshold(cls, v):
        if v == "" or v is None:
            return 20.0
        return v


settings = Settings()
