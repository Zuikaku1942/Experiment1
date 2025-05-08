import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import binascii
import datetime
import random
import time

class SatelliteCommSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("卫星移动通信简化版协议 - 增强版")
        self.root.geometry("900x700")
        self.root.configure(bg="#ffffff")  # 背景改为白色
        
        # 定义协议常量
        self.FRAME_HEADER = "6d656f77"  # "meow" 的16进制
        self.FRAME_FOOTER = "6d696b756d61"  # "mikuma" 的16进制
        
        # 定义帧类型
        self.FRAME_TYPES = {
            "实验帧": "01",
            "数据帧": "02",
            "控制帧": "03"
        }
        
        # 定义地址 (两个字节)
        self.ADDRESSES = {
            "卫星控制中心": "A101",
            "移动终端1": "B202",
            "移动终端2": "C303",
            "地面站": "D404"
        }
        
        # 传输历史记录
        self.transmission_history = []
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50")
        self.style.configure("TLabel", background="#ffffff")  # 背景改为白色
        self.style.configure("TFrame", background="#ffffff")  # 背景改为白色
        
        self.create_widgets()
        
    def create_widgets(self):
        # 创建标题框架
        title_frame = tk.Frame(self.root, bg="#66ccff", padx=10, pady=10)  # 标题背景改为浅蓝色
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame, 
            text="卫星移动通信简化版协议仿真系统", 
            font=("Arial", 18, "bold"),
            bg="#66ccff",  # 浅蓝色
            fg="white"
        )
        title_label.pack()
        
        # 创建主框架
        main_frame = tk.Frame(self.root, bg="#ffffff", padx=20, pady=15)  # 背景改为白色
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选项卡
        tab_control = ttk.Notebook(main_frame)
        
        # 创建帧生成器选项卡
        frame_generator_tab = ttk.Frame(tab_control)
        tab_control.add(frame_generator_tab, text="帧生成器")
        
        # 创建帧分析器选项卡
        frame_analyzer_tab = ttk.Frame(tab_control)
        tab_control.add(frame_analyzer_tab, text="帧分析器")
        
        # 创建监控日志选项卡
        monitor_tab = ttk.Frame(tab_control)
        tab_control.add(monitor_tab, text="监控日志")
        
        tab_control.pack(expand=True, fill=tk.BOTH)
        
        # 帧生成器选项卡内容
        self.setup_frame_generator(frame_generator_tab)
        
        # 帧分析器选项卡内容
        self.setup_frame_analyzer(frame_analyzer_tab)
        
        # 监控日志选项卡内容
        self.setup_monitor_tab(monitor_tab)
        
        # 创建状态栏
        status_frame = tk.Frame(self.root, bg="#e0e0e0", padx=10, pady=5)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame, 
            text="就绪 - 系统初始化完成",
            bg="#e0e0e0",
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT)
        
        # 时间标签
        self.time_label = tk.Label(
            status_frame, 
            text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            bg="#e0e0e0",
            anchor=tk.E
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # 更新时间
        self.update_time()
    
    def setup_frame_generator(self, parent):
        # 创建输入框架
        input_frame = ttk.LabelFrame(parent, text="协议参数设置", style="Red.TLabelframe")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 正文输入
        payload_label = ttk.Label(input_frame, text="帧正文:")
        payload_label.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        
        self.payload_entry = ttk.Entry(input_frame, width=50)
        self.payload_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.payload_entry.insert(0, "Hello Satellite")
        
        # 源地址选择
        src_addr_label = ttk.Label(input_frame, text="源地址:")
        src_addr_label.grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        
        self.src_addr_var = tk.StringVar()
        src_addr_combo = ttk.Combobox(input_frame, textvariable=self.src_addr_var, width=20)
        src_addr_combo['values'] = list(self.ADDRESSES.keys())
        src_addr_combo.current(0)
        src_addr_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 目标地址选择
        dest_addr_label = ttk.Label(input_frame, text="目标地址:")
        dest_addr_label.grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        
        self.dest_addr_var = tk.StringVar()
        dest_addr_combo = ttk.Combobox(input_frame, textvariable=self.dest_addr_var, width=20)
        dest_addr_combo['values'] = list(self.ADDRESSES.keys())
        dest_addr_combo.current(1)
        dest_addr_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 帧类型选择
        frame_type_label = ttk.Label(input_frame, text="帧类型:")
        frame_type_label.grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        
        self.frame_type_var = tk.StringVar()
        frame_type_combo = ttk.Combobox(input_frame, textvariable=self.frame_type_var, width=20)
        frame_type_combo['values'] = list(self.FRAME_TYPES.keys())
        frame_type_combo.current(0)
        frame_type_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 高级选项
        advanced_frame = ttk.LabelFrame(parent, text="高级选项", style="Red.TLabelframe")
        advanced_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 自动添加校验和
        self.checksum_var = tk.BooleanVar(value=True)
        checksum_check = ttk.Checkbutton(
            advanced_frame, 
            text="添加校验和", 
            variable=self.checksum_var,
            bg="#ffffff"  # 背景改为白色
        )
        checksum_check.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        
        # 模拟传输延迟
        self.simulate_delay_var = tk.BooleanVar(value=False)
        simulate_delay_check = ttk.Checkbutton(
            advanced_frame, 
            text="模拟传输延迟", 
            variable=self.simulate_delay_var,
            bg="#ffffff"  # 背景改为白色
        )
        simulate_delay_check.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 按钮框架
        button_frame = tk.Frame(parent, bg="#ffffff")  # 背景改为白色
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 生成帧按钮
        generate_button = ttk.Button(
            button_frame, 
            text="生成数据帧", 
            command=self.generate_frame,
            style="TButton"
        )
        generate_button.pack(side=tk.LEFT, padx=5)
        
        # 传输按钮
        transmit_button = ttk.Button(
            button_frame, 
            text="传输", 
            command=self.transmit_frame
        )
        transmit_button.pack(side=tk.LEFT, padx=5)
        
        # 清除按钮
        clear_button = ttk.Button(
            button_frame, 
            text="清除", 
            command=self.clear_generator
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 创建输出框架
        output_frame = ttk.LabelFrame(parent, text="数据帧结构", style="Red.TLabelframe")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 数据帧结构显示
        self.frame_display = scrolledtext.ScrolledText(output_frame, height=5, wrap=tk.WORD)
        self.frame_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 帧解析显示
        frame_analysis_label = ttk.Label(output_frame, text="帧解析:")
        frame_analysis_label.pack(anchor=tk.W)
        
        self.frame_analysis = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD)
        self.frame_analysis.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def setup_frame_analyzer(self, parent):
        # 创建输入框架
        input_frame = ttk.LabelFrame(parent, text="帧解析器", style="Red.TLabelframe")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 帧输入
        frame_label = ttk.Label(input_frame, text="输入16进制帧:")
        frame_label.pack(anchor=tk.W, pady=5)
        
        self.frame_input = scrolledtext.ScrolledText(input_frame, height=4, wrap=tk.WORD)
        self.frame_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(input_frame, bg="#ffffff")  # 背景改为白色
        button_frame.pack(fill=tk.X, pady=10)
        
        # 解析按钮
        analyze_button = ttk.Button(
            button_frame, 
            text="解析帧", 
            command=self.analyze_frame
        )
        analyze_button.pack(side=tk.LEFT, padx=5)
        
        # 清除按钮
        clear_button = ttk.Button(
            button_frame, 
            text="清除", 
            command=self.clear_analyzer
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 创建输出框架
        output_frame = ttk.LabelFrame(parent, text="解析结果", style="Red.TLabelframe")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 解析结果显示
        self.analyzer_result = scrolledtext.ScrolledText(output_frame, height=15, wrap=tk.WORD)
        self.analyzer_result.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def setup_monitor_tab(self, parent):
        # 创建监控日志框架
        monitor_frame = ttk.LabelFrame(parent, text="通信监控日志", style="Red.TLabelframe")
        monitor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 监控日志显示
        self.monitor_log = scrolledtext.ScrolledText(monitor_frame, height=20, wrap=tk.WORD)
        self.monitor_log.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(parent, bg="#ffffff")  # 背景改为白色
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 清除日志按钮
        clear_log_button = ttk.Button(
            button_frame, 
            text="清除日志", 
            command=self.clear_monitor_log
        )
        clear_log_button.pack(side=tk.LEFT, padx=5)
        
        # 导出日志按钮
        export_log_button = ttk.Button(
            button_frame, 
            text="导出日志", 
            command=self.export_log
        )
        export_log_button.pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = SatelliteCommSimulator(root)
    root.mainloop()