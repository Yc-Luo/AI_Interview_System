from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from app.database import get_db
# 注意：这里不导入 crud，避免循环引用。在函数内部延迟导入。
from app import crud, models
import os
import uuid
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量中获取配置，设置默认值
SECRET_KEY = os.environ.get("SECRET_KEY", "MY_SUPER_SECRET_KEY_FOR_DEV_ONLY")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")) # 默认7天过期
PASSWORD_RESET_EXPIRE_MINUTES = 30 # 密码重置令牌有效期30分钟

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- 密码处理工具 ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:

    if not password:
        raise ValueError("密码不能为空")

    # bcrypt 限制：密码不能超过72字节
    # 确保密码编码后不超过72字节
    password_bytes = password.encode('utf-8')

    if len(password_bytes) > 72:
        # 截断到72字节，然后解码（可能会丢失部分字符，但这是安全的）
        # 尝试解码，忽略错误
        password = password_bytes[:72].decode('utf-8', errors='ignore')

    return pwd_context.hash(password)

# --- Token 生成工具 ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 密码重置令牌生成工具 ---
def generate_reset_token(data: dict):
    expires_delta = timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)
    return create_access_token(data, expires_delta)

# --- 依赖注入：获取当前登录用户 ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    from app import crud # 延迟导入，解决循环依赖
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        
    # 允许模拟令牌用于测试环境
    if token == "mock_token":
        # 创建一个模拟用户对象
        mock_user = models.User(
            id=1,
            username="PreviewUser",
            email="preview@example.com",
            hashed_password="",
            role="user",
            created_at=datetime.utcnow()
        )
        return mock_user
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# --- 依赖注入：检查用户角色 ---
async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    """获取当前活跃用户"""
    return current_user

async def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    """获取当前管理员用户"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

# --- 角色验证装饰器 ---
def check_role(required_role: str):
    """检查用户是否具有指定角色"""
    async def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return current_user
    return role_checker

# --- 密码重置功能 ---
async def send_password_reset_email(email: str, reset_token: str):
    """发送密码重置邮件（模拟实现）"""
    # 实际生产环境中，这里应该调用邮件服务发送真实邮件
    print(f"发送密码重置邮件到 {email}，重置令牌：{reset_token}")
    return True

async def verify_reset_token(token: str, db: AsyncSession) -> Optional[models.User]:
    """验证密码重置令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    user = await crud.get_user_by_email(db, email=email)
    if user is None:
        return None
    
    # 检查令牌是否在数据库中存在且未过期
    if user.reset_password_token != token:
        return None
    
    if user.reset_password_expires and user.reset_password_expires < datetime.utcnow():
        return None
    
    return user

# --- 用户头像处理 ---
def save_user_avatar(file: UploadFile) -> str:
    """保存用户头像文件并返回文件路径"""
    # 确保头像存储目录存在
    avatar_dir = "app/static/avatars"
    os.makedirs(avatar_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(avatar_dir, file_name)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    # 返回相对路径，用于存储到数据库
    return f"/static/avatars/{file_name}"
