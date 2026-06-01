"""
CI 环境下的通知模块
使用 PushPlus (https://www.pushplus.plus/) 发送微信消息
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class QQDirectNotifier:
    """
    消息通知器（PushPlus 实现）

    通过 PushPlus 服务发送微信消息。
    使用方式：
      1. 注册 PushPlus (https://www.pushplus.plus/)
      2. 微信扫码登录
      3. 获取 Token
      4. 设置环境变量 QQ_NOTIFY_API_KEY（复用了同一个变量名）
    """

    API_URL = "https://www.pushplus.plus/send"

    def __init__(self):
        self.token = os.getenv("QQ_NOTIFY_API_KEY", "")
        self.enabled = bool(self.token)

    def send(self, title: str, content: str) -> bool:
        if not self.enabled:
            logger.info("消息推送未启用（未配置 QQ_NOTIFY_API_KEY）")
            return False

        try:
            import requests

            logger.info("正在通过 PushPlus 发送消息...")
            resp = requests.post(
                self.API_URL,
                json={
                    "token": self.token,
                    "title": title,
                    "content": content,
                },
                timeout=15,
            )
            result = resp.json()
            if result.get("code") == 200:
                logger.info("消息发送成功")
                return True
            else:
                logger.error(f"消息发送失败: {result}")
                return False

        except ImportError:
            logger.error("缺少 requests 库，无法发送消息")
            return False
        except Exception as e:
            logger.error(f"消息发送异常: {e}")
            return False

    def send_alert(self, dorm_number: str, kbalance: Optional[float] = None,
                   zbalance: Optional[float] = None) -> bool:
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
        title = "❌ 电费检测异常"
        content = f"检测任务执行失败：\n{error_msg}"
        return self.send(title, content)
