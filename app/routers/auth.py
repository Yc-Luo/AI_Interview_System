from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud, auth, models
from app.database import get_db
from datetime import datetime, timedelta
from app.config.logging import logger

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=schemas.ApiResponse, summary="用户注册", description="创建新用户账号，返回用户基本信息")
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    注册新用户
    
    - **username**: 用户名，必须唯一
    - **email**: 邮箱地址，必须有效
    - **password**: 密码，建议包含大小写字母、数字和特殊字符
    
    返回:
    - 成功: 200 OK，返回用户基本信息
    - 失败: 400 Bad Request，用户名已被注册
    """
    try:
        logger.info(f"用户注册请求: 用户名={user.username}, 邮箱={user.email}")
        
        db_user = await crud.get_user_by_username(db, username=user.username)
        # 验证密码长度
        if len(user.password.encode('utf-8')) > 72:
            logger.warning(f"用户注册失败: 密码过长 (用户名={user.username})")
            return {
                "code": 400,
                "message": "密码过长，请使用72字符以内的密码",
                "data": None
            }
        if db_user:
            logger.warning(f"用户注册失败: 用户名已存在 (用户名={user.username})")
            return {
                "code": 400,
                "message": "Username already registered",
                "data": None
            }
        new_user = await crud.create_user(db=db, user=user)
        
        logger.info(f"用户注册成功: 用户ID={new_user.id}, 用户名={new_user.username}")
        return {
            "code": 200,
            "message": "User registered successfully",
            "data": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role,
                "avatar_url": new_user.avatar_url
            }
        }
    except Exception as e:
        logger.error(f"用户注册异常: 用户名={user.username}, 错误信息={str(e)}")
        return {
            "code": 500,
            "message": f"Failed to register user: {str(e)}",
            "data": None
        }

@router.post("/login", response_model=schemas.ApiResponse, summary="用户登录", description="使用用户名或邮箱登录，获取访问令牌")
async def login(user: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    """
    用户登录
    
    - **username**: 用户名（可选，与email二选一）
    - **email**: 邮箱地址（可选，与username二选一）
    - **password**: 登录密码
    
    返回:
    - 成功: 200 OK，返回访问令牌和用户信息
    - 失败: 401 Unauthorized，用户名或密码错误
    """
    try:
        logger.info(f"用户登录请求: 用户名={user.username}, 邮箱={user.email}")
        
        # 根据提供的字段获取用户
        if user.username:
            db_user = await crud.get_user_by_username(db, username=user.username)
            login_identifier = f"用户名={user.username}"
        elif user.email:
            db_user = await crud.get_user_by_email(db, email=user.email)
            login_identifier = f"邮箱={user.email}"
        else:
            logger.warning(f"用户登录失败: 未提供用户名或邮箱")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either username or email must be provided",
            )
        
        # 验证密码
        if not db_user:
            logger.warning(f"用户登录失败: 用户不存在 ({login_identifier})")
            return {
                "code": 401,
                "message": "Incorrect username or password",
                "data": None
            }
        
        if not auth.verify_password(user.password, db_user.hashed_password):
            logger.warning(f"用户登录失败: 密码错误 ({login_identifier})")
            return {
                "code": 401,
                "message": "Incorrect username or password",
                "data": None
            }
        
        # 生成 Token
        access_token = auth.create_access_token(data={"sub": db_user.username})
        
        logger.info(f"用户登录成功: 用户ID={db_user.id}, 用户名={db_user.username}")
        return {
            "code": 200,
            "message": "Login successful",
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "username": db_user.username,
                "user_id": db_user.id,
                "avatar_url": db_user.avatar_url
            }
        }
    except HTTPException as e:
        # 已处理的HTTP异常，直接抛出
        raise
    except Exception as e:
        logger.error(f"用户登录异常: 用户名={user.username}, 邮箱={user.email}, 错误信息={str(e)}")
        return {
            "code": 500,
            "message": f"Failed to login: {str(e)}",
            "data": None
        }

@router.post("/reset-password/request", response_model=schemas.ApiResponse, summary="请求重置密码", description="发送密码重置邮件")
async def request_password_reset(request: schemas.PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """
    请求重置密码
    
    - **email**: 注册邮箱地址
    
    返回:
    - 成功: 200 OK，密码重置邮件已发送
    - 失败: 404 Not Found，用户不存在
    """
    # 检查用户是否存在
    user = await crud.get_user_by_email(db, email=request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 生成重置令牌
    reset_token = auth.generate_reset_token(data={"sub": user.email})
    expires_at = datetime.utcnow() + timedelta(minutes=auth.PASSWORD_RESET_EXPIRE_MINUTES)
    
    # 更新用户的重置令牌和过期时间
    await crud.update_user_reset_token(db, user, reset_token, expires_at)
    
    # 发送重置邮件（模拟实现）
    await auth.send_password_reset_email(user.email, reset_token)
    
    return {
        "code": 200,
        "message": "Password reset email sent",
        "data": None
    }

@router.post("/reset-password/verify", response_model=schemas.ApiResponse, summary="验证重置令牌", description="验证密码重置令牌是否有效")
async def verify_password_reset(request: schemas.PasswordResetVerify, db: AsyncSession = Depends(get_db)):
    """
    验证重置令牌
    
    - **token**: 密码重置令牌
    
    返回:
    - 成功: 200 OK，令牌有效
    - 失败: 400 Bad Request，令牌无效或已过期
    """
    user = await auth.verify_reset_token(request.token, db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    return {
        "code": 200,
        "message": "Reset token is valid",
        "data": {
            "email": user.email
        }
    }

@router.post("/reset-password", response_model=schemas.ApiResponse, summary="设置新密码", description="使用重置令牌设置新密码")
async def reset_password(request: schemas.PasswordReset, db: AsyncSession = Depends(get_db)):
    """
    设置新密码
    
    - **token**: 密码重置令牌
    - **new_password**: 新密码
    
    返回:
    - 成功: 200 OK，密码已重置
    - 失败: 400 Bad Request，令牌无效或已过期
    """
    user = await auth.verify_reset_token(request.token, db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # 更新用户密码
    await crud.update_user_password(db, user, request.new_password)
    
    return {
        "code": 200,
        "message": "Password reset successful",
        "data": None
    }

@router.post("/avatar", response_model=schemas.ApiResponse, summary="上传用户头像", description="上传用户头像，支持常见图片格式")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上传用户头像
    
    - **file**: 头像文件，支持JPG、PNG、GIF等常见图片格式
    
    返回:
    - 成功: 200 OK，头像上传成功，返回头像URL
    - 失败: 400 Bad Request，文件格式不支持
    - 失败: 401 Unauthorized，未授权访问
    """
    # 检查文件类型
    allowed_extensions = ["jpg", "jpeg", "png", "gif", "webp"]
    file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File type not allowed. Please upload a JPG, PNG, GIF or WEBP image.")
    
    # 保存头像文件
    avatar_url = auth.save_user_avatar(file)
    
    # 更新用户头像
    await crud.update_user_avatar(db, current_user, avatar_url)
    
    return {
        "code": 200,
        "message": "Avatar uploaded successfully",
        "data": {
            "avatar_url": avatar_url
        }
    }
