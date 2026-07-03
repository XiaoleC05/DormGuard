"""
业务逻辑层
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta, date
from typing import Optional, Tuple, List
from app.models import PowerRecord, AlertRule, AlertLog
from app.schemas import PowerRecordCreate, AlertRuleCreate, AlertRuleUpdate
from app.crawler import get_crawler
from app.alert import get_alert_manager
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def _threshold_for(rule: AlertRule, category: str) -> float:
    """读取规则阈值，未设置时回退到 DEFAULT_ALERT_THRESHOLD。"""
    if category == "ac" and rule.kthreshold is not None:
        return rule.kthreshold
    if category == "light" and rule.zthreshold is not None:
        return rule.zthreshold
    return settings.DEFAULT_ALERT_THRESHOLD


def is_qq_alert_paused() -> tuple[bool, Optional[str]]:
    """检查 QQ 告警是否处于暂停期（QQ_ALERT_PAUSE_UNTIL 之前不发自动告警）"""
    pause_until = settings.QQ_ALERT_PAUSE_UNTIL
    if not pause_until or not str(pause_until).strip():
        return False, None
    try:
        resume_date = datetime.strptime(str(pause_until).strip(), "%Y-%m-%d").date()
    except ValueError:
        logger.warning(f"QQ_ALERT_PAUSE_UNTIL 格式无效：{pause_until}，忽略暂停配置")
        return False, None
    if date.today() < resume_date:
        return True, f"QQ告警已暂停，将于 {resume_date} 恢复"
    return False, None


class PowerRecordService:
    """电费记录服务"""
    
    @staticmethod
    def create_record(db: Session, record: PowerRecordCreate) -> PowerRecord:
        """创建电费记录，并计算用电量差值"""
        # 获取上次记录
        last_record = PowerRecordService.get_latest_record(db, record.dorm_number)
        
        # 计算用电量差值
        kpower_consumption = None
        zpower_consumption = None
        
        if last_record:
            # 计算空调用电量差值（当前值 - 上次值）
            if record.kbalance is not None and last_record.kbalance is not None:
                kpower_consumption = record.kbalance - last_record.kbalance
                # 如果差值为负，说明可能是充值了，设为None
                if kpower_consumption < 0:
                    kpower_consumption = None
            
            # 计算照明用电量差值（当前值 - 上次值）
            if record.zbalance is not None and last_record.zbalance is not None:
                zpower_consumption = record.zbalance - last_record.zbalance
                # 如果差值为负，说明可能是充值了，设为None
                if zpower_consumption < 0:
                    zpower_consumption = None
        
        # 创建记录
        record_dict = record.dict()
        record_dict['kpower_consumption'] = kpower_consumption
        record_dict['zpower_consumption'] = zpower_consumption
        
        db_record = PowerRecord(**record_dict)
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    
    @staticmethod
    def get_latest_record(db: Session, dorm_number: str) -> Optional[PowerRecord]:
        """获取最新的电费记录"""
        return db.query(PowerRecord).filter(
            PowerRecord.dorm_number == dorm_number
        ).order_by(desc(PowerRecord.record_time)).first()
    
    @staticmethod
    def count_records(db: Session, dorm_number: str) -> int:
        """统计电费记录总数"""
        return db.query(PowerRecord).filter(
            PowerRecord.dorm_number == dorm_number
        ).count()

    @staticmethod
    def get_records(db: Session, dorm_number: str, limit: int = 100, offset: int = 0) -> List[PowerRecord]:
        """获取电费记录列表（分页）"""
        return db.query(PowerRecord).filter(
            PowerRecord.dorm_number == dorm_number
        ).order_by(desc(PowerRecord.record_time)).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_records_by_date_range(db: Session, dorm_number: str, 
                                   start_date: datetime, end_date: datetime) -> List[PowerRecord]:
        """按日期范围获取记录"""
        return db.query(PowerRecord).filter(
            PowerRecord.dorm_number == dorm_number,
            PowerRecord.record_time >= start_date,
            PowerRecord.record_time <= end_date
        ).order_by(desc(PowerRecord.record_time)).all()


class AlertRuleService:
    """告警规则服务"""
    
    @staticmethod
    def create_rule(db: Session, rule: AlertRuleCreate) -> AlertRule:
        """创建告警规则"""
        rule_data = rule.dict()

        if rule.qq_enabled:
            if not settings.QQ_BOT_GROUP_ID or not str(settings.QQ_BOT_GROUP_ID).strip():
                raise ValueError("启用QQ告警时须在系统配置中填写告警群号")

        if 'room_id' in rule_data:
            if rule_data['room_id'] == '' or (rule_data['room_id'] and not rule_data['room_id'].strip()):
                rule_data['room_id'] = None
            elif rule_data['room_id']:
                rule_data['room_id'] = rule_data['room_id'].strip()

        db_rule = AlertRule(**rule_data)
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
        return db_rule
    
    @staticmethod
    def get_rule(db: Session, dorm_number: str) -> Optional[AlertRule]:
        """获取告警规则"""
        return db.query(AlertRule).filter(
            AlertRule.dorm_number == dorm_number
        ).first()
    
    @staticmethod
    def get_all_rules(db: Session) -> List[AlertRule]:
        """获取所有告警规则"""
        return db.query(AlertRule).all()
    
    @staticmethod
    def update_rule(db: Session, dorm_number: str, rule_update: AlertRuleUpdate) -> Optional[AlertRule]:
        """更新告警规则"""
        rule = AlertRuleService.get_rule(db, dorm_number)
        if not rule:
            return None
        
        update_data = rule_update.dict(exclude_unset=True)
        final_qq_enabled = update_data.get('qq_enabled', rule.qq_enabled)

        if final_qq_enabled:
            if not settings.QQ_BOT_GROUP_ID or not str(settings.QQ_BOT_GROUP_ID).strip():
                raise ValueError("启用QQ告警时须在系统配置中填写告警群号")

        if 'room_id' in update_data:
            if update_data['room_id'] == '' or (update_data['room_id'] and not update_data['room_id'].strip()):
                update_data['room_id'] = None
            elif update_data['room_id']:
                update_data['room_id'] = update_data['room_id'].strip()

        for key, value in update_data.items():
            setattr(rule, key, value)
        
        db.commit()
        db.refresh(rule)
        return rule
    
    @staticmethod
    def delete_rule(db: Session, dorm_number: str) -> bool:
        """删除告警规则"""
        rule = AlertRuleService.get_rule(db, dorm_number)
        if not rule:
            return False
        db.delete(rule)
        db.commit()
        return True


class AlertLogService:
    """告警日志服务"""
    
    @staticmethod
    def create_log(db: Session, dorm_number: str, balance: float, threshold: float,
                   alert_category: Optional[str], alert_type: str, alert_status: str, 
                   alert_message: Optional[str] = None) -> AlertLog:
        """创建告警日志"""
        log = AlertLog(
            dorm_number=dorm_number,
            alert_category=alert_category,
            balance=balance,
            threshold=threshold,
            alert_type=alert_type,
            alert_status=alert_status,
            alert_message=alert_message
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_logs(db: Session, dorm_number: Optional[str] = None, limit: int = 50) -> List[AlertLog]:
        """获取告警日志"""
        query = db.query(AlertLog)
        if dorm_number:
            query = query.filter(AlertLog.dorm_number == dorm_number)
        return query.order_by(desc(AlertLog.created_at)).limit(limit).all()


class CrawlerService:
    """爬虫服务"""
    
    @staticmethod
    def crawl_and_save(db: Session, force_alert: bool = False, skip_alert: bool = False) -> bool:
        """
        执行爬虫任务并保存数据（支持多宿舍）
        遍历所有启用的告警规则，为每个宿舍获取电费数据
        
        Args:
            db: 数据库会话
            force_alert: 是否强制发送告警（忽略防频繁告警限制，用于手动触发）
            skip_alert: 是否跳过告警检查（手动触发时设置为True，只获取数据不触发告警）
        
        Returns:
            bool: 是否至少成功获取一个宿舍的数据
        """
        try:
            # 获取所有启用的告警规则
            enabled_rules = db.query(AlertRule).filter(AlertRule.enabled == True).all()
            
            if not enabled_rules:
                logger.warning("没有启用的告警规则，跳过爬虫任务")
                return False
            
            logger.info(f"找到 {len(enabled_rules)} 个启用的告警规则，开始获取电费数据")
            
            crawler = get_crawler()
            success_count = 0
            failed_count = 0
            
            # 遍历每个启用的告警规则
            for rule in enabled_rules:
                if not rule.room_id:
                    error_msg = f"宿舍 {rule.dorm_number} 未配置room_id，无法查询电费数据。请在监控面板编辑告警规则，填写房间ID（room_id）"
                    logger.warning(error_msg)
                    failed_count += 1
                    # 如果是单一规则且未配置room_id，抛出异常以便API返回更友好的错误信息
                    if len(enabled_rules) == 1:
                        raise ValueError(error_msg)
                    continue
                
                try:
                    # 使用告警规则中的room_id和dorm_number获取数据
                    data = crawler.fetch_power_data(dorm_number=rule.dorm_number, room_id=rule.room_id)
                    
                    if not data:
                        logger.warning(f"宿舍 {rule.dorm_number} 未获取到数据")
                        failed_count += 1
                        continue
                    
                    # 保存记录
                    record = PowerRecordCreate(**data)
                    PowerRecordService.create_record(db, record)
                    
                    logger.info(f"成功抓取并保存电费数据：{data['dorm_number']}, 空调余量 {data.get('kbalance', 'N/A')} 度, 照明余量 {data.get('zbalance', 'N/A')} 度")
                    
                    # 检查是否需要告警（如果skip_alert为True，则跳过告警检查）
                    if not skip_alert:
                        CrawlerService.check_and_alert(db, data['dorm_number'], data.get('kbalance'), data.get('zbalance'), force_alert=force_alert)
                    else:
                        logger.info(f"手动触发模式：跳过告警检查，仅获取数据")
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"获取宿舍 {rule.dorm_number} 的电费数据失败：{e}", exc_info=True)
                    failed_count += 1
                    continue
            
            logger.info(f"爬虫任务完成：成功 {success_count} 个，失败 {failed_count} 个")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"爬虫任务执行失败：{e}", exc_info=True)
            import traceback
            logger.error(f"详细错误信息：{traceback.format_exc()}")
            return False
    
    @staticmethod
    def check_and_alert(db: Session, dorm_number: str, kbalance: Optional[float] = None, zbalance: Optional[float] = None, force_alert: bool = False):
        """当空调/照明余量低于规则阈值时触发告警。"""
        rule = AlertRuleService.get_rule(db, dorm_number)

        if not rule:
            logger.warning(f"Alert rule not found: {dorm_number}")
            return

        if not rule.enabled:
            logger.info(f"Alert rule disabled: {dorm_number}")
            return

        kthreshold = _threshold_for(rule, "ac")
        zthreshold = _threshold_for(rule, "light")
        logger.info(
            f"Checking alerts: dorm={dorm_number}, kbalance={kbalance}, zbalance={zbalance}, "
            f"kthreshold={kthreshold}, zthreshold={zthreshold}, force={force_alert}"
        )

        triggered = False

        if kbalance is not None:
            if kbalance < kthreshold:
                triggered = True
                logger.info(f"AC alert triggered: {dorm_number}, balance {kbalance:.2f} < {kthreshold:.2f}")
                CrawlerService._send_alert(
                    db, rule, dorm_number, kbalance, kthreshold, 'ac', '空调', force_alert=force_alert
                )
            else:
                logger.info(f"AC balance normal: {dorm_number}, balance {kbalance:.2f} >= {kthreshold:.2f}")

        if zbalance is not None:
            if zbalance < zthreshold:
                triggered = True
                logger.info(f"Lighting alert triggered: {dorm_number}, balance {zbalance:.2f} < {zthreshold:.2f}")
                CrawlerService._send_alert(
                    db, rule, dorm_number, zbalance, zthreshold, 'light', '照明', force_alert=force_alert
                )
            else:
                logger.info(f"Lighting balance normal: {dorm_number}, balance {zbalance:.2f} >= {zthreshold:.2f}")

        if not triggered:
            logger.info(
                f"No alert triggered for dorm {dorm_number}; balances above thresholds "
                f"(ac>={kthreshold}, light>={zthreshold})"
            )

    @staticmethod
    def _should_send_alert(db: Session, dorm_number: str, category: str, category_name: str, 
                          alert_type: str, force_alert: bool = False) -> tuple[bool, Optional[str]]:
        """
        检查是否应该发送告警（防频繁告警机制）
        
        Args:
            db: 数据库会话
            dorm_number: 宿舍号
            category: 告警类别（ac/light）
            category_name: 告警类别名称（空调/照明）
            alert_type: 告警类型（email/qq）
            force_alert: 是否强制发送告警
        
        Returns:
            (should_send, reason) 元组
            should_send: 是否应该发送
            reason: 原因说明（如果should_send=False）
        """
        if force_alert:
            return True, None

        if alert_type == 'qq':
            paused, pause_reason = is_qq_alert_paused()
            if paused:
                return False, pause_reason
        
        cooldown_hours = settings.ALERT_COOLDOWN_HOURS
        
        # 查找该类别和类型的最近一次成功告警
        last_success_log = db.query(AlertLog).filter(
            AlertLog.dorm_number == dorm_number,
            AlertLog.alert_category == category,
            AlertLog.alert_type == alert_type,
            AlertLog.alert_status == 'success'
        ).order_by(desc(AlertLog.created_at)).first()
        
        if last_success_log:
            time_diff = datetime.now() - last_success_log.created_at
            if time_diff < timedelta(hours=cooldown_hours):
                return False, f"距离上次{alert_type}告警成功不足{cooldown_hours}小时（{int(time_diff.total_seconds() / 60)}分钟前）"
        
        # 如果上次告警失败，允许立即重试
        last_failed_log = db.query(AlertLog).filter(
            AlertLog.dorm_number == dorm_number,
            AlertLog.alert_category == category,
            AlertLog.alert_type == alert_type,
            AlertLog.alert_status == 'failed'
        ).order_by(desc(AlertLog.created_at)).first()
        
        if last_failed_log:
            logger.info(f"上次{alert_type}告警失败，允许立即重试：{dorm_number} ({category_name})")
        
        return True, None
    
    @staticmethod
    def _send_alert(db: Session, rule: AlertRule, dorm_number: str, balance: float, 
                    threshold: float, category: str, category_name: str, force_alert: bool = False):
        """
        发送告警
        
        Args:
            db: 数据库会话
            rule: 告警规则
            dorm_number: 宿舍号
            balance: 当前余量
            threshold: 告警阈值
            category: 告警类别（ac/light）
            category_name: 告警类别名称（空调/照明）
            force_alert: 是否强制发送告警（忽略防频繁告警限制）
        """
        latest_record = PowerRecordService.get_latest_record(db, dorm_number)
        kbalance = latest_record.kbalance if latest_record else None
        zbalance = latest_record.zbalance if latest_record else None

        if not rule.qq_enabled:
            logger.warning(f"告警规则中未启用QQ告警：{dorm_number} ({category_name})")
            return

        qq_should_send, qq_reason = CrawlerService._should_send_alert(
            db, dorm_number, category, category_name, 'qq', force_alert
        )
        if not qq_should_send:
            logger.info(f"跳过QQ告警：{qq_reason}")
            return

        logger.info(
            f"准备发送QQ告警：{dorm_number} ({category_name}), 余额={balance:.2f}度, "
            f"阈值={threshold:.2f}度, 告警群={settings.QQ_BOT_GROUP_ID}"
        )
        alert_manager = get_alert_manager()
        results = alert_manager.send_alert(
            dorm_number=dorm_number,
            category_name=category_name,
            balance=balance,
            threshold=threshold,
            qq_enabled=True,
            kbalance=kbalance,
            zbalance=zbalance,
        )
        qq_success = results.get('qq', False)
        error_msg = results.get('qq_error') if not qq_success else None
        if not qq_success and not error_msg:
            error_msg = qq_reason or "QQ消息发送失败"

        AlertLogService.create_log(
            db, dorm_number, balance, threshold, category,
            'qq', 'success' if qq_success else 'failed',
            alert_message=error_msg,
        )

        if qq_success:
            rule.last_alert_time = datetime.now()
            db.commit()
            logger.info(
                f"QQ告警发送成功：{dorm_number}, {category_name}余量 {balance:.2f} 度, 阈值 {threshold:.2f} 度"
            )
        else:
            db.commit()
            logger.warning(
                f"QQ告警发送失败：{dorm_number}, {category_name}余量 {balance:.2f} 度, 阈值 {threshold:.2f} 度，将在下次检查时重试"
            )
