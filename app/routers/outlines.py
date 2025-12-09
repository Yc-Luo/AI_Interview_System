from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import schemas, crud, models, auth
from app.database import get_db
from app.config.logging import logger

# 创建路由对象，前缀是 /api/outlines
router = APIRouter(
    prefix="/api/outlines",
    tags=["outlines"],
)

# 1. 创建提纲接口
@router.post("", response_model=schemas.ApiResponse, summary="创建提纲", description="创建新的面试提纲，包含多个模块和问题")
async def create_new_outline(
    outline: schemas.OutlineCreate, 
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的面试提纲
    
    - **title**: 提纲标题，必填
    - **description**: 提纲描述，可选
    - **modules**: 提纲模块列表，每个模块包含标题和问题列表
    
    返回:
    - 成功: 200 OK，返回创建的提纲详情
    - 失败: 401 Unauthorized，未授权访问
    - 失败: 500 Internal Server Error，创建提纲失败
    """
    try:
        logger.info(f"用户创建提纲请求: 用户ID={current_user.id}, 用户名={current_user.username}, 提纲标题={outline.title}")
        
        # 使用从认证系统获取的真实用户ID
        new_outline = await crud.create_outline(db=db, outline=outline, user_id=current_user.id)
        
        logger.info(f"提纲创建成功: 提纲ID={new_outline.id}, 标题={new_outline.title}, 创建者ID={current_user.id}")
        
        # 手动将模型对象转换为字典，确保Pydantic可以序列化
        outline_dict = {
            "id": new_outline.id,
            "title": new_outline.title,
            "description": new_outline.description,
            "created_at": new_outline.created_at,
            "modules": [
                {
                    "title": module.title,
                    "questions": [
                        {
                            "content": question.content,
                            "is_key_question": question.is_key_question,
                            "follow_up_directions": question.follow_up_directions
                        }
                        for question in module.questions
                    ]
                }
                for module in new_outline.modules
            ]
        }
        return {
            "code": 200,
            "message": "Outline created successfully",
            "data": outline_dict
        }
    except Exception as e:
        logger.error(f"提纲创建失败: 用户ID={current_user.id}, 用户名={current_user.username}, 错误信息={str(e)}")
        return {
            "code": 500,
            "message": f"Failed to create outline: {str(e)}",
            "data": None
        }


# 2. 获取提纲列表接口
@router.get("", response_model=schemas.ApiResponse, summary="获取提纲列表", description="获取所有面试提纲列表，支持分页")
async def read_outlines(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """
    获取面试提纲列表
    
    - **skip**: 跳过的记录数，默认0
    - **limit**: 返回的记录数，默认20，最大100
    
    返回:
    - 成功: 200 OK，返回提纲列表和分页信息
    """
    # 限制最大返回数量
    limit = min(limit, 100)
    
    # 获取提纲总数
    from sqlalchemy import func
    from sqlalchemy.future import select
    total_result = await db.execute(select(func.count(models.Outline.id)))
    total = total_result.scalar() or 0
    
    # 获取分页数据
    outlines = await crud.get_outlines(db, skip=skip, limit=limit)
    
    # 手动将模型对象转换为字典，确保Pydantic可以序列化
    outlines_dict = [
        {
            "id": outline.id,
            "title": outline.title,
            "description": outline.description,
            "created_at": outline.created_at,
            "modules": [
                {
                    "title": module.title,
                    "questions": [
                        {
                            "content": question.content,
                            "is_key_question": question.is_key_question,
                            "follow_up_directions": question.follow_up_directions
                        }
                        for question in module.questions
                    ]
                }
                for module in outline.modules
            ]
        }
        for outline in outlines
    ]
    
    # 构建分页响应
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": outlines_dict,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    }


# 3. 获取单个提纲详情接口
@router.get("/{outline_id}", response_model=schemas.ApiResponse, summary="获取提纲详情", description="根据ID获取单个面试提纲的详细信息，包含关联的AI配置")
async def read_outline(outline_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取单个面试提纲详情
    
    - **outline_id**: 提纲ID，必填
    
    返回:
    - 成功: 200 OK，返回提纲详情，包含关联的AI配置
    - 失败: 404 Not Found，提纲不存在
    """
    outline = await crud.get_outline(db, outline_id=outline_id)
    if not outline:
        return {
            "code": 404,
            "message": "Outline not found",
            "data": None
        }
    
    # 查询关联的AI配置
    from sqlalchemy import select
    ai_config_result = await db.execute(
        select(models.AIConfig).where(models.AIConfig.outline_id == outline_id)
    )
    ai_config = ai_config_result.scalar_one_or_none()
    
    # 手动将模型对象转换为字典，确保Pydantic可以序列化
    outline_dict = {
        "id": outline.id,
        "title": outline.title,
        "description": outline.description,
        "created_at": outline.created_at,
        "modules": [
            {
                "title": module.title,
                "questions": [
                    {
                        "content": question.content,
                        "is_key_question": question.is_key_question,
                        "follow_up_directions": question.follow_up_directions
                    }
                    for question in module.questions
                ]
            }
            for module in outline.modules
        ],
        "ai_config": {
            "id": ai_config.id,
            "name": ai_config.name,
            "role_settings": ai_config.role_settings,
            "strategy": ai_config.strategy
        } if ai_config else None
    }
    return {
        "code": 200,
        "message": "success",
        "data": outline_dict
    }


# 4. 删除提纲接口
@router.delete("/{outline_id}", response_model=schemas.ApiResponse, summary="删除提纲", description="根据ID删除面试提纲")
async def delete_outline(outline_id: int, db: AsyncSession = Depends(get_db)):
    """
    删除面试提纲
    
    - **outline_id**: 提纲ID，必填
    
    返回:
    - 成功: 200 OK，提纲删除成功
    """
    await crud.delete_outline(db, outline_id=outline_id)
    return {
        "code": 200,
        "message": "Outline deleted successfully",
        "data": None
    }


# 5. 更新提纲接口
@router.put("/{outline_id}", response_model=schemas.ApiResponse, summary="更新提纲", description="根据ID更新面试提纲的内容")
async def update_outline(
    outline_id: int,
    outline: schemas.OutlineCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新面试提纲
    
    - **outline_id**: 提纲ID，必填
    - **outline**: 提纲更新内容，包含标题、描述和模块列表
    
    返回:
    - 成功: 200 OK，返回更新后的提纲详情
    - 失败: 401 Unauthorized，未授权访问
    - 失败: 404 Not Found，提纲不存在
    """
    updated_outline = await crud.update_outline(db=db, outline_id=outline_id, outline=outline)
    if not updated_outline:
        return {
            "code": 404,
            "message": "Outline not found",
            "data": None
        }
    # 手动将模型对象转换为字典，确保Pydantic可以序列化
    outline_dict = {
        "id": updated_outline.id,
        "title": updated_outline.title,
        "description": updated_outline.description,
        "created_at": updated_outline.created_at,
        "modules": [
            {
                "title": module.title,
                "questions": [
                    {
                        "content": question.content,
                        "is_key_question": question.is_key_question,
                        "follow_up_directions": question.follow_up_directions
                    }
                    for question in module.questions
                ]
            }
            for module in updated_outline.modules
        ]
    }
    return {
        "code": 200,
        "message": "Outline updated successfully",
        "data": outline_dict
    }