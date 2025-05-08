import sys
import numpy as np  # 用于数值计算
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,  # Qt界面组件
                             QHBoxLayout, QLabel, QComboBox, QLineEdit, 
                             QPushButton, QGridLayout, QGroupBox, QDoubleSpinBox, 
                             QSpinBox, QSplitter)
from PyQt5.QtCore import Qt, QTimer  # Qt核心功能
import matplotlib.pyplot as plt  # 绘图库
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # Matplotlib的Qt后端
from matplotlib.figure import Figure
from scipy import signal as sg  # 信号处理库

class SignalCanvas(FigureCanvas):
    """信号显示画布类，用于显示波形
    继承自FigureCanvas，提供了波形绘制功能"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """初始化画布
        args:
            parent: 父窗口
            width: 画布宽度（英寸）
            height: 画布高度（英寸）
            dpi: 分辨率
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)  # 添加子图
        super(SignalCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.fig.tight_layout()  # 自动调整布局

    def plot_analog_signal(self, t, signal, title):
        self.axes.clear()
        self.axes.plot(t, signal, 'b-')
        self.axes.set_title(title)
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Amplitude (V)')
        self.axes.grid(True)
        self.fig.tight_layout()
        self.draw()

    def plot_digital_signal(self, t, signal, title, bits):
        self.axes.clear()
        self.axes.step(t, signal, 'r-', where='post')
        self.axes.set_title(title)
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Digital Value (0/1)')
        self.axes.grid(True)
        
        # 设置固定的y轴范围，只显示0和1两个值，因为PWM是二值信号
        self.axes.set_ylim([-0.1, 1.1])
        
        self.fig.tight_layout()
        self.draw()
        
    def plot_reconstructed_signal(self, t, signal, title, original_signal=None):
        self.axes.clear()
        self.axes.plot(t, signal, 'g-')
        if original_signal is not None:
            self.axes.plot(t, original_signal, 'b--', alpha=0.5)
            self.axes.legend(['Reconstructed', 'Original'])
            
        self.axes.set_title(title)
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Amplitude (V)')
        self.axes.grid(True)
        self.fig.tight_layout()
        self.draw()

class ADConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize signal generation and timing variables first
        self.duration = 0.1  # 100ms of signal
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_signal)
        self.is_running = False
        
        # Now initialize the UI
        self.initUI()
        
        # Initial setup after UI is created
        self.on_wave_type_changed()
        
        # Generate initial signal
        self.update_signal()

    def initUI(self):
        # Window title
        self.setWindowTitle('Satellite Communication Simulation - ADC Module')
        self.setGeometry(100, 100, 1600, 700)  # 扩大窗口宽度以容纳三个图表
        
        # Main layout with splitter
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        # Create a horizontal splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left, middle, and right widgets
        left_widget = QWidget()
        middle_widget = QWidget()
        right_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        middle_layout = QVBoxLayout(middle_widget)
        right_layout = QVBoxLayout(right_widget)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(middle_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 500, 500])  # Initial sizes
        
        # Input signal canvas
        self.input_canvas = SignalCanvas(self, width=5, height=4)
        left_layout.addWidget(self.input_canvas)
        
        # Output signal canvas (PWM)
        self.output_canvas = SignalCanvas(self, width=5, height=4)
        middle_layout.addWidget(self.output_canvas)
        
        # Reconstructed signal canvas
        self.reconstructed_canvas = SignalCanvas(self, width=5, height=4)
        right_layout.addWidget(self.reconstructed_canvas)
        
        # Input parameters group
        input_group = QGroupBox("Input Parameters")
        input_params_layout = QGridLayout()
        input_group.setLayout(input_params_layout)
        left_layout.addWidget(input_group)
        
        # Wave type selector
        input_params_layout.addWidget(QLabel("Wave Type:"), 0, 0)
        self.wave_type = QComboBox()
        self.wave_type.addItems(["Sine", "Square", "Triangle"])
        self.wave_type.currentIndexChanged.connect(self.on_wave_type_changed)
        input_params_layout.addWidget(self.wave_type, 0, 1)
        
        # Frequency input
        input_params_layout.addWidget(QLabel("Freq (kHz):"), 1, 0)
        self.frequency = QDoubleSpinBox()
        self.frequency.setRange(0.1, 1000.0)
        self.frequency.setValue(10.0)
        self.frequency.valueChanged.connect(self.update_signal)
        input_params_layout.addWidget(self.frequency, 1, 1)
        
        # Amplitude input
        input_params_layout.addWidget(QLabel("Amp (V):"), 2, 0)
        self.amplitude = QDoubleSpinBox()
        self.amplitude.setRange(0.1, 10.0)  # 将上限从原来的值改为10.0V
        self.amplitude.setValue(5.0)
        self.amplitude.valueChanged.connect(self.update_signal)
        input_params_layout.addWidget(self.amplitude, 2, 1)
        
        # Duty cycle input (only for square wave)
        input_params_layout.addWidget(QLabel("Duty (%):"), 3, 0)
        self.duty_cycle = QDoubleSpinBox()
        self.duty_cycle.setRange(1.0, 99.0)
        self.duty_cycle.setValue(50.0)
        self.duty_cycle.valueChanged.connect(self.update_signal)
        input_params_layout.addWidget(self.duty_cycle, 3, 1)
        
        # AD conversion parameters group
        output_group = QGroupBox("ADC Parameters")
        output_params_layout = QGridLayout()
        output_group.setLayout(output_params_layout)
        middle_layout.addWidget(output_group)
        
        # Bits selector
        output_params_layout.addWidget(QLabel("Bits:"), 0, 0)
        self.bits = QComboBox()
        self.bits.addItems(["8bit", "10bit", "12bit", "16bit"])
        self.bits.setCurrentIndex(0)  # Default to 8 bits
        self.bits.currentIndexChanged.connect(self.update_signal)
        output_params_layout.addWidget(self.bits, 0, 1)
        
        # Sampling rate
        output_params_layout.addWidget(QLabel("Sample Rate (kHz):"), 1, 0)
        self.sample_rate = QDoubleSpinBox()
        self.sample_rate.setRange(0.1, 5000.0)  # 修改上限为5000.0 kHz
        self.sample_rate.setSingleStep(1.0)      # 增加步进值便于调节
        self.sample_rate.setValue(1.0)
        self.sample_rate.valueChanged.connect(self.update_signal)
        output_params_layout.addWidget(self.sample_rate, 1, 1)
        
        # Reference voltage
        output_params_layout.addWidget(QLabel("Ref Voltage (V):"), 2, 0)
        self.ref_voltage = QDoubleSpinBox()
        self.ref_voltage.setRange(1.0, 20.0)
        self.ref_voltage.setValue(5.0)
        self.ref_voltage.valueChanged.connect(self.update_signal)
        output_params_layout.addWidget(self.ref_voltage, 2, 1)
        
        # PWM frequency
        output_params_layout.addWidget(QLabel("PWM Freq (kHz):"), 3, 0)
        self.pwm_frequency = QDoubleSpinBox()
        self.pwm_frequency.setRange(0.05, 5.0)
        self.pwm_frequency.setSingleStep(0.05)
        self.pwm_frequency.setValue(0.5)
        self.pwm_frequency.valueChanged.connect(self.update_signal)
        output_params_layout.addWidget(self.pwm_frequency, 3, 1)
        
        # Monitoring display
        output_params_layout.addWidget(QLabel("Monitor:"), 4, 0)
        self.monitor = QLabel("采样点: 0, 数字值: 0")
        output_params_layout.addWidget(self.monitor, 4, 1)
        
        # DA conversion parameters group
        reconst_group = QGroupBox("DAC Parameters")
        reconst_params_layout = QGridLayout()
        reconst_group.setLayout(reconst_params_layout)
        right_layout.addWidget(reconst_group)
        
        # Low-pass filter cutoff frequency
        reconst_params_layout.addWidget(QLabel("LPF Cutoff (kHz):"), 0, 0)
        self.cutoff_freq = QDoubleSpinBox()
        self.cutoff_freq.setRange(0.1, 100.0)
        self.cutoff_freq.setSingleStep(0.1)  # 将步进值从默认的1.0改为0.1
        self.cutoff_freq.setValue(20.0)
        self.cutoff_freq.valueChanged.connect(self.update_signal)
        reconst_params_layout.addWidget(self.cutoff_freq, 0, 1)
        
        # Filter order
        reconst_params_layout.addWidget(QLabel("Filter Order:"), 1, 0)
        self.filter_order = QSpinBox()
        self.filter_order.setRange(1, 8)
        self.filter_order.setValue(4)
        self.filter_order.valueChanged.connect(self.update_signal)
        reconst_params_layout.addWidget(self.filter_order, 1, 1)
        
        # Filter type
        reconst_params_layout.addWidget(QLabel("Filter Type:"), 2, 0)
        self.filter_type = QComboBox()
        self.filter_type.addItems(["Moving Avg", "Butterworth"])
        self.filter_type.setCurrentIndex(0)
        self.filter_type.currentIndexChanged.connect(self.update_signal)
        reconst_params_layout.addWidget(self.filter_type, 2, 1)
        
        # Show original signal option
        reconst_params_layout.addWidget(QLabel("Show Original:"), 3, 0)
        self.show_original = QComboBox()
        self.show_original.addItems(["Yes", "No"])
        self.show_original.setCurrentIndex(0)
        self.show_original.currentIndexChanged.connect(self.update_signal)
        reconst_params_layout.addWidget(self.show_original, 3, 1)
        
        # Reconstructed signal monitoring
        reconst_params_layout.addWidget(QLabel("Quality:"), 4, 0)
        self.recon_monitor = QLabel("Error: 0V, SNR: 0dB")
        reconst_params_layout.addWidget(self.recon_monitor, 4, 1)
        
        # Control buttons
        control_layout = QHBoxLayout()
        main_layout.addLayout(control_layout)
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.toggle_simulation)
        control_layout.addWidget(self.start_button)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_simulation)
        control_layout.addWidget(self.reset_button)
        
    def on_wave_type_changed(self):
        # Enable/disable duty cycle based on wave type
        wave_type = self.wave_type.currentText()
        self.duty_cycle.setEnabled(wave_type == "Square")
        self.update_signal()
        
    def update_signal(self):
        try:
            # Get parameters
            wave_type = self.wave_type.currentText()
            frequency = self.frequency.value()
            amplitude = self.amplitude.value()
            duty_cycle = self.duty_cycle.value() / 100  # Convert to fraction
            sample_rate = self.sample_rate.value()  # kHz
            bits_text = self.bits.currentText()
            bits = int(bits_text.replace("bit", ""))
            ref_voltage = self.ref_voltage.value()
            pwm_frequency = self.pwm_frequency.value()  # kHz
            cutoff_freq = self.cutoff_freq.value()  # kHz
            filter_order = self.filter_order.value()
            filter_type = self.filter_type.currentText()
            show_original = self.show_original.currentText() == "Yes"
            
            # 生成时间轴，采样率为kHz，需乘1000
            t = np.linspace(0, self.duration, int(self.duration * sample_rate * 1000), endpoint=False)

            # 波形生成公式 frequency 直接用kHz
            if wave_type == "Sine":
                analog_signal = amplitude * np.sin(2 * np.pi * frequency * t)
                signal_title = f"sin wave (Frequency: {frequency}kHz, Amplitude: {amplitude}V)"
                
            elif wave_type == "Square":
                analog_signal = amplitude * (((t * frequency) % 1) < duty_cycle).astype(float)
                analog_signal = analog_signal * 2 - amplitude  # Center around 0
                signal_title = f"square wave (Frequency: {frequency}kHz, Amplitude: {amplitude}V, Duty: {duty_cycle*100}%)"
                
            elif wave_type == "Triangle":
                analog_signal = amplitude * 2 * np.abs(2 * ((t * frequency) % 1) - 1) - amplitude
                signal_title = f"Triangle wave (Frequency: {frequency}kHz, Amplitude: {amplitude}V)"
            
            # Plot analog signal
            self.input_canvas.plot_analog_signal(t, analog_signal, signal_title)
            
            # Perform AD conversion to get digital values (quantized levels)
            digital_values = self.analog_to_digital_values(analog_signal, bits, ref_voltage)
            
            # Convert digital values to PWM signal
            pwm_signal = self.digital_to_pwm(t, digital_values, bits, pwm_frequency)
            
            # Plot PWM signal
            output_title = f"Converted_Wave ({bits}bit量化, PWM频率: {pwm_frequency}kHz)"
            self.output_canvas.plot_digital_signal(t, pwm_signal, output_title, bits)
            
            # Convert PWM signal back to analog
            reconstructed_signal = self.pwm_to_analog(t, pwm_signal, cutoff_freq, filter_order, ref_voltage, filter_type)
            
            # Calculate error metrics
            if len(analog_signal) > 0:
                rmse = np.sqrt(np.mean((analog_signal - reconstructed_signal) ** 2))
                if np.sum(analog_signal ** 2) > 0:
                    snr = 10 * np.log10(np.sum(analog_signal ** 2) / np.sum((analog_signal - reconstructed_signal) ** 2))
                else:
                    snr = 0
                self.recon_monitor.setText(f"Error: {rmse:.3f} V, SNR: {snr:.2f} dB")
            
            # Plot reconstructed signal
            recon_title = f"Reconstructed Wave (滤波器截止: {cutoff_freq}kHz, 类型: {filter_type})"
            original_signal = analog_signal if show_original else None
            self.reconstructed_canvas.plot_reconstructed_signal(t, reconstructed_signal, recon_title, original_signal)
            
            # Update monitoring display
            if len(t) > 0:
                midpoint_idx = len(t) // 2
                digital_value = digital_values[midpoint_idx]
                max_val = 2**bits - 1
                duty_cycle_percentage = (digital_value / max_val) * 100
                self.monitor.setText(f"T: {t[midpoint_idx]:.4f}s, V: {analog_signal[midpoint_idx]:.2f}V, "
                                   f"D: {int(digital_value)}, PWM: {duty_cycle_percentage:.1f}%")
        except Exception as e:
            print(f"错误: {e}")
            # 在遇到错误时仍然保持基本UI功能
    
    def analog_to_digital_values(self, analog_signal, bits, reference_voltage):
        """将模拟信号转换为数字值（量化级别）"""
        # Clip signal to reference voltage range
        clipped_signal = np.clip(analog_signal, -reference_voltage, reference_voltage)
        
        # Calculate max digital value
        max_val = 2**bits - 1
        
        # Normalize to 0 - max_val range
        normalized = ((clipped_signal + reference_voltage) / (2 * reference_voltage)) * max_val
        
        # Round to nearest integer and clip to valid range
        digital_values = np.round(normalized).clip(0, max_val)
        
        return digital_values
    
    def digital_to_pwm(self, t, digital_values, bits, pwm_frequency):
        """将数字值转换为PWM信号"""
        # pwm_frequency 单位为kHz
        max_val = 2**bits - 1
        pwm_period = 1.0 / (pwm_frequency * 1000)  # kHz转Hz
        pwm_signal = np.zeros_like(t)
        for i, time in enumerate(t):
            position_in_period = (time % pwm_period) / pwm_period
            duty_cycle = digital_values[i] / max_val
            if position_in_period < duty_cycle:
                pwm_signal[i] = 1.0
            else:
                pwm_signal[i] = 0.0
        return pwm_signal
    
    def pwm_to_analog(self, t, pwm_signal, cutoff_freq, filter_order, reference_voltage, filter_type):
        """将PWM信号转换回模拟信号，使用低通滤波器模拟DA转换过程"""
        # 计算采样频率
        if len(t) < 2:
            return np.zeros_like(pwm_signal)
            
        fs = 1.0 / (t[1] - t[0])  # 采样频率

        if filter_type == "Moving Avg":
            # 使用移动平均滤波
            window_size = max(1, int((1.0 / (cutoff_freq * 1000)) * fs))
            kernel = np.ones(window_size) / window_size
            filtered = np.convolve(pwm_signal, kernel, mode='same')
        else:
            # 使用巴特沃斯滤波器
            try:
                # 确保归一化截止频率在有效范围内
                nyq = 0.5 * fs  # 奈奎斯特频率
                normal_cutoff = min(0.99, cutoff_freq * 1000 / nyq)  # 归一化截止频率限制在0.99以下
                
                # 设计滤波器
                b, a = sg.butter(filter_order, normal_cutoff, btype='low', analog=False)
                
                # 应用滤波器
                filtered = sg.filtfilt(b, a, pwm_signal)
            except Exception as e:
                print(f"滤波器错误: {e}")
                # 如果巴特沃斯滤波器出错，回退到移动平均
                window_size = max(1, int((1.0 / (cutoff_freq * 1000)) * fs))
                kernel = np.ones(window_size) / window_size
                filtered = np.convolve(pwm_signal, kernel, mode='same')
        
        # 将滤波后的PWM信号映射回模拟电压范围
        reconstructed_signal = (filtered * 2 - 1) * reference_voltage
        
        return reconstructed_signal
    
    def toggle_simulation(self):
        if self.is_running:
            self.timer.stop()
            self.start_button.setText("Start")
            self.is_running = False
        else:
            self.timer.start(50)  # Update every 50ms
            self.start_button.setText("Pause")
            self.is_running = True
    
    def reset_simulation(self):
        # Reset parameters to default
        self.wave_type.setCurrentIndex(0)
        self.frequency.setValue(10.0)
        self.amplitude.setValue(5.0)
        self.duty_cycle.setValue(50.0)
        self.sample_rate.setValue(1.0)
        self.bits.setCurrentIndex(0)
        self.ref_voltage.setValue(5.0)
        self.pwm_frequency.setValue(0.5)
        self.cutoff_freq.setValue(20.0)
        self.filter_order.setValue(4)
        self.filter_type.setCurrentIndex(0)
        
        # Stop simulation if running
        if self.is_running:
            self.toggle_simulation()
        
        # Update signal
        self.update_signal()

def main():
    app = QApplication(sys.argv)
    window = ADConverterApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()