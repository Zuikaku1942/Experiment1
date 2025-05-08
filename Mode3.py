import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import binascii
import datetime
import random
import time
import math

class SatelliteCommSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("卫星移动通信简化版协议 - 超级无敌版")
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
        self.style.configure("TLabel", background="#f5f5f5")
        self.style.configure("TFrame", background="#f5f5f5")
        
        self.create_widgets()
        
    def create_widgets(self):
        # 创建标题框架
        title_frame = tk.Frame(self.root, bg="#66ccff", padx=10, pady=10)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame, 
            text="卫星移动通信仿真系统喵wwww", 
            font=("Arial", 18, "bold"),
            bg="#66ccff",
            fg="white"
        )
        title_label.pack()
        
        # 创建主框架
        main_frame = tk.Frame(self.root, bg="#ffffff", padx=20, pady=15)
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
        
        # 创建调制解调选项卡
        modulation_tab = ttk.Frame(tab_control)
        tab_control.add(modulation_tab, text="调制解调")

        tab_control.pack(expand=True, fill=tk.BOTH)
        
        # 帧生成器选项卡内容
        self.setup_frame_generator(frame_generator_tab)
        
        # 帧分析器选项卡内容
        self.setup_frame_analyzer(frame_analyzer_tab)
        
        # 监控日志选项卡内容
        self.setup_monitor_tab(monitor_tab)
        
        # 调制解调选项卡内容
        self.setup_modulation_tab(modulation_tab)
        
        # 创建状态栏
        status_frame = tk.Frame(self.root, bg="#ffffff", padx=10, pady=5)
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
            bg="#ffffff",
            anchor=tk.E
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # 更新时间
        self.update_time()
    
    def setup_frame_generator(self, parent):
        # 创建输入框架
        input_frame = ttk.LabelFrame(parent, text="协议参数设置")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 正文输入
        payload_label = ttk.Label(input_frame, text="帧正文:")
        payload_label.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        
        self.payload_entry = ttk.Entry(input_frame, width=50)
        self.payload_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.payload_entry.insert(0, "wa ta shi wa MIKUMA  desu")
        
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
        advanced_frame = ttk.LabelFrame(parent, text="高级选项")
        advanced_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 自动添加校验和
        self.checksum_var = tk.BooleanVar(value=True)
        checksum_check = ttk.Checkbutton(
            advanced_frame, 
            text="添加校验和", 
            variable=self.checksum_var
        )
        checksum_check.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        
        # 模拟传输延迟
        self.simulate_delay_var = tk.BooleanVar(value=False)
        simulate_delay_check = ttk.Checkbutton(
            advanced_frame, 
            text="模拟传输延迟", 
            variable=self.simulate_delay_var
        )
        simulate_delay_check.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 按钮框架
        button_frame = tk.Frame(parent, bg="#f5f5f5")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 生成帧按钮
        generate_button = ttk.Button(
            button_frame, 
            text="生成数据帧喵", 
            command=self.generate_frame,
            style="TButton"
        )
        generate_button.pack(side=tk.LEFT, padx=5)
        
        # 传输按钮
        transmit_button = ttk.Button(
            button_frame, 
            text="传输喵", 
            command=self.transmit_frame
        )
        transmit_button.pack(side=tk.LEFT, padx=5)
        
        # 清除按钮
        clear_button = ttk.Button(
            button_frame, 
            text="清除喵", 
            command=self.clear_generator
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 创建输出框架
        output_frame = ttk.LabelFrame(parent, text="数据帧结构")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 数据帧结构显示
        self.frame_display = scrolledtext.ScrolledText(output_frame, height=5, wrap=tk.WORD)
        self.frame_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 帧解析显示
        frame_analysis_label = ttk.Label(output_frame, text="帧解析喵:")
        frame_analysis_label.pack(anchor=tk.W)
        
        self.frame_analysis = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD)
        self.frame_analysis.pack(fill=tk.BOTH, expand=True, pady=5)
        
    def setup_frame_analyzer(self, parent):
        # 创建输入框架
        input_frame = ttk.LabelFrame(parent, text="帧解析器喵")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 帧输入
        frame_label = ttk.Label(input_frame, text="输入16进制帧喵:")
        frame_label.pack(anchor=tk.W, pady=5)
        
        self.frame_input = scrolledtext.ScrolledText(input_frame, height=4, wrap=tk.WORD)
        self.frame_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(input_frame, bg="#f5f5f5")
        button_frame.pack(fill=tk.X, pady=10)
        
        # 解析按钮
        analyze_button = ttk.Button(
            button_frame, 
            text="解析帧喵", 
            command=self.analyze_frame
        )
        analyze_button.pack(side=tk.LEFT, padx=5)
        
        # 清除按钮
        clear_button = ttk.Button(
            button_frame, 
            text="清除喵喵喵", 
            command=self.clear_analyzer
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 创建输出框架
        output_frame = ttk.LabelFrame(parent, text="解析结果喵")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 解析结果显示
        self.analyzer_result = scrolledtext.ScrolledText(output_frame, height=15, wrap=tk.WORD)
        self.analyzer_result.pack(fill=tk.BOTH, expand=True, pady=5)
        
    def setup_monitor_tab(self, parent):
        # 创建监控日志框架
        monitor_frame = ttk.LabelFrame(parent, text="通信监控日志喵")
        monitor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 监控日志显示
        self.monitor_log = scrolledtext.ScrolledText(monitor_frame, height=20, wrap=tk.WORD)
        self.monitor_log.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(parent, bg="#ffffff")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 清除日志按钮
        clear_log_button = ttk.Button(
            button_frame, 
            text="清除日志喵呜", 
            command=self.clear_monitor_log
        )
        clear_log_button.pack(side=tk.LEFT, padx=5)
        
        # 导出日志按钮
        export_log_button = ttk.Button(
            button_frame, 
            text="导出日志呜", 
            command=self.export_log
        )
        export_log_button.pack(side=tk.LEFT, padx=5)
    
    def setup_modulation_tab(self, parent):
        """设置调制解调选项卡"""
        # 创建左侧调制部分框架
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 创建右侧解调部分框架 
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 调制部分
        modulation_frame = ttk.LabelFrame(left_frame, text="BPSK调制喵")
        modulation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # [原有调制部分代码保持不变]
        hex_label = ttk.Label(modulation_frame, text="16进制输入喵:")
        hex_label.pack(anchor=tk.W, pady=5)
        
        self.hex_input = scrolledtext.ScrolledText(modulation_frame, height=3, wrap=tk.WORD)
        self.hex_input.pack(fill=tk.X, pady=5)
        
        bin_label = ttk.Label(modulation_frame, text="二进制序列喵:")
        bin_label.pack(anchor=tk.W, pady=5)
        
        self.bin_display = scrolledtext.ScrolledText(modulation_frame, height=3, wrap=tk.WORD)
        self.bin_display.pack(fill=tk.X, pady=5)
        
        mod_button_frame = tk.Frame(modulation_frame, bg="#f5f5f5")
        mod_button_frame.pack(fill=tk.X, pady=10)
        
        modulate_button = ttk.Button(
            mod_button_frame,
            text="BPSK调制喵",
            command=self.perform_modulation
        )
        modulate_button.pack(side=tk.LEFT, padx=5)
        
        clear_mod_button = ttk.Button(
            mod_button_frame,
            text="清除喵",
            command=self.clear_modulation
        )
        clear_mod_button.pack(side=tk.LEFT, padx=5)
        
        # 解调部分
        demodulation_frame = ttk.LabelFrame(right_frame, text="BPSK解调喵")
        demodulation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        bin_input_label = ttk.Label(demodulation_frame, text="二进制输入喵:")
        bin_input_label.pack(anchor=tk.W, pady=5)
        
        self.bin_input = scrolledtext.ScrolledText(demodulation_frame, height=3, wrap=tk.WORD)
        self.bin_input.pack(fill=tk.X, pady=5)
        
        hex_output_label = ttk.Label(demodulation_frame, text="16进制输出喵:")
        hex_output_label.pack(anchor=tk.W, pady=5)
        
        self.hex_output = scrolledtext.ScrolledText(demodulation_frame, height=3, wrap=tk.WORD)
        self.hex_output.pack(fill=tk.X, pady=5)
        
        demod_button_frame = tk.Frame(demodulation_frame, bg="#f5f5f5")
        demod_button_frame.pack(fill=tk.X, pady=10)
        
        demodulate_button = ttk.Button(
            demod_button_frame,
            text="BPSK解调喵",
            command=self.perform_demodulation
        )
        demodulate_button.pack(side=tk.LEFT, padx=5)
        
        clear_demod_button = ttk.Button(
            demod_button_frame,
            text="清除喵",
            command=self.clear_demodulation
        )
        clear_demod_button.pack(side=tk.LEFT, padx=5)
        
        # 波形显示区域
        wave_frame = ttk.LabelFrame(parent, text="调制/解调波形")
        wave_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.wave_canvas = tk.Canvas(wave_frame, bg="white", height=200)
        self.wave_canvas.pack(fill=tk.BOTH, expand=True, pady=5)

    def string_to_hex(self, text):
        """将字符串转换为16进制表示"""
        if not text:
            return ""
        hex_data = binascii.hexlify(text.encode()).decode()
        return hex_data
    
    def hex_to_string(self, hex_text):
        """将16进制转换回字符串"""
        try:
            bytes_data = binascii.unhexlify(hex_text)
            return bytes_data.decode()
        except:
            return f"[无法解码的16进制: {hex_text}]"
    
    def calculate_checksum(self, data):
        """计算简单的校验和"""
        # 将16进制字符串转换为字节
        try:
            bytes_data = binascii.unhexlify(data)
            # 计算简单的校验和 (所有字节的和模256)
            checksum = sum(bytes_data) % 256
            return f"{checksum:02x}"
        except:
            return "00"
    
    def generate_frame(self):
        """生成完整的数据帧"""
        # 获取输入内容
        payload = self.payload_entry.get()
        src_addr_key = self.src_addr_var.get()
        dest_addr_key = self.dest_addr_var.get()
        frame_type_key = self.frame_type_var.get()
        
        # 输入验证
        if not payload:
            messagebox.showwarning("输入错误", "请输入帧正文")
            return
        
        # 转换成16进制
        src_addr = self.ADDRESSES[src_addr_key]
        dest_addr = self.ADDRESSES[dest_addr_key]
        frame_type = self.FRAME_TYPES[frame_type_key]
        payload_hex = self.string_to_hex(payload)
        
        # 构建帧内容
        frame_content = f"{src_addr}{dest_addr}{frame_type}{payload_hex}"
        
        # 添加校验和
        checksum = ""
        if self.checksum_var.get():
            checksum = self.calculate_checksum(frame_content)
            frame_content = f"{frame_content}{checksum}"
        
        # 构建完整帧
        complete_frame = f"{self.FRAME_HEADER}{frame_content}{self.FRAME_FOOTER}"
        
        # 显示完整帧
        self.frame_display.delete(1.0, tk.END)
        self.frame_display.insert(tk.END, complete_frame)
        
        # 显示帧解析
        self.frame_analysis.delete(1.0, tk.END)
        frame_analysis_text = (
            f"帧头 (meow): {self.FRAME_HEADER}\n"
            f"源地址 ({src_addr_key}): {src_addr}\n"
            f"目标地址 ({dest_addr_key}): {dest_addr}\n"
            f"类型 ({frame_type_key}): {frame_type}\n"
            f"正文: {payload_hex} (原文: {payload})\n"
        )
        
        if self.checksum_var.get():
            frame_analysis_text += f"校验和: {checksum}\n"
            
        frame_analysis_text += (
            f"帧尾 (mikuma): {self.FRAME_FOOTER}\n\n"
            f"总长度: {len(complete_frame)//2} 字节"
        )
        
        self.frame_analysis.insert(tk.END, frame_analysis_text)
        
        # 更新状态栏
        self.status_label.config(text="帧生成成功")
        
        return complete_frame
    
    def transmit_frame(self):
        """模拟传输帧"""
        # 先生成帧
        frame = self.generate_frame()
        if not frame:
            return
        
        # 更新状态栏
        self.status_label.config(text="正在传输...")
        
        # 模拟传输延迟
        if self.simulate_delay_var.get():
            self.root.update()
            time.sleep(random.uniform(0.5, 1.5))
        
        # 获取源和目标地址
        src_addr_key = self.src_addr_var.get()
        dest_addr_key = self.dest_addr_var.get()
        frame_type_key = self.frame_type_var.get()
        
        # 生成时间戳
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # 添加到监控日志
        log_entry = (
            f"[{timestamp}] 传输帧:\n"
            f"  类型: {frame_type_key}\n"
            f"  源: {src_addr_key}\n"
            f"  目标: {dest_addr_key}\n"
            f"  大小: {len(frame)//2} 字节\n"
            f"  帧: {frame[:20]}...{frame[-20:]}\n\n"
        )
        
        self.monitor_log.insert(tk.END, log_entry)
        self.monitor_log.see(tk.END)
        
        # 添加到传输历史
        self.transmission_history.append({
            'timestamp': timestamp,
            'src': src_addr_key,
            'dest': dest_addr_key,
            'type': frame_type_key,
            'frame': frame
        })
        
        # 更新状态栏
        self.status_label.config(text=f"帧已成功传输至 {dest_addr_key}")
        
        # 模拟接收确认
        if not self.simulate_delay_var.get():
            self.root.update()
            time.sleep(0.5)
        
        confirm_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        confirm_log = (
            f"[{confirm_timestamp}] 接收确认:\n"
            f"  源: {dest_addr_key}\n"
            f"  目标: {src_addr_key}\n"
            f"  状态: 成功\n\n"
        )
        
        self.monitor_log.insert(tk.END, confirm_log)
        self.monitor_log.see(tk.END)
    
    def analyze_frame(self):
        """解析输入的帧"""
        # 获取输入帧
        frame = self.frame_input.get(1.0, tk.END).strip()
        
        # 输入验证
        if not frame:
            messagebox.showwarning("输入错误", "请输入要解析的帧")
            return
        
        # 清除结果
        self.analyzer_result.delete(1.0, tk.END)
        
        # 验证帧格式
        if not frame.startswith(self.FRAME_HEADER) or not frame.endswith(self.FRAME_FOOTER):
            self.analyzer_result.insert(tk.END, "错误: 无效的帧格式，缺少正确的帧头或帧尾\n")
            return
        
        # 移除帧头和帧尾
        content = frame[len(self.FRAME_HEADER):-len(self.FRAME_FOOTER)]
        
        # 提取地址和类型
        if len(content) < 12:
            self.analyzer_result.insert(tk.END, "错误: 帧内容过短，无法解析\n")
            return
        
        src_addr = content[:4]
        dest_addr = content[4:8]
        frame_type = content[8:10]
        
        # 判断是否有校验和 (简单假设最后2个字符是校验和)
        has_checksum = len(content) > 10
        
        # 提取有效载荷和校验和
        if has_checksum:
            payload_hex = content[10:-2]
            checksum = content[-2:]
        else:
            payload_hex = content[10:]
            checksum = None
        
        # 查找地址和类型的名称
        src_addr_name = "未知"
        dest_addr_name = "未知"
        frame_type_name = "未知"
        
        for name, addr in self.ADDRESSES.items():
            if addr == src_addr:
                src_addr_name = name
            if addr == dest_addr:
                dest_addr_name = name
        
        for name, type_code in self.FRAME_TYPES.items():
            if type_code == frame_type:
                frame_type_name = name
        
        # 尝试解码有效载荷
        try:
            payload = self.hex_to_string(payload_hex)
        except:
            payload = "[无法解码]"
        
        # 生成解析结果
        result = (
            f"帧解析结果:\n\n"
            f"帧头: {self.FRAME_HEADER} (meow)\n"
            f"源地址: {src_addr} ({src_addr_name})\n"
            f"目标地址: {dest_addr} ({dest_addr_name})\n"
            f"帧类型: {frame_type} ({frame_type_name})\n"
            f"有效载荷 (16进制): {payload_hex}\n"
            f"有效载荷 (解码): {payload}\n"
        )
        
        if checksum:
            # 验证校验和
            calc_checksum = self.calculate_checksum(content[:-2])
            checksum_valid = calc_checksum == checksum
            
            result += (
                f"校验和: {checksum}"
                f" ({'有效' if checksum_valid else '无效 - 应为 '+calc_checksum})\n"
            )
        
        result += (
            f"帧尾: {self.FRAME_FOOTER} (mikuma)\n\n"
            f"总帧长度: {len(frame)//2} 字节"
        )
        
        self.analyzer_result.insert(tk.END, result)
    
    def clear_generator(self):
        """清除生成器选项卡"""
        self.payload_entry.delete(0, tk.END)
        self.frame_display.delete(1.0, tk.END)
        self.frame_analysis.delete(1.0, tk.END)
        self.status_label.config(text="就绪")
    
    def clear_analyzer(self):
        """清除分析器选项卡"""
        self.frame_input.delete(1.0, tk.END)
        self.analyzer_result.delete(1.0, tk.END)
    
    def clear_monitor_log(self):
        """清除监控日志"""
        self.monitor_log.delete(1.0, tk.END)
        self.transmission_history = []
    
    def export_log(self):
        """导出监控日志"""
        log_content = self.monitor_log.get(1.0, tk.END)
        if not log_content.strip():
            messagebox.showinfo("提示", "日志为空，无需导出")
            return
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"satellite_comm_log_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write("卫星移动通信协议仿真系统日志\n")
                f.write(f"导出时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                f.write(log_content)
            
            messagebox.showinfo("成功", f"日志已成功导出到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"导出日志失败: {str(e)}")
    
    def update_time(self):
        """更新状态栏时间"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def hex_to_binary(self, hex_string):
        """将16进制字符串转换为二进制字符串"""
        try:
            # 移除空格和换行符
            hex_string = hex_string.strip()
            # 将16进制转换为整数，然后转换为二进制字符串
            binary = bin(int(hex_string, 16))[2:]  # 移除'0b'前缀
            # 确保二进制字符串长度为8的倍数
            padding = len(binary) % 8
            if padding:
                binary = '0' * (8 - padding) + binary
            return binary
        except ValueError:
            return None

    def draw_bpsk_waveform(self, binary_data):
        """在画布上绘制BPSK调制波形"""
        self.wave_canvas.delete("all")  # 清除画布
        
        # 设置绘图参数
        width = self.wave_canvas.winfo_width()
        height = self.wave_canvas.winfo_height()
        mid_y = height / 2
        amplitude = height / 3
        samples_per_bit = 20
        
        # 绘制中心线
        self.wave_canvas.create_line(0, mid_y, width, mid_y, fill="gray", dash=(2, 4))
        
        # 绘制BPSK波形
        x = 0
        for bit in binary_data:
            phase = 0 if bit == '1' else 180  # 0度相位表示1，180度相位表示0
            for i in range(samples_per_bit):
                x1 = x + i * (width / (len(binary_data) * samples_per_bit))
                x2 = x + (i + 1) * (width / (len(binary_data) * samples_per_bit))
                
                # 计算正弦波的两个点
                y1 = mid_y + amplitude * \
                     math.sin(2 * math.pi * (i/samples_per_bit) + math.radians(phase))
                y2 = mid_y + amplitude * \
                     math.sin(2 * math.pi * ((i+1)/samples_per_bit) + math.radians(phase))
                
                self.wave_canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
            x += width / len(binary_data)

    def perform_modulation(self):
        """执行BPSK调制"""
        hex_input = self.hex_input.get(1.0, tk.END).strip()
        if not hex_input:
            messagebox.showwarning("输入错误", "请输入16进制数据")
            return
        
        binary = self.hex_to_binary(hex_input)
        if binary is None:
            messagebox.showerror("错误", "无效的16进制输入")
            return
        
        # 显示二进制序列
        self.bin_display.delete(1.0, tk.END)
        self.bin_display.insert(tk.END, binary)
        
        # 绘制BPSK波形
        self.draw_bpsk_waveform(binary)
        
        # 更新状态栏
        self.status_label.config(text=f"BPSK调制完成 - 数据长度: {len(binary)}比特")

    def clear_modulation(self):
        """清除调制部分的所有内容"""
        self.hex_input.delete(1.0, tk.END)
        self.bin_display.delete(1.0, tk.END)
        self.wave_canvas.delete("all")
        self.status_label.config(text="就绪")

    def binary_to_hex(self, binary_string):
        """将二进制字符串转换为16进制字符串"""
        try:
            # 确保二进制字符串长度是4的倍数
            padding = len(binary_string) % 4
            if padding:
                binary_string = '0' * (4 - padding) + binary_string
                
            # 每4位二进制转换为1位16进制
            hex_string = hex(int(binary_string, 2))[2:]
            
            # 确保输出是偶数长度
            if len(hex_string) % 2:
                hex_string = '0' + hex_string
                
            return hex_string.upper()
        except ValueError:
            return None

    def perform_demodulation(self):
        """执行BPSK解调"""
        binary_input = self.bin_input.get(1.0, tk.END).strip()
        if not binary_input:
            messagebox.showwarning("输入错误", "请输入二进制数据")
            return
        
        # 验证输入是否为有效的二进制串
        if not all(bit in '01' for bit in binary_input):
            messagebox.showerror("错误", "输入必须只包含0和1")
            return
        
        # 转换为16进制
        hex_result = self.binary_to_hex(binary_input)
        if hex_result is None:
            messagebox.showerror("错误", "二进制转换失败")
            return
        
        # 显示16进制结果
        self.hex_output.delete(1.0, tk.END)
        self.hex_output.insert(tk.END, hex_result)
        
        # 绘制波形 (使用相同的波形绘制函数)
        self.draw_bpsk_waveform(binary_input)
        
        # 更新状态栏
        self.status_label.config(text=f"BPSK解调完成 - 数据长度: {len(binary_input)}比特")

    def clear_demodulation(self):
        """清除解调部分的所有内容"""
        self.bin_input.delete(1.0, tk.END)
        self.hex_output.delete(1.0, tk.END)
        self.wave_canvas.delete("all")
        self.status_label.config(text="就绪")

if __name__ == "__main__":
    root = tk.Tk()
    app = SatelliteCommSimulator(root)
    root.mainloop()