"""
Pydantic模型（API请求/响应模型）
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PowerRecordBase(BaseModel):
    """电费记录基础模型"""
    dorm_number: str  # 宿舍号（如：320、324）
    balance: float  # 电费余量（度），主要监控项，通常是空调余量
    kbalance: Optional[float] = None  # 空调余量（度），从API获取的空调专用电费余量
    zbalance: Optional[float] = None  # 照明余量（度），从API获取的照明专用电费余量
    kpower_consumption: Optional[float] = None  # 空调用电量（度），与上次记录的差值
    zpower_consumption: Optional[float] = None  # 照明用电量（度），与上次记录的差值
    power_consumption: Optional[float] = None  # 用电量（度），已废弃，保留用于兼容性


class PowerRecordCreate(PowerRecordBase):
    pass


class PowerRecordResponse(PowerRecordBase):
    id: int
    record_time: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class PowerRecordListResponse(BaseModel):
    items: List[PowerRecordResponse]
    total: int


class AlertRuleBase(BaseModel):
    """告警规则基础模型"""
    dorm_number: str
    room_id: Optional[str] = None
    kthreshold: Optional[float] = None
    zthreshold: Optional[float] = None
    enabled: bool = True
    qq_enabled: bool = False


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    """告警规则更新模型，所有字段均为可选"""
    room_id: Optional[str] = None
    kthreshold: Optional[float] = None
    zthreshold: Optional[float] = None
    enabled: Optional[bool] = None
    qq_enabled: Optional[bool] = None


class AlertRuleResponse(AlertRuleBase):
    id: int
    last_alert_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlertLogResponse(BaseModel):
    """告警日志响应模型"""
    id: int  # 主键ID
    dorm_number: str  # 宿舍号（如：320、324）
    alert_category: Optional[str] = None  # 告警类别：ac（空调）/light（照明），标识是哪个类型的电费余量触发了告警
    balance: float  # 触发告警时的余量（度）
    threshold: float  # 告警阈值（度）
    alert_type: str  # 告警类型：qq（QQ告警）；历史数据可能含 email
    alert_status: str  # 告警状态：success（发送成功）/failed（发送失败）
    alert_message: Optional[str] = None  # 告警消息内容
    created_at: datetime  # 创建时间，告警发送的时间
    
    class Config:
        from_attributes = True
