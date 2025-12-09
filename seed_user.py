import asyncio
import sys
import os

# 将当前目录加入 Python 路径
sys.path.append(os.getcwd())

from app.database import AsyncSessionLocal
from app import models, auth
from sqlalchemy.future import select

async def create_default_user():
    print("🚀 正在连接数据库...")
    async with AsyncSessionLocal() as db:
        # 1. 检查是否存在 ID=1 的用户
        result = await db.execute(select(models.User).where(models.User.id == 1))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"✅ 用户 (ID=1) 已存在: {user.username}")
        else:
            print("🛠️ 用户不存在，正在创建默认管理员 (ID=1)...")
            
            # 2. 生成加密密码
            hashed_pwd = auth.get_password_hash("admin123")
            
            new_user = models.User(
                id=1,  # 强制指定 ID 为 1
                username="admin",
                email="admin@example.com",
                hashed_password=hashed_pwd
            )
            db.add(new_user)
            await db.commit()
            print("🎉 成功！默认用户创建完成。")
            print("👉 用户名: admin")
            print("👉 密  码: admin123")

if __name__ == "__main__":
    asyncio.run(create_default_user())