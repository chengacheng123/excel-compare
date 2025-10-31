import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta


class AdvancedAccountingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("高级记账软件 - 带搜索功能")
        self.root.geometry("1000x800")

        # 初始化数据库
        self.init_database()

        # 创建界面
        self.create_widgets()

        # 加载数据
        self.load_data()

    def init_database(self):
        """初始化数据库"""
        self.conn = sqlite3.connect('accounting.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS transactions
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                date
                                TEXT
                                NOT
                                NULL,
                                type
                                TEXT
                                NOT
                                NULL,
                                category
                                TEXT
                                NOT
                                NULL,
                                amount
                                REAL
                                NOT
                                NULL,
                                description
                                TEXT
                            )
                            ''')
        self.conn.commit()

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="高级记账软件", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="新增记账记录", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        self.create_input_form(input_frame)

        # 搜索区域
        search_frame = ttk.LabelFrame(main_frame, text="搜索和筛选", padding="10")
        search_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        self.create_search_panel(search_frame)

        # 记录列表
        list_frame = ttk.LabelFrame(main_frame, text="交易记录", padding="10")
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        self.create_transaction_list(list_frame)

        # 统计信息
        stats_frame = ttk.LabelFrame(main_frame, text="统计信息", padding="10")
        stats_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.create_statistics(stats_frame)

        # 配置网格权重
        self.configure_grid_weights(main_frame, list_frame)

    def create_search_panel(self, parent):
        """创建搜索面板"""
        # 第一行搜索条件
        row = 0

        # 关键词搜索
        ttk.Label(parent, text="关键词:").grid(row=row, column=0, sticky=tk.W, padx=(0, 5))
        self.search_keyword = ttk.Entry(parent, width=15)
        self.search_keyword.grid(row=row, column=1, sticky=tk.W, padx=(0, 15))

        # 类型筛选
        ttk.Label(parent, text="类型:").grid(row=row, column=2, sticky=tk.W, padx=(0, 5))
        self.search_type = ttk.Combobox(parent, values=["全部", "收入", "支出"], width=8, state="readonly")
        self.search_type.set("全部")
        self.search_type.grid(row=row, column=3, sticky=tk.W, padx=(0, 15))

        # 类别筛选
        ttk.Label(parent, text="类别:").grid(row=row, column=4, sticky=tk.W, padx=(0, 5))
        categories = ["全部", "餐饮", "交通", "购物", "娱乐", "医疗", "教育", "工资", "奖金", "投资", "其他"]
        self.search_category = ttk.Combobox(parent, values=categories, width=8, state="readonly")
        self.search_category.set("全部")
        self.search_category.grid(row=row, column=5, sticky=tk.W, padx=(0, 15))

        # 第二行搜索条件
        row = 1

        # 日期范围
        ttk.Label(parent, text="开始日期:").grid(row=row, column=0, sticky=tk.W, padx=(0, 5))
        self.search_start_date = ttk.Entry(parent, width=12)
        self.search_start_date.grid(row=row, column=1, sticky=tk.W, padx=(0, 15))

        ttk.Label(parent, text="结束日期:").grid(row=row, column=2, sticky=tk.W, padx=(0, 5))
        self.search_end_date = ttk.Entry(parent, width=12)
        self.search_end_date.grid(row=row, column=3, sticky=tk.W, padx=(0, 15))

        # 金额范围
        ttk.Label(parent, text="最小金额:").grid(row=row, column=4, sticky=tk.W, padx=(0, 5))
        self.search_min_amount = ttk.Entry(parent, width=10)
        self.search_min_amount.grid(row=row, column=5, sticky=tk.W, padx=(0, 15))

        ttk.Label(parent, text="最大金额:").grid(row=row, column=6, sticky=tk.W, padx=(0, 5))
        self.search_max_amount = ttk.Entry(parent, width=10)
        self.search_max_amount.grid(row=row, column=7, sticky=tk.W)

        # 第三行按钮
        row = 2
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=8, pady=(15, 5))

        ttk.Button(button_frame, text="搜索", command=self.search_transactions).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="重置搜索", command=self.reset_search).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="快速筛选-本月", command=lambda: self.quick_filter('month')).pack(side=tk.LEFT,
                                                                                                        padx=(0, 10))
        ttk.Button(button_frame, text="快速筛选-本周", command=lambda: self.quick_filter('week')).pack(side=tk.LEFT,
                                                                                                       padx=(0, 10))
        ttk.Button(button_frame, text="显示全部", command=self.load_data).pack(side=tk.LEFT)

        # 设置默认日期
        self.set_default_dates()

    def set_default_dates(self):
        """设置默认日期范围"""
        today = datetime.now()
        first_day = today.replace(day=1)
        self.search_start_date.insert(0, first_day.strftime("%Y-%m-%d"))
        self.search_end_date.insert(0, today.strftime("%Y-%m-%d"))

    def search_transactions(self):
        """执行搜索"""
        try:
            # 构建查询条件
            conditions = []
            params = []

            # 关键词搜索（描述和类别）
            keyword = self.search_keyword.get().strip()
            if keyword:
                conditions.append("(description LIKE ? OR category LIKE ?)")
                params.extend([f'%{keyword}%', f'%{keyword}%'])

            # 类型筛选
            trans_type = self.search_type.get()
            if trans_type != "全部":
                conditions.append("type = ?")
                params.append(trans_type)

            # 类别筛选
            category = self.search_category.get()
            if category != "全部":
                conditions.append("category = ?")
                params.append(category)

            # 日期范围
            start_date = self.search_start_date.get().strip()
            end_date = self.search_end_date.get().strip()
            if start_date:
                conditions.append("date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("date <= ?")
                params.append(end_date)

            # 金额范围
            min_amount = self.search_min_amount.get().strip()
            max_amount = self.search_max_amount.get().strip()
            if min_amount:
                conditions.append("amount >= ?")
                params.append(float(min_amount))
            if max_amount:
                conditions.append("amount <= ?")
                params.append(float(max_amount))

            # 构建SQL查询
            sql = "SELECT * FROM transactions"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            sql += " ORDER BY date DESC, id DESC"

            # 执行查询
            self.cursor.execute(sql, params)
            rows = self.cursor.fetchall()

            # 更新显示
            self.update_display(rows)

            # 显示搜索结果统计
            messagebox.showinfo("搜索完成", f"找到 {len(rows)} 条记录")

        except Exception as e:
            messagebox.showerror("搜索错误", f"搜索时出错: {str(e)}")

    def quick_filter(self, filter_type):
        """快速筛选"""
        today = datetime.now()

        if filter_type == 'month':
            # 本月数据
            first_day = today.replace(day=1)
            self.search_start_date.delete(0, tk.END)
            self.search_start_date.insert(0, first_day.strftime("%Y-%m-%d"))
            self.search_end_date.delete(0, tk.END)
            self.search_end_date.insert(0, today.strftime("%Y-%m-%d"))

        elif filter_type == 'week':
            # 本周数据
            start_of_week = today - timedelta(days=today.weekday())
            self.search_start_date.delete(0, tk.END)
            self.search_start_date.insert(0, start_of_week.strftime("%Y-%m-%d"))
            self.search_end_date.delete(0, tk.END)
            self.search_end_date.insert(0, today.strftime("%Y-%m-%d"))

        # 自动执行搜索
        self.search_transactions()

    def reset_search(self):
        """重置搜索条件"""
        self.search_keyword.delete(0, tk.END)
        self.search_type.set("全部")
        self.search_category.set("全部")
        self.search_start_date.delete(0, tk.END)
        self.search_end_date.delete(0, tk.END)
        self.search_min_amount.delete(0, tk.END)
        self.search_max_amount.delete(0, tk.END)
        self.set_default_dates()
        self.load_data()

    def update_display(self, rows):
        """更新表格显示"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 显示新数据
        for row in rows:
            formatted_row = list(row)
            formatted_row[4] = f"{row[4]:.2f}"
            self.tree.insert("", "end", values=formatted_row)

        # 更新统计信息（基于当前显示的数据）
        self.update_stats_for_display(rows)

    def update_stats_for_display(self, rows):
        """基于显示的数据更新统计"""
        income = 0
        expense = 0

        for row in rows:
            if row[2] == "收入":  # type字段
                income += row[4]  # amount字段
            elif row[2] == "支出":
                expense += row[4]

        balance = income - expense

        stats_text = (f"显示记录: {len(rows)} 条 | "
                      f"总收入: ¥{income:,.2f} | "
                      f"总支出: ¥{expense:,.2f} | "
                      f"余额: ¥{balance:,.2f}")

        self.stats_label.config(text=stats_text)

    # 其他方法保持不变（create_input_form, create_transaction_list等）
    def create_input_form(self, parent):
        """创建输入表单"""
        # 简化的输入表单，与之前相同
        ttk.Label(parent, text="日期:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.date_entry = ttk.Entry(parent, width=12)
        self.date_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(parent, text="类型:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.type_var = tk.StringVar(value="支出")
        type_combo = ttk.Combobox(parent, textvariable=self.type_var, values=["收入", "支出"], width=8,
                                  state="readonly")
        type_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))

        ttk.Label(parent, text="类别:").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.category_var = tk.StringVar()
        categories = ["餐饮", "交通", "购物", "娱乐", "医疗", "教育", "工资", "奖金", "投资", "其他"]
        category_combo = ttk.Combobox(parent, textvariable=self.category_var, values=categories, width=8)
        category_combo.grid(row=0, column=5, sticky=tk.W, padx=(0, 20))

        ttk.Label(parent, text="金额:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.amount_entry = ttk.Entry(parent, width=12)
        self.amount_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 20))

        ttk.Label(parent, text="描述:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10))
        self.desc_entry = ttk.Entry(parent, width=30)
        self.desc_entry.grid(row=1, column=3, columnspan=3, sticky=(tk.W, tk.E))

        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=6, pady=(10, 0))

        ttk.Button(button_frame, text="添加记录", command=self.add_transaction).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="清空输入", command=self.clear_inputs).pack(side=tk.LEFT)

        parent.columnconfigure(3, weight=1)

    def create_transaction_list(self, parent):
        """创建交易记录列表"""
        columns = ("ID", "日期", "类型", "类别", "金额", "描述")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)

        column_widths = {"ID": 50, "日期": 100, "类型": 80, "类别": 100, "金额": 100, "描述": 200}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col])

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        ttk.Button(parent, text="删除选中记录", command=self.delete_transaction).grid(row=1, column=0, pady=(10, 0),
                                                                                      sticky=tk.W)

    def create_statistics(self, parent):
        """创建统计信息显示"""
        self.stats_label = ttk.Label(parent, text="正在加载统计信息...", font=("Arial", 11))
        self.stats_label.grid(row=0, column=0, sticky=tk.W)

    def configure_grid_weights(self, main_frame, list_frame):
        """配置网格权重"""
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def add_transaction(self):
        """添加交易记录"""
        try:
            date = self.date_entry.get()
            trans_type = self.type_var.get()
            category = self.category_var.get()
            amount = self.amount_entry.get()
            description = self.desc_entry.get()

            if not all([date, trans_type, category, amount]):
                messagebox.showerror("错误", "请填写所有必填字段!")
                return

            try:
                amount = float(amount)
                if amount <= 0:
                    messagebox.showerror("错误", "金额必须大于0!")
                    return
            except ValueError:
                messagebox.showerror("错误", "金额必须是有效的数字!")
                return

            self.cursor.execute(
                "INSERT INTO transactions (date, type, category, amount, description) VALUES (?, ?, ?, ?, ?)",
                (date, trans_type, category, amount, description)
            )
            self.conn.commit()

            self.load_data()
            self.clear_inputs()
            messagebox.showinfo("成功", "记账记录添加成功!")

        except Exception as e:
            messagebox.showerror("错误", f"添加记录时出错: {str(e)}")

    def delete_transaction(self):
        """删除选中的交易记录"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的记录!")
            return

        if messagebox.askyesno("确认删除", "确定要删除选中的记录吗？"):
            try:
                for item in selected:
                    trans_id = self.tree.item(item)['values'][0]
                    self.cursor.execute("DELETE FROM transactions WHERE id=?", (trans_id,))

                self.conn.commit()
                self.load_data()
                messagebox.showinfo("成功", f"已删除 {len(selected)} 条记录!")
            except Exception as e:
                messagebox.showerror("错误", f"删除记录时出错: {str(e)}")

    def load_data(self):
        """加载所有数据"""
        try:
            self.cursor.execute("SELECT * FROM transactions ORDER BY date DESC, id DESC")
            rows = self.cursor.fetchall()
            self.update_display(rows)
        except Exception as e:
            messagebox.showerror("错误", f"加载数据时出错: {str(e)}")

    def clear_inputs(self):
        """清空输入框"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.type_var.set("支出")
        self.category_var.set("")
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedAccountingApp(root)
    root.mainloop()