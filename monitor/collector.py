from datetime import datetime
from monitor.cpu import get_cpu_info
from monitor.gpu import get_gpu_info
from monitor.memory import get_memory_info
from monitor.io import get_disk_io
from monitor.network import get_network_info
from monitor.tcp import get_tcp_congestion

def collect_all_metrics():
    data = {}
    data.update(get_cpu_info())
    data.update(get_gpu_info())
    data.update(get_memory_info())
    data.update(get_disk_io())
    data.update(get_network_info())
    data.update(get_tcp_congestion())
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ✅ 添加这个（用于模型推理）
    algo = data.get("tcp_congestion_control", "unknown")
    data["tcp_congestion_encoded"] = {
        "cubic": 0,
        "bbr": 1,
        "reno": 2
    }.get(algo, -1)

    return data

