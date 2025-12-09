# app/routers/participants.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_db

router = APIRouter(
    prefix="/api/participants",
    tags=["participants"],
)

@router.post("", response_model=schemas.ApiResponse, summary="创建参与者", description="创建新的参与者，关联到指定项目")
async def create_participant(participant: schemas.ParticipantCreate, db: AsyncSession = Depends(get_db)):
    """
    创建新的参与者
    
    - **project_id**: 项目ID，必填，参与者关联的项目
    - **metadata**: 参与者元数据，可选，包含浏览器信息、设备信息等
    
    返回:
    - 成功: 200 OK，返回创建的参与者ID和项目ID
    - 失败: 404 Not Found，项目不存在
    """
    try:
        new_participant = await crud.create_participant(db, participant)
        
        return {
            "code": 200,
            "message": "Participant created successfully",
            "data": {
                "participant_id": new_participant.id,
                "project_id": new_participant.project_id,
                "created_at": new_participant.created_at
            }
        }
    except ValueError as e:
        return {"code": 404, "message": str(e), "data": None}
    except Exception as e:
        return {"code": 500, "message": f"Failed to create participant: {str(e)}", "data": None}

@router.get("/info", response_model=schemas.ApiResponse, summary="获取参与者信息", description="根据参与者ID获取参与者信息")
async def get_participant_info(participant_id: str, db: AsyncSession = Depends(get_db)):
    """
    获取参与者信息
    
    - **participant_id**: 参与者ID，必填
    
    返回:
    - 成功: 200 OK，返回参与者详情
    - 失败: 404 Not Found，参与者不存在
    """
    participant = await crud.get_participant(db, participant_id)
    if not participant:
        return {"code": 404, "message": "Participant not found", "data": None}
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": participant.id,
            "project_id": participant.project_id,
            "created_at": participant.created_at,
            "last_accessed_at": participant.last_accessed_at,
            "participant_metadata": participant.participant_metadata
        }
    }

@router.put("/access", response_model=schemas.ApiResponse, summary="更新参与者访问时间", description="更新参与者的最后访问时间")
async def update_participant_access_time(participant_id: str, db: AsyncSession = Depends(get_db)):
    """
    更新参与者的最后访问时间
    
    - **participant_id**: 参与者ID，必填
    
    返回:
    - 成功: 200 OK，返回更新后的最后访问时间
    - 失败: 404 Not Found，参与者不存在
    """
    participant = await crud.update_participant_access(db, participant_id)
    if not participant:
        return {"code": 404, "message": "Participant not found", "data": None}
    
    return {
        "code": 200,
        "message": "Access time updated successfully",
        "data": {
            "participant_id": participant.id,
            "last_accessed_at": participant.last_accessed_at
        }
    }

@router.get("", response_model=schemas.ApiResponse, summary="获取参与者列表", description="获取参与者列表，支持按项目ID过滤和分页")
async def read_participants(project_id: str = None, skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """
    获取参与者列表
    
    - **project_id**: 项目ID，可选，用于过滤关联的参与者
    - **skip**: 跳过的记录数，默认0
    - **limit**: 返回的记录数，默认20，最大100
    
    返回:
    - 成功: 200 OK，返回参与者列表和分页信息
    """
    # 限制最大返回数量
    limit = min(limit, 100)
    
    from sqlalchemy.future import select
    from sqlalchemy import func
    from app.models import Participant
    
    # 构建基本查询
    base_query = select(Participant)
    if project_id:
        base_query = base_query.where(Participant.project_id == project_id)
    
    # 获取总记录数
    count_query = select(func.count(Participant.id))
    if project_id:
        count_query = count_query.where(Participant.project_id == project_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 获取分页数据
    result = await db.execute(
        base_query.offset(skip).limit(limit)
    )
    participants = result.scalars().all()
    
    # 手动将模型对象转换为字典
    participants_dict = [
        {
            "id": participant.id,
            "project_id": participant.project_id,
            "created_at": participant.created_at,
            "last_accessed_at": participant.last_accessed_at,
            "participant_metadata": participant.participant_metadata
        }
        for participant in participants
    ]
    
    # 构建分页响应
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": participants_dict,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    }
