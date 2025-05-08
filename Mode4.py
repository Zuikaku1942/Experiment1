import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
import random
import datetime  # 添加这一行
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# 添加以下中文字体配置
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

class BeamControlSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("卫星波束复用控制系统喵")
        self.root.geometry("1200x800")
        
        # 定义常量
        self.BEAM_CONFIGS = {
            "4波束": 4,
            "7波束": 7,
            "12波束": 12
        }
        
        # 波束状态
        self.beams = {}
        self.current_config = "4波束"
        
        # 频率资源
        self.frequencies = {
            "F1": {"freq": "2.4GHz", "color": "red"},
            "F2": {"freq": "5.0GHz", "color": "blue"},
            "F3": {"freq": "8.0GHz", "color": "green"},
            "F4": {"freq": "12GHz", "color": "purple"}
        }
        
        # 创建界面
        self.create_widgets()
        
        # 初始化波束
        self.initialize_beams()
        
    def create_widgets(self):
        """创建GUI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="5")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 波束配置选择
        ttk.Label(control_frame, text="波束配置:").pack(anchor=tk.W, pady=5)
        self.beam_var = tk.StringVar(value="4波束")
        beam_combo = ttk.Combobox(
            control_frame, 
            textvariable=self.beam_var,
            values=list(self.BEAM_CONFIGS.keys()),
            state="readonly"
        )
        beam_combo.pack(fill=tk.X, pady=5)
        beam_combo.bind("<<ComboboxSelected>>", self.on_config_change)
        
        # 功率控制
        power_frame = ttk.LabelFrame(control_frame, text="功率控制", padding="5")
        power_frame.pack(fill=tk.X, pady=5)
        
        self.power_scale = ttk.Scale(
            power_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL
        )
        self.power_scale.set(50)
        self.power_scale.pack(fill=tk.X)
        self.power_scale.bind("<Motion>", self.update_power)
        
        # 干扰监控阈值
        interference_frame = ttk.LabelFrame(control_frame, text="干扰监控", padding="5")
        interference_frame.pack(fill=tk.X, pady=5)
        
        self.interference_threshold = ttk.Scale(
            interference_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL
        )
        self.interference_threshold.set(30)
        self.interference_threshold.pack(fill=tk.X)
        
        # 频率信息显示
        freq_info_frame = ttk.LabelFrame(control_frame, text="频率资源说明", padding="5")
        freq_info_frame.pack(fill=tk.X, pady=5)
        
        # 创建频率颜色说明
        frequencies_info = {
            "F1 (2.4GHz)": "red",
            "F2 (5.0GHz)": "blue",
            "F3 (8.0GHz)": "green",
            "F4 (12GHz)": "purple"
        }
        
        for freq, color in frequencies_info.items():
            freq_frame = tk.Frame(freq_info_frame)
            freq_frame.pack(fill=tk.X, pady=2)
            
            color_box = tk.Canvas(freq_frame, width=15, height=15)
            color_box.create_rectangle(0, 0, 15, 15, fill=color, outline="")
            color_box.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(freq_frame, text=freq).pack(side=tk.LEFT)

        # 添加说明文本
        info_text = ("波束颜色透明度表示功率大小\n"
                    "相邻波束使用不同频率以避免干扰\n"
                    "优化分配按钮可自动调整频率分配")
        ttk.Label(freq_info_frame, text=info_text, justify=tk.LEFT).pack(pady=5)

        # 控制按钮
        ttk.Button(
            control_frame, 
            text="更新配置",
            command=self.update_configuration
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            control_frame,
            text="优化分配",
            command=self.optimize_resources
        ).pack(fill=tk.X, pady=5)
        
        # 在control_frame中添加干扰检查按钮
        ttk.Button(
            control_frame,
            text="干扰检查",
            command=self.check_interference
        ).pack(fill=tk.X, pady=5)
        
        # 右侧显示区域
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 波束分布图
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=display_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 状态监控
        monitor_frame = ttk.LabelFrame(display_frame, text="状态监控", padding="5")
        monitor_frame.pack(fill=tk.X, pady=5)
        
        self.monitor_text = scrolledtext.ScrolledText(
            monitor_frame,
            height=6,
            wrap=tk.WORD
        )
        self.monitor_text.pack(fill=tk.X)
        
    def initialize_beams(self):
        """初始化波束配置"""
        num_beams = self.BEAM_CONFIGS[self.current_config]
        self.beams.clear()
        
        for i in range(num_beams):
            angle = (2 * math.pi * i) / num_beams
            self.beams[i] = {
                "position": (math.cos(angle), math.sin(angle)),
                "power": 50,
                "frequency": random.choice(list(self.frequencies.keys())),
                "active": True
            }
        
        self.draw_beams()
        self.update_monitor(f"初始化{self.current_config}配置完成")
        
    def draw_beams(self):
        """绘制波束分布"""
        self.ax.clear()
        self.ax.set_aspect('equal')
        
        # 绘制覆盖圆
        circle = plt.Circle((0, 0), 1, fill=False, color='gray')
        self.ax.add_artist(circle)
        
        # 绘制波束
        for beam_id, beam in self.beams.items():
            x, y = beam["position"]
            color = self.get_frequency_color(beam["frequency"])
            alpha = beam["power"] / 100
            
            if beam["active"]:
                circle = plt.Circle(
                    (x * 0.7, y * 0.7), 
                    0.3, 
                    color=color, 
                    alpha=alpha
                )
                self.ax.add_artist(circle)
                self.ax.text(
                    x * 0.7, 
                    y * 0.7, 
                    f"B{beam_id}\n{beam['frequency']}", 
                    ha='center', 
                    va='center'
                )
        
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.set_title(f"波束分布 - {self.current_config}")
        self.canvas.draw()
        
    def check_interference(self):
        """检查波束间干扰"""
        threshold = self.interference_threshold.get()
        interference_found = False
        
        for beam_id1, beam1 in self.beams.items():
            for beam_id2, beam2 in self.beams.items():
                if beam_id1 >= beam_id2:
                    continue
                    
                if beam1["frequency"] == beam2["frequency"]:
                    # 计算波束间距离
                    x1, y1 = beam1["position"]
                    x2, y2 = beam2["position"]
                    distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                    
                    # 如果距离小于阈值且使用相同频率，记录干扰
                    if distance < (threshold/50):  # 将阈值归一化
                        interference_found = True
                        self.update_monitor(
                            f"警告: 波束{beam_id1}和波束{beam_id2}存在潜在干扰"
                            f"(频率:{beam1['frequency']}, 距离:{distance:.2f})"
                        )
        
        if not interference_found:
            self.update_monitor("干扰检查完成: 未发现明显干扰")
    def get_frequency_color(self, freq):
        """获取频率对应的颜色"""
        return self.frequencies[freq]["color"]
        
    def update_monitor(self, message):
        """更新监控信息"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.monitor_text.insert(tk.END, f"[{current_time}] {message}\n")
        self.monitor_text.see(tk.END)
        
    def on_config_change(self, event):
        """波束配置改变处理"""
        new_config = self.beam_var.get()
        if new_config != self.current_config:
            self.current_config = new_config
            self.initialize_beams()
            
    def update_power(self, event):
        """更新功率设置"""
        power = self.power_scale.get()
        for beam in self.beams.values():
            beam["power"] = power
        self.draw_beams()
        
    def optimize_resources(self):
        """优化资源分配"""
        # 简单的频率重分配策略
        used_frequencies = set()
        for beam_id, beam in self.beams.items():
            available_frequencies = [f for f in self.frequencies if f not in used_frequencies]
            if not available_frequencies:
                available_frequencies = list(self.frequencies.keys())
            
            new_freq = random.choice(available_frequencies)
            beam["frequency"] = new_freq
            used_frequencies.add(new_freq)
            
        self.draw_beams()
        self.update_monitor("完成资源优化分配")
        
    def update_configuration(self):
        """更新波束配置"""
        self.initialize_beams()
        self.update_monitor(f"{self.current_config}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BeamControlSystem(root)
    root.mainloop()