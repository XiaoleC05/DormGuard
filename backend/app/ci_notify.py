"""
CI 环境下的通知模块
使用 QMsg 服务 (https://qmsg.zendee.cn/) 直接发送 QQ 消息，无需运行 QQ 客户端
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class QQDirectNotifier:
    """
    QQ 直推通知器

    通过 QMsg 服务 (https://qmsg.zendee.cn/) 发送 QQ 消息。
    使用方式：
      1. 注册 QMsg (https://qmsg.zendee.cn/)
      2. 绑定接收 QQ 号
      3. 获取 API Key
      4. 设置环境变量 QQ_NOTIFY_API_KEY
    """

    API_BASE = "https://qmsg.zendee.cn"

    def __init__(self):
        self.api_key = os.getenv("QQ_NOTIFY_API_KEY", "")
        self.enabled = bool(self.api_key)

    def send(self, title: str, content: str, msg_type: str = "text") -> bool:
        """
        发送 QQ 消息

        Args:
            title: 消息标题
            content: 消息正文
            msg_type: 消息类型 (text/markdown)

        Returns:
            bool: 发送是否成功
        """
        if not self.enabled:
            logger.info("QQ 直推未启用（未配置 QQ_NOTIFY_API_KEY）")
            return False

        try:
            import requests

            message = f"{title}\n{content}"
            url = f"{self.API_BASE}/send/{self.api_key}"

            logger.info("正在通过 QMsg 发送 QQ 消息...")
            resp = requests.post(
                url,
                data={"msg": message, "type": msg_type},
                timeout=15,
            )
            result = resp.json()
            if result.get("code") == 0 or result.get("success"):
                logger.info("QQ 消息发送成功")
                return True
            else:
                logger.error(f"QQ 消息发送失败: {result}")
                return False

        except ImportError:
            logger.error("缺少 requests 库，无法发送 QQ 消息")
            return False
        except Exception as e:
            logger.error(f"QQ 消息发送异常: {e}")
            return False

    def send_alert(self, dorm_number: str, kbalance: Optional[float] = None,
                   zbalance: Optional[float] = None) -> bool:
        """发送电费告警通知"""
        title = "⚠️ 宿舍电费告警"
        content = (
            f"宿舍号：{dorm_number}\n"
            f"━━━━━━━━━━━━━━━━\n"
        )
        if kbalance is not None:
            content += f"空调余量：{kbalance:.2f} 度 ⚠️\n"
        if zbalance is not None:
            content += f"照明余量：{zbalance:.2f} 度 ⚠️\n"
        content += (
            f"\n请及时充值，避免停电！\n"
            f"数据来源：西华大学一卡通"
        )
        return self.send(title, content)

    def send_report(self, dorm_number: str, kbalance: Optional[float] = None,
                    zbalance: Optional[float] = None,
                    kpower: Optional[float] = None,
                    zpower: Optional[float] = None) -> bool:
        """发送电费日报"""
        title = "📊 宿舍电费日报"
        content = (
            f"宿舍号：{dorm_number}\n"
            f"━━━━━━━━━━━━━━━━\n"
        )
        if kbalance is not None:
            content += f"空调余量：{kbalance:.2f} 度\n"
            if kpower is not None:
                content += f"空调用电：{kpower:.2f} 度\n"
        if zbalance is not None:
            content += f"照明余量：{zbalance:.2f} 度\n"
            if zpower is not None:
                content += f"照明用电：{zpower:.2f} 度\n"
        content += (
            f"\n数据来源：西华大学一卡通\n"
            f"https://github.com/XiaoleC05/dorm-power-guard-lite"
        )
        return self.send(title, content)

    def send_error(self, error_msg: str) -> bool:
        """发送错误通知"""
        title = "❌ 电费检测异常"
        content = f"检测任务执行失败：\n{error_msg}"
        return self.send(title, content)
