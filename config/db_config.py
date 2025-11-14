# 数据库连接配置（根据实际环境修改）
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,  # MySQL默认端口
    "user": "root",
    "password": "2002529",  # 替换为实际密码
    "database": "knowledge_graph",
    "charset": "utf8mb4",
    "autocommit": False,  # 手动提交事务
    "connection_timeout": 10,  # 连接超时10秒
    "pool_name": "qa_pool",
    "pool_size": 5  # 连接池大小
}

# 数据库初始化SQL（创建表结构）
DB_INIT_SQL = """
CREATE DATABASE IF NOT EXISTS knowledge_graph DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE knowledge_graph;

CREATE TABLE IF NOT EXISTS knowledge_triple (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity1 VARCHAR(255) NOT NULL COMMENT '实体1',
    relation VARCHAR(255) NOT NULL COMMENT '关系',
    entity2 VARCHAR(255) NOT NULL COMMENT '实体2（答案）',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_entity1 (entity1),
    INDEX idx_relation (relation),
    INDEX idx_entity2 (entity2),
    UNIQUE KEY uk_triple (entity1, relation, entity2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识三元组表';
"""