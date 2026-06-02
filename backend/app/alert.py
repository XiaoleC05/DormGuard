"""
告警模块（邮件、QQ机器人）
"""
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Dict, List
from app.config import settings
from app.templates import get_email_template, get_email_text_template
import logging

logger = logging.getLogger(__name__)


class EmailAlert:
    """邮件告警"""
    
    def __init__(self):
        self.enabled = settings.EMAIL_ENABLED
        self.smtp_host = settings.EMAIL_SMTP_HOST
        self.smtp_port = settings.EMAIL_SMTP_PORT
        self.smtp_user = settings.EMAIL_SMTP_USER
        self.smtp_password = settings.EMAIL_SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM  # 发送方邮箱（全局配置）
    
    def send(self, dorm_number: str, category: str, category_name: str, 
             balance: float, threshold: float, 
             email_address: Optional[str] = None,
             kbalance: Optional[float] = None,
             zbalance: Optional[float] = None) -> bool:
        """
        发送邮件告警
        
        Args:
            dorm_number: 宿舍号
            category: 告警类别（ac/light）
            category_name: 告警类别名称（空调/照明）
            balance: 当前余量（度）
            threshold: 告警阈值（度）
            email_address: 接收邮箱地址（优先使用规则中的邮箱）
            kbalance: 空调余量（度，可选）
            zbalance: 照明余量（度，可选）
        """
        if not self.enabled:
            logger.info("邮件告警未启用")
            return False
        
        # 确定接收邮箱：必须使用规则中配置的邮箱，不能使用全局配置
        recipients = []
        if email_address:
            # 使用规则中配置的邮箱
            recipients = [email.strip() for email in email_address.split(',') if email.strip()]
        
        if not recipients:
            logger.error("未配置接收邮箱地址（必须在前端告警规则中填入接收邮箱）")
            return False
        
        if not all([self.smtp_host, self.smtp_user, self.smtp_password, self.email_from]):
            logger.error("邮件SMTP配置不完整")
            return False
        
        try:
            # 使用模板生成邮件内容
            subject, html_body = get_email_template(
                dorm_number=dorm_number,
                category=category,
                category_name=category_name,
                balance=balance,
                threshold=threshold,
                kbalance=kbalance,
                zbalance=zbalance
            )
            
            # 生成纯文本版本（备用）
            _, text_body = get_email_text_template(
                dorm_number=dorm_number,
                category=category,
                category_name=category_name,
                balance=balance,
                threshold=threshold,
                kbalance=kbalance,
                zbalance=zbalance
            )
            
            # 构建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # 添加纯文本版本
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # 添加HTML版本
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件
            if self.smtp_port == 465:
                # SSL端口，使用SMTP_SSL
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.email_from, recipients, msg.as_string())
                server.quit()
            else:
                # 普通端口，使用STARTTLS
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    if self.smtp_port == 587:
                        server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.email_from, recipients, msg.as_string())
            
            logger.info(f"邮件告警发送成功：{dorm_number}, {category_name}余量 {balance} 度, 发送至 {', '.join(recipients)}")
            return True
            
        except Exception as e:
            logger.error(f"邮件告警发送失败：{e}", exc_info=True)
            return False


class QQBotAlert:
    """QQ机器人告警"""
    
    def __init__(self):
        self.enabled = settings.QQ_BOT_ENABLED
        self.api_url = settings.QQ_BOT_API_URL
        # 注意：不再使用全局配置的 group_id 和 user_id 作为接收方
        # 接收方必须从告警规则中获取（qq_receiver_id）
    
    def send(self, dorm_number: str, category: str, category_name: str,
             balance: float, threshold: float,
             kbalance: Optional[float] = None,
             zbalance: Optional[float] = None,
             qq_receiver_id: Optional[str] = None) -> bool:
        """
        发送QQ消息告警
        
        Args:
            dorm_number: 宿舍号
            category: 告警类别（ac/light）
            category_name: 告警类别名称（空调/照明）
            balance: 当前余量（度）
            threshold: 告警阈值（度）
            kbalance: 空调余量（度，可选）
            zbalance: 照明余量（度，可选）
            qq_receiver_id: QQ接收者ID（群号或用户QQ号，可选，优先使用此参数）
        
        Returns:
            bool: 发送是否成功
        """
        if not self.enabled:
            logger.debug("QQ告警未启用（全局配置）")
            return False
        
        if not self.api_url:
            logger.error("QQ机器人API地址未配置")
            return False
        
        # 确定接收QQ号：必须使用规则中配置的qq_receiver_id，不能使用全局配置
        if not qq_receiver_id:
            logger.error("未配置接收QQ号或群号（必须在前端告警规则中填入接收QQ号或群号）")
            return False
        
        receiver_id = qq_receiver_id
        
        try:
            # 构建告警消息
            message = self._build_message(dorm_number, category_name, balance, threshold, kbalance, zbalance)
            
            # 判断是群号还是用户QQ号
            try:
                if receiver_id.startswith("group:") or receiver_id.startswith("g:"):
                    _, actual_id = receiver_id.split(":", 1)
                    group_id = int(actual_id.strip())
                    url = f"{self.api_url}/api/send_group_msg"
                    data = {"group_id": group_id, "message": message}
                    target_info = f"群 {group_id}"
                else:
                    receiver_num = int(receiver_id)
                    if receiver_num >= 1000000000:
                        url = f"{self.api_url}/api/send_group_msg"
                        data = {"group_id": receiver_num, "message": message}
                        target_info = f"群 {receiver_id}"
                    else:
                        url = f"{self.api_url}/api/send_private_msg"
                        data = {"user_id": receiver_num, "message": message}
                        target_info = f"用户 {receiver_id}"
            except ValueError:
                logger.error(f"QQ接收者ID格式错误：{receiver_id}")
                return False
            
            # 准备请求头
            headers = {
                "Content-Type": "application/json"
            }
            if hasattr(settings, 'QQ_BOT_ACCESS_TOKEN') and settings.QQ_BOT_ACCESS_TOKEN:
                headers["Authorization"] = f"Bearer {settings.QQ_BOT_ACCESS_TOKEN}"
            
            # 发送请求
            logger.info(f"正在发送QQ告警到{target_info}：{dorm_number}, {category_name}余量 {balance:.2f} 度")
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            # 处理响应
            if response.status_code == 200:
                result = response.json()
                # OneBot 协议返回格式：{"status": "ok", "retcode": 0, "data": {...}}
                if result.get("status") == "ok" or result.get("retcode") == 0:
                    logger.info(f"QQ告警发送成功：{dorm_number}, {category_name}余量 {balance:.2f} 度 -> {target_info}")
                    return True
                else:
                    error_msg = result.get("msg", str(result))
                    # 特殊处理：如果返回 "There are no bots to get"，说明NapCatQQ未连接
                    if "no bots" in error_msg.lower() or "There are no bots" in error_msg or "no bot" in error_msg.lower():
                        error_msg = "NoneBot未连接NapCatQQ。请检查：1) NapCatQQ是否已启动并登录 2) NapCatQQ是否已连接到NoneBot（WebSocket连接）"
                    logger.error(f"QQ告警发送失败（API返回错误）：{error_msg}")
                    return False
            else:
                error_text = response.text[:200]  # 限制错误信息长度
                logger.error(f"QQ告警API请求失败：HTTP {response.status_code}, 响应：{error_text}")
                return False
                
        except requests.exceptions.Timeout:
            error_msg = f"QQ告警发送超时：NoneBot可能响应缓慢或NapCatQQ未连接。请检查NoneBot和NapCatQQ状态"
            logger.error(error_msg)
            return False
        except requests.exceptions.ConnectionError as e:
            error_msg = f"QQ告警连接失败：无法连接到NoneBot（{self.api_url}）。请检查：1) NoneBot是否在运行（端口8080） 2) NapCatQQ是否已启动并连接到NoneBot"
            logger.error(error_msg)
            logger.error(f"连接错误详情：{str(e)}")
            return False
        except Exception as e:
            logger.error(f"QQ告警发送失败：{dorm_number}, {category_name}, 错误：{e}", exc_info=True)
            return False
    
    def _build_message(self, dorm_number: str, category_name: str, balance: float, 
                      threshold: float, kbalance: Optional[float] = None, 
                      zbalance: Optional[float] = None) -> str:
        """
        构建告警消息
        
        Args:
            dorm_number: 宿舍号
            category_name: 告警类别名称（空调/照明）
            balance: 当前余量（度）
            threshold: 告警阈值（度）
            kbalance: 空调余量（度，可选）
            zbalance: 照明余量（度，可选）
        
        Returns:
            str: 格式化后的告警消息
        """
        message = f"【西华大学电费告警】\n"
        message += f"━━━━━━━━━━━━━━━━━━\n"
        message += f"宿舍号：{dorm_number}\n"
        message += f"告警类别：{category_name}\n"
        message += f"当前余量：{balance:.2f} 度\n"
        message += f"告警阈值：{threshold:.2f} 度\n"
        
        # 显示完整余量信息
        if kbalance is not None or zbalance is not None:
            message += f"\n【完整余量信息】\n"
            if kbalance is not None:
                message += f"  空调余量：{kbalance:.2f} 度"
                if kbalance < threshold:
                    message += " ⚠️"
                message += "\n"
            if zbalance is not None:
                message += f"  照明余量：{zbalance:.2f} 度"
                if zbalance < threshold:
                    message += " ⚠️"
                message += "\n"
        
        message += f"\n⚠️ 请及时充值，避免停电影响正常生活！\n"
        message += f"━━━━━━━━━━━━━━━━━━\n"
        message += f"数据来源：西华大学一卡通宿舍用电小程序\n"
        message += f"管理员QQ：714085964"
        
        return message


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.email_alert = EmailAlert()
        self.qq_alert = QQBotAlert()
    
    def send_alert(self, dorm_number: str, category: str, category_name: str,
                   balance: float, threshold: float,
                   email_enabled: bool = False, 
                   email_address: Optional[str] = None,
                   qq_enabled: bool = False,
                   qq_receiver_id: Optional[str] = None,
                   kbalance: Optional[float] = None,
                   zbalance: Optional[float] = None) -> Dict[str, bool]:
        """
        发送告警
        
        Args:
            dorm_number: 宿舍号
            category: 告警类别（ac/light）
            category_name: 告警类别名称（空调/照明）
            balance: 当前余量（度）
            threshold: 告警阈值（度）
            email_enabled: 是否启用邮件告警
            email_address: 接收邮箱地址
            qq_enabled: 是否启用QQ告警
            qq_receiver_id: QQ接收者ID（群号或用户QQ号，可选）
            kbalance: 空调余量（度，可选）
            zbalance: 照明余量（度，可选）
        
        Returns:
            {'email': bool, 'qq': bool} - 发送结果字典
        """
        results = {'email': False, 'qq': False}
        
        # 发送邮件告警
        if email_enabled:
            try:
                results['email'] = self.email_alert.send(
                    dorm_number=dorm_number,
                    category=category,
                    category_name=category_name,
                    balance=balance,
                    threshold=threshold,
                    email_address=email_address,
                    kbalance=kbalance,
                    zbalance=zbalance
                )
            except Exception as e:
                logger.error(f"邮件告警发送异常：{e}", exc_info=True)
                results['email'] = False
        
        # 发送QQ告警
        if qq_enabled:
            try:
                results['qq'] = self.qq_alert.send(
                    dorm_number=dorm_number,
                    category=category,
                    category_name=category_name,
                    balance=balance,
                    threshold=threshold,
                    kbalance=kbalance,
                    zbalance=zbalance,
                    qq_receiver_id=qq_receiver_id
                )
            except Exception as e:
                logger.error(f"QQ告警发送异常：{e}", exc_info=True)
                results['qq'] = False
        
        return results


def get_alert_manager() -> AlertManager:
    """获取告警管理器实例"""
    return AlertManager()
