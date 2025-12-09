#!/usr/bin/env python3
"""
认证功能单元测试
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.database import get_db
import asyncio

# 创建测试客户端
client = TestClient(app)

# 同步测试，不需要特殊的fixture设置

# 测试用户注册
def test_register_user():
    """测试用户注册功能"""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser1",
            "email": "test1@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    assert response.json()["code"] == 200
    assert response.json()["message"] == "User registered successfully"
    assert "id" in response.json()["data"]
    assert response.json()["data"]["username"] == "testuser1"
    assert response.json()["data"]["email"] == "test1@example.com"

# 测试用户登录
def test_login_user():
    """测试用户登录功能"""
    # 先注册一个用户
    client.post(
        "/api/auth/register",
        json={
            "username": "testlogin",
            "email": "login@example.com",
            "password": "testpassword123"
        }
    )
    
    # 测试登录
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testlogin",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    assert response.json()["code"] == 200
    assert response.json()["message"] == "Login successful"
    assert "access_token" in response.json()["data"]
    assert "token_type" in response.json()["data"]
    assert response.json()["data"]["token_type"] == "bearer"
    assert "username" in response.json()["data"]

# 测试登录失败（密码错误）
def test_login_failed_wrong_password():
    """测试使用错误密码登录"""
    # 先注册一个用户
    client.post(
        "/api/auth/register",
        json={
            "username": "wrongpass",
            "email": "wrongpass@example.com",
            "password": "testpassword123"
        }
    )
    
    # 使用错误密码登录
    response = client.post(
        "/api/auth/login",
        json={
            "username": "wrongpass",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 200
    assert response.json()["code"] == 401
    assert response.json()["message"] == "Incorrect username or password"

# 测试登录失败（用户不存在）
def test_login_failed_user_not_exists():
    """测试使用不存在的用户登录"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "notexist",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    assert response.json()["code"] == 401
    assert response.json()["message"] == "Incorrect username or password"
