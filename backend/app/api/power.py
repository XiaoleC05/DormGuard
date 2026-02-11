"""
电费记录API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.schemas import PowerRecordResponse, PowerRecordCreate
from app.services import PowerRecordService

router = APIRouter()


@router.post("/records", response_model=PowerRecordResponse, summary="创建电费记录")
async def create_record(record: PowerRecordCreate, db: Session = Depends(get_db)):
    """创建电费记录"""
    return PowerRecordService.create_record(db, record)


@router.get("/records/{dorm_number}/latest", response_model=PowerRecordResponse, summary="获取最新记录")
async def get_latest_record(dorm_number: str, db: Session = Depends(get_db)):
    """获取指定宿舍的最新电费记录"""
    try:
        record = PowerRecordService.get_latest_record(db, dorm_number)
        if not record:
            raise HTTPException(status_code=404, detail="未找到记录")
        return record
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"获取最新记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/records/{dorm_number}", response_model=List[PowerRecordResponse], summary="获取记录列表")
async def get_records(
    dorm_number: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取指定宿舍的电费记录列表"""
    try:
        return PowerRecordService.get_records(db, dorm_number, limit)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"获取记录列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/records/{dorm_number}/range", response_model=List[PowerRecordResponse], summary="按日期范围获取记录")
async def get_records_by_range(
    dorm_number: str,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """按日期范围获取电费记录"""
    return PowerRecordService.get_records_by_date_range(db, dorm_number, start_date, end_date)
