-- 数据库初始化脚本
-- 创建必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建数据库用户（如果不存在）
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'admin') THEN
        CREATE ROLE admin WITH LOGIN PASSWORD 'Password123';
    END IF;
END
$$;

-- 授予用户权限
GRANT ALL PRIVILEGES ON DATABASE interview_agent_db TO admin;