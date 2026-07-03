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

LOW_BALANCE_ALERT_THRESHOLD = 10.0


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
    def get_records(db: Session, dorm_number: str, limit: int = 100) -> List[PowerRecord]:
        """获取电费记录列表"""
        return db.query(PowerRecord).filter(
            PowerRecord.dorm_number == dorm_number
        ).order_by(desc(PowerRecord.record_time)).limit(limit).all()
    
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
        # 验证：启用邮箱告警时必须提供接收邮箱地址
        if rule.email_enabled:
            if not rule.email_address or not rule.email_address.strip():
                raise ValueError("启用邮件告警时必须输入接收邮箱地址")
        
        # 验证：启用QQ告警时必须提供接收QQ号或群号
        if rule.qq_enabled:
            if not rule.qq_receiver_id or not rule.qq_receiver_id.strip():
                raise ValueError("启用QQ告警时必须输入接收QQ号或群号")
        
        # 处理空字符串，转换为None以保持数据库一致性
        if 'room_id' in rule_data:
            if rule_data['room_id'] == '' or (rule_data['room_id'] and not rule_data['room_id'].strip()):
                rule_data['room_id'] = None
            elif rule_data['room_id']:
                rule_data['room_id'] = rule_data['room_id'].strip()
        
        if 'email_address' in rule_data:
            if rule_data['email_address'] == '' or (rule_data['email_address'] and not rule_data['email_address'].strip()):
                rule_data['email_address'] = None
            elif rule_data['email_address']:
                rule_data['email_address'] = rule_data['email_address'].strip()
        
        if 'qq_receiver_id' in rule_data:
            if rule_data['qq_receiver_id'] == '' or (rule_data['qq_receiver_id'] and not rule_data['qq_receiver_id'].strip()):
                rule_data['qq_receiver_id'] = None
            elif rule_data['qq_receiver_id']:
                rule_data['qq_receiver_id'] = rule_data['qq_receiver_id'].strip()
        
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
        # 确定最终的email_enabled和qq_enabled状态
        final_email_enabled = update_data.get('email_enabled', rule.email_enabled)
        final_qq_enabled = update_data.get('qq_enabled', rule.qq_enabled)
        
        # 验证：启用邮箱告警时必须提供接收邮箱地址
        if final_email_enabled:
            email_address = update_data.get('email_address', rule.email_address)
            if not email_address or not str(email_address).strip():
                raise ValueError("启用邮件告警时必须输入接收邮箱地址")
        
        # 验证：启用QQ告警时必须提供接收QQ号或群号
        if final_qq_enabled:
            qq_receiver_id = update_data.get('qq_receiver_id', rule.qq_receiver_id)
            if not qq_receiver_id or not str(qq_receiver_id).strip():
                raise ValueError("启用QQ告警时必须输入接收QQ号或群号")
        
        # 处理空字符串，转换为None以保持数据库一致性
        if 'room_id' in update_data:
            if update_data['room_id'] == '' or (update_data['room_id'] and not update_data['room_id'].strip()):
                update_data['room_id'] = None
            elif update_data['room_id']:
                update_data['room_id'] = update_data['room_id'].strip()
        
        if 'email_address' in update_data:
            if update_data['email_address'] == '' or (update_data['email_address'] and not update_data['email_address'].strip()):
                update_data['email_address'] = None
            elif update_data['email_address']:
                update_data['email_address'] = update_data['email_address'].strip()
        
        if 'qq_receiver_id' in update_data:
            if update_data['qq_receiver_id'] == '' or (update_data['qq_receiver_id'] and not update_data['qq_receiver_id'].strip()):
                update_data['qq_receiver_id'] = None
            elif update_data['qq_receiver_id']:
                update_data['qq_receiver_id'] = update_data['qq_receiver_id'].strip()
        
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
        """
        Trigger alerts when AC or lighting balance drops below 10.
        """
        rule = AlertRuleService.get_rule(db, dorm_number)

        if not rule:
            logger.warning(f"Alert rule not found: {dorm_number}")
            return

        if not rule.enabled:
            logger.info(f"Alert rule disabled: {dorm_number}")
            return

        threshold = LOW_BALANCE_ALERT_THRESHOLD
        logger.info(
            f"Checking alerts: dorm={dorm_number}, kbalance={kbalance}, zbalance={zbalance}, threshold={threshold}, force={force_alert}"
        )

        triggered = False

        if kbalance is not None:
            if kbalance < threshold:
                triggered = True
                logger.info(f"AC alert triggered: {dorm_number}, balance {kbalance:.2f} < {threshold:.2f}")
                CrawlerService._send_alert(
                    db, rule, dorm_number, kbalance, threshold, 'ac', '空调', force_alert=force_alert
                )
            else:
                logger.info(f"AC balance normal: {dorm_number}, balance {kbalance:.2f} >= {threshold:.2f}")

        if zbalance is not None:
            if zbalance < threshold:
                triggered = True
                logger.info(f"Lighting alert triggered: {dorm_number}, balance {zbalance:.2f} < {threshold:.2f}")
                CrawlerService._send_alert(
                    db, rule, dorm_number, zbalance, threshold, 'light', '照明', force_alert=force_alert
                )
            else:
                logger.info(f"Lighting balance normal: {dorm_number}, balance {zbalance:.2f} >= {threshold:.2f}")

        if not triggered:
            logger.info(f"No alert triggered for dorm {dorm_number}; both balances are >= 10")

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
        # 获取当前最新的记录以获取完整的余量信息
        latest_record = PowerRecordService.get_latest_record(db, dorm_number)
        kbalance = latest_record.kbalance if latest_record else None
        zbalance = latest_record.zbalance if latest_record else None
        
        # 分别检查每种告警类型是否应该发送
        email_should_send = True
        qq_should_send = True
        email_reason = None
        qq_reason = None
        
        if rule.email_enabled:
            email_should_send, email_reason = CrawlerService._should_send_alert(
                db, dorm_number, category, category_name, 'email', force_alert
            )
            if not email_should_send:
                logger.info(f"跳过邮件告警：{email_reason}")
        
        if rule.qq_enabled:
            qq_should_send, qq_reason = CrawlerService._should_send_alert(
                db, dorm_number, category, category_name, 'qq', force_alert
            )
            if not qq_should_send:
                logger.info(f"跳过QQ告警：{qq_reason}")
        
        # 检查告警配置
        logger.info(f"告警配置检查：{dorm_number} ({category_name}), 邮件启用={rule.email_enabled}, QQ启用={rule.qq_enabled}, 邮件地址={rule.email_address}, QQ接收者={getattr(rule, 'qq_receiver_id', None)}")
        
        # 如果两种告警都被跳过，直接返回
        if not email_should_send and not qq_should_send:
            logger.warning(f"所有告警类型都被跳过：{dorm_number} ({category_name}), 邮件原因={email_reason}, QQ原因={qq_reason}")
            return
        
        # 如果告警方式未启用，记录警告
        if not rule.email_enabled and not rule.qq_enabled:
            logger.warning(f"告警规则中未启用任何告警方式：{dorm_number} ({category_name})")
            return
        
        # 发送告警（只发送允许发送的类型）
        logger.info(f"准备发送告警：{dorm_number} ({category_name}), 余额={balance:.2f}度, 阈值={threshold:.2f}度")
        alert_manager = get_alert_manager()
        results = alert_manager.send_alert(
            dorm_number=dorm_number,
            category=category,
            category_name=category_name,
            balance=balance,
            threshold=threshold,
            email_enabled=rule.email_enabled and email_should_send,
            email_address=rule.email_address,
            qq_enabled=rule.qq_enabled and qq_should_send,
            qq_receiver_id=getattr(rule, 'qq_receiver_id', None),  # 从规则中获取QQ接收者ID
            kbalance=kbalance,
            zbalance=zbalance
        )
        logger.info(f"告警发送结果：{dorm_number} ({category_name}), 邮件={results.get('email', False)}, QQ={results.get('qq', False)}")
        
        # 记录告警日志（记录所有尝试发送的告警）
        email_success = False
        qq_success = False
        
        if rule.email_enabled:
            email_success = results.get('email', False)
            error_msg = None if email_success else email_reason or "邮件发送失败"
            AlertLogService.create_log(
                db, dorm_number, balance, threshold, category,
                'email', 'success' if email_success else 'failed',
                alert_message=error_msg
            )
        
        if rule.qq_enabled:
            qq_success = results.get('qq', False)
            # 如果失败，尝试从告警日志中获取更详细的错误信息
            if not qq_success:
                # 检查最近的QQ告警日志，获取详细错误
                recent_qq_log = db.query(AlertLog).filter(
                    AlertLog.dorm_number == dorm_number,
                    AlertLog.alert_category == category,
                    AlertLog.alert_type == 'qq'
                ).order_by(desc(AlertLog.created_at)).first()
                
                if recent_qq_log and recent_qq_log.alert_message:
                    error_msg = recent_qq_log.alert_message
                else:
                    error_msg = qq_reason or "QQ消息发送失败，请检查NoneBot和NapCatQQ连接状态"
            else:
                error_msg = None
            
            AlertLogService.create_log(
                db, dorm_number, balance, threshold, category,
                'qq', 'success' if qq_success else 'failed',
                alert_message=error_msg
            )
        
        # 更新最后告警时间（只要有一种告警成功就更新）
        if email_success or qq_success:
            rule.last_alert_time = datetime.now()
            db.commit()
            success_types = []
            if email_success:
                success_types.append("邮件")
            if qq_success:
                success_types.append("QQ")
            logger.info(f"告警发送成功（{'+'.join(success_types)}）：{dorm_number}, {category_name}余量 {balance:.2f} 度, 阈值 {threshold:.2f} 度")
        else:
            # 即使失败也提交日志记录
            db.commit()
            failed_types = []
            if rule.email_enabled:
                failed_types.append("邮件")
            if rule.qq_enabled:
                failed_types.append("QQ")
            logger.warning(f"告警发送失败（{'+'.join(failed_types)}）：{dorm_number}, {category_name}余量 {balance:.2f} 度, 阈值 {threshold:.2f} 度，将在下次检查时重试")
