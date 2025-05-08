import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QGridLayout, QGroupBox, QDoubleSpinBox, QSpinBox, QSplitter)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy import signal as sg


class SignalCanvas(FigureCanvas):
    """信号显示画布类，用于显示波形"""
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

    def plot_digital_signal(self, t, signal, title):
        self.axes.clear()
        self.axes.step(t, signal, 'r-', where='post')
        self.axes.set_title(title)
        self.axes.set_xlabel('Time (s)')
        self.axes.set_ylabel('Digital Value (0/1)')
        self.axes.grid(True)
        self.axes.set_ylim([-0.1, 1.1])
        self.fig.tight_layout()
        self.draw()

    def plot_encoded_signal(self, data, title):
        self.axes.clear()
        self.axes.plot(data, 'g-o')
        self.axes.set_title(title)
        self.axes.set_xlabel('Bit Position')
        self.axes.set_ylabel('Bit Value')
        self.axes.grid(True)
        self.axes.set_ylim([-0.1, 1.1])
        self.fig.tight_layout()
        self.draw()


class TurboEncoder:
    """Turbo编码器实现"""
    def __init__(self):
        pass

    def interleave(self, bits):
        length = len(bits)
        result = [0] * length
        for i in range(length):
            new_pos = (3 * i + 7) % length
            result[new_pos] = bits[i]
        return result

    def rsc_encode(self, bits, initial_state=0):
        output = []
        state = initial_state
        for bit in bits:
            parity_bit = (bit + ((state >> 1) & 1) + (state & 1)) % 2
            state = ((state << 1) | bit) & 0x3
            output.append(parity_bit)
        return output

    def encode(self, input_bits):
        systematic_bits = input_bits.copy()
        parity1 = self.rsc_encode(input_bits)
        interleaved_bits = self.interleave(input_bits)
        parity2 = self.rsc_encode(interleaved_bits)
        return {
            'encoded': systematic_bits + parity1 + parity2,
            'components': {
                'systematic': systematic_bits,
                'parity1': parity1,
                'parity2': parity2
            }
        }


class IntegratedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.duration = 0.1
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_signal)
        self.is_running = False
        self.encoder = TurboEncoder()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Integrated AD/DA and Turbo Encoder System')
        self.setGeometry(100, 100, 1500, 800)

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # 左侧面板 - 信号生成和AD转换
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # 输入信号显示
        self.input_canvas = SignalCanvas(self, width=5, height=3)
        left_layout.addWidget(self.input_canvas)

        # PWM信号显示
        self.pwm_canvas = SignalCanvas(self, width=5, height=3)
        left_layout.addWidget(self.pwm_canvas)

        # 参数控制组
        params_group = QGroupBox("Signal Parameters")
        params_layout = QGridLayout()
        params_group.setLayout(params_layout)

        # 波形类型选择（固定频率10kHz）
        params_layout.addWidget(QLabel("Wave Type:"), 0, 0)
        self.wave_type = QComboBox()
        self.wave_type.addItems(["Sine", "Square", "Triangle"])
        self.wave_type.currentIndexChanged.connect(self.update_signal)
        params_layout.addWidget(self.wave_type, 0, 1)

        # 幅值控制
        params_layout.addWidget(QLabel("Amplitude (V):"), 1, 0)
        self.amplitude = QDoubleSpinBox()
        self.amplitude.setRange(0.1, 10.0)
        self.amplitude.setValue(5.0)
        self.amplitude.valueChanged.connect(self.update_signal)
        params_layout.addWidget(self.amplitude, 1, 1)

        left_layout.addWidget(params_group)

        # 右侧面板 - Turbo编码显示
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Turbo编码结果显示
        self.encoded_canvas = SignalCanvas(self, width=5, height=3)
        right_layout.addWidget(self.encoded_canvas)

        # 编码信息显示
        self.encoding_info = QLabel()
        self.encoding_info.setWordWrap(True)
        right_layout.addWidget(self.encoding_info)

        # 添加面板到主布局
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        # 控制按钮
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.toggle_simulation)
        control_layout.addWidget(self.start_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_simulation)
        control_layout.addWidget(self.reset_button)

        left_layout.addLayout(control_layout)

    def update_signal(self):
        try:
            # 生成基本信号参数
            frequency = 10.0  # 固定10kHz
            amplitude = self.amplitude.value()
            wave_type = self.wave_type.currentText()
            sample_rate = 100.0  # 采样率100kHz

            # 生成时间数组
            t = np.linspace(0, self.duration, int(self.duration * sample_rate * 1000), endpoint=False)

            # 生成模拟信号
            if wave_type == "Sine":
                analog_signal = amplitude * np.sin(2 * np.pi * frequency * t)
                signal_title = f"Sine Wave (10kHz, {amplitude}V)"
            elif wave_type == "Square":
                analog_signal = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
                signal_title = f"Square Wave (10kHz, {amplitude}V)"
            else:  # Triangle
                analog_signal = amplitude * 2 * np.abs(2 * ((t * frequency) % 1) - 1) - amplitude
                signal_title = f"Triangle Wave (10kHz, {amplitude}V)"

            # 显示模拟信号
            self.input_canvas.plot_analog_signal(t, analog_signal, signal_title)

            # AD转换（8位）
            max_val = 255  # 8位ADC
            normalized = ((analog_signal + amplitude) / (2 * amplitude)) * max_val
            digital_values = np.round(normalized).clip(0, max_val)

            # 生成PWM信号
            pwm_frequency = 50.0  # PWM频率50kHz
            pwm_signal = self.digital_to_pwm(t, digital_values)
            self.pwm_canvas.plot_digital_signal(t, pwm_signal, f"PWM Signal (8-bit, {pwm_frequency}kHz)")

            # 将PWM信号转换为二进制序列
            binary_sequence = self.pwm_to_binary(pwm_signal)

            # Turbo编码
            encoded_result = self.encoder.encode(binary_sequence)

            # 显示编码结果
            self.encoded_canvas.plot_encoded_signal(
                encoded_result['encoded'],
                "Turbo Encoded Signal"
            )

            # 更新编码信息显示
            self.update_encoding_info(binary_sequence, encoded_result)

        except Exception as e:
            print(f"Error in signal update: {str(e)}")

    def digital_to_pwm(self, t, digital_values):
        pwm_frequency = 50.0  # 50kHz
        pwm_period = 1.0 / (pwm_frequency * 1000)
        pwm_signal = np.zeros_like(t)

        for i, time in enumerate(t):
            position_in_period = (time % pwm_period) / pwm_period
            duty_cycle = digital_values[i] / 255  # 8-bit
            pwm_signal[i] = 1.0 if position_in_period < duty_cycle else 0.0

        return pwm_signal

    def pwm_to_binary(self, pwm_signal, sample_points=32):
        samples = np.array_split(pwm_signal, sample_points)
        binary = [1 if np.mean(sample) > 0.5 else 0 for sample in samples]
        return binary

    def update_encoding_info(self, input_bits, encoded_result):
        info_text = f"""
        Input Sequence Length: {len(input_bits)}
        Encoded Length: {len(encoded_result['encoded'])}
        Systematic Bits: {len(encoded_result['components']['systematic'])}
        Parity1 Bits: {len(encoded_result['components']['parity1'])}
        Parity2 Bits: {len(encoded_result['components']['parity2'])}
        """
        self.encoding_info.setText(info_text)

    def toggle_simulation(self):
        if self.is_running:
            self.timer.stop()
            self.start_button.setText("Start")
        else:
            self.timer.start(100)  # 更新频率10Hz
            self.start_button.setText("Stop")
        self.is_running = not self.is_running

    def reset_simulation(self):
        self.wave_type.setCurrentIndex(0)
        self.amplitude.setValue(5.0)
        if self.is_running:
            self.toggle_simulation()
        self.update_signal()


def main():
    app = QApplication(sys.argv)
    window = IntegratedApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()