#!/bin/bash

# 设置脚本严格模式
set -euo pipefail

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 部署脚本
echo -e "${GREEN}=== 开始部署面试系统 ===${NC}"

# 1. 构建前端
echo -e "\n${YELLOW}1. 构建前端应用...${NC}"
./build_frontend.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}前端构建失败，部署中断！${NC}"
    exit 1
fi

# 2. 停止并移除旧容器
echo -e "\n${YELLOW}2. 停止并移除旧容器...${NC}"
docker-compose down --remove-orphans

# 3. 构建并启动新容器
echo -e "\n${YELLOW}3. 构建并启动新容器...${NC}"
docker-compose up -d --build

# 4. 等待服务启动并检查健康状态
echo -e "\n${YELLOW}4. 检查服务健康状态...${NC}"
sleep 10

# 检查各服务状态
APP_STATUS=$(docker inspect --format='{{.State.Health.Status}}' interview_app_container 2>/dev/null || echo "unhealthy")
DB_STATUS=$(docker inspect --format='{{.State.Health.Status}}' interview_db_container 2>/dev/null || echo "unhealthy")
REDIS_STATUS=$(docker inspect --format='{{.State.Health.Status}}' interview_redis_container 2>/dev/null || echo "unhealthy")
WEB_STATUS=$(docker inspect --format='{{.State.Running}}' interview_web_container 2>/dev/null || echo "false")

# 输出健康检查结果
echo -e "\n${YELLOW}服务健康检查结果：${NC}"
echo -e "应用服务：${GREEN}${APP_STATUS}${NC}"
echo -e "数据库服务：${GREEN}${DB_STATUS}${NC}"
echo -e "Redis服务：${GREEN}${REDIS_STATUS}${NC}"
echo -e "Web服务：${GREEN}${WEB_STATUS}${NC}"

# 验证所有服务是否正常运行
if [ "$APP_STATUS" = "healthy" ] && [ "$DB_STATUS" = "healthy" ] && [ "$REDIS_STATUS" = "healthy" ] && [ "$WEB_STATUS" = "true" ]; then
    echo -e "\n${GREEN}=== 应用部署成功！ ===${NC}"
    echo -e "${GREEN}前端应用访问地址：http://localhost${NC}"
    echo -e "${GREEN}后端API访问地址：http://localhost/api${NC}"
    echo -e "${GREEN}健康检查地址：http://localhost/health${NC}"
    echo -e "\n${YELLOW}提示：使用 ./check_logs.sh 查看服务日志${NC}"
else
    echo -e "\n${RED}=== 应用部署失败！ ===${NC}"
    echo -e "${RED}部分服务未正常启动，请检查日志获取详细信息${NC}"
    echo -e "${YELLOW}命令：./check_logs.sh${NC}"
    exit 1
fi