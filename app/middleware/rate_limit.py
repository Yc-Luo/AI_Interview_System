from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.schemas import ApiResponse

# 创建速率限制器，使用客户端IP作为唯一标识符
limiter = Limiter(key_func=get_remote_address)

# 速率限制异常处理
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content=ApiResponse(
            code=429,
            message="Rate limit exceeded. Please try again later.",
            data=None
        ).model_dump()
    )

# 配置速率限制器到FastAPI应用
def configure_rate_limiter(app: FastAPI):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
