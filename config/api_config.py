"""API 配置模块 - 实验室管理系统 API 的基本配置"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class APIConfig:
    """API 配置类"""
    
    BASE_URL = os.getenv("LAB_API_BASE_URL", "http://localhost:8000/api")
    TIMEOUT = int(os.getenv("LAB_API_TIMEOUT", "30"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # 预留的 API 端点分类（6个主要模块）
    ENDPOINTS = {
        "devices": "/devices",           # 设备模块
        "experiments": "/experiments",   # 实验模块
        "users": "/users",               # 用户模块
        "reservations": "/reservations", # 预约模块
        "reports": "/reports",           # 报告模块
        "settings": "/settings",         # 设置模块
    }
