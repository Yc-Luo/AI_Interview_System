# AI Interview 部署说明

## 项目结构

```
deployment/
├── app/               # 后端代码（FastAPI应用）
├── database/          # 数据库配置
│   └── init.sql       # 数据库初始化脚本
├── frontend/          # 前端代码（HTML和JavaScript文件）
├── deploy.sh          # 部署脚本
├── docker-compose.yml # Docker Compose配置
├── Dockerfile         # Docker镜像构建文件
├── nginx.conf         # Nginx配置
├── requirements.txt   # Python依赖
└── seed_user.py       # 默认用户创建脚本
```

## 部署步骤

### 1. 环境准备

确保服务器已安装以下软件：
- Docker 20.10+
- Docker Compose 2.0+

### 2. 初始化环境

```bash
# 进入部署目录
cd deployment

# 初始化环境
./deploy.sh init
```

### 3. 启动服务

```bash
# 启动所有服务
./deploy.sh up
```

### 4. 验证部署

服务启动后，可以通过以下方式验证：

- API根路径：http://localhost:8000/
- Swagger文档：http://localhost:8000/docs
- ReDoc文档：http://localhost:8000/redoc

### 5. 其他命令

```bash
# 查看服务状态
./deploy.sh status

# 查看服务日志
./deploy.sh logs

# 重启服务
./deploy.sh restart

# 停止服务
./deploy.sh down

# 清理资源
./deploy.sh clean
```

## 环境变量配置

部署时会自动创建.env文件，包含以下主要配置项：

```env
# JWT配置
SECRET_KEY=MY_SUPER_SECRET_KEY_FOR_DEV_ONLY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 数据库配置
DATABASE_URL=postgresql+asyncpg://admin:Password123@db:5432/interview_agent_db

# Redis配置
REDIS_URL=redis://redis:6379/0

# 其他配置
DEBUG=True
```

## 数据库管理

### 初始化数据库

首次启动服务时，FastAPI应用会自动创建数据库表结构。

### 创建默认用户

```bash
# 进入容器
docker exec -it interview_app_container bash

# 执行默认用户创建脚本
python seed_user.py
```

## 日志管理

日志文件位于：
- 应用日志：app/logs/
- Docker日志：可通过`./deploy.sh logs`查看

## 安全建议

1. 在生产环境中，修改.env文件中的SECRET_KEY为强随机字符串
2. 修改数据库密码为强密码
3. 禁用DEBUG模式
4. 配置SSL证书
5. 配置防火墙规则，只开放必要端口
6. 定期备份数据库

## 故障排查

### 服务无法启动

```bash
# 查看日志
./deploy.sh logs

# 检查服务状态
./deploy.sh status
```

### 数据库连接失败

```bash
# 检查数据库容器状态
./deploy.sh status

# 查看数据库日志
docker logs interview_db_container
```

### API访问失败

```bash
# 检查应用日志
docker logs interview_app_container

# 检查API状态
curl -v http://localhost:8000/
```

## 版本信息

- 后端框架：FastAPI 0.122.0
- 数据库：PostgreSQL 15
- 缓存：Redis 7
- Python：3.11

## 联系信息

如有问题，请联系项目开发团队。