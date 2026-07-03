"""QQ 机器人告警模块"""
import logging
from typing import Dict, Optional

import requests

from app.config import settings

logger = logging.getLogger(__name__)


def _parse_group_id(raw: Optional[str]) -> Optional[int]:
    """解析告警群号，仅支持群号（纯数字）。"""
    if not raw or not str(raw).strip():
        return None
    value = str(raw).strip()
    if value.startswith("group:") or value.startswith("g:"):
        value = value.split(":", 1)[1].strip()
    try:
        return int(value)
    except ValueError:
        return None


class QQBotAlert:
    """QQ机器人告警（仅群消息）"""

    def __init__(self):
        self.enabled = settings.QQ_BOT_ENABLED
        self.api_url = settings.QQ_BOT_API_URL
        self.bot_id = settings.QQ_BOT_ID
        self.group_id = settings.QQ_BOT_GROUP_ID

    def send(
        self,
        dorm_number: str,
        category_name: str,
        balance: float,
        threshold: float,
        kbalance: Optional[float] = None,
        zbalance: Optional[float] = None,
    ) -> bool:
        if not self.enabled:
            logger.debug("QQ告警未启用（全局配置）")
            return False

        if not self.api_url:
            logger.error("QQ机器人API地址未配置")
            return False

        group_num = _parse_group_id(self.group_id)
        if group_num is None:
            logger.error("未配置告警群号（请在系统配置中填写 QQ_BOT_GROUP_ID）")
            return False

        try:
            message = self._build_message(
                dorm_number, category_name, balance, threshold, kbalance, zbalance
            )
            url = f"{self.api_url}/api/send_group_msg"
            data = {"group_id": group_num, "message": message}
            headers = {"Content-Type": "application/json"}

            logger.info(
                f"正在发送QQ群告警到群 {group_num}：{dorm_number}, {category_name}余量 {balance:.2f} 度"
            )
            response = requests.post(url, json=data, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "ok" or result.get("retcode") == 0:
                    logger.info(
                        f"QQ群告警发送成功：{dorm_number}, {category_name}余量 {balance:.2f} 度 -> 群 {group_num}"
                    )
                    return True
                error_msg = result.get("msg", str(result))
                if "no bots" in error_msg.lower() or "no bot" in error_msg.lower():
                    error_msg = "NoneBot未连接NapCatQQ，请检查 NapCat 是否已登录并连接"
                logger.error(f"QQ告警发送失败（API返回错误）：{error_msg}")
                return False

            logger.error(
                f"QQ告警API请求失败：HTTP {response.status_code}, 响应：{response.text[:200]}"
            )
            return False
        except requests.exceptions.Timeout:
            logger.error("QQ告警发送超时：NoneBot可能响应缓慢或NapCat未连接")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"QQ告警连接失败：无法连接到NoneBot（{self.api_url}）：{e}")
            return False
        except Exception as e:
            logger.error(f"QQ告警发送失败：{dorm_number}, {category_name}, 错误：{e}", exc_info=True)
            return False

    def _build_message(
        self,
        dorm_number: str,
        category_name: str,
        balance: float,
        threshold: float,
        kbalance: Optional[float] = None,
        zbalance: Optional[float] = None,
    ) -> str:
        message = "【宿舍电费告警】\n"
        message += "━━━━━━━━━━━━━━━━━━\n"
        message += f"宿舍号：{dorm_number}\n"
        message += f"告警类型：{category_name}余量不足\n"
        message += f"当前余量：{balance:.2f} 度\n"
        message += f"告警阈值：{threshold:.2f} 度\n"

        if kbalance is not None or zbalance is not None:
            message += "\n📊 详细余量：\n"
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

        message += "\n⚠️ 请及时充值，避免停电影响正常生活！\n"
        message += "━━━━━━━━━━━━━━━━━━\n"
        message += "数据来源：西华大学一卡通宿舍用电小程序\n"
        message += f"机器人QQ：{self.bot_id} · 告警群：{self.group_id}"
        return message


class AlertManager:
    """告警管理器"""

    def __init__(self):
        self.qq_alert = QQBotAlert()

    def send_alert(
        self,
        dorm_number: str,
        category_name: str,
        balance: float,
        threshold: float,
        qq_enabled: bool = False,
        kbalance: Optional[float] = None,
        zbalance: Optional[float] = None,
    ) -> Dict[str, bool]:
        results = {"qq": False}
        if not qq_enabled:
            return results
        try:
            results["qq"] = self.qq_alert.send(
                dorm_number=dorm_number,
                category_name=category_name,
                balance=balance,
                threshold=threshold,
                kbalance=kbalance,
                zbalance=zbalance,
            )
        except Exception as e:
            logger.error(f"QQ告警发送异常：{e}", exc_info=True)
            results["qq"] = False
        return results


_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
