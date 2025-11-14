"""
核心模块 (core)
===============

本模块包含智能问答系统的核心功能组件：

- QAEngine: 问答引擎主类，整合各模块功能
  - 处理用户问题查询
  - 管理知识学习流程
  - 协调数据库和NLP模块

主要类和函数：
    QAEngine: 问答引擎类，提供问答和学习功能
"""

from .qa_engine import QAEngine

# 定义模块的公共API
__all__ = ['QAEngine']

# 版本信息
__version__ = '1.0.0'
__author__ = 'Knowledge QA System'

print("✅ Core 模块初始化完成 - 问答引擎已就绪")