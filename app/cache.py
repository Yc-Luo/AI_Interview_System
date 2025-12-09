import os
from typing import Optional, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Redis配置
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

# Redis客户端（初始化为None，稍后尝试初始化）
redis_client = None
async_redis_client = None

# 尝试导入redis模块并初始化客户端
try:
    import redis
    # 尝试创建同步Redis客户端
    try:
        redis_client = redis.from_url(REDIS_URL, password=REDIS_PASSWORD)
        # 测试连接
        redis_client.ping()
        print("Redis同步客户端初始化成功")
    except Exception as e:
        print(f"Redis同步客户端初始化失败: {e}")
        redis_client = None
        
    # 异步客户端将在init_redis中尝试初始化
except ImportError:
    print("redis模块未安装，缓存功能将不可用")

async def init_redis():
    """初始化异步Redis客户端"""
    global async_redis_client
    try:
        import redis
        async_redis_client = redis.asyncio.from_url(
            REDIS_URL,
            password=REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True
        )
        # 测试连接
        await async_redis_client.ping()
        print("Redis异步客户端初始化成功")
    except Exception as e:
        print(f"Redis异步客户端初始化失败: {e}")
        async_redis_client = None

async def close_redis():
    """关闭异步Redis客户端"""
    if async_redis_client:
        try:
            await async_redis_client.aclose()
            print("Redis异步客户端已关闭")
        except Exception as e:
            print(f"关闭Redis异步客户端失败: {e}")

# 缓存键生成函数
def generate_cache_key(prefix: str, **kwargs) -> str:
    """生成缓存键"""
    key_parts = [prefix]
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    return ":".join(key_parts)

# 同步缓存操作
def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    """设置缓存"""
    if not redis_client:
        return False
    try:
        return redis_client.set(key, value, ex=expire)
    except Exception as e:
        print(f"Error setting cache: {e}")
        return False

def get_cache(key: str) -> Optional[Any]:
    """获取缓存"""
    if not redis_client:
        return None
    try:
        return redis_client.get(key)
    except Exception as e:
        print(f"Error getting cache: {e}")
        return None

def delete_cache(key: str) -> bool:
    """删除缓存"""
    if not redis_client:
        return False
    try:
        return redis_client.delete(key) > 0
    except Exception as e:
        print(f"Error deleting cache: {e}")
        return False

def delete_cache_pattern(pattern: str) -> int:
    """删除匹配模式的所有缓存"""
    if not redis_client:
        return 0
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception as e:
        print(f"Error deleting cache pattern: {e}")
        return 0

# 异步缓存操作
async def async_set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    """异步设置缓存"""
    if not async_redis_client:
        return False
    try:
        await async_redis_client.set(key, value, ex=expire)
        return True
    except Exception as e:
        print(f"Error setting cache: {e}")
        return False

async def async_get_cache(key: str) -> Optional[Any]:
    """异步获取缓存"""
    if not async_redis_client:
        return None
    try:
        return await async_redis_client.get(key)
    except Exception as e:
        print(f"Error getting cache: {e}")
        return None

async def async_delete_cache(key: str) -> bool:
    """异步删除缓存"""
    if not async_redis_client:
        return False
    try:
        result = await async_redis_client.delete(key)
        return result > 0
    except Exception as e:
        print(f"Error deleting cache: {e}")
        return False

async def async_delete_cache_pattern(pattern: str) -> int:
    """异步删除匹配模式的所有缓存"""
    if not async_redis_client:
        return 0
    try:
        keys = await async_redis_client.keys(pattern)
        if keys:
            return await async_redis_client.delete(*keys)
        return 0
    except Exception as e:
        print(f"Error deleting cache pattern: {e}")
        return 0
