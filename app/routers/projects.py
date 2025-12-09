# app/routers/projects.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, models, auth
from app.database import get_db

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
)

@router.post("", response_model=schemas.ApiResponse, summary="创建项目", description="创建新的面试项目，关联提纲和AI配置")
async def create_project(project: schemas.ProjectCreate, current_user: models.User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    创建新的面试项目
    
    - **name**: 项目名称，必填
    - **outline_id**: 关联的提纲ID，必填
    - **ai_config_id**: 关联的AI配置ID，必填
    - **status**: 项目状态，默认active
    
    返回:
    - 成功: 200 OK，返回创建的项目详情和访谈链接
    - 失败: 404 Not Found，提纲或AI配置不存在
    - 失败: 409 Conflict，提纲或AI配置已关联到其他项目
    """
    try:
        new_project = await crud.create_project(db, project)
        
        # 构造返回给前端的“访谈链接”
        # 注意：实际生产中应该是您的域名，这里我们假设是被访谈者页面
        guest_link = f"P-GUEST_INTERVIEW.html?projectId={new_project.id}"
        
        return {
            "code": 200,
            "message": "Project published successfully",
            "data": {
                "id": new_project.id,
                "name": new_project.name,
                "guest_link": guest_link,
                "outline_id": new_project.outline_id,
                "ai_config_id": new_project.ai_config_id,
                "status": new_project.status
            }
        }
    except ValueError as e:
        return {
            "code": 404,
            "message": str(e),
            "data": None
        }
    except Exception as e:
        # 检查是否是唯一约束冲突
        if "unique constraint" in str(e).lower():
            return {
                "code": 409,
                "message": "Outline or AI config is already associated with another project",
                "data": None
            }
        return {
            "code": 500,
            "message": f"Failed to create project: {str(e)}",
            "data": None
        }


# 新增：获取项目列表
@router.get("", response_model=schemas.ApiResponse, summary="获取项目列表", description="获取面试项目列表，支持分页和按提纲ID过滤")
async def read_projects(skip: int = 0, limit: int = 20, outline_id: int = None, db: AsyncSession = Depends(get_db)):
    """
    获取面试项目列表
    
    - **skip**: 跳过的记录数，默认0
    - **limit**: 返回的记录数，默认20，最大100
    - **outline_id**: 提纲ID，可选，用于过滤关联的项目
    
    返回:
    - 成功: 200 OK，返回项目列表和分页信息
    """
    # 限制最大返回数量
    limit = min(limit, 100)
    
    projects = await crud.get_projects(db, skip=skip, limit=limit, outline_id=outline_id)
    
    # 获取项目总数
    from sqlalchemy import func
    from sqlalchemy.future import select
    base_query = select(func.count(models.Project.id))
    if outline_id:
        base_query = base_query.where(models.Project.outline_id == outline_id)
    total_result = await db.execute(base_query)
    total = total_result.scalar() or 0
    
    return {
        "code": 200, 
        "message": "success", 
        "data": {
            "items": projects,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    }


# 新增：获取单个项目详情
@router.get("/{project_id}", response_model=schemas.ApiResponse, summary="获取项目详情", description="根据ID获取单个面试项目的详细信息")
async def read_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """
    获取单个面试项目详情
    
    - **project_id**: 项目ID，必填
    
    返回:
    - 成功: 200 OK，返回项目详情和关联的提纲标题
    - 失败: 404 Not Found，项目不存在
    """
    # 直接在路由中实现复杂查询，获取项目详情和关联的提纲标题
    from sqlalchemy.future import select
    from app.models import Outline
    
    result = await db.execute(
        select(models.Project, Outline.title.label("outline_title"))
        .join(Outline, models.Project.outline_id == Outline.id)
        .where(models.Project.id == project_id)
    )
    
    row = result.first()
    if not row:
        return {"code": 404, "message": "Project not found", "data": None}
    
    proj, outline_title = row
    
    # 手动构造返回字典
    project_dict = {
        "id": proj.id,
        "outline_id": proj.outline_id,
        "ai_config_id": proj.ai_config_id,
        "status": proj.status,
        "created_at": proj.created_at,
        "outline_title": outline_title,
        "session_count": 0  # 暂时硬编码为0，后续可从session表聚合查询
    }
    
    return {"code": 200, "message": "success", "data": project_dict}


# 新增：更新项目
@router.put("/{project_id}", response_model=schemas.ApiResponse, summary="更新项目", description="根据ID更新面试项目的内容")
async def update_project(project_id: str, update_data: dict, current_user: models.User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    更新面试项目
    
    - **project_id**: 项目ID，必填
    - **update_data**: 更新数据，支持更新status和ai_config_id字段
    
    返回:
    - 成功: 200 OK，返回更新后的项目详情
    - 失败: 404 Not Found，项目不存在
    """
    # 获取现有项目
    existing_project = await crud.get_project(db, project_id)
    if not existing_project:
        return {"code": 404, "message": "Project not found", "data": None}
    
    # 更新项目，只更新提供的字段
    if "status" in update_data:
        existing_project.status = update_data["status"]
    if "ai_config_id" in update_data:
        existing_project.ai_config_id = update_data["ai_config_id"]
    
    # 保存更新
    db.add(existing_project)
    await db.commit()
    await db.refresh(existing_project)
    
    # 构造返回给前端的“访谈链接”
    guest_link = f"P-GUEST_INTERVIEW.html?projectId={existing_project.id}"
    
    return {
        "code": 200,
        "message": "Project updated successfully",
        "data": {
            "id": existing_project.id,
            "guest_link": guest_link,
            "outline_id": existing_project.outline_id,
            "ai_config_id": existing_project.ai_config_id,
            "status": existing_project.status
        }
    }

# 新增：删除项目
@router.delete("/{project_id}", response_model=schemas.ApiResponse, summary="删除项目", description="根据ID删除面试项目")
async def delete_project(project_id: str, current_user: models.User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    删除面试项目
    
    - **project_id**: 项目ID，必填
    
    返回:
    - 成功: 200 OK，项目删除成功
    - 失败: 404 Not Found，项目不存在
    """
    # 获取现有项目
    existing_project = await crud.get_project(db, project_id)
    if not existing_project:
        return {"code": 404, "message": "Project not found", "data": None}
    
    # 删除项目
    await db.delete(existing_project)
    await db.commit()
    
    return {
        "code": 200,
        "message": "Project deleted successfully",
        "data": None
    }

