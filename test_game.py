import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
import time
from typing import Dict, List, Tuple, Optional

# 设置matplotlib支持中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


class Country:
    """表示一个国家，包含其经济指标和贸易政策"""

    def __init__(self, name: str, initial_gdp: float = 1000.0,
                 initial_unemployment: float = 5.0,
                 initial_inflation: float = 2.0):
        self.name = name
        self.gdp = initial_gdp  # 国内生产总值（十亿美元）
        self.unemployment = initial_unemployment  # 失业率（百分比）
        self.inflation = initial_inflation  # 通货膨胀率（百分比）
        self.foreign_reserves = 100.0  # 外汇储备（十亿美元）
        self.trade_partners = {}  # 贸易伙伴及其关税税率 {国家名称: 关税税率}
        self.export_demand = {}  # 对各国的出口需求 {国家名称: 需求值}
        self.imports = {}  # 从各国的进口 {国家名称: 进口额}
        self.year = 1  # 当前游戏年份

        # 用于绘图的数据历史
        self.gdp_history = [initial_gdp]
        self.unemployment_history = [initial_unemployment]
        self.inflation_history = [initial_inflation]
        self.trade_balance_history = [0]

    def add_trade_partner(self, partner: 'Country', tariff_rate: float = 0.1):
        """添加贸易伙伴并设置初始关税税率"""
        self.trade_partners[partner.name] = tariff_rate
        self.export_demand[partner.name] = random.uniform(50, 100)
        self.imports[partner.name] = random.uniform(30, 80)

    def adjust_tariff(self, partner_name: str, new_tariff: float):
        """调整对特定贸易伙伴的关税税率"""
        if partner_name in self.trade_partners:
            self.trade_partners[partner_name] = new_tariff
            return True
        return False

    def simulate_year(self):
        """模拟一年的经济发展"""
        # 基础经济增长
        base_gdp_growth = random.uniform(1.0, 3.0)
        gdp_change = self.gdp * (base_gdp_growth / 100)

        # 计算贸易平衡
        trade_balance = 0
        for partner_name, demand in self.export_demand.items():
            tariff = self.trade_partners.get(partner_name, 0.1)
            # 关税越高，出口需求越低
            effective_demand = demand * (1 - tariff)
            export_value = effective_demand * 0.8  # 出口价值
            gdp_change += export_value * 0.3  # 出口对GDP的贡献

            # 进口影响
            import_value = self.imports.get(partner_name, 0)
            # 关税收入
            tariff_revenue = import_value * tariff
            gdp_change += tariff_revenue * 0.1  # 关税收入对GDP的贡献

            trade_balance += export_value - import_value

        # 更新外汇储备
        self.foreign_reserves += trade_balance

        # 贸易平衡影响GDP
        if trade_balance > 0:
            gdp_change += trade_balance * 0.05  # 贸易顺差促进增长
        else:
            gdp_change -= abs(trade_balance) * 0.03  # 贸易逆差抑制增长

        # 高关税可能导致国内通货膨胀
        avg_tariff = sum(self.trade_partners.values()) / len(self.trade_partners) if self.trade_partners else 0
        inflation_impact = avg_tariff * 2
        self.inflation += inflation_impact - 0.5  # 随机波动

        # 经济状况影响失业率
        if gdp_change > 0:
            unemployment_change = -min(0.5, gdp_change / self.gdp * 0.8)
        else:
            unemployment_change = max(0.5, abs(gdp_change) / self.gdp * 1.2)
        self.unemployment += unemployment_change

        # 更新GDP
        self.gdp += gdp_change

        # 调整进口需求
        for partner_name in self.imports:
            # 经济增长会增加进口需求
            self.imports[partner_name] *= (1 + gdp_change / self.gdp * 0.7)
            # 通货膨胀会抑制进口需求
            self.imports[partner_name] /= (1 + self.inflation / 100 * 0.5)

        # 调整出口需求（贸易伙伴的反馈）
        for partner_name in self.export_demand:
            # 如果对某国关税过高，可能导致报复性关税
            if self.trade_partners[partner_name] > 0.25:
                retaliation_chance = min(0.7, (self.trade_partners[partner_name] - 0.2) * 5)
                if random.random() < retaliation_chance:
                    self.export_demand[partner_name] *= 0.8
                    return f"警告: {partner_name}因您的高关税实施了报复性贸易限制！"

        # 随机事件
        event_message = self._handle_random_event()

        # 更新历史数据
        self.gdp_history.append(self.gdp)
        self.unemployment_history.append(self.unemployment)
        self.inflation_history.append(self.inflation)
        self.trade_balance_history.append(trade_balance)

        # 更新年份
        self.year += 1

        return event_message

    def _handle_random_event(self):
        """处理随机经济事件"""
        events = [
            ("全球经济繁荣", 0.1, lambda: (self.gdp * random.uniform(0.02, 0.04), -0.7, -0.5)),
            ("全球经济衰退", 0.1, lambda: (-self.gdp * random.uniform(0.01, 0.03), 0.9, 0.8)),
            ("技术突破", 0.15, lambda: (self.gdp * random.uniform(0.015, 0.035), -0.5, -0.3)),
            ("自然灾害", 0.05, lambda: (-self.gdp * random.uniform(0.01, 0.02), 0.4, 0.3)),
            ("能源价格暴跌", 0.1, lambda: (self.gdp * random.uniform(0.01, 0.025), -0.3, -1.2)),
            ("能源价格飙升", 0.1, lambda: (-self.gdp * random.uniform(0.01, 0.02), 0.5, 1.5)),
            (None, 0.45, lambda: (0, 0, 0))  # 无事件
        ]

        weights = [event[1] for event in events]
        event = random.choices(events, weights=weights)[0]

        if event[0]:
            gdp_effect, unemp_effect, infl_effect = event[2]()
            self.gdp += gdp_effect
            self.unemployment += unemp_effect
            self.inflation += infl_effect
            return f"事件: {event[0]}!"

        return None

    def get_economic_summary(self) -> str:
        """获取当前经济状况摘要"""
        summary = f"\n=== {self.name} 经济状况 ({self.year}年) ===\n"
        summary += f"国内生产总值: {self.gdp:.2f} 十亿美元\n"
        summary += f"失业率: {self.unemployment:.1f}%\n"
        summary += f"通货膨胀率: {self.inflation:.1f}%\n"
        summary += f"外汇储备: {self.foreign_reserves:.2f} 十亿美元\n"

        trade_summary = "\n贸易情况:\n"
        total_exports = sum(self.export_demand.values()) * 0.8
        total_imports = sum(self.imports.values())
        trade_balance = total_exports - total_imports

        trade_summary += f"总出口: {total_exports:.2f} 十亿美元\n"
        trade_summary += f"总进口: {total_imports:.2f} 十亿美元\n"
        trade_summary += f"贸易平衡: {trade_balance:+.2f} 十亿美元\n"

        return summary + trade_summary


class TradeSimulationGUI:
    """贸易模拟游戏图形界面"""

    def __init__(self, root):
        self.root = root
        self.root.title("国家贸易模拟器")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # 设置主题颜色
        self.bg_color = "#f5f5f5"
        self.header_color = "#165DFF"
        self.card_color = "#ffffff"
        self.text_color = "#1D2129"
        self.button_color = "#165DFF"
        self.button_text_color = "#ffffff"

        # 创建国家
        self.player_country = Country("华夏共和国")
        self.trade_partners = self._create_trade_partners()
        self._setup_initial_trade_relations()

        # 游戏状态
        self.game_over = False

        # 创建UI
        self._create_widgets()
        self._update_display()

    def _create_trade_partners(self) -> List[Country]:
        """创建AI控制的贸易伙伴国家"""
        return [
            Country("西方联盟", 1500.0, 4.5, 1.8),
            Country("南方共同体", 800.0, 7.2, 3.5),
            Country("北方联邦", 600.0, 5.8, 2.2),
            Country("东方群岛", 400.0, 3.9, 1.5)
        ]

    def _setup_initial_trade_relations(self):
        """设置初始贸易关系"""
        for partner in self.trade_partners:
            self.player_country.add_trade_partner(partner)
            partner.add_trade_partner(self.player_country)

    def _create_widgets(self):
        """创建UI组件"""
        # 主框架
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 顶部标题
        self.header_frame = tk.Frame(self.main_frame, bg=self.header_color, height=80)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        self.header_frame.pack_propagate(False)

        self.title_label = tk.Label(self.header_frame, text="国家贸易模拟器",
                                    font=("SimHei", 24, "bold"),
                                    bg=self.header_color, fg="white")
        self.title_label.pack(pady=20)

        # 年份显示
        self.year_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.year_frame.pack(fill=tk.X, pady=(0, 10))

        self.year_label = tk.Label(self.year_frame, text=f"第 {self.player_country.year} 年",
                                   font=("SimHei", 16), bg=self.bg_color)
        self.year_label.pack(side=tk.LEFT, padx=10)

        # 主要内容区域 - 使用Notebook创建标签页
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # 经济概览标签页
        self.overview_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.overview_frame, text="经济概览")

        # 贸易政策标签页
        self.policy_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.policy_frame, text="贸易政策")

        # 贸易伙伴标签页
        self.partners_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.partners_frame, text="贸易伙伴")

        # 事件日志标签页
        self.log_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.log_frame, text="事件日志")

        # 创建各标签页内容
        self._create_overview_tab()
        self._create_policy_tab()
        self._create_partners_tab()
        self._create_log_tab()

        # 底部按钮区域
        self.button_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.button_frame.pack(fill=tk.X, pady=10)

        self.next_year_btn = tk.Button(self.button_frame, text="进入下一年",
                                       bg=self.button_color, fg=self.button_text_color,
                                       font=("SimHei", 12), command=self._simulate_next_year)
        self.next_year_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        self.help_btn = tk.Button(self.button_frame, text="游戏帮助",
                                  bg="#6c757d", fg="white",
                                  font=("SimHei", 12), command=self._show_help)
        self.help_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        # 事件日志
        self.event_log = []

    def _create_overview_tab(self):
        """创建经济概览标签页"""
        # 左侧经济指标
        self.indicators_frame = tk.LabelFrame(self.overview_frame, text="经济指标",
                                              font=("SimHei", 14), bg=self.bg_color)
        self.indicators_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # GDP
        self.gdp_frame = tk.Frame(self.indicators_frame, bg=self.card_color)
        self.gdp_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)

        self.gdp_label = tk.Label(self.gdp_frame, text="国内生产总值:",
                                  font=("SimHei", 12), bg=self.card_color)
        self.gdp_label.pack(side=tk.LEFT, padx=10)

        self.gdp_value = tk.Label(self.gdp_frame, text="1000.00 十亿美元",
                                  font=("SimHei", 12, "bold"), bg=self.card_color)
        self.gdp_value.pack(side=tk.RIGHT, padx=10)

        # 失业率
        self.unemployment_frame = tk.Frame(self.indicators_frame, bg=self.card_color)
        self.unemployment_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)

        self.unemployment_label = tk.Label(self.unemployment_frame, text="失业率:",
                                           font=("SimHei", 12), bg=self.card_color)
        self.unemployment_label.pack(side=tk.LEFT, padx=10)

        self.unemployment_value = tk.Label(self.unemployment_frame, text="5.0%",
                                           font=("SimHei", 12, "bold"), bg=self.card_color)
        self.unemployment_value.pack(side=tk.RIGHT, padx=10)

        # 通货膨胀率
        self.inflation_frame = tk.Frame(self.indicators_frame, bg=self.card_color)
        self.inflation_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)

        self.inflation_label = tk.Label(self.inflation_frame, text="通货膨胀率:",
                                        font=("SimHei", 12), bg=self.card_color)
        self.inflation_label.pack(side=tk.LEFT, padx=10)

        self.inflation_value = tk.Label(self.inflation_frame, text="2.0%",
                                        font=("SimHei", 12, "bold"), bg=self.card_color)
        self.inflation_value.pack(side=tk.RIGHT, padx=10)

        # 外汇储备
        self.reserves_frame = tk.Frame(self.indicators_frame, bg=self.card_color)
        self.reserves_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)

        self.reserves_label = tk.Label(self.reserves_frame, text="外汇储备:",
                                       font=("SimHei", 12), bg=self.card_color)
        self.reserves_label.pack(side=tk.LEFT, padx=10)

        self.reserves_value = tk.Label(self.reserves_frame, text="100.00 十亿美元",
                                       font=("SimHei", 12, "bold"), bg=self.card_color)
        self.reserves_value.pack(side=tk.RIGHT, padx=10)

        # 贸易平衡
        self.trade_balance_frame = tk.Frame(self.indicators_frame, bg=self.card_color)
        self.trade_balance_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)

        self.trade_balance_label = tk.Label(self.trade_balance_frame, text="贸易平衡:",
                                            font=("SimHei", 12), bg=self.card_color)
        self.trade_balance_label.pack(side=tk.LEFT, padx=10)

        self.trade_balance_value = tk.Label(self.trade_balance_frame, text="0.00 十亿美元",
                                            font=("SimHei", 12, "bold"), bg=self.card_color)
        self.trade_balance_value.pack(side=tk.RIGHT, padx=10)

        # 右侧图表
        self.charts_frame = tk.LabelFrame(self.overview_frame, text="经济趋势",
                                          font=("SimHei", 14), bg=self.bg_color)
        self.charts_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建图表
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _create_policy_tab(self):
        """创建贸易政策标签页"""
        # 关税调整区域
        self.tariff_frame = tk.LabelFrame(self.policy_frame, text="关税政策",
                                          font=("SimHei", 14), bg=self.bg_color)
        self.tariff_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建贸易伙伴的关税调整控件
        self.tariff_widgets = {}
        for i, partner in enumerate(self.trade_partners):
            frame = tk.Frame(self.tariff_frame, bg=self.card_color)
            frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)

            label = tk.Label(frame, text=f"{partner.name}:",
                             font=("SimHei", 12), bg=self.card_color)
            label.pack(side=tk.LEFT, padx=10)

            tariff_var = tk.DoubleVar(value=self.player_country.trade_partners[partner.name] * 100)
            scale = tk.Scale(frame, from_=0, to=50, orient=tk.HORIZONTAL,
                             resolution=1, length=200, bg=self.card_color)
            scale.config(variable=tariff_var)
            scale.pack(side=tk.LEFT, padx=10)

            value_label = tk.Label(frame, textvariable=tariff_var,
                                   font=("SimHei", 12), bg=self.card_color, width=5)
            value_label.pack(side=tk.LEFT, padx=5)

            percent_label = tk.Label(frame, text="%",
                                     font=("SimHei", 12), bg=self.card_color)
            percent_label.pack(side=tk.LEFT)

            apply_btn = tk.Button(frame, text="应用",
                                  bg=self.button_color, fg=self.button_text_color,
                                  font=("SimHei", 10),
                                  command=lambda p=partner.name, v=tariff_var: self._apply_tariff(p, v))
            apply_btn.pack(side=tk.RIGHT, padx=10)

            self.tariff_widgets[partner.name] = {
                "frame": frame,
                "scale": scale,
                "value_label": value_label,
                "var": tariff_var
            }

    def _create_partners_tab(self):
        """创建贸易伙伴标签页"""
        # 贸易伙伴列表
        self.partners_list_frame = tk.LabelFrame(self.partners_frame, text="贸易伙伴",
                                                 font=("SimHei", 14), bg=self.bg_color)
        self.partners_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建表格
        columns = ("国家", "关税", "出口额", "进口额", "贸易平衡")
        self.partners_tree = ttk.Treeview(self.partners_list_frame, columns=columns, show="headings")

        # 设置列标题
        for col in columns:
            self.partners_tree.heading(col, text=col)
            width = 150 if col != "国家" else 200
            self.partners_tree.column(col, width=width, anchor=tk.CENTER)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.partners_list_frame, orient=tk.VERTICAL, command=self.partners_tree.yview)
        self.partners_tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.partners_tree.pack(fill=tk.BOTH, expand=True)

    def _create_log_tab(self):
        """创建事件日志标签页"""
        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD,
                                                  font=("SimHei", 12), bg=self.card_color)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_text.config(state=tk.DISABLED)

    def _update_display(self):
        """更新UI显示"""
        # 更新年份
        self.year_label.config(text=f"第 {self.player_country.year} 年")

        # 更新经济指标
        self.gdp_value.config(text=f"{self.player_country.gdp:.2f} 十亿美元")
        self.unemployment_value.config(text=f"{self.player_country.unemployment:.1f}%")
        self.inflation_value.config(text=f"{self.player_country.inflation:.1f}%")
        self.reserves_value.config(text=f"{self.player_country.foreign_reserves:.2f} 十亿美元")

        # 计算并更新贸易平衡
        total_exports = sum(self.player_country.export_demand.values()) * 0.8
        total_imports = sum(self.player_country.imports.values())
        trade_balance = total_exports - total_imports
        self.trade_balance_value.config(text=f"{trade_balance:+.2f} 十亿美元")

        # 更新关税政策标签页
        for partner_name, widgets in self.tariff_widgets.items():
            widgets["var"].set(self.player_country.trade_partners[partner_name] * 100)

        # 更新贸易伙伴标签页
        self.partners_tree.delete(*self.partners_tree.get_children())
        for partner_name in self.player_country.trade_partners:
            tariff = self.player_country.trade_partners[partner_name] * 100
            exports = self.player_country.export_demand[partner_name] * 0.8
            imports = self.player_country.imports.get(partner_name, 0)
            balance = exports - imports

            # 添加到表格
            self.partners_tree.insert("", tk.END, values=(
                partner_name,
                f"{tariff:.1f}%",
                f"{exports:.2f}B",
                f"{imports:.2f}B",
                f"{balance:+.2f}B"
            ))

        # 更新图表
        self._update_charts()

    def _update_charts(self):
        """更新经济趋势图表"""
        # 清除现有图表
        self.ax1.clear()
        self.ax2.clear()

        # 年份列表
        years = list(range(1, self.player_country.year + 1))

        # GDP和贸易平衡图表
        self.ax1.plot(years, self.player_country.gdp_history, 'b-', label='GDP')
        self.ax1.set_ylabel('GDP (十亿美元)', color='b')
        self.ax1.tick_params(axis='y', labelcolor='b')

        ax1_twin = self.ax1.twinx()
        ax1_twin.plot(years, self.player_country.trade_balance_history, 'r-', label='贸易平衡')
        ax1_twin.set_ylabel('贸易平衡 (十亿美元)', color='r')
        ax1_twin.tick_params(axis='y', labelcolor='r')

        self.ax1.set_title('GDP与贸易平衡趋势')
        self.ax1.grid(True, linestyle='--', alpha=0.7)

        # 失业率和通货膨胀率图表
        self.ax2.plot(years, self.player_country.unemployment_history, 'g-', label='失业率')
        self.ax2.set_ylabel('失业率 (%)', color='g')
        self.ax2.tick_params(axis='y', labelcolor='g')

        ax2_twin = self.ax2.twinx()
        ax2_twin.plot(years, self.player_country.inflation_history, 'm-', label='通货膨胀率')
        ax2_twin.set_ylabel('通货膨胀率 (%)', color='m')
        ax2_twin.tick_params(axis='y', labelcolor='m')

        self.ax2.set_title('失业率与通货膨胀率趋势')
        self.ax2.set_xlabel('年份')
        self.ax2.grid(True, linestyle='--', alpha=0.7)

        # 调整布局
        self.fig.tight_layout()
        self.canvas.draw()

    def _apply_tariff(self, partner_name, tariff_var):
        """应用关税调整"""
        new_tariff = tariff_var.get() / 100  # 转换为小数
        success = self.player_country.adjust_tariff(partner_name, new_tariff)

        if success:
            self._log_event(f"已将对{partner_name}的关税调整为{new_tariff * 100:.1f}%")
            self._update_display()

    def _log_event(self, message):
        """记录事件到日志"""
        self.event_log.append(f"第{self.player_country.year}年: {message}")

        # 更新日志显示
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        for event in self.event_log:
            self.log_text.insert(tk.END, event + "\n\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def _simulate_next_year(self):
        """模拟下一年"""
        if self.game_over:
            messagebox.showinfo("游戏结束", "游戏已结束，请重新启动。")
            return

        # 显示处理中消息
        self.next_year_btn.config(state=tk.DISABLED, text="处理中...")
        self.root.update()

        # 模拟一年
        event_message = self.player_country.simulate_year()

        # 记录事件
        if event_message:
            self._log_event(event_message)

        # 更新显示
        self._update_display()

        # 检查游戏是否结束
        if self.player_country.year > 5:
            self._end_game()
        else:
            self._log_event("年度经济报告已更新")
            self.next_year_btn.config(state=tk.NORMAL, text="进入下一年")

    def _end_game(self):
        """结束游戏并显示结果"""
        self.game_over = True
        self.next_year_btn.config(state=tk.DISABLED, text="游戏结束")

        # 计算总体变化
        initial_gdp = 1000.0
        initial_unemployment = 5.0
        initial_inflation = 2.0

        gdp_growth = (self.player_country.gdp - initial_gdp) / initial_gdp * 100
        unemployment_change = self.player_country.unemployment - initial_unemployment
        inflation_change = self.player_country.inflation - initial_inflation

        # 评分
        score = 0
        if gdp_growth > 15:
            score += 3
        elif gdp_growth > 10:
            score += 2
        elif gdp_growth > 5:
            score += 1

        if unemployment_change < -2:
            score += 3
        elif unemployment_change < 0:
            score += 2
        elif unemployment_change < 2:
            score += 1

        if abs(inflation_change) < 1:
            score += 3
        elif abs(inflation_change) < 2:
            score += 2
        elif abs(inflation_change) < 3:
            score += 1

        # 显示结果
        result_message = f"你已完成5年的执政期!\n\n"
        result_message += f"GDP 增长率: {gdp_growth:.2f}%\n"
        result_message += f"失业率 变化: {unemployment_change:+.1f}%\n"
        result_message += f"通货膨胀率 变化: {inflation_change:+.1f}%\n\n"
        result_message += f"你的最终得分为: {score}/9\n\n"

        if score >= 8:
            result_message += "优秀! 你的经济政策取得了显著成效，国家繁荣昌盛。"
        elif score >= 6:
            result_message += "良好! 你的政策基本有效，经济保持稳定增长。"
        elif score >= 4:
            result_message += "一般。经济表现平平，还有改进空间。"
        else:
            result_message += "需要改进。你的政策导致了经济问题，下次要做出更明智的选择。"

        self._log_event("游戏结束 - 查看结果")
        messagebox.showinfo("游戏结果", result_message)

    def _show_help(self):
        """显示游戏帮助"""
        help_message = """国家贸易模拟器帮助

游戏目标:
作为国家领导人，你需要通过调整贸易政策来促进国家经济发展。
你的目标是在5年内保持健康的经济增长、低失业率和稳定的通货膨胀。

游戏操作:
1. 调整关税: 在"贸易政策"标签页中，你可以调整对各个贸易伙伴的关税税率。
   提高关税会增加政府收入，但可能导致贸易伙伴的报复和国内通货膨胀。
   降低关税会促进国际贸易，但可能影响国内产业。

2. 观察经济指标: 在"经济概览"标签页中，你可以查看关键经济指标和趋势图表。
   关注GDP、失业率、通货膨胀率和贸易平衡的变化。

3. 管理贸易伙伴: 在"贸易伙伴"标签页中，你可以查看与各国的贸易情况。

4. 进入下一年: 点击"进入下一年"按钮来模拟一年的经济发展。

特殊事件:
游戏中可能会发生各种随机事件，如全球经济繁荣或衰退、技术突破、自然灾害等，
这些事件会影响你的国家经济。

评分标准:
游戏结束后，你将根据GDP增长率、失业率变化和通货膨胀控制情况获得评分。

祝你好运!"""

        messagebox.showinfo("游戏帮助", help_message)


if __name__ == "__main__":
    root = tk.Tk()
    app = TradeSimulationGUI(root)
    root.mainloop()

