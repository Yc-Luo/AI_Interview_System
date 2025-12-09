# app/routers/sessions.py

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, delete, update
from app import schemas, crud, models
from app.database import get_db
from app.utils.excel_helper import generate_excel_bytes
from datetime import datetime, timezone
from typing import List

router = APIRouter(
    prefix="/api/sessions",
    tags=["sessions"],
)

# ==========================================
# 1. 静态路由 (必须放在动态路由 /{id} 之前)
# ==========================================

@router.post("", response_model=schemas.ApiResponse, summary="创建会话")
async def start_new_session(session: schemas.SessionCreate, db: AsyncSession = Depends(get_db)):
    # ... (代码保持不变) ...
    project = await crud.get_project(db, session.project_id)
    if not project:
        return {"code": 404, "message": "Project not found"}
    new_session = await crud.create_session(db, session)
    return {
        "code": 200, 
        "message": "Session started", 
        "data": {"session_id": new_session.id, "project_id": new_session.project_id}
    }

@router.get("", response_model=schemas.ApiResponse, summary="获取会话列表")
async def read_sessions(project_id: str = None, skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    # ... (代码保持不变) ...
    limit = min(limit, 100)
    base_query = select(models.Session)
    if project_id:
        base_query = base_query.where(models.Session.project_id == project_id)
    
    count_query = select(func.count(models.Session.id))
    if project_id:
        count_query = count_query.where(models.Session.project_id == project_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 按时间倒序排列（通常列表页需要最新的在前面）
    base_query = base_query.order_by(models.Session.created_at.desc()) 
    
    result = await db.execute(base_query.offset(skip).limit(limit))
    sessions = result.scalars().all()
    
    sessions_dict = [
        {
            "id": session.id,
            "project_id": session.project_id,
            "interviewee_info": session.interviewee_info,
            "transcript": session.transcript,
            "start_time": session.start_time,
            "is_starred": session.is_starred,
            "note": session.note,
            "created_at": session.created_at # 建议直接用 created_at
        }
        for session in sessions
    ]
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": sessions_dict,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    }

@router.get("/stats", response_model=schemas.ApiResponse, summary="获取会话统计")
async def get_session_stats(db: AsyncSession = Depends(get_db)):
    # ... (代码保持不变) ...
    result = await db.execute(select(func.count(models.Session.id)))
    total = result.scalar() or 0
    return {"code": 200, "message": "success", "data": {"total": total}}

# ✅ 修正：将 export 移到了 /{id} 之前
@router.get("/export", summary="导出会话数据", response_model=None)
async def export_sessions(
    project_id: str = None,
    ids: str = None,
    db: AsyncSession = Depends(get_db)
):
    try:
        base_query = select(models.Session)
        
        if project_id:
            base_query = base_query.where(models.Session.project_id == project_id)
        elif ids:
            session_ids = ids.split(",")
            base_query = base_query.where(models.Session.id.in_(session_ids))
        else:
            return JSONResponse(
                status_code=400, 
                content={"code": 400, "message": "Either project_id or ids is required"}
            )
        
        result = await db.execute(base_query)
        sessions = result.scalars().all()
        
        if not sessions:
            # 如果是导出请求但没有数据，还是建议返回一个空的 Excel 或者明确的提示，
            # 这里的 JSON 返回可能会导致前端处理 Blob 时报错，但逻辑上是通的
            return JSONResponse(
                content={"code": 200, "message": "No sessions found", "data": []}
            )
        
        excel_bytes = generate_excel_bytes(sessions)
        
        filename = f"export_{project_id or 'selected'}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition" # 建议加上这行，防止前端读不到文件名
            }
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"code": 500, "message": str(e)})

# ✅ 修正：将 batch 删除移到了 /{id} 之前
@router.delete("/batch", response_model=schemas.ApiResponse, summary="批量删除会话")
async def delete_sessions_batch(request: dict = Body(...), db: AsyncSession = Depends(get_db)):
    ids = request.get("ids", [])
    if not ids:
        return {"code": 400, "message": "No session IDs provided"}
    
    # 批量删除
    await db.execute(delete(models.Session).where(models.Session.id.in_(ids)))
    await db.commit()
    
    return {
        "code": 200,
        "message": f"Successfully deleted {len(ids)} sessions",
        "data": {"deleted_count": len(ids)}
    }


# ==========================================
# 2. 动态路由 (必须放在最后)
# ==========================================

@router.put("/{id}/star", response_model=schemas.ApiResponse)
async def update_session_star(id: str, request: schemas.StarRequest, db: AsyncSession = Depends(get_db)):
    # ... (代码保持不变) ...
    result = await db.execute(select(models.Session).where(models.Session.id == id))
    session = result.scalar_one_or_none()
    if not session:
        return {"code": 404, "message": "Session not found"}
    await db.execute(update(models.Session).where(models.Session.id == id).values(is_starred=request.is_starred))
    await db.commit()
    return {"code": 200, "message": "Star status updated", "data": {"is_starred": request.is_starred}}

@router.put("/{id}/note", response_model=schemas.ApiResponse)
async def update_session_note(id: str, request: schemas.NoteRequest, db: AsyncSession = Depends(get_db)):
    # ... (代码保持不变) ...
    result = await db.execute(select(models.Session).where(models.Session.id == id))
    session = result.scalar_one_or_none()
    if not session:
        return {"code": 404, "message": "Session not found"}
    await db.execute(update(models.Session).where(models.Session.id == id).values(note=request.note))
    await db.commit()
    return {"code": 200, "message": "Note updated", "data": {"note": request.note}}

@router.put("/{id}/end", response_model=schemas.ApiResponse)
async def end_session(id: str, db: AsyncSession = Depends(get_db)):
    # ... (代码保持不变) ...
    result = await db.execute(select(models.Session).where(models.Session.id == id))
    session = result.scalar_one_or_none()
    if not session:
        return {"code": 404, "message": "Session not found"}
    now = datetime.now(timezone.utc)
    await db.execute(update(models.Session).where(models.Session.id == id).values(end_time=now))
    await db.commit()
    return {"code": 200, "message": "Session ended", "data": {"session_id": id, "end_time": now}}

@router.get("/{id}", response_model=schemas.ApiResponse)
async def get_session_detail(id: str, db: AsyncSession = Depends(get_db)):
    # ... (代码保持不变) ...
    result = await db.execute(select(models.Session).where(models.Session.id == id))
    session = result.scalar_one_or_none()
    if not session:
        return {"code": 404, "message": "Session not found"}
    session_dict = {
        "id": session.id,
        "project_id": session.project_id,
        "interviewee_info": session.interviewee_info,
        "transcript": session.transcript,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "is_starred": session.is_starred,
        "note": session.note,
        "created_at": session.created_at
    }
    return {"code": 200, "message": "success", "data": session_dict}

@router.delete("/{id}", response_model=schemas.ApiResponse)
async def delete_session(id: str, db: AsyncSession = Depends(get_db)):
    # ... (代码保持不变) ...
    result = await db.execute(select(models.Session).where(models.Session.id == id))
    session = result.scalar_one_or_none()
    if not session:
        return {"code": 404, "message": "Session not found"}
    await db.execute(delete(models.Session).where(models.Session.id == id))
    await db.commit()
    return {"code": 200, "message": "Session deleted", "data": {"id": id}}