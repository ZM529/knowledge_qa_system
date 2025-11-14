#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
================

用于初始化知识问答系统的数据库和表结构。

使用步骤：
1. 确保MySQL服务正在运行
2. 检查config/db_config.py中的数据库连接信息
3. 运行此脚本：python init_database.py

作者: Knowledge QA System
"""

import mysql.connector
import sys
from config.db_config import DB_CONFIG, DB_INIT_SQL


def init_database():
    """初始化数据库和表结构"""
    print("🔧 开始初始化数据库...")
    
    # 临时的连接配置（不指定数据库名）
    temp_config = DB_CONFIG.copy()
    temp_database = temp_config.pop('database')
    
    try:
        # 1. 连接到MySQL服务器（不指定数据库）
        print(f"📡 连接到MySQL服务器: {temp_config['host']}:{temp_config.get('port', 3306)}")
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        print("✅ MySQL连接成功")
        
        # 2. 执行初始化SQL
        print("📝 执行数据库初始化脚本...")
        # 分割SQL语句（以分号分隔）
        sql_statements = [stmt.strip() for stmt in DB_INIT_SQL.split(';') if stmt.strip()]
        
        for i, sql in enumerate(sql_statements, 1):
            if sql:
                try:
                    cursor.execute(sql)
                    print(f"   ✅ SQL {i} 执行成功")
                except mysql.connector.Error as e:
                    print(f"   ⚠️ SQL {i} 执行警告: {e}")
        
        connection.commit()
        print("✅ 数据库初始化完成")
        
        # 3. 验证表是否创建成功
        print("\n🔍 验证表结构...")
        cursor.execute("USE knowledge_graph;")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        
        if tables:
            print("📋 已创建的表:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("⚠️ 未找到任何表")
            
        # 4. 显示表结构信息
        if ('knowledge_triple',) in tables:
            print("\n📊 knowledge_triple 表结构:")
            cursor.execute("DESCRIBE knowledge_triple;")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[0]}: {col[1]} {'(主键)' if col[0] == 'id' else ''}")
        
        print("\n🎉 数据库初始化完成！现在可以运行问答系统了。")
        
    except mysql.connector.Error as e:
        print(f"❌ 数据库初始化失败: {e}")
        print("\n💡 可能的解决方案:")
        print("   1. 检查MySQL服务是否正在运行")
        print("   2. 检查config/db_config.py中的连接信息是否正确")
        print("   3. 确保用户有创建数据库的权限")
        print("   4. 检查防火墙设置")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            
    return True


def test_connection():
    """测试数据库连接"""
    print("🧪 测试数据库连接...")
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 测试查询
        cursor.execute("SELECT COUNT(*) FROM knowledge_triple;")
        count = cursor.fetchone()[0]
        
        print(f"✅ 数据库连接成功，当前存储 {count} 个知识点")
        
        # 显示一些示例数据
        if count > 0:
            cursor.execute("SELECT entity1, relation, entity2 FROM knowledge_triple LIMIT 3;")
            examples = cursor.fetchall()
            print("\n📝 示例知识点:")
            for i, (e1, rel, e2) in enumerate(examples, 1):
                print(f"   {i}. {e1} - {rel} - {e2}")
        
        cursor.close()
        connection.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ 连接测试失败: {e}")
        return False


if __name__ == "__main__":
    print("="*50)
    print("🧠 知识问答系统 - 数据库初始化工具")
    print("="*50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 仅测试连接
        success = test_connection()
    else:
        # 完整初始化
        success = init_database()
    
    if success:
        print("\n✨ 系统已准备就绪！运行 'python main.py' 开始问答")
    else:
        print("\n💥 初始化失败，请检查错误信息并重试")
        sys.exit(1)