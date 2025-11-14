"""
智能问答系统 - 图形界面版本
使用 tkinter 创建友好的用户界面
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from core.qa_engine import QAEngine
import threading


class QAGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 智能问答系统")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # 学习模式状态
        self.learning_mode = False
        self.current_question = ""
        
        # 创建界面（必须在初始化引擎之前，因为add_message需要chat_display）
        self.create_widgets()
        
        # 初始化问答引擎（在界面创建之后）
        self.qa_engine = None
        self.init_qa_engine()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def init_qa_engine(self):
        """初始化问答引擎"""
        try:
            self.qa_engine = QAEngine()
            self.add_message("🤖", "✅ 系统初始化成功！", "system")
        except Exception as e:
            messagebox.showerror("错误", f"系统初始化失败：{str(e)}")
            self.root.quit()
    
    def create_widgets(self):
        """创建界面组件"""
        # 标题区域
        title_frame = tk.Frame(self.root, bg="#4a90e2", height=60)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🤖 智能问答系统",
            font=("Microsoft YaHei", 18, "bold"),
            bg="#4a90e2",
            fg="white"
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            title_frame,
            text="支持精准问答 + 自动学习功能",
            font=("Microsoft YaHei", 10),
            bg="#4a90e2",
            fg="#e8f4f8"
        )
        subtitle_label.pack()
        
        # 输入区域 - 先创建并放在底部，确保显示
        input_container = tk.Frame(self.root, bg="#f0f0f0", height=70)
        input_container.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)
        input_container.pack_propagate(False)
        
        input_frame = tk.Frame(input_container, bg="#f0f0f0")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        self.input_entry = tk.Entry(
            input_frame,
            font=("Microsoft YaHei", 12),
            relief=tk.SOLID,
            borderwidth=2,
            bg="white",
            fg="#333333",
            insertbackground="#4a90e2",
            highlightthickness=2,
            highlightcolor="#4a90e2",
            highlightbackground="#cccccc"
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), ipady=8)
        self.input_entry.bind("<Return>", lambda e: self.send_message())
        self.input_entry.bind("<FocusIn>", lambda e: self.input_entry.config(highlightbackground="#4a90e2"))
        self.input_entry.bind("<FocusOut>", lambda e: self.input_entry.config(highlightbackground="#cccccc"))
        
        self.send_button = tk.Button(
            input_frame,
            text="发送",
            font=("Microsoft YaHei", 11, "bold"),
            bg="#4a90e2",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=25,
            pady=8,
            command=self.send_message,
            activebackground="#357abd",
            activeforeground="white"
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # 对话显示区域 - 放在中间，会自动填充剩余空间
        chat_frame = tk.Frame(self.root, bg="white")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Microsoft YaHei", 11),
            bg="white",
            fg="#333333",
            relief=tk.FLAT,
            padx=15,
            pady=15,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # 配置文本标签样式
        self.chat_display.tag_config("user", foreground="#2c3e50", font=("Microsoft YaHei", 11, "bold"))
        self.chat_display.tag_config("bot", foreground="#3498db", font=("Microsoft YaHei", 11))
        self.chat_display.tag_config("system", foreground="#95a5a6", font=("Microsoft YaHei", 10, "italic"))
        self.chat_display.tag_config("error", foreground="#e74c3c", font=("Microsoft YaHei", 11))
        
        # 添加欢迎消息
        self.add_message("🤖", "欢迎使用智能问答系统！请输入您的问题。", "system")
        
        # 确保输入框获得焦点
        self.root.after(100, lambda: self.input_entry.focus_set())
        
    def add_message(self, sender, message, tag="bot"):
        """添加消息到对话显示区域"""
        self.chat_display.config(state=tk.NORMAL)
        
        if sender == "你":
            self.chat_display.insert(tk.END, f"{sender}：", "user")
        elif sender == "🤖":
            self.chat_display.insert(tk.END, f"{sender}：", tag)
        else:
            self.chat_display.insert(tk.END, f"🤖 {sender}：", tag)
        
        self.chat_display.insert(tk.END, f"{message}\n\n", tag)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
        """发送消息并处理问答"""
        question = self.input_entry.get().strip()
        if not question:
            return
        
        # 清空输入框
        self.input_entry.delete(0, tk.END)
        
        # 显示用户问题
        self.add_message("你", question, "user")
        
        # 如果在学习模式，将输入作为答案处理
        if self.learning_mode:
            self.process_answer(question)
            return
        
        # 禁用输入，防止重复提交
        self.input_entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        
        # 在新线程中处理问题，避免界面卡顿
        threading.Thread(target=self.process_question, args=(question,), daemon=True).start()
    
    def process_question(self, question):
        """处理用户问题"""
        try:
            # 使用静默模式
            answer, status_msg = self.qa_engine.answer_question(question, silent=True)
            
            # 在主线程中更新UI
            self.root.after(0, self.update_ui_after_question, question, answer, status_msg)
        except Exception as e:
            self.root.after(0, self.show_error, f"处理问题时出错：{str(e)}")
    
    def update_ui_after_question(self, question, answer, status_msg):
        """更新UI（回答问题后）"""
        # 显示状态消息
        if status_msg:
            self.add_message("🤖", status_msg, "error")
        
        # 如果有答案，显示答案
        if answer:
            self.add_message("🤖", answer, "bot")
            self.enable_input()
        else:
            # 无答案，进入学习模式
            self.current_question = question
            self.learning_mode = True
            self.add_message("🤖", f"抱歉，我还不知道答案～ 请告诉我'{question}'的答案？", "bot")
            self.enable_input()
    
    def process_answer(self, answer):
        """处理用户提供的答案（学习模式）"""
        if not answer.strip():
            self.add_message("🤖", "答案不能为空，本次学习取消～", "error")
            self.learning_mode = False
            self.current_question = ""
            return
        
        # 禁用输入
        self.input_entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        
        # 在新线程中处理学习
        threading.Thread(
            target=self.learn_knowledge_thread,
            args=(self.current_question, answer),
            daemon=True
        ).start()
    
    def learn_knowledge_thread(self, question, answer):
        """在学习线程中处理知识学习"""
        try:
            # 先尝试自动提取，检查是否需要手动输入
            entity1, relation = self.qa_engine.triple_extractor.extract_entity_and_relation(question)
            
            if not entity1 or not relation:
                # 需要手动输入，在主线程中显示对话框
                self.root.after(0, self.show_triple_input_dialog, question, answer)
            else:
                # 可以直接学习
                success, msg = self.qa_engine.learn_knowledge(
                    question, answer, silent=True, input_callback=None
                )
                self.root.after(0, self.update_ui_after_learning, success, msg)
        except Exception as e:
            self.root.after(0, self.show_error, f"学习知识时出错：{str(e)}")
    
    def show_triple_input_dialog(self, question, answer):
        """显示三元组输入对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("手动补充知识点结构")
        dialog.geometry("500x300")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(
            dialog,
            text="📌 系统无法自动识别知识点结构，请手动补充：",
            font=("Microsoft YaHei", 10),
            bg="white",
            fg="#333333"
        ).pack(pady=10)
        
        # 实体输入
        tk.Label(dialog, text="实体：", font=("Microsoft YaHei", 10), bg="white").pack(anchor=tk.W, padx=20)
        entity_entry = tk.Entry(dialog, font=("Microsoft YaHei", 11), width=40)
        entity_entry.pack(padx=20, pady=5, fill=tk.X)
        entity_entry.insert(0, question.split('的')[0] if '的' in question else question[:20])
        
        # 关系输入
        tk.Label(dialog, text="关系：", font=("Microsoft YaHei", 10), bg="white").pack(anchor=tk.W, padx=20, pady=(10, 0))
        relation_entry = tk.Entry(dialog, font=("Microsoft YaHei", 11), width=40)
        relation_entry.pack(padx=20, pady=5, fill=tk.X)
        relation_entry.insert(0, "是")
        
        # 答案确认
        tk.Label(dialog, text="答案：", font=("Microsoft YaHei", 10), bg="white").pack(anchor=tk.W, padx=20, pady=(10, 0))
        answer_entry = tk.Entry(dialog, font=("Microsoft YaHei", 11), width=40)
        answer_entry.pack(padx=20, pady=5, fill=tk.X)
        answer_entry.insert(0, answer)
        
        result = {"entity": None, "relation": None, "answer": None, "confirmed": False}
        
        def confirm():
            result["entity"] = entity_entry.get().strip()
            result["relation"] = relation_entry.get().strip()
            result["answer"] = answer_entry.get().strip()
            result["confirmed"] = True
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog, bg="white")
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="确认",
            font=("Microsoft YaHei", 10, "bold"),
            bg="#4a90e2",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=5,
            command=confirm
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="取消",
            font=("Microsoft YaHei", 10),
            bg="#95a5a6",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=5,
            command=cancel
        ).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        
        if result["confirmed"] and result["entity"] and result["relation"]:
            # 使用手动输入的三元组进行学习
            threading.Thread(
                target=self.learn_with_triple,
                args=(result["entity"], result["relation"], result["answer"]),
                daemon=True
            ).start()
        else:
            self.learning_mode = False
            self.current_question = ""
            self.enable_input()
            if result["confirmed"]:
                self.add_message("🤖", "输入不完整，学习取消～", "error")
    
    def learn_with_triple(self, entity1, relation, entity2):
        """使用指定的三元组进行学习"""
        try:
            success = self.qa_engine.db_operation.save_knowledge(entity1, relation, entity2)
            if success:
                msg = f"学习成功！下次再问相关问题时我就知道啦～"
            else:
                msg = "学习失败，请重试～"
            self.root.after(0, self.update_ui_after_learning, success, msg)
        except Exception as e:
            self.root.after(0, self.show_error, f"保存知识时出错：{str(e)}")
    
    def update_ui_after_learning(self, success, msg):
        """更新UI（学习后）"""
        self.add_message("🤖", msg, "bot" if success else "error")
        self.learning_mode = False
        self.current_question = ""
        self.enable_input()
    
    def enable_input(self):
        """启用输入框"""
        self.input_entry.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.input_entry.focus()
    
    def show_error(self, error_msg):
        """显示错误消息"""
        self.add_message("🤖", error_msg, "error")
        self.enable_input()
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.qa_engine:
            self.qa_engine.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = QAGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

