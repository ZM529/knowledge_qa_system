"""
配置模块 (config)
================

本模块提供知识问答系统的配置管理功能：

- 数据库配置：MySQL连接参数、连接池设置
- 系统配置：应用参数、调试选项
- 初始化脚本：数据库表结构创建SQL

主要组件：
    DB_CONFIG: 数据库连接配置字典
    DB_INIT_SQL: 数据库初始化SQL脚本
    
使用示例：
    from config.db_config import DB_CONFIG
    
    # 获取数据库连接
    connection = mysql.connector.connect(**DB_CONFIG)

作者: Knowledge QA System
版本: 1.0.0
"""

from .db_config import DB_CONFIG, DB_INIT_SQL

# 定义模块的公共API
__all__ = ['DB_CONFIG', 'DB_INIT_SQL']

print("✅ Config 模块初始化完成 - 配置管理器已就绪")