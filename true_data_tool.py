#!/usr/bin/python3
import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading

class DeviceStatus:
    def __init__(self):
        self.status_color = 0  # 颜色传感器匹配状态
        self.status_probe1 = 0  # 通断状态1

class ImpedanceDataFrame:
    def __init__(self):
        self.line_volume = 0  # 初始化为整数
        self.device_status = DeviceStatus()  # 初始化为DeviceStatus类的实例
        self.data_byte = []

class ImpedanceFrame:
    def __init__(self):
        self.head = [0, 0, 0]  # 初始化为整数列表
        self.length = 0  # 初始化为整数
        self.seq_num = 0  # 初始化为整数
        self.slot_number = 0  # 初始化为整数
        self.type = 0  # 初始化为整数
        self.data = ImpedanceDataFrame()
        self.checknum = 0

    def parse_from_bytes(self, byte_data):
        # 根据实际数据格式和偏移解析字节数组
        self.head = list(byte_data[:3])
        self.length = byte_data[3]
        self.seq_num = byte_data[4]
        self.slot_number = byte_data[5]
        self.type = byte_data[6]

        # 解析 ImpedanceDataFrame 中的数据
        data_frame_offset = 7
        self.data.line_volume = byte_data[data_frame_offset]
        
        # 解析 DeviceStatus 中的数据
        device_status_offset = data_frame_offset + 1
        self.data.device_status.status_color = byte_data[device_status_offset]
        self.data.device_status.status_probe1 = byte_data[device_status_offset + 1]
        
        # 解析 ImpedanceDataFrame 中的 data_byte
        data_byte_offset = device_status_offset + 2
        data_byte_length = data_byte_length = int.from_bytes(byte_data[3], byteorder='big') - 8 - 3
        # 假设第一个字节表示 data_byte 的长度
        self.data.data_byte = byte_data[data_byte_offset:data_byte_offset + data_byte_length]

        # 解析 checknum
        checknum_offset = data_byte_offset + data_byte_length
        self.checknum = byte_data[checknum_offset]

class SerialDebugAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Debug Assistant")

        # Serial Port Configuration
        self.serial_ports = ttk.Combobox(root, values=self.get_available_ports())
        self.serial_port_label = tk.Label(root, text="Serial Port:")
        self.baud_rate_label = tk.Label(root, text="Baud Rate:")
        self.baud_rate = ttk.Combobox(root, values=["9600", "115200"])
        self.connect_button = tk.Button(root, text="Connect", command=self.connect_serial)
        self.disconnect_button = tk.Button(root, text="Disconnect", command=self.disconnect_serial)
        self.disconnect_button.grid(row=0, column=5, padx=5, pady=5)
        
        # 添加一个标志，用于控制线程的运行状态
        self.running = True

        # Text Area for Displaying Data
        self.text_area = tk.Text(root, state="disabled", wrap="word", height=10, width=50)
        self.scrollbar = tk.Scrollbar(root, command=self.text_area.yview)
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        # Entry for User Input
        self.input_entry = tk.Entry(root, width=40)
        self.send_button = tk.Button(root, text="Send", command=self.send_data)

        # Layout
        self.serial_port_label.grid(row=0, column=0, padx=5, pady=5)
        self.serial_ports.grid(row=0, column=1, padx=5, pady=5)
        self.baud_rate_label.grid(row=0, column=2, padx=5, pady=5)
        self.baud_rate.grid(row=0, column=3, padx=5, pady=5)
        self.connect_button.grid(row=0, column=4, padx=5, pady=5)

        self.text_area.grid(row=1, column=0, columnspan=5, padx=5, pady=5)
        self.scrollbar.grid(row=1, column=5, sticky="ns")

        self.input_entry.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        self.send_button.grid(row=2, column=3, columnspan=2, padx=5, pady=5)

        # 绑定关闭窗口时关闭串口的方法
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Serial Port Object
        self.ser = None

        # 将变量定义为实例变量
        self.g_u8FrameHeader = [0xA5, 0xFF, 0xCC]
        self.g_u8ReceiveByteHeaderPosition = 0
        self.g_u8ReceiveBytePosition = 0
        self.g_u8DataReceiveBuffer = []
        self.binary_data = []

        


    def disconnect_serial(self):
        # 停止读取线程
        self.running = False

        # 关闭串口连接
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.text_area.config(state="normal")
            self.text_area.insert(tk.END, "Disconnected\n")
            self.text_area.config(state="disabled")

    def on_closing(self):
        # 如果串口打开，关闭串口
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.root.destroy()

    def get_available_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports

    def connect_serial(self):
        self.running = True
        port = self.serial_ports.get()
        baud_rate = int(self.baud_rate.get())

        try:
            self.ser = serial.Serial(port, baud_rate, timeout=1)
            self.text_area.config(state="normal")
            self.text_area.insert(tk.END, f"Connected to {port} at {baud_rate} baud\n")
            self.text_area.config(state="disabled")

            # Start a separate thread for reading from the serial port
            read_thread = threading.Thread(target=self.read_from_serial)
            read_thread.start()
        except serial.SerialException as e:
            self.text_area.config(state="normal")
            self.text_area.insert(tk.END, f"Error: {str(e)}\n")
            self.text_area.config(state="disabled")

    def read_from_serial(self):
        with open('output.txt', 'a') as file:
            while self.running:  # 使用标志来控制线程运行状态
                try:
                    if self.ser and self.ser.is_open:
                        data = self.ser.read(1)
                        self.g_u8DataReceiveBuffer.append(data)
                        if self.g_u8ReceiveByteHeaderPosition < 3:
                            expected_byte = self.g_u8FrameHeader[self.g_u8ReceiveByteHeaderPosition]
                            if data[0] == expected_byte:
                                self.g_u8ReceiveByteHeaderPosition += 1
                                self.g_u8ReceiveBytePosition += 1
                            else:
                                # 帧头校验失败并复位帧头校验指针
                                self.g_u8ReceiveByteHeaderPosition = 0
                                self.g_u8ReceiveBytePosition = 0
                                self.g_u8DataReceiveBuffer.clear()
                        else:
                            # HEADER MATCHES
                            # 帧头校验成功
                            self.g_u8ReceiveBytePosition += 1

                            # 如果所有数据都已接收，重置指针，然后进入类型区分
                            if len(self.g_u8DataReceiveBuffer) >= 4:
                                if self.g_u8ReceiveBytePosition == int.from_bytes(self.g_u8DataReceiveBuffer[3], byteorder='big'):
                                    # 在这里添加类型区分的逻辑
                                    if 2 == int.from_bytes(self.g_u8DataReceiveBuffer[6], byteorder='big'):
                                        # 定义表格的行数和列数
                                        num_rows = 24
                                        num_cols = impedance_frame.data.line_volume
                                        impedance_frame = ImpedanceFrame()
                                        impedance_frame.parse_from_bytes(self.g_u8DataReceiveBuffer)
                                        # 将十六进制数值拼接为字符串
                                        hex_value = ''.join(format(byte, '02X') for byte in impedance_frame.data.data_byte)
                                        # 十六进制字符串转二进制字符串
                                        binary_value = bin(int(hex_value, 16))[2:].zfill(4 * impedance_frame.data.line_volume)
                                        table = [[int(binary_value[i * num_cols + j]) for j in range(num_cols)] for i in range(num_rows)]
                                    # 重置指针
                                    self.g_u8ReceiveByteHeaderPosition = 0
                                    self.g_u8ReceiveBytePosition = 0
                                    self.g_u8DataReceiveBuffer.clear()

                except serial.SerialException as e:
                    self.text_area.config(state="normal")
                    self.text_area.insert(tk.END, f"Error: {str(e)}\n")
                    self.text_area.config(state="disabled")
                    break  # 在异常时退出线程

    def send_data(self):
        data = self.input_entry.get()
        if self.ser and self.ser.is_open:
            self.ser.write(data.encode('utf-8'))
            self.text_area.config(state="normal")
            self.text_area.insert(tk.END, f"Sent: {data}\n")
            self.text_area.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialDebugAssistant(root)
    root.mainloop()
