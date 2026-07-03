from fastapi import APIRouter, Depends
from app.api import power, alert, system, auth_routes, admin
from app.auth import get_current_user

router = APIRouter()

router.include_router(auth_routes.router, prefix="/auth", tags=["登录"])
router.include_router(
    power.router,
    prefix="/power",
    tags=["电费记录"],
    dependencies=[Depends(get_current_user)],
)
router.include_router(
    alert.router,
    prefix="/alert",
    tags=["告警管理"],
    dependencies=[Depends(get_current_user)],
)
router.include_router(
    system.router,
    prefix="/system",
    tags=["系统管理"],
    dependencies=[Depends(get_current_user)],
)
router.include_router(admin.router, prefix="/admin", tags=["管理配置"])
