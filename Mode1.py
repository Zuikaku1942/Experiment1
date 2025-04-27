import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QComboBox, QLineEdit, 
                            QPushButton, QGridLayout, QGroupBox, QDoubleSpinBox, 
                            QSpinBox)
from PyQt5.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.signal import lfilter
#正文
class SignalCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(SignalCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.fig.tight_layout()

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
        self.axes.set_ylim([-0.1, 1.1])
        self.fig.tight_layout()
        self.draw()

class ADConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.duration = 0.1  # 100ms of signal
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_signal)
        self.is_running = False
        
        self.initUI()
        
        self.on_wave_type_changed()
        self.update_signal()

    def initUI(self):
        self.setWindowTitle('卫星通信仿真系统 - AD转换模块')
        self.setGeometry(100, 100, 1800, 700)  # Increased width for three canvases
        
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        # Create a horizontal layout for three canvases
        canvas_layout = QHBoxLayout()
        main_layout.addLayout(canvas_layout)
        
        # Left: Input signal canvas
        self.input_canvas = SignalCanvas(self, width=5, height=4)
        canvas_layout.addWidget(self.input_canvas)
        
        # Middle: PWM output canvas
        self.output_canvas = SignalCanvas(self, width=5, height=4)
        canvas_layout.addWidget(self.output_canvas)
        
        # Right: Reconstructed analog canvas
        self.reconstructed_canvas = SignalCanvas(self, width=5, height=4)
        canvas_layout.addWidget(self.reconstructed_canvas)
        
        # Parameters layout
        params_layout = QHBoxLayout()
        main_layout.addLayout(params_layout)
        
        # Input parameters group
        input_group = QGroupBox("输入波形参数")
        input_params_layout = QGridLayout()
        input_group.setLayout(input_params_layout)
        params_layout.addWidget(input_group)
        
        input_params_layout.addWidget(QLabel("波形类型:"), 0, 0)
        self.wave_type = QComboBox()
        self.wave_type.addItems(["正弦波", "方波", "三角波"])
        self.wave_type.currentIndexChanged.connect(self.on_wave_type_changed)
        input_params_layout.addWidget(self.wave_type, 0, 1)
        
        input_params_layout.addWidget(QLabel("频率 (kHz):"), 1, 0)
        self.frequency = QDoubleSpinBox()
        self.frequency.setRange(0.1, 1000.0)
        self.frequency.setValue(10.0)
        self.frequency.valueChanged.connect(self.update_signal)
        input_params_layout.addWidget(self.frequency, 1, 1)
        
        input_params_layout.addWidget(QLabel("幅值 (V):"), 2, 0)
        self.amplitude = QDoubleSpinBox()
        self.amplitude.setRange(0.1, 10.0)
        self.amplitude.setValue(5.0)
        self.amplitude.valueChanged.connect(self.update_signal)
        input_params_layout.addWidget(self.amplitude, 2, 1)
        
        input_params_layout.addWidget(QLabel("占空比 (%):"), 3, 0)
        self.duty_cycle = QDoubleSpinBox()
        self.duty_cycle.setRange(1.0, 99.0)
        self.duty_cycle.setValue(50.0)
        self.duty_cycle.valueChanged.connect(self.update_signal)
        input_params_layout.addWidget(self.duty_cycle, 3, 1)
        
        # Output parameters group
        output_group = QGroupBox("AD转换参数")
        output_params_layout = QGridLayout()
        output_group.setLayout(output_params_layout)
        params_layout.addWidget(output_group)
        
        output_params_layout.addWidget(QLabel("量化位数:"), 0, 0)
        self.bits = QComboBox()
        self.bits.addItems(["8位", "10位", "12位", "16位"])
        self.bits.setCurrentIndex(0)
        self.bits.currentIndexChanged.connect(self.update_signal)
        output_params_layout.addWidget(self.bits, 0, 1)
        
        # Sampling rate
        output_params_layout.addWidget(QLabel("采样率 (Hz):"), 1, 0)
        self.sample_rate = QSpinBox()
        self.sample_rate.setRange(100, 10000)
        self.sample_rate.setValue(1000)
        self.sample_rate.valueChanged.connect(self.update_signal)
        output_params_layout.addWidget(self.sample_rate, 1, 1)
        
        output_params_layout.addWidget(QLabel("参考电压 (V):"), 2, 0)
        self.ref_voltage = QDoubleSpinBox()
        self.ref_voltage.setRange(1.0, 20.0)
        self.ref_voltage.setValue(5.0)
        self.ref_voltage.valueChanged.connect(self.update_signal)
        output_params_layout.addWidget(self.ref_voltage, 2, 1)
        
        # PWM frequency (new parameter)
        output_params_layout.addWidget(QLabel("PWM频率 (Hz):"), 3, 0)
        self.pwm_frequency = QSpinBox()
        self.pwm_frequency.setRange(50, 5000)
        self.pwm_frequency.setValue(500)
        self.pwm_frequency.valueChanged.connect(self.update_signal)
        output_params_layout.addWidget(self.pwm_frequency, 3, 1)
        
        output_params_layout.addWidget(QLabel("监测点:"), 4, 0)
        self.monitor = QLabel("采样点: 0, 数字值: 0")
        output_params_layout.addWidget(self.monitor, 4, 1)
        
        # Control buttons
        control_layout = QHBoxLayout()
        main_layout.addLayout(control_layout)
        
        self.start_button = QPushButton("开始模拟")
        self.start_button.clicked.connect(self.toggle_simulation)
        control_layout.addWidget(self.start_button)
        
        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.reset_simulation)
        control_layout.addWidget(self.reset_button)
        
    def on_wave_type_changed(self):
        wave_type = self.wave_type.currentText()
        self.duty_cycle.setEnabled(wave_type == "方波")
        self.update_signal()
        
    def reconstruct_analog_signal(self, pwm_signal, sample_rate, ref_voltage):
        """Reconstruct analog signal from PWM using a moving average filter"""
        # Number of samples for moving average (simulate low-pass filter)
        window_size = int(sample_rate / self.pwm_frequency.value() / 2)
        if window_size < 1:
            window_size = 1
        
        # Apply moving average filter
        filter_coeffs = np.ones(window_size) / window_size
        reconstructed = lfilter(filter_coeffs, 1, pwm_signal)
        
        # Scale to reference voltage range (-Vref to +Vref)
        reconstructed = reconstructed * 2 * ref_voltage - ref_voltage
        
        return reconstructed

    def update_signal(self):
        wave_type = self.wave_type.currentText()
        frequency = self.frequency.value()
        amplitude = self.amplitude.value()
        duty_cycle = self.duty_cycle.value() / 100  # Convert to fraction
        sample_rate = self.sample_rate.value()
        bits_text = self.bits.currentText()
        bits = int(bits_text.replace("位", ""))
        ref_voltage = self.ref_voltage.value()
        pwm_frequency = self.pwm_frequency.value()  # kHz
        
        # Generate time array
        t = np.linspace(0, self.duration, int(self.duration * sample_rate), endpoint=False)
        
        # Generate analog signal based on selected wave type
        if wave_type == "正弦波":
            analog_signal = amplitude * np.sin(2 * np.pi * frequency * t)
            signal_title = f"sin wave (Frequency: {frequency}KHz, Amplitude: {amplitude}V)"
            
        elif wave_type == "方波":
            analog_signal = amplitude * (((t * frequency) % 1) < duty_cycle).astype(float)
            analog_signal = analog_signal * 2 - amplitude  # Center around 0
            signal_title = f"square wave (Frequency: {frequency}KHz, Amplitude: {amplitude}V, Duty: {duty_cycle*100}%)"
            
        elif wave_type == "三角波":
            analog_signal = amplitude * 2 * np.abs(2 * ((t * frequency) % 1) - 1) - amplitude
            signal_title = f"Triangle wave (Frequency: {frequency}KHz, Amplitude: {amplitude}V)"
        
        self.input_canvas.plot_analog_signal(t, analog_signal, signal_title)
        
        digital_values = self.analog_to_digital_values(analog_signal, bits, ref_voltage)
        pwm_signal = self.digital_to_pwm(t, digital_values, bits, pwm_frequency)
        
        # Plot PWM signal
        output_title = f"Converted_Wave ({bits}位量化, PWM频率: {pwm_frequency}Hz)"
        self.output_canvas.plot_digital_signal(t, pwm_signal, output_title, bits)
        
        # Reconstruct analog signal from PWM
        reconstructed_signal = self.reconstruct_analog_signal(pwm_signal, sample_rate, ref_voltage)
        reconstructed_title = f"Reconstructed Analog Signal (PWM频率: {pwm_frequency}Hz)"
        self.reconstructed_canvas.plot_analog_signal(t, reconstructed_signal, reconstructed_title)
        
        if len(t) > 0:
            midpoint_idx = len(t) // 2
            digital_value = digital_values[midpoint_idx]
            max_val = 2**bits - 1
            duty_cycle_percentage = (digital_value / max_val) * 100
            self.monitor.setText(f"采样点: {t[midpoint_idx]:.4f}s, 模拟值: {analog_signal[midpoint_idx]:.2f}V, "
                                f"数字值: {int(digital_value)}, PWM占空比: {duty_cycle_percentage:.1f}%")
    
    def analog_to_digital_values(self, analog_signal, bits, reference_voltage):
        clipped_signal = np.clip(analog_signal, -reference_voltage, reference_voltage)
        max_val = 2**bits - 1
        normalized = ((clipped_signal + reference_voltage) / (2 * reference_voltage)) * max_val
        digital_values = np.round(normalized).clip(0, max_val)
        return digital_values
    
    def digital_to_pwm(self, t, digital_values, bits, pwm_frequency):
        """将数字值转换为PWM信号"""
        # Calculate the max digital value
        max_val = 2**bits - 1
        
        # Calculate PWM period in seconds
        pwm_period = 1.0 / pwm_frequency
        
        # Initialize PWM signal with zeros
        pwm_signal = np.zeros_like(t)
        for i, time in enumerate(t):
            position_in_period = (time % pwm_period) / pwm_period
            duty_cycle = digital_values[i] / max_val
            if position_in_period < duty_cycle:
                pwm_signal[i] = 1.0
            else:
                pwm_signal[i] = 0.0
        return pwm_signal
    
    def toggle_simulation(self):
        if self.is_running:
            self.timer.stop()
            self.start_button.setText("开始模拟")
            self.is_running = False
        else:
            self.timer.start(50)
            self.start_button.setText("暂停模拟")
            self.is_running = True
    
    def reset_simulation(self):
        self.wave_type.setCurrentIndex(0)
        self.frequency.setValue(10.0)
        self.amplitude.setValue(5.0)
        self.duty_cycle.setValue(50.0)
        self.sample_rate.setValue(1000)
        self.bits.setCurrentIndex(0)
        self.ref_voltage.setValue(5.0)
        self.pwm_frequency.setValue(500)
        if self.is_running:
            self.toggle_simulation()
        self.update_signal()

def main():
    app = QApplication(sys.argv)
    window = ADConverterApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()