#数据库连接管理：负责数据库连接的创建和关闭，解耦连接逻辑
import mysql.connector
from mysql.connector import Error
from config.db_config import DB_CONFIG

class DBConnector:
    def __init__(self):
        self.connection = None
        self.config = DB_CONFIG

    def connect(self):
        """创建数据库连接"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                print("✅ 成功连接到MySQL数据库")
            return self.connection
        except Error as e:
            print(f"❌ 数据库连接失败: {e}")
            raise  # 终止程序，必须解决连接问题

    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ 数据库连接已关闭")

    def get_cursor(self, dictionary=True):
        """获取游标（默认返回字典格式结果）"""
        self.connect()  # 确保连接有效
        return self.connection.cursor(dictionary=dictionary)