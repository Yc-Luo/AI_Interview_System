#!/bin/bash

# 设置脚本严格模式
set -euo pipefail

# 构建前端应用
echo "=== 开始构建前端应用 ==="

# 进入前端目录
cd "$(dirname "$0")/frontend-vue"

# 清理旧的构建文件和node_modules（可选，可根据需要启用）
echo "清理旧的构建文件..."
rm -rf dist node_modules package-lock.json || true

# 安装依赖
echo "安装前端依赖..."
npm install --legacy-peer-deps

# 构建应用
echo "构建前端应用..."
npm run build

# 检查构建结果
if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
    echo "=== 前端构建成功！ ==="
    echo "构建产物路径：$(pwd)/dist"
else
    echo "=== 前端构建失败！ ==="
    echo "构建目录dist不存在或为空"
    exit 1
fi

# 返回项目根目录
cd ..