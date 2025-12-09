# app/routers/ai_configs.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_db

router = APIRouter(
    prefix="/api/ai-configs",
    tags=["ai-configs"],
)

@router.post("", response_model=schemas.ApiResponse, summary="创建AI配置", description="创建新的AI面试配置，包含角色设置和策略")
async def create_ai_config(config: schemas.AIConfigCreate, db: AsyncSession = Depends(get_db)):
    """
    创建新的AI面试配置
    
    - **name**: 配置名称，必填
    - **role_settings**: AI角色设置，包含角色、性格、语气等
    - **strategy**: AI面试策略，包含问题顺序、追问深度等
    - **outline_id**: 关联的提纲ID，可选
    
    返回:
    - 成功: 200 OK，返回创建的配置ID
    """
    new_config = await crud.create_ai_config(db, config)
    return {
        "code": 200,
        "message": "success",
        "data": {"id": new_config.id}
    }

@router.get("/{config_id}", response_model=schemas.ApiResponse, summary="获取AI配置详情", description="根据ID获取单个AI面试配置的详细信息")
async def read_ai_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取单个AI面试配置详情
    
    - **config_id**: 配置ID，必填
    
    返回:
    - 成功: 200 OK，返回配置详情
    - 失败: 404 Not Found，配置不存在
    """
    config = await crud.get_ai_config(db, config_id)
    if config is None:
        return {
            "code": 404,
            "message": "Config not found",
            "data": None
        }
    # 手动将模型对象转换为字典，确保Pydantic可以序列化
    config_dict = {
        "id": config.id,
        "name": config.name,
        "role_settings": config.role_settings,
        "strategy": config.strategy,
        "outline_id": config.outline_id
    }
    return {
        "code": 200,
        "message": "success",
        "data": config_dict
    }

@router.get("", response_model=schemas.ApiResponse, summary="获取AI配置列表", description="获取AI面试配置列表，支持按提纲ID过滤")
async def read_ai_configs(outline_id: int = None, skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """
    获取AI面试配置列表
    
    - **outline_id**: 提纲ID，可选，用于过滤关联的配置
    - **skip**: 跳过的记录数，默认0
    - **limit**: 返回的记录数，默认20，最大100
    
    返回:
    - 成功: 200 OK，返回配置列表和分页信息
    """
    # 限制最大返回数量
    limit = min(limit, 100)
    
    # 获取配置列表
    configs = await crud.get_ai_configs(db, outline_id=outline_id, skip=skip, limit=limit)
    
    # 获取配置总数
    from sqlalchemy import func
    from sqlalchemy.future import select
    from app.models import AIConfig
    
    query = select(func.count(AIConfig.id))
    if outline_id:
        query = query.where(AIConfig.outline_id == outline_id)
    
    total_result = await db.execute(query)
    total = total_result.scalar() or 0
    
    # 手动将模型对象转换为字典，确保Pydantic可以序列化
    configs_dict = [
        {
            "id": config.id,
            "name": config.name,
            "role_settings": config.role_settings,
            "strategy": config.strategy,
            "outline_id": config.outline_id
        }
        for config in configs
    ]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": configs_dict,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    }

@router.put("/{config_id}", response_model=schemas.ApiResponse, summary="更新AI配置", description="根据ID更新AI面试配置的内容")
async def update_ai_config(config_id: int, config: schemas.AIConfigCreate, db: AsyncSession = Depends(get_db)):
    """
    更新AI面试配置
    
    - **config_id**: 配置ID，必填
    - **config**: 配置更新内容，包含名称、角色设置、策略和关联的提纲ID
    
    返回:
    - 成功: 200 OK，返回更新后的配置详情
    - 失败: 404 Not Found，配置不存在
    """
    updated_config = await crud.update_ai_config(db, config_id, config)
    if updated_config is None:
        return {
            "code": 404,
            "message": "Config not found",
            "data": None
        }
    # 手动将模型对象转换为字典，确保Pydantic可以序列化
    config_dict = {
        "id": updated_config.id,
        "name": updated_config.name,
        "role_settings": updated_config.role_settings,
        "strategy": updated_config.strategy,
        "outline_id": updated_config.outline_id
    }
    return {
        "code": 200,
        "message": "success",
        "data": config_dict
    }

@router.delete("/{config_id}", response_model=schemas.ApiResponse, summary="删除AI配置", description="根据ID删除AI面试配置")
async def delete_ai_config(config_id: int, db: AsyncSession = Depends(get_db)):
    """
    删除AI面试配置
    
    - **config_id**: 配置ID，必填
    
    返回:
    - 成功: 200 OK，返回删除成功信息
    - 失败: 404 Not Found，配置不存在
    """
    deleted_config = await crud.delete_ai_config(db, config_id)
    if deleted_config is None:
        return {
            "code": 404,
            "message": "Config not found",
            "data": None
        }
    return {
        "code": 200,
        "message": "AI config deleted successfully",
        "data": {"id": config_id}
    }