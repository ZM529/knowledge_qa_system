#数据库操作：封装数据查询、保存的 SQL 操作，隔离数据层与业务层
from datetime import datetime
from mysql.connector import Error
from database.db_connect import DBConnector

class DBOperation:
    def __init__(self):
        self.connector = DBConnector()

    def query_knowledge(self, entity1, relation):
        """
        根据实体和关系查询答案（支持正向和反向查询）
        :param entity1: 实体1
        :param relation: 关系
        :return: 实体2（答案）或None
        """
        cursor = None
        try:
            cursor = self.connector.get_cursor()
            
            # 正向查询：entity1 → entity2
            query_sql = """
                SELECT entity2 FROM knowledge_triple 
                WHERE entity1 = %s AND relation LIKE %s
                LIMIT 1
            """
            # 模糊匹配关系，提升容错率
            cursor.execute(query_sql, (entity1, f'%{relation}%'))
            result = cursor.fetchone()
            if result:
                return result['entity2']
            
            # 反向查询：entity2 → entity1（当正向查询失败时）
            # 例如："中国的首都是什么？" → 查询 entity2="中国的首都" 的记录，返回 entity1="北京"
            reverse_query_sql = """
                SELECT entity1 FROM knowledge_triple 
                WHERE entity2 = %s AND relation LIKE %s
                LIMIT 1
            """
            cursor.execute(reverse_query_sql, (entity1, f'%{relation}%'))
            result = cursor.fetchone()
            if result:
                return result['entity1']
            
            # 如果关系为空或匹配失败，尝试无关系匹配
            if not relation or relation.strip() == '':
                # 正向无关系查询
                query_sql_no_rel = """
                    SELECT entity2 FROM knowledge_triple 
                    WHERE entity1 = %s
                    LIMIT 1
                """
                cursor.execute(query_sql_no_rel, (entity1,))
                result = cursor.fetchone()
                if result:
                    return result['entity2']
                
                # 反向无关系查询
                reverse_query_sql_no_rel = """
                    SELECT entity1 FROM knowledge_triple 
                    WHERE entity2 = %s
                    LIMIT 1
                """
                cursor.execute(reverse_query_sql_no_rel, (entity1,))
                result = cursor.fetchone()
                if result:
                    return result['entity1']
            
            return None
        except Error as e:
            print(f"❌ 数据库查询失败: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def save_knowledge(self, entity1, relation, entity2):
        """
        保存知识三元组（存在则更新）
        :param entity1: 实体1
        :param relation: 关系
        :param entity2: 实体2（答案）
        :return: 保存成功返回True，失败返回False
        """
        cursor = None
        try:
            cursor = self.connector.get_cursor(dictionary=False)
            insert_sql = """
                INSERT INTO knowledge_triple (entity1, relation, entity2, create_time)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE entity2 = %s, create_time = %s
            """
            now = datetime.now()
            cursor.execute(
                insert_sql,
                (entity1, relation, entity2, now, entity2, now)
            )
            self.connector.connection.commit()
            print(f"✅ 知识点已保存：{entity1} - {relation} - {entity2}")
            return True
        except Error as e:
            self.connector.connection.rollback()
            print(f"❌ 数据库保存失败: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def get_all_relations(self):
        """
        获取数据库中所有不重复的关系词列表
        :return: 关系词列表
        """
        cursor = None
        try:
            cursor = self.connector.get_cursor()
            query_sql = "SELECT DISTINCT relation FROM knowledge_triple ORDER BY relation"
            cursor.execute(query_sql)
            results = cursor.fetchall()
            return [row['relation'] for row in results] if results else []
        except Error as e:
            print(f"❌ 获取关系词列表失败: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def close(self):
        """关闭数据库连接"""
        self.connector.close()