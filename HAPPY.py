import sys
import ctypes
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QMainWindow,QGridLayout, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel, QComboBox, \
    QLineEdit, QGridLayout
from PyQt5.QtCore import Qt, QTimer


class SerialPort:
    def __init__(self):
        self.serial = None
        self.port = None
        self.baud_rate = 115200
        self.data_bits = 8
        self.parity = serial.PARITY_NONE
        self.stop_bits = serial.STOPBITS_ONE

    def open(self, port_name):
        try:
            self.serial = serial.Serial(port_name, self.baud_rate, self.data_bits, self.parity, self.stop_bits)
            self.port = port_name
            return True
        except Exception as e:
            print(f"Error opening port: {e}")
            return False

    def close(self):
        if self.serial and self.serial.is_open:
            self.serial.close()

    def send(self, data):
        if self.serial and self.serial.is_open:
            self.serial.write(data)

    def receive(self):
        if self.serial and self.serial.is_open:
            return self.serial.read_all()
        return b''


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.serial_port = SerialPort()

        #按钮库
        #白天
        self.commands = {
            "马赛克算法":"2C 12 00 01  00 00 31 15 22 00 FF 5B",
            "自动白平衡": "2C 12 80 01  01 ff 31 15 22 00 FF 5B",
            "自动白平衡不同统计域": "2C 12 80 01  01 f0 31 15 22 00 FF 5B",
            "白平衡": "2C 12 40 01 01 f0 22 15 31 00 FF 5B",
            "白平衡不同阈值": "2C 12 40 01 01 f0 31 15 22 00 FF 5B",
            "RGB转YUV": "2C 12 60 01 01 f0 31 15 22 00 FF 5B",
            "YUV转RGB": "2C 12 61 01 01 f0 31 15 22 00 FF 5B",
            "全局GAMMA变换": "2C 12 69 01 01 f0 31 15 22 00 FF 5B",
            "局部GAMMA变换": "2C 12 71 01 01 f0 31 15 22 00 FF 5B",
            "边缘特征": "  2C 12 65 01 01 f0 31 15 22 00 FF 5B",
            "特征HDR融合":"2C 12 67 01 01 f0 27 11 1B 00 FF 5B",
            "最终" : "2C 12 71 01 01 F0 27 11 1B 00 00 5B",
            "自定义": "2C 12 00 00 00 00 00 00 00 00 FF 5B"

        }
        #查找库
        self.commandsfind = {
            "D马赛克算法": "2C 12 00 01  00 00 31 15 22 00 FF 5B",
            "D自动白平衡": "2C 12 80 01  01 ff 31 15 22 00 FF 5B",
            "D自动白平衡不同统计域": "2C 12 80 01  01 f0 31 15 22 00 FF 5B",
            "D白平衡": "2C 12 40 01 01 f0 22 15 31 00 FF 5B",
            "D白平衡不同阈值": "2C 12 40 01 01 f0 31 15 22 00 FF 5B",
            "DRGB转YUV": "2C 12 60 01 01 f0 31 15 22 00 FF 5B",
            "DYUV转RGB": "2C 12 61 01 01 f0 31 15 22 00 FF 5B",
            "D全局GAMMA变换": "2C 12 69 01 01 f0 31 15 22 00 FF 5B",
            "D局部GAMMA变换": "2C 12 71 01 01 f0 31 15 22 00 FF 5B",
            "D边缘特征": "  2C 12 65 01 01 f0 31 15 22 00 FF 5B",
            "D特征HDR融合": "2C 12 67 01 01 f0 31 15 22 00 FF 5B",
            "D最终": "2C 12 71 01 01 F0 27 11 1B 00 00 5B",

            "N马赛克算法": "2C 12 00 01  00 00 31 15 22 FF FF 5B",
            "N自动白平衡": "2C 12 80 01  01 ff 31 15 22 FF FF 5B",
            "N自动白平衡不同统计域": "2C 12 80 01  01 f0 31 15 22 FF FF 5B",
            "N白平衡": "2C 12 40 01 01 f0 22 15 31 FF FF 5B",
            "N白平衡不同阈值": "2C 12 40 01 01 f0 31 15 22 FF FF 5B",
            "NRGB转YUV": "2C 12 60 01 01 f0 22 15 31 FF FF 5B",
            "NYUV转RGB": "2C 12 61 01 01 f0 22 15 31 FF FF 5B",
            "N全局GAMMA变换": "2C 12 69 01 01 f0 22 15 31 FF FF 5B",
            "N局部GAMMA变换": "2C 12 71 01 01 f0 22 15 31 FF FF 5B",
            "N边缘特征": " 2C 12 65 01 01 f0 22 15 31 FF FF 5B",
            "N特征HDR融合": "2C 12 6f 01 01 f0 22 15 31 FF FF 5B",
            "自定义": "2C 12 00 00 00 00 00 00 00 00 FF 5B"

        }

        self.setWindowTitle("HAPPY上位机")
        self.setGeometry(100, 100, 800, 600)

        # Create Widgets
        self.setup_ui()
        self.setup_menu()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QGridLayout()

        # Team ID
        self.team_id_label = QLabel("队伍编号: CICC2848")
        layout.addWidget(self.team_id_label, 0, 0, 1, 3)

        # Port Selection
        self.port_combo = QComboBox()
        self.refresh_ports()
        layout.addWidget(QLabel("选择串口:"), 1, 0)
        layout.addWidget(self.port_combo, 1, 1, 1, 2)

        # Serial Parameters
        self.data_bits_combo = QComboBox()
        self.data_bits_combo.addItems(["7", "8"])
        self.data_bits_combo.setCurrentText("8")
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["None", "Odd", "Even"])
        self.parity_combo.setCurrentText("None")
        self.stop_bits_combo = QComboBox()
        self.stop_bits_combo.addItems(["1", "1.5", "2"])
        self.stop_bits_combo.setCurrentText("1")

        layout.addWidget(QLabel("数据位:"), 2, 0)
        layout.addWidget(self.data_bits_combo, 2, 1)
        layout.addWidget(QLabel("校验位:"), 2, 2)
        layout.addWidget(self.parity_combo, 2, 3)
        layout.addWidget(QLabel("停止位:"), 2, 4)
        layout.addWidget(self.stop_bits_combo, 2, 5)

        # Command Buttons
        self.button_layout = QGridLayout()
        row, col = 0, 0
        for name in self.commands:
            button = QPushButton(name)
            button.clicked.connect(lambda checked, n=name: self.send_command(n))
            self.button_layout.addWidget(button, row, col)
            col += 1
            if col >= 3:  # 每行最多3个按钮
                col = 0
                row += 1

        layout.addLayout(self.button_layout, 3,0, 1, 6)

        # Command Editor
        self.command_input = QLineEdit()
        layout.addWidget(QLabel("自定义命令:"), 4, 0)
        layout.addWidget(self.command_input, 4, 1, 1, 4)

        self.custom_send_button = QPushButton("发送自定义命令")
        self.custom_send_button.clicked.connect(self.send_custom_command)
        layout.addWidget(self.custom_send_button, 4, 5)

        # Display Areas
        self.send_display = QTextEdit()
        self.send_display.setReadOnly(True)
        layout.addWidget(QLabel("发送数据:"), 5, 0)
        layout.addWidget(self.send_display, 5, 1, 1, 6)

        self.receive_display = QTextEdit()
        self.receive_display.setReadOnly(True)
        layout.addWidget(QLabel("接收数据:"), 6, 0)
        layout.addWidget(self.receive_display, 6, 1, 1, 6)


        main_widget.setLayout(layout)

        # Timer for periodic read
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.timer.start(100)

    def setup_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("文件")

        open_port_action = file_menu.addAction("打开串口")
        open_port_action.triggered.connect(self.open_serial_port)

        close_port_action = file_menu.addAction("关闭串口")
        close_port_action.triggered.connect(self.close_serial_port)

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def open_serial_port(self):
        port = self.port_combo.currentText()
        data_bits = int(self.data_bits_combo.currentText())
        parity = self.parity_combo.currentText()
        stop_bits = float(self.stop_bits_combo.currentText())

        self.serial_port.data_bits = data_bits
        self.serial_port.parity = {'None': serial.PARITY_NONE, 'Odd': serial.PARITY_ODD, 'Even': serial.PARITY_EVEN}[
            parity]
        self.serial_port.stop_bits = \
        {1: serial.STOPBITS_ONE, 1.5: serial.STOPBITS_ONE_POINT_FIVE, 2: serial.STOPBITS_TWO}[stop_bits]

        if self.serial_port.open(port):
            self.send_display.append(f"串口 {port} 打开成功")
        else:
            self.send_display.append(f"串口 {port} 打开失败")

    def close_serial_port(self):
        self.serial_port.close()
        self.send_display.append("串口已关闭")

    def send_command(self, command_name):
        command = self.commands.get(command_name)
        if command:
            self.serial_port.send(bytes.fromhex(command))
            self.send_display.append(f"发送: {command}")

    def send_custom_command(self):
        command_text = self.command_input.text()
        if command_text:
            command_name, *params = command_text.split()
            command = self.commandsfind.get(command_name)
            if command:
                command_bytes = bytearray.fromhex(command)
                if command_name == "自动白平衡":
                    if len(params) == 2:
                        param1 = int(params[0])
                        param2 = int(params[1])
                        command_bytes[4] = param1
                        command_bytes[5] = param2
                elif command_name == "白平衡":
                    if len(params) == 3:
                        param1, param2, param3 = map(int, params)
                        command_bytes[7] = param1
                        command_bytes[8] = param2
                        command_bytes[9] = param3
                elif command_name == "自定义":
                    if len(params) == 8:
                        param1, param2, param3, param4, param5, param6, param7, param8 = [int(p, 16) for p in params]
                        command_bytes[2] = param1
                        command_bytes[3] = param2
                        command_bytes[4] = param3
                        command_bytes[5] = param4
                        command_bytes[6] = param5
                        command_bytes[7] = param6
                        command_bytes[8] = param7
                        command_bytes[9] = param8
                self.serial_port.send(command_bytes)
                self.send_display.append(f"发送: {command_bytes.hex().upper()}")
            else:
                self.send_display.append(f"未知命令: {command_name}")

    def read_serial(self):
        data = self.serial_port.receive()
        if data:
            self.receive_display.append(data.decode('utf-8'))


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
