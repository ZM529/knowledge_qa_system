# 三元组提取（NLP 模块）：专注于问题和答案的解析，提取知识三元组，便于后续扩展 NLP 能力
class TripleExtractor:
    def __init__(self, db_relations=None):
        """
        初始化三元组提取器
        :param db_relations: 从数据库获取的关系词列表，用于提高匹配准确性
        """
        # 基础关系词列表（作为后备）
        self.base_relations = [
            '英文缩写', '创始人', '开发者', '是', '提出', '发明', '创建',
            '属于', '来自', '颜色', '大小', '重量', '长度', '宽度', '高度',
            '年龄', '生日', '国籍', '职业', '公司', '学校', '城市', '国家',
            '首都', '语言', '货币', '人口', '面积', 'GDP', '总统', '总理',
            '朝代', '年份', '时期', '时代'
        ]
        # 合并数据库关系词和基础关系词，去重
        all_relations = list(set(self.base_relations + (db_relations or [])))
        # 按长度从长到短排序，优先匹配长关系词
        self.all_relations = sorted(all_relations, key=len, reverse=True)

    def extract_entity_and_relation(self, question):
        """
        从问题中提取实体1和关系（用于查询）
        支持多种问题格式：
        1. "Python的创始人是谁" → (Python, 创始人)
        2. "人工智能英文缩写" → (人工智能, 英文缩写)
        3. "北京是中国的什么" → (北京, 是)
        4. "中国的首都是什么" → (中国的首都, 是) - 支持反向查询
        5. "爱因斯坦提出什么？" → (爱因斯坦, 提出) - 优先匹配关系词
        :param question: 用户问题
        :return: (entity1, relation) 或 (None, None)
        """
        entity1 = None
        relation = None
        question = question.strip()

        # 方法1: 优先匹配关系词（如"提出"、"发明"等），避免被疑问词干扰
        # 这样可以正确处理"爱因斯坦提出什么？"这种情况
        for rel in self.all_relations:
            if rel in question:
                # 找到关系词的位置
                rel_index = question.find(rel)
                # 关系词之前的部分作为实体1
                entity1_candidate = question[:rel_index].strip()
                # 如果实体不为空，且关系词后面可能跟着疑问词（如"什么"、"谁"等），这是正常情况
                if entity1_candidate:
                    entity1 = entity1_candidate
                    relation = rel
                    # 清理实体末尾可能的"的"字（但保留复合实体如"中国的首都"）
                    if entity1.endswith('的') and len(entity1) > 1:
                        # 检查是否是复合实体（包含多个"的"）
                        if entity1.count('的') > 1 or (entity1.count('的') == 1 and len(entity1.split('的')[0]) > 2):
                            pass  # 保留复合实体
                        else:
                            entity1 = entity1[:-1].strip()
                    return entity1, relation

        # 方法2: 处理"XX是什么"、"XX是谁"等格式
        # 优先匹配长关键词，避免误匹配
        question_patterns = [
            ('是什么', '是'),
            ('是谁', '是'),
            ('的什么', '是'),
            ('的谁', '是'),
        ]
        
        for pattern, default_rel in question_patterns:
            if pattern in question:
                # 提取"XX是什么"中的XX部分
                entity1 = question.split(pattern)[0].strip()
                relation = default_rel
                # 如果实体中包含"的"，保留完整实体（如"中国的首都"）
                if entity1:
                    return entity1, relation

        # 方法3: 提取实体1（分割停止词，但保留包含"的"的复合实体）
        stop_words = ['是', '什么', '谁', '哪', '哪一', '多少', '几', '怎么', '如何']
        for word in stop_words:
            if word in question:
                # 分割停止词，但需要特殊处理"的"
                parts = question.split(word)
                if parts:
                    entity1 = parts[0].strip()
                    # 如果实体以"的"结尾，说明是复合实体，保留它
                    # 例如："中国的首都是什么" → entity1="中国的首都"
                    if entity1.endswith('的'):
                        # 继续查找，看是否有更完整的实体
                        # 对于"中国的首都是什么"，应该保留"中国的首都"
                        pass
                    break

        # 提取关系（核心属性）
        if entity1:
            relation_keywords = ['是什么', '是谁', '是', '属于', '来自', '开发', '创建', '提出', '发明', '英文缩写']
            for keyword in relation_keywords:
                if keyword in question:
                    # 分割出关系部分（例如："Python的创始人是谁" → "创始人"）
                    if f"{entity1}的" in question:
                        parts = question.split(f"{entity1}的")[-1].split(keyword)[0].strip()
                        relation = parts if parts else keyword.replace('是', '').strip()
                    elif keyword in question:
                        # 处理"实体+关系"格式（如"人工智能英文缩写"）
                        remaining = question[len(entity1):].strip()
                        if remaining.startswith('的'):
                            remaining = remaining[1:].strip()
                        if keyword in remaining:
                            if remaining == keyword or remaining.startswith(keyword):
                                relation = keyword.replace('是什么', '是').replace('是谁', '是')
                            else:
                                relation = remaining.split(keyword)[0].strip() if remaining.split(keyword)[0].strip() else keyword.replace('是什么', '是').replace('是谁', '是')
                        else:
                            relation = keyword.replace('是什么', '是').replace('是谁', '是')
                    break
            
            # 如果没有找到关系，但实体已提取，尝试默认关系
            if not relation and entity1:
                # 检查问题中是否包含"是"
                if '是' in question:
                    relation = '是'

        return entity1, relation

    def extract_triple(self, question, answer, silent=False, input_callback=None):
        """
        从问题和答案中提取完整三元组（实体1-关系-实体2）
        :param question: 用户问题
        :param answer: 用户提供的答案
        :param silent: 是否静默模式（不打印，不等待输入）
        :param input_callback: 输入回调函数，格式：input_callback(prompt) -> str，用于GUI模式
        :return: (entity1, relation, entity2)
        """
        # 先尝试自动提取
        entity1, relation = self.extract_entity_and_relation(question)
        entity2 = answer.strip()

        # 自动提取失败时，引导用户手动输入
        if not entity1 or not relation:
            if silent:
                # GUI模式：使用回调函数获取输入
                if input_callback:
                    entity1 = input_callback("请输入实体（例如：Python）：") or ""
                    relation = input_callback("请输入关系（例如：创始人）：") or ""
                    entity2 = input_callback("请确认答案（例如：吉多·范罗苏姆）：") or answer.strip()
                else:
                    # 如果无法获取输入，使用默认值
                    entity1 = question.split('的')[0] if '的' in question else question[:10]
                    relation = '是'
            else:
                # 命令行模式：使用input
                print("\n📌 系统无法自动识别知识点结构，请手动补充：")
                entity1 = input("请输入实体（例如：Python）：").strip()
                relation = input("请输入关系（例如：创始人）：").strip()
                entity2 = input("请确认答案（例如：吉多·范罗苏姆）：").strip()

        return entity1, relation, entity2