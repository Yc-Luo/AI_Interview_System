from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy import JSON
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    role = Column(String, default="user")  # 用户角色，默认user，可选admin
    avatar_url = Column(String, nullable=True)  # 用户头像URL
    reset_password_token = Column(String, nullable=True)  # 密码重置令牌
    reset_password_expires = Column(DateTime(timezone=True), nullable=True)  # 密码重置令牌过期时间
    outlines = relationship("Outline", back_populates="creator")

class Outline(Base):
    __tablename__ = "outlines"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)  # 添加索引
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    creator = relationship("User", back_populates="outlines")
    project = relationship("Project", back_populates="outline", uselist=False)  # 一对一关系，使用uselist=False
    modules = relationship("Module", back_populates="outline", cascade="all, delete-orphan")

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    outline_id = Column(Integer, ForeignKey("outlines.id"), index=True)  # 添加索引
    outline = relationship("Outline", back_populates="modules")
    questions = relationship("Question", back_populates="module", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    is_key_question = Column(Boolean, default=False, index=True)  # 添加索引，方便按关键问题筛选
    follow_up_directions = Column(JSON, default=list) 
    module_id = Column(Integer, ForeignKey("modules.id"), index=True)  # 添加索引
    module = relationship("Module", back_populates="questions")

class AIConfig(Base):
    __tablename__ = "ai_configs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # 添加索引，方便按名称查询
    role_settings = Column(JSON, default=dict) 
    strategy = Column(JSON, default=dict)
    outline_id = Column(Integer, ForeignKey("outlines.id", ondelete="CASCADE"), nullable=True, index=True, unique=True)  # 添加唯一约束，确保一个提纲只能有一个AI配置
    # 添加与Project模型的反向关系
    project = relationship("Project", back_populates="ai_config", uselist=False)  # 一对一关系，使用uselist=False

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    outline_id = Column(Integer, ForeignKey("outlines.id", ondelete="CASCADE"), index=True, unique=True)  # 添加唯一约束，确保一个提纲对应唯一一个项目
    ai_config_id = Column(Integer, ForeignKey("ai_configs.id", ondelete="CASCADE"), index=True, unique=True)  # 添加唯一约束，确保一个AI配置对应唯一一个项目
    status = Column(String, default="active", index=True)  # 添加索引，方便按状态筛选
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # 添加索引，方便按创建时间排序
    # 添加关系
    outline = relationship("Outline", back_populates="project", uselist=False)  # 一对一关系，使用uselist=False
    ai_config = relationship("AIConfig", back_populates="project", uselist=False)  # 一对一关系，使用uselist=False
    sessions = relationship("Session", back_populates="project", cascade="all, delete-orphan")
    participants = relationship("Participant", back_populates="project", cascade="all, delete-orphan")

class Participant(Base):
    __tablename__ = "participants"
    id = Column(String, primary_key=True, index=True)  # 使用UUID作为主键
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), index=True)  # 多对一关联到Project
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # 创建时间
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # 最后访问时间
    participant_metadata = Column(JSON, default=dict)  # 参与者元数据
    
    # 反向关系
    project = relationship("Project", back_populates="participants")
    sessions = relationship("Session", back_populates="participant", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), index=True)  # 添加索引
    participant_id = Column(String, ForeignKey("participants.id", ondelete="SET NULL"), index=True)  # 关联到Participant
    interviewee_info = Column(JSON, default=dict)
    transcript = Column(JSON, default=list) 
    start_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # 添加索引，方便按开始时间排序
    end_time = Column(DateTime(timezone=True), nullable=True, index=True)  # 添加索引，方便按结束时间筛选
    expires_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # 添加索引，方便查询过期会话
    is_starred = Column(Boolean, default=False, index=True)  # 添加星标状态字段
    note = Column(Text, nullable=True)  # 添加备注字段
    
    # 反向关系
    project = relationship("Project", back_populates="sessions")
    participant = relationship("Participant", back_populates="sessions")
