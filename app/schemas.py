from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Auth ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str
    
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        # 确保至少提供了username或email中的一个
        if not self.username and not self.email:
            raise ValueError("Either username or email must be provided")

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str = "user"
    avatar_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# 密码重置相关Schema
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str

class PasswordResetVerify(BaseModel):
    token: str

# --- Outline ---
class QuestionBase(BaseModel):
    content: str
    is_key_question: bool = False
    follow_up_directions: List[str] = []

class ModuleBase(BaseModel):
    title: str
    questions: List[QuestionBase]

class OutlineCreate(BaseModel):
    title: str
    description: Optional[str] = None
    modules: List[ModuleBase]

class OutlineResponse(OutlineCreate):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- AI Config ---
class AIConfigCreate(BaseModel):
    name: str
    role_settings: Dict[str, Any]
    strategy: Dict[str, Any]
    outline_id: Optional[int] = None

# --- Project ---
class ProjectCreate(BaseModel):
    name: str
    outline_id: int
    ai_config_id: int
    status: str = "active"

# --- Participant ---
class ParticipantCreate(BaseModel):
    project_id: str
    participant_metadata: Optional[Dict[str, Any]] = {}

class ParticipantResponse(BaseModel):
    id: str
    project_id: str
    created_at: datetime
    last_accessed_at: datetime
    participant_metadata: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)

# --- Session & Chat ---
class SessionCreate(BaseModel):
    project_id: str
    participant_id: Optional[str] = None
    interviewee_info: Optional[Dict[str, Any]] = {}

class SessionResponse(BaseModel):
    id: str
    project_id: str
    start_time: datetime

class ChatRequest(BaseModel):
    session_id: str
    content: str

class StarRequest(BaseModel):
    is_starred: bool

class NoteRequest(BaseModel):
    note: str

# --- Common Response ---
class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None
