#!/bin/bash

# 设置脚本严格模式
set -euo pipefail

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 查看服务日志
echo -e "${GREEN}=== 应用服务日志 ===${NC}"
docker logs --tail 50 interview_app_container || echo -e "${RED}获取应用日志失败${NC}"

echo -e "\n${GREEN}=== Nginx 服务日志 ===${NC}"
docker logs --tail 50 interview_web_container || echo -e "${RED}获取Nginx日志失败${NC}"

echo -e "\n${GREEN}=== PostgreSQL 数据库日志 ===${NC}"
docker logs --tail 50 interview_db_container || echo -e "${RED}获取数据库日志失败${NC}"

echo -e "\n${GREEN}=== Redis 服务日志 ===${NC}"
docker logs --tail 50 interview_redis_container || echo -e "${RED}获取Redis日志失败${NC}"

echo -e "\n${YELLOW}提示：使用 'docker logs -f <容器名>' 可以实时查看日志${NC}"