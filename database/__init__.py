"""
数据库模块 (database)
==================

本模块提供知识问答系统的数据存储和访问功能：

- DBConnector: 数据库连接管理器
  - 处理MySQL连接
  - 管理连接池和连接生命周期
  - 提供cursor对象

- DBOperation: 数据库操作封装
  - 知识查询：支持模糊匹配和精确查询
  - 知识保存：支持插入和更新操作
  - 事务管理：确保数据一致性

主要类：
    DBConnector: 数据库连接器
    DBOperation: 数据库操作类
"""

from .db_connect import DBConnector
from .db_operation import DBOperation

# 定义模块的公共API
__all__ = ['DBConnector', 'DBOperation']

print("✅ Database 模块初始化完成 - 数据库连接器已就绪")