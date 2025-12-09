from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 检查是否为测试环境
is_test = os.environ.get("TESTING", "false").lower() == "true"

# 1. 数据库连接地址 - 使用PostgreSQL
# 从环境变量获取数据库配置，默认使用PostgreSQL
# 使用当前系统用户名作为数据库用户，无需密码
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql+asyncpg://luoyuchen@localhost:5432/interview_db"
)

# 2. 创建异步引擎
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=False, # 测试环境关闭SQL语句打印，减少日志输出
    # PostgreSQL不需要check_same_thread参数
)

# 3. 创建会话工厂
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 4. 创建模型基类 (以后所有的数据库表都要继承它)
Base = declarative_base()

# 5. 获取数据库会话的依赖函数 (给 API 用的)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
