#!/usr/bin/python3
import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
from datetime import datetime  # 添加导入语句

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
        with open('received_data.txt', 'a') as file:
            while self.running:  # 使用标志来控制线程运行状态
                try:
                    if self.ser and self.ser.is_open:
                        data = self.ser.readline()
                        if data:
                            hex_data = ' '.join(format(byte, '02X') for byte in data)

                            if 'A5' in hex_data:
                                hex_data = hex_data.replace('A5', '\nA5')

                            # 获取当前系统时间并添加到每一行的开头
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            file.write(f"{timestamp} - {hex_data}\n")
                            file.flush()
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
