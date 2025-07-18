import os
import re

BLOCK_PATH = "/sys/block/"

def is_valid_disk(device):
    """
    判断是否为有效的物理磁盘设备（跳过 loop 和 sr）
    """
    return re.match(r"^sd[a-z]$", device)

def read_queue_param(device, param):
    """
    读取某个磁盘设备的 queue 参数
    """
    path = f"{BLOCK_PATH}{device}/queue/{param}"
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return "N/A"

def get_io_params():
    """
    获取所有物理磁盘的 I/O 调优参数：
    - scheduler：I/O 调度算法
    - nr_requests：队列深度
    - read_ahead_kb：预读大小
    """
    devices = os.listdir(BLOCK_PATH)
    results = {}

    for dev in devices:
        if not is_valid_disk(dev):
            continue  # 跳过 loop 设备、光驱等

        results[dev] = {
            "scheduler": read_queue_param(dev, "scheduler"),
            "nr_requests": read_queue_param(dev, "nr_requests"),
            "read_ahead_kb": read_queue_param(dev, "read_ahead_kb")
        }

    return results

# 支持独立调试运行
if __name__ == "__main__":
    import json
    io_params = get_io_params()
    print(json.dumps(io_params, indent=2))

