#!/usr/bin/python3
import matplotlib.pyplot as plt

downsampled_count = 30

# 读取日志文件
with open('bat_log.txt', 'r') as file:
    lines = file.readlines()

# 处理数据
data = []
for line in lines:
    fields = line.split()
    if len(fields) >= 3 and fields[2] == '09':
        if len(fields) >= 5:
            hex_value = fields[3] + fields[4]
            decimal_value = int(hex_value, 16)
            data.append(decimal_value)

# 截断到最接近的十的倍数
truncated_length = (len(data) // downsampled_count) * downsampled_count
data = data[:truncated_length]

# 降采样，每十个数据取一个平均值
downsampled_data = [sum(data[i:i+downsampled_count]) / downsampled_count for i in range(0, len(data), downsampled_count)]

# 计算每个数据点对应的时间（以分钟为单位）
time_interval_minutes = 1.5 * downsampled_count / 60  # 时间间隔为1.5秒，转换为分钟
time_points = [i * time_interval_minutes for i in range(len(downsampled_data))]

# 绘制散点图
plt.scatter(time_points, downsampled_data)
plt.xlabel('Time (minutes)')
plt.ylabel('Average Decimal Value (Downsampled)')
plt.title('Downsampled Scatter Plot of Decimal Values over Time')
plt.show()
