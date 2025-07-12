#!/usr/bin/env python3
"""
WSGI入口文件，用于gunicorn启动
"""
import os
import sys
from app import app, initialize_model, COMPARTMENT_ID

# 检查必要的环境变量
if not COMPARTMENT_ID:
    print("错误: 请设置环境变量 OCI_COMPARTMENT_ID")
    sys.exit(1)

# 初始化模型
initialize_model()

print("Oracle OCI 文本分类 API 启动中...")
print(f"Compartment ID: {COMPARTMENT_ID[:10]}...")

# 当使用gunicorn启动时，这个文件会被导入
# gunicorn会自动调用app作为WSGI应用