from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app import crud, models
from app.config.logging import logger
from app.utils.excel_helper import generate_excel_bytes

router = APIRouter(prefix="/api/export", tags=["export"])


@router.post("/selected", summary="导出选中内容")
async def export_selected(
    session_ids: List[str] = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """
    导出选中的会话内容
    
    - **session_ids**: 会话ID列表
    """
    try:
        # 1. 转换 ID 类型 (防止数据库是 Int 但前端传了 Str)
        # 如果你的数据库 ID 是整数，这里强转一下更安全；如果是 UUID 字符串，则不需要 int()
        # safe_ids = [int(sid) for sid in session_ids] 
        safe_ids = session_ids 

        # 2. ✅ 正确的 ORM 查询写法
        # 使用 select(模型) 而不是 select(表)
        stmt = select(models.Session).where(models.Session.id.in_(safe_ids))
        result = await db.execute(stmt)
        sessions = result.scalars().all() # scalars() 获取 ORM 对象列表
        
        if not sessions:
            logger.warning("未找到选中的会话数据")
        
        # 3. 生成Excel
        excel_file = generate_excel_bytes(sessions)
        
        # 4. 返回
        headers = {'Content-Disposition': 'attachment; filename="selected_interviews.xlsx"'}
        return StreamingResponse(
            excel_file,
            headers=headers,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        import traceback
        logger.error(f"导出选中内容失败: {e}")
        logger.error(traceback.format_exc()) # 打印详细报错
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/project/{project_id}", summary="导出项目所有内容")
async def export_project_all(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    导出指定项目下的所有会话内容
    
    - **project_id**: 项目ID
    """
    try:
        # ✅ 正确的 ORM 查询写法
        stmt = select(models.Session).where(models.Session.project_id == project_id)
        result = await db.execute(stmt)
        sessions = result.scalars().all()
        
        excel_file = generate_excel_bytes(sessions)
        
        headers = {'Content-Disposition': f'attachment; filename="project_{project_id}_all.xlsx"'}
        return StreamingResponse(
            excel_file,
            headers=headers,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        import traceback
        logger.error(f"导出项目所有内容失败: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/session/{session_id}", summary="导出单个会话")
async def export_single_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    导出单个会话内容
    
    - **session_id**: 会话ID
    """
    try:
        # ✅ 正确的 ORM 查询写法
        stmt = select(models.Session).where(models.Session.id == session_id)
        result = await db.execute(stmt)
        session = result.scalars().first() # 获取单个对象
        
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        excel_file = generate_excel_bytes([session])
        
        headers = {'Content-Disposition': f'attachment; filename="session_{session_id}_export.xlsx"'}
        return StreamingResponse(
            excel_file,
            headers=headers,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"导出单个会话失败: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
