from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_db
from app.services.llm_service import get_ai_reply

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=schemas.ApiResponse, summary="AI聊天交互", description="与AI面试官进行聊天交互，获取AI回复")
async def chat_with_ai(request: schemas.ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    与AI面试官进行聊天交互
    
    - **session_id**: 会话ID，必填，聊天所属的会话
    - **content**: 用户输入内容，必填，用户的发言或回答
    
    返回:
    - 成功: 200 OK，返回AI的回复内容
    - 失败: 404 Not Found，会话不存在或上下文丢失
    - 失败: 410 Gone，会话已过期
    - 失败: 500 Internal Server Error，AI回复生成失败
    """
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import update
    from sqlalchemy.future import select
    from app.models import Session
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 1. 检查会话是否存在并更新过期时间
        result = await db.execute(select(Session).where(Session.id == request.session_id))
        session = result.scalar_one_or_none()
        
        if not session:
            logger.error(f"Session not found: {request.session_id}")
            return {"code": 404, "message": "Session not found"}
        
        # 2. 检查会话是否过期
        now = datetime.now(timezone.utc)
        if session.expires_at:
            # 确保session.expires_at带有时区信息
            if session.expires_at.tzinfo is None:
                session.expires_at = session.expires_at.replace(tzinfo=timezone.utc)
            if session.expires_at < now:
                logger.error(f"Session expired: {request.session_id}, expires_at: {session.expires_at}, now: {now}")
                return {"code": 410, "message": "Session expired"}
        
        # 3. 更新会话过期时间（延长1小时）
        new_expires_at = now + timedelta(hours=1)
        await db.execute(
            update(Session)
            .where(Session.id == request.session_id)
            .values(expires_at=new_expires_at)
        )
        await db.commit()
        
        # 4. 记录用户发言
        await crud.add_message_to_session(db, request.session_id, "user", request.content)
        logger.info(f"Added user message to session {request.session_id}: {request.content[:50]}...")
        
        # 5. 获取完整上下文 (提纲+人设+项目+参与者)
        context = await crud.get_session_context(db, request.session_id)
        if not context:
            logger.error(f"Failed to get session context for session {request.session_id}")
            return {"code": 404, "message": "Session context not found"}
        
        # 验证上下文完整性
        if not context.get("outline"):
            logger.error(f"Outline not found for session {request.session_id}, project: {context.get('project', {}).id if context.get('project') else 'unknown'}")
            return {"code": 404, "message": "Interview outline not found"}
            
        if not context.get("ai_config"):
            logger.error(f"AI config not found for session {request.session_id}, project: {context.get('project', {}).id if context.get('project') else 'unknown'}")
            return {"code": 404, "message": "AI configuration not found"}
        
        # 6. 生成 AI 回复 (核心耗时操作)
        logger.info(f"Generating AI reply for session {request.session_id}")
        ai_reply_text = await get_ai_reply(context, request.content)
        
        # 7. 记录 AI 发言
        await crud.add_message_to_session(db, request.session_id, "ai", ai_reply_text)
        logger.info(f"Added AI reply to session {request.session_id}: {ai_reply_text[:50]}...")
        
        return {
            "code": 200,
            "message": "success",
            "data": {"reply": ai_reply_text}
        }
    except Exception as e:
        logger.error(f"Error in chat_with_ai: {str(e)}", exc_info=True)
        return {
            "code": 500,
            "message": f"Failed to get AI reply: {str(e)}",
            "data": None
        }