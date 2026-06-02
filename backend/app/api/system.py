"""
系统管理API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import CrawlerService, PowerRecordService, AlertRuleService
from app.config import settings
import logging
import requests

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/crawl", summary="手动触发爬虫任务")
async def manual_crawl(db: Session = Depends(get_db)):
    """手动触发一次爬虫任务，重新获取最新余额数据"""
    try:
        logger.info("收到手动触发爬虫任务请求")
        
        # 检查是否有启用的告警规则
        from app.models import AlertRule
        enabled_rules = db.query(AlertRule).filter(AlertRule.enabled == True).all()
        
        if not enabled_rules:
            return {
                "success": False,
                "message": "未找到启用的告警规则，请先在监控面板创建并启用告警规则"
            }
        
        # 检查room_id配置
        rule_without_room_id = [r for r in enabled_rules if not r.room_id]
        if rule_without_room_id:
            return {
                "success": False,
                "message": f"告警规则中未配置room_id，请在监控面板编辑规则并填写房间ID（room_id）"
            }
        
        # 手动触发时，获取数据并检查告警（强制发送告警，忽略防频繁告警限制）
        success = CrawlerService.crawl_and_save(db, force_alert=True, skip_alert=False)
        if success:
            return {
                "success": True,
                "message": "数据获取成功，已更新最新电量"
            }
        else:
            # 获取更详细的错误信息
            error_details = []
            for rule in enabled_rules:
                if rule.room_id:
                    error_details.append(f"宿舍{rule.dorm_number}(room_id={rule.room_id})")
            
            if error_details:
                return {
                    "success": False,
                    "message": f"数据获取失败，请检查：1) 网络连接是否正常 2) 认证信息(openid/JSESSIONID)是否有效 3) room_id是否正确。已尝试：{', '.join(error_details)}"
                }
            else:
                return {
                    "success": False,
                    "message": "数据获取失败，请检查网络连接和认证信息"
                }
    except Exception as e:
        import traceback
        logger.error(f"手动触发爬虫任务异常：{e}", exc_info=True)
        logger.error(f"详细错误信息：{traceback.format_exc()}")
        error_msg = str(e)
        # 提供更友好的错误信息
        if "room_id" in error_msg.lower() or "未配置" in error_msg:
            return {
                "success": False,
                "message": "告警规则中未配置room_id，请在监控面板编辑规则并填写房间ID"
            }
        return {
            "success": False,
            "message": f"数据获取异常：{error_msg}"
        }




@router.post("/report", summary="发送电费实时报告到QQ群")
async def send_power_report(db: Session = Depends(get_db)):
    """按真实流程发送电费报告：使用最新采集记录，只发送空调/照明余额"""
    try:
        dorm_number = str(settings.CRAWLER_DORM_NUMBER)
        latest = PowerRecordService.get_latest_record(db, dorm_number)
        if not latest:
            return {"success": False, "message": "暂无电费记录，请先执行一次爬虫采集"}

        if not settings.QQ_BOT_ENABLED or not settings.QQ_BOT_API_URL:
            return {"success": False, "message": "QQ机器人未启用或API地址未配置"}

        rule = AlertRuleService.get_rule(db, dorm_number)
        receiver = getattr(rule, "qq_receiver_id", None) if rule else None
        if not receiver:
            return {"success": False, "message": "未找到QQ接收配置（请在告警规则中填写群号）"}

        receiver = receiver.strip()
        if receiver.startswith("group:") or receiver.startswith("g:"):
            receiver = receiver.split(":", 1)[1].strip()

        try:
            group_id = int(receiver)
        except ValueError:
            return {"success": False, "message": f"QQ群号配置无效：{receiver}"}

        msg = (
            "【电费实时报告】\n"
            f"宿舍: {latest.dorm_number}\n"
            f"空调余额: {latest.kbalance if latest.kbalance is not None else 'N/A'} 度\n"
            f"照明余额: {latest.zbalance if latest.zbalance is not None else 'N/A'} 度\n"
            f"记录时间: {latest.record_time}\n"
            "来源: 后端实时记录"
        )

        resp = requests.post(
            f"{settings.QQ_BOT_API_URL}/api/send_group_msg",
            json={"group_id": group_id, "message": msg},
            timeout=10,
        )

        if resp.status_code != 200:
            return {"success": False, "message": f"发送失败，HTTP {resp.status_code}", "detail": resp.text[:200]}

        data = resp.json()
        if data.get("status") == "ok" or data.get("retcode") == 0:
            return {"success": True, "message": "电费实时报告发送成功", "report": msg}

        return {"success": False, "message": "发送失败", "detail": data}
    except Exception as e:
        logger.error(f"发送电费实时报告异常：{e}", exc_info=True)
        return {"success": False, "message": f"发送异常：{str(e)}"}

@router.get("/qq-config", summary="获取QQ机器人全局配置")
async def get_qq_config():
    """获取QQ机器人全局配置（群号和用户QQ号）"""
    return {
        "group_id": settings.QQ_BOT_GROUP_ID,
        "user_id": settings.QQ_BOT_USER_ID,
        "enabled": settings.QQ_BOT_ENABLED
    }


@router.get("/config", summary="获取系统配置信息")
async def get_config():
    """获取系统配置信息（宿舍号等）"""
    return {
        "dorm_number": settings.CRAWLER_DORM_NUMBER
    }


@router.get("/qq-status", summary="检查QQ机器人连接状态")
async def check_qq_status():
    """检查QQ机器人（NoneBot和NapCatQQ）的连接状态"""
    import requests
    from app.config import settings
    
    if not settings.QQ_BOT_ENABLED:
        return {
            "success": False,
            "message": "QQ机器人告警未启用（全局配置）",
            "nonebot_running": False,
            "napcat_connected": False
        }
    
    if not settings.QQ_BOT_API_URL:
        return {
            "success": False,
            "message": "QQ机器人API地址未配置",
            "nonebot_running": False,
            "napcat_connected": False
        }
    
    try:
        # 检查NoneBot状态
        response = requests.get(f"{settings.QQ_BOT_API_URL}/api/get_status", timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "ok" and result.get("retcode") == 0:
                data = result.get("data", {})
                return {
                    "success": True,
                    "message": "QQ机器人连接正常",
                    "nonebot_running": True,
                    "napcat_connected": data.get("online", False),
                    "bot_id": data.get("bot_id")
                }
            else:
                error_msg = result.get("msg", "未知错误")
                return {
                    "success": False,
                    "message": f"NoneBot状态异常：{error_msg}",
                    "nonebot_running": True,
                    "napcat_connected": False
                }
        else:
            return {
                "success": False,
                "message": f"无法连接到NoneBot（HTTP {response.status_code}）",
                "nonebot_running": False,
                "napcat_connected": False
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "无法连接到NoneBot，请检查NoneBot是否在运行（端口8080）",
            "nonebot_running": False,
            "napcat_connected": False
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "连接NoneBot超时，请检查NoneBot是否响应正常",
            "nonebot_running": False,
            "napcat_connected": False
        }
    except Exception as e:
        logger.error(f"检查QQ机器人状态异常：{e}", exc_info=True)
        return {
            "success": False,
            "message": f"检查QQ机器人状态时发生异常：{str(e)}",
            "nonebot_running": False,
            "napcat_connected": False
        }
