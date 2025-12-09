from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import schemas

router = APIRouter(
    prefix="/api/activities",
    tags=["activities"],
)

@router.get("", response_model=schemas.ApiResponse, summary="获取最近活动", description="获取系统最近活动记录")
async def get_activities(db: AsyncSession = Depends(get_db)):
    """
    获取系统最近活动记录
    
    返回:
    - 成功: 200 OK，返回活动列表
    """
    # 目前返回空列表，因为活动功能尚未实现
    return {
        "code": 200,
        "message": "success",
        "data": []
    }
