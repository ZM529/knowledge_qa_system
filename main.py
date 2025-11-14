from core.qa_engine import QAEngine

def main():
    # 初始化问答引擎
    qa_engine = QAEngine()
    print("======================================")
    print("🤖 智能问答系统（输入 'quit' 退出）")
    print("📚 支持精准问答+自动学习功能")
    print("======================================")

    try:
        # 交互式对话循环
        while True:
            question = input("\n你：").strip()
            if question.lower() == 'quit':
                print("🤖 再见！欢迎下次使用～")
                break
            if not question:
                print("🤖 请输入有效的问题哦～")
                continue

            # 1. 尝试回答问题
            answer, status_msg = qa_engine.answer_question(question)
            if status_msg:
                print(status_msg)
            if answer:
                print(f"🤖 {answer}")
                continue

            # 2. 无答案，进入学习模式
            print(f"🤖 抱歉，我还不知道答案～ 请告诉我'{question}'的答案？")
            user_answer = input("你（答案）：").strip()
            success, learn_msg = qa_engine.learn_knowledge(question, user_answer)
            if learn_msg:
                print(learn_msg)
    finally:
        # 关闭资源
        qa_engine.close()

if __name__ == "__main__":
    main()