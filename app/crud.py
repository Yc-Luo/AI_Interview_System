from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app import models, schemas, auth
import uuid
from datetime import datetime

# Auth
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user_password(db: AsyncSession, user: models.User, new_password: str):
    """更新用户密码"""
    hashed_password = auth.get_password_hash(new_password)
    user.hashed_password = hashed_password
    user.reset_password_token = None
    user.reset_password_expires = None
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_reset_token(db: AsyncSession, user: models.User, reset_token: str, expires_at: datetime):
    """更新用户密码重置令牌"""
    user.reset_password_token = reset_token
    user.reset_password_expires = expires_at
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_avatar(db: AsyncSession, user: models.User, avatar_url: str):
    """更新用户头像"""
    user.avatar_url = avatar_url
    await db.commit()
    await db.refresh(user)
    return user

# Outline
async def create_outline(db: AsyncSession, outline: schemas.OutlineCreate, user_id: int):
    db_modules = []
    for m in outline.modules:
        db_questions = []
        for q in m.questions:
            db_questions.append(models.Question(
                content=q.content, 
                is_key_question=q.is_key_question, 
                follow_up_directions=q.follow_up_directions
            ))
        db_modules.append(models.Module(title=m.title, questions=db_questions))
    
    db_outline = models.Outline(
        title=outline.title, 
        description=outline.description, 
        creator_id=user_id, 
        modules=db_modules
    )
    db.add(db_outline)
    await db.commit()
    
    # 预加载所有关系字段，避免MissingGreenlet错误
    from sqlalchemy.orm import selectinload
    from sqlalchemy.future import select
    
    result = await db.execute(
        select(models.Outline)
        .options(
            selectinload(models.Outline.modules)
            .selectinload(models.Module.questions)
        )
        .where(models.Outline.id == db_outline.id)
    )
    
    return result.scalar_one_or_none()

async def get_outlines(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Outline)
        .options(
            selectinload(models.Outline.modules)
            .selectinload(models.Module.questions)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_outline(db: AsyncSession, outline_id: int):
    result = await db.execute(
        select(models.Outline)
        .options(
            selectinload(models.Outline.modules)
            .selectinload(models.Module.questions)
        )
        .where(models.Outline.id == outline_id)
    )
    return result.scalar_one_or_none()

async def delete_outline(db: AsyncSession, outline_id: int):
    from sqlalchemy import update
    
    # 1. 先将关联的AI配置的outline_id设置为NULL
    await db.execute(
        update(models.AIConfig)
        .where(models.AIConfig.outline_id == outline_id)
        .values(outline_id=None)
    )
    
    # 2. 然后删除提纲
    result = await db.execute(
        select(models.Outline)
        .where(models.Outline.id == outline_id)
    )
    outline = result.scalar_one_or_none()
    if outline:
        await db.delete(outline)
        await db.commit()
        return True
    return False

async def update_outline(db: AsyncSession, outline_id: int, outline: schemas.OutlineCreate):
    # 预加载所有关系字段，避免MissingGreenlet错误
    from sqlalchemy.orm import selectinload
    from sqlalchemy.future import select
    
    result = await db.execute(
        select(models.Outline)
        .options(
            selectinload(models.Outline.modules)
            .selectinload(models.Module.questions)
        )
        .where(models.Outline.id == outline_id)
    )
    db_outline = result.scalar_one_or_none()
    if not db_outline:
        return None
    
    # 更新提纲基本信息
    db_outline.title = outline.title
    db_outline.description = outline.description
    
    # 删除现有模块和问题
    for module in db_outline.modules:
        await db.delete(module)
    
    # 创建新模块和问题
    db_modules = []
    for m in outline.modules:
        db_questions = []
        for q in m.questions:
            db_questions.append(models.Question(
                content=q.content, 
                is_key_question=q.is_key_question, 
                follow_up_directions=q.follow_up_directions
            ))
        db_modules.append(models.Module(title=m.title, questions=db_questions, outline=db_outline))
    
    db_outline.modules = db_modules
    await db.commit()
    
    result = await db.execute(
        select(models.Outline)
        .options(
            selectinload(models.Outline.modules)
            .selectinload(models.Module.questions)
        )
        .where(models.Outline.id == outline_id)
    )
    
    return result.scalar_one_or_none()

# AI Config
async def create_ai_config(db: AsyncSession, config: schemas.AIConfigCreate):
    db_config = models.AIConfig(
        name=config.name, 
        role_settings=config.role_settings, 
        strategy=config.strategy,
        outline_id=config.outline_id
    )
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config

async def get_ai_config(db: AsyncSession, config_id: int):
    result = await db.execute(select(models.AIConfig).where(models.AIConfig.id == config_id))
    return result.scalar_one_or_none()

async def get_ai_configs(db: AsyncSession, outline_id: int = None, skip: int = 0, limit: int = 100):
    query = select(models.AIConfig)
    if outline_id is not None:
        query = query.where(models.AIConfig.outline_id == outline_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_ai_config(db: AsyncSession, config_id: int, config: schemas.AIConfigCreate):
    result = await db.execute(select(models.AIConfig).where(models.AIConfig.id == config_id))
    db_config = result.scalar_one_or_none()
    if db_config is None:
        return None
    
    # 更新 AI 配置
    db_config.name = config.name
    db_config.role_settings = config.role_settings
    db_config.strategy = config.strategy
    db_config.outline_id = config.outline_id
    
    await db.commit()
    await db.refresh(db_config)
    return db_config

async def delete_ai_config(db: AsyncSession, config_id: int):
    result = await db.execute(select(models.AIConfig).where(models.AIConfig.id == config_id))
    db_config = result.scalar_one_or_none()
    if db_config is None:
        return None
    
    await db.delete(db_config)
    await db.commit()
    return db_config

# Project
async def create_project(db: AsyncSession, project: schemas.ProjectCreate):
    # 验证提纲是否存在
    outline = await db.get(models.Outline, project.outline_id)
    if not outline:
        raise ValueError(f"Outline with id {project.outline_id} not found")
    
    # 验证AI配置是否存在
    ai_config = await db.get(models.AIConfig, project.ai_config_id)
    if not ai_config:
        raise ValueError(f"AI Config with id {project.ai_config_id} not found")
    
    project_uuid = str(uuid.uuid4())
    db_project = models.Project(
        id=project_uuid, 
        name=project.name,  # 使用schema中的name字段
        outline_id=project.outline_id, 
        ai_config_id=project.ai_config_id, 
        status=project.status
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

async def get_project(db: AsyncSession, project_id: str):
    result = await db.execute(
        select(models.Project)
        .options(
            selectinload(models.Project.ai_config),
            selectinload(models.Project.outline).selectinload(models.Outline.modules).selectinload(models.Module.questions)
        )
        .where(models.Project.id == project_id)
    )
    return result.scalar_one_or_none()

async def get_project_with_details(db: AsyncSession, project_id: str):
    """获取项目详情，包括AI配置、提纲、参与者和会话"""
    result = await db.execute(
        select(models.Project)
        .options(
            selectinload(models.Project.ai_config),
            selectinload(models.Project.outline).selectinload(models.Outline.modules).selectinload(models.Module.questions),
            selectinload(models.Project.participants),
            selectinload(models.Project.sessions).selectinload(models.Session.participant)
        )
        .where(models.Project.id == project_id)
    )
    return result.scalar_one_or_none()

# Participant
async def create_participant(db: AsyncSession, participant: schemas.ParticipantCreate):
    # 验证项目是否存在
    project = await db.get(models.Project, participant.project_id)
    if not project:
        raise ValueError(f"Project with id {participant.project_id} not found")
    
    participant_uuid = str(uuid.uuid4())
    db_participant = models.Participant(
        id=participant_uuid,
        project_id=participant.project_id,
        participant_metadata=participant.participant_metadata
    )
    db.add(db_participant)
    await db.commit()
    await db.refresh(db_participant)
    return db_participant

async def get_participant(db: AsyncSession, participant_id: str):
    result = await db.execute(select(models.Participant).where(models.Participant.id == participant_id))
    return result.scalar_one_or_none()

async def update_participant_access(db: AsyncSession, participant_id: str):
    from datetime import datetime, timezone
    result = await db.execute(select(models.Participant).where(models.Participant.id == participant_id))
    participant = result.scalar_one_or_none()
    if participant:
        participant.last_accessed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(participant)
    return participant

# Session
async def create_session(db: AsyncSession, session: schemas.SessionCreate):
    from datetime import timedelta, timezone
    session_uuid = str(uuid.uuid4())
    # 设置会话过期时间为1小时后
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=1)
    
    # 验证项目是否存在
    project = await db.get(models.Project, session.project_id)
    if not project:
        raise ValueError(f"Project with id {session.project_id} not found")
    
    # 如果提供了participant_id，验证参与者是否存在
    if session.participant_id:
        participant = await db.get(models.Participant, session.participant_id)
        if not participant:
            raise ValueError(f"Participant with id {session.participant_id} not found")
    
    db_session = models.Session(
        id=session_uuid, 
        project_id=session.project_id, 
        participant_id=session.participant_id,
        interviewee_info=session.interviewee_info, 
        transcript=[], 
        start_time=now,
        expires_at=expires_at
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

async def add_message_to_session(db: AsyncSession, session_id: str, role: str, content: str):
    result = await db.execute(select(models.Session).where(models.Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session: return None
    
    current = list(session.transcript) if session.transcript else []
    current.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
    session.transcript = current
    
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(session, "transcript")
    await db.commit()
    return session

async def get_session_context(db: AsyncSession, session_id: str):
    # 预加载所有需要的关系
    result = await db.execute(
        select(models.Session)
        .options(
            selectinload(models.Session.project)
            .options(
                selectinload(models.Project.ai_config),
                selectinload(models.Project.outline)
                .selectinload(models.Outline.modules)
                .selectinload(models.Module.questions)
            ),
            selectinload(models.Session.participant)
        )
        .where(models.Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        return None
    
    # 检查会话是否过期
    from datetime import timezone
    if session.expires_at and session.expires_at < datetime.now(timezone.utc):
        return None
    
    project = session.project
    if not project:
        return None
    
    ai_config = project.ai_config
    outline = project.outline
    
    if not outline:
        return None
    
    return {"session": session, "ai_config": ai_config, "outline": outline, "project": project, "participant": session.participant}


# 获取项目列表
async def get_projects(db: AsyncSession, skip: int = 0, limit: int = 100, outline_id: int = None):
    # 这里我们做一个简单的多表查询，把 Outline 的标题也查出来方便前端显示
    # 实际项目中可能需要更复杂的 join
    query = select(models.Project, models.Outline.title.label("outline_title"))
    query = query.join(models.Outline, models.Project.outline_id == models.Outline.id)
    
    # 如果提供了outline_id，添加过滤条件
    if outline_id is not None:
        query = query.where(models.Project.outline_id == outline_id)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    projects = []
    for row in result:
        proj, title = row
        # 手动构造一个包含 title 和 outline_id 的字典返回
        p_dict = {
            "id": proj.id,
            "status": proj.status,
            "created_at": proj.created_at,
            "outline_title": title,
            "outline_id": proj.outline_id,
            "ai_config_id": proj.ai_config_id,
            "session_count": 0 # 这里暂时写 0，后续可聚合查询 session 表
        }
        projects.append(p_dict)
        
    return projects