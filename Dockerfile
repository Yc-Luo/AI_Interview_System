# 第一阶段：构建阶段
FROM python:3.11-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt
COPY requirements.txt .

# 安装Python依赖到虚拟环境，使用--no-cache-dir减小镜像大小
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# 第二阶段：运行阶段
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户，提高安全性
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m appuser

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 复制应用代码
COPY app/ ./app/

# 设置环境变量
ENV PYTHONPATH="."
ENV PATH="/opt/venv/bin:$PATH"

# 创建必要的目录并设置权限
RUN mkdir -p /app/app/static /app/app/logs && \
    chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
