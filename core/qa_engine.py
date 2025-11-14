# 核心问答引擎：整合各模块，实现问答主逻辑（查询→无答案→学习→保存）
from database.db_operation import DBOperation
from nlp.triple_extractor import TripleExtractor

class QAEngine:
    def __init__(self):
        self.db_operation = DBOperation()
        # 从数据库获取关系词列表，提高实体识别准确性
        db_relations = self.db_operation.get_all_relations()
        self.triple_extractor = TripleExtractor(db_relations=db_relations)

    def answer_question(self, question, silent=False):
        """
        处理用户问题，返回答案（或进入学习模式）
        :param question: 用户问题
        :param silent: 是否静默模式（不打印，只返回消息）
        :return: (answer, status_message) 
                - answer: 存在答案返回字符串，无答案返回None（触发学习流程）
                - status_message: 状态消息（如"无法识别实体"等）
        """
        # 1. 提取问题中的实体和关系
        entity1, relation = self.triple_extractor.extract_entity_and_relation(question)
        if not entity1:
            msg = "无法识别问题中的核心实体，请换种方式提问～"
            if not silent:
                print(msg)
            return None, msg

        # 2. 查询数据库
        answer = self.db_operation.query_knowledge(entity1, relation)
        if answer:
            return answer, None
        return None, None

    def learn_knowledge(self, question, user_answer, silent=False, input_callback=None):
        """
        学习新知识点并保存到数据库
        :param question: 用户问题
        :param user_answer: 用户提供的答案
        :param silent: 是否静默模式（不打印，只返回消息）
        :param input_callback: 输入回调函数，用于GUI模式获取手动输入
        :return: (success, message) 学习成功返回(True, "学习成功消息")，失败返回(False, "错误消息")
        """
        if not user_answer.strip():
            msg = "答案不能为空，本次学习取消～"
            if not silent:
                print(msg)
            return False, msg

        # 1. 提取三元组（需要处理手动输入的情况）
        entity1, relation, entity2 = self.triple_extractor.extract_triple(question, user_answer, silent=silent, input_callback=input_callback)

        # 2. 保存到数据库
        success = self.db_operation.save_knowledge(entity1, relation, entity2)
        if success:
            msg = f"学习成功！下次再问'{question}'我就知道啦～"
            if not silent:
                print(msg)
            return True, msg
        else:
            msg = "学习失败，请重试～"
            if not silent:
                print(msg)
            return False, msg

    def close(self):
        """关闭资源（数据库连接）"""
        self.db_operation.close()