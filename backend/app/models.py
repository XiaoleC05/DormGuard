"""
数据库模型
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class PowerRecord(Base):
    """
    电费记录表
    
    存储从西华大学电费系统抓取的电费数据，包括余量和用电量信息。
    支持多宿舍监控，每个宿舍通过dorm_number和room_id关联。
    """
    __tablename__ = "power_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID，自增")
    dorm_number = Column(String(50), nullable=False, index=True, comment="宿舍号（如：320、324），用于标识不同的宿舍")
    balance = Column(Float, nullable=False, comment="电费余量（度），主要监控项，通常是空调余量，用于判断是否需要告警")
    kbalance = Column(Float, nullable=True, comment="空调余量（度），从API获取的空调专用电费余量")
    zbalance = Column(Float, nullable=True, comment="照明余量（度），从API获取的照明专用电费余量")
    kpower_consumption = Column(Float, nullable=True, comment="空调用电量（度），与上次记录的差值，表示本次记录周期内的空调用电量")
    zpower_consumption = Column(Float, nullable=True, comment="照明用电量（度），与上次记录的差值，表示本次记录周期内的照明用电量")
    power_consumption = Column(Float, nullable=True, comment="用电量（度），已废弃，保留用于兼容性，请使用kpower_consumption和zpower_consumption")
    record_time = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="记录时间，数据抓取的时间点")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间，记录插入数据库的时间")
    
    def __repr__(self):
        return f"<PowerRecord(id={self.id}, dorm={self.dorm_number}, balance={self.balance})>"


class AlertRule(Base):
    """
    告警规则表
    
    存储单一宿舍的告警配置，包括阈值设置和 QQ 告警开关。
    本项目仅支持单一宿舍监控，最多存在一条规则。
    """
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID，自增")
    dorm_number = Column(String(50), nullable=False, unique=True, comment="宿舍号（如：320、324），从配置文件读取，唯一标识监控的宿舍")
    room_id = Column(String(50), nullable=True, comment="房间ID（roomid），从西华大学电费系统API获取，用于查询该宿舍的电费数据，多宿舍监控必需")
    kthreshold = Column(Float, nullable=True, comment="空调告警阈值（度），当空调余量低于此值时触发告警")
    zthreshold = Column(Float, nullable=True, comment="照明告警阈值（度），当照明余量低于此值时触发告警")
    enabled = Column(Boolean, default=True, nullable=False, index=True, comment="是否启用告警规则，False时不会触发任何告警")
    qq_enabled = Column(Boolean, default=False, nullable=False, comment="是否启用QQ告警，True时当余量低于阈值会发送QQ消息")
    last_alert_time = Column(DateTime, nullable=True, comment="最后告警时间，用于防止频繁告警，记录最近一次成功发送告警的时间")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间，规则创建的时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间，规则最后修改的时间")
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, dorm={self.dorm_number}, kthreshold={self.kthreshold}, zthreshold={self.zthreshold})>"


class AlertLog(Base):
    """
    告警日志表
    
    记录所有告警发送的历史记录，包括成功和失败的告警，用于审计和问题排查。
    """
    __tablename__ = "alert_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID，自增")
    dorm_number = Column(String(50), nullable=False, index=True, comment="宿舍号（如：320、324），标识触发告警的宿舍")
    alert_category = Column(String(20), nullable=True, comment="告警类别：ac（空调）/light（照明），标识是哪个类型的电费余量触发了告警")
    balance = Column(Float, nullable=False, comment="触发告警时的余量（度），记录告警触发时的实际电费余量")
    threshold = Column(Float, nullable=False, comment="告警阈值（度），记录触发告警时使用的阈值")
    alert_type = Column(String(20), nullable=False, comment="告警类型：qq（QQ告警）；历史数据可能含 email")
    alert_status = Column(String(20), nullable=False, comment="告警状态：success（发送成功）/failed（发送失败），标识告警是否成功发送")
    alert_message = Column(Text, nullable=True, comment="告警消息内容，记录实际发送的告警消息文本")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间，告警发送的时间")
    
    def __repr__(self):
        return f"<AlertLog(id={self.id}, dorm={self.dorm_number}, type={self.alert_type})>"
