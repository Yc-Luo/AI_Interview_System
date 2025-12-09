from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import outlines, ai_configs, projects, sessions, chat, auth, activities, participants, export
from app.schemas import ApiResponse
from app.middleware.rate_limit import configure_rate_limiter
from app import cache
import traceback
import logging
import os
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# 配置日志
from app.config.logging import logger

# Prometheus监控指标
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status_code'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])
EXCEPTION_COUNT = Counter('http_exceptions_total', 'Total HTTP Exceptions', ['method', 'endpoint', 'exception_type'])

# 检查是否为测试环境
is_test = os.environ.get("TESTING", "false").lower() == "true"

# 仅在非测试环境中使用lifespan
if not is_test:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print("正在初始化数据库表结构...")
        async with engine.begin() as conn:
            # 先删除所有表，然后重新创建，解决 schema 不匹配问题
            await conn.run_sync(Base.metadata.create_all)
        print("数据库表结构初始化完成！")
        
        # 初始化Redis缓存
        try:
            await cache.init_redis()
            print("Redis缓存初始化完成！")
        except Exception as e:
            print(f"Redis缓存初始化失败: {e}")
        
        yield
        
        # 关闭Redis缓存
        try:
            await cache.close_redis()
            print("Redis缓存已关闭！")
        except Exception as e:
            print(f"关闭Redis缓存失败: {e}")
    
    app = FastAPI(
        title="AI Interview Agent Backend",
        description="AI驱动的面试系统后端API，支持提纲管理、AI配置、项目管理、会话管理等功能。",
        version="1.0.0",
        contact={
            "name": "AI Interview Agent Team",
            "email": "contact@ai-interview-agent.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        docs_url="/docs",  # Swagger UI文档地址
        redoc_url="/redoc",  # ReDoc文档地址
        openapi_url="/openapi.json",  # OpenAPI schema地址
        lifespan=lifespan
    )
else:
    # 测试环境不使用lifespan
    app = FastAPI(
        title="AI Interview Agent Backend",
        description="AI驱动的面试系统后端API，支持提纲管理、AI配置、项目管理、会话管理等功能。",
        version="1.0.0",
        contact={
            "name": "AI Interview Agent Team",
            "email": "contact@ai-interview-agent.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        docs_url="/docs",  # Swagger UI文档地址
        redoc_url="/redoc",  # ReDoc文档地址
        openapi_url="/openapi.json",  # OpenAPI schema地址
    )

# 允许跨域 (CORS 配置，解决 Load Failed 问题)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 监控中间件
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    
    # 记录请求开始时间
    start_time = time.time()
    
    try:
        # 处理请求
        response = await call_next(request)
        
        # 记录请求计数
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=response.status_code).inc()
        
        # 记录请求延迟
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
        
        return response
    except Exception as e:
        # 记录异常
        exception_type = type(e).__name__
        EXCEPTION_COUNT.labels(method=method, endpoint=endpoint, exception_type=exception_type).inc()
        raise

# 挂载静态文件服务，用于访问用户头像
# 确保静态文件目录存在
static_dir = "app/static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 配置速率限制器
configure_rate_limiter(app)

app.include_router(auth.router)
app.include_router(outlines.router)
app.include_router(ai_configs.router)
app.include_router(projects.router)
app.include_router(participants.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(activities.router)
app.include_router(export.router)
from app.routers import speech
app.include_router(speech.router)

# Prometheus监控端点
@app.get("/metrics", tags=["monitoring"])
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 记录完整的错误堆栈
    logger.error(f"Unexpected error: {exc}")
    logger.error(traceback.format_exc())
    
    # 检查是否是HTTPException
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(
                code=exc.status_code,
                message=exc.detail,
                data=None
            ).model_dump()
        )
    
    # 其他异常返回500
    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            code=500,
            message="Internal Server Error",
            data=None
        ).model_dump()
    )

@app.get("/")
async def root():
    return ApiResponse(
        code=200,
        message="Hello! The Backend is running.",
        data={}
    )
