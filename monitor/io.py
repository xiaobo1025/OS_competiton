'''
import psutil

def get_disk_io():
    io = psutil.disk_io_counters()
    return {
        "read_bytes": io.read_bytes,
        "write_bytes": io.write_bytes
    }
'''

import psutil
import os
import glob

def get_disk_io():
    """获取完整的磁盘 I/O 信息，包括队列深度、调度策略等"""
    data = {
        # 原有指标
        "read_bytes": 0,
        "write_bytes": 0,
        
        # 扩展指标
        "devices": {}  # 按设备细分的详细信息
    }
    
    # 获取全局 I/O 统计（保持原有逻辑）
    try:
        io = psutil.disk_io_counters()
        data.update({
            "read_bytes": io.read_bytes,
            "write_bytes": io.write_bytes
        })
    except:
        pass
    
    # 获取每个磁盘设备的详细信息
    for device in get_disk_devices():
        device_data = {
            "io_scheduler": get_io_scheduler(device),
            "queue_depth": get_queue_depth(device),
            "sector_size": get_sector_size(device),
            "io_stats": get_device_io_stats(device)
        }
        data["devices"][device] = device_data
    
    return data

# 辅助函数：获取所有物理磁盘设备（如 sda, nvme0n1）
def get_disk_devices():
    devices = []
    for block in glob.glob("/sys/block/*"):
        device = os.path.basename(block)
        # 过滤掉 RAM 盘、loop 设备等非物理磁盘
        if not (device.startswith("ram") or device.startswith("loop")):
            devices.append(device)
    return devices

# 辅助函数：获取磁盘 I/O 调度器
def get_io_scheduler(device):
    try:
        with open(f"/sys/block/{device}/queue/scheduler", "r") as f:
            return f.read().strip().split()[0].strip("[]")  # 获取当前激活的调度器
    except:
        return "unknown"

# 辅助函数：获取磁盘队列深度
def get_queue_depth(device):
    try:
        with open(f"/sys/block/{device}/queue/nr_requests", "r") as f:
            return int(f.read().strip())
    except:
        return -1

# 辅助函数：获取磁盘扇区大小
def get_sector_size(device):
    try:
        with open(f"/sys/block/{device}/queue/physical_block_size", "r") as f:
            return int(f.read().strip())
    except:
        return -1

# 辅助函数：获取设备级 I/O 统计（更详细的性能指标）
def get_device_io_stats(device):
    try:
        with open(f"/sys/block/{device}/stat", "r") as f:
            stats = f.read().split()
            return {
                "read_ios": int(stats[0]),         # 读 I/O 操作数
                "read_merges": int(stats[1]),      # 读合并次数
                "read_sectors": int(stats[2]),     # 读扇区数
                "read_ticks": int(stats[3]),       # 读耗时（毫秒）
                "write_ios": int(stats[4]),        # 写 I/O 操作数
                "write_merges": int(stats[5]),     # 写合并次数
                "write_sectors": int(stats[6]),    # 写扇区数
                "write_ticks": int(stats[7]),      # 写耗时（毫秒）
                "in_flight": int(stats[8]),        # 正在处理的 I/O 数
                "io_ticks": int(stats[9]),         # I/O 总耗时
                "time_in_queue": int(stats[10])    # I/O 在队列中的总时间
            }
    except:
        return {"error": "failed to read stats"}
   