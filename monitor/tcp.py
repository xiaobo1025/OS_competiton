'''
import subprocess

def get_tcp_congestion():
    try:
        result = subprocess.run(['sysctl', 'net.ipv4.tcp_congestion_control'], capture_output=True, text=True)
        algo = result.stdout.strip().split('=')[1].strip()
        return {"tcp_congestion_control": algo}
    except:
        return {"tcp_congestion_control": "unknown"}
'''
  
import subprocess
import re

def get_tcp_congestion():
    """获取完整的TCP参数，包括拥塞控制算法和socket缓冲区大小"""
    data = {
        # 原有指标
        "tcp_congestion_control": "unknown",
        
        # 新增指标：socket缓冲区大小
        "tcp_rmem_min": -1,    # 接收缓冲区最小值
        "tcp_rmem_default": -1,  # 接收缓冲区默认值
        "tcp_rmem_max": -1,    # 接收缓冲区最大值
        "tcp_wmem_min": -1,    # 发送缓冲区最小值
        "tcp_wmem_default": -1,  # 发送缓冲区默认值
        "tcp_wmem_max": -1,    # 发送缓冲区最大值
        
        # 其他TCP关键参数
        "tcp_timestamps": -1,  # 是否启用时间戳
        "tcp_sack": -1,        # 是否启用选择性确认
        "tcp_fastopen": -1     # TCP快速打开
    }
    
    try:
        # 获取TCP拥塞控制算法
        result = subprocess.run(['sysctl', 'net.ipv4.tcp_congestion_control'], 
                               capture_output=True, text=True, check=True)
        data["tcp_congestion_control"] = result.stdout.strip().split('=')[1].strip()
    except:
        pass
    
    # 获取socket缓冲区参数
    try:
        result = subprocess.run(['sysctl', 'net.ipv4.tcp_rmem'], 
                               capture_output=True, text=True, check=True)
        # 输出格式：net.ipv4.tcp_rmem = 4096    87380   6291456
        values = list(map(int, re.findall(r'\d+', result.stdout)))
        if len(values) == 3:
            data["tcp_rmem_min"] = values[0]
            data["tcp_rmem_default"] = values[1]
            data["tcp_rmem_max"] = values[2]
    except:
        pass
    
    try:
        result = subprocess.run(['sysctl', 'net.ipv4.tcp_wmem'], 
                               capture_output=True, text=True, check=True)
        values = list(map(int, re.findall(r'\d+', result.stdout)))
        if len(values) == 3:
            data["tcp_wmem_min"] = values[0]
            data["tcp_wmem_default"] = values[1]
            data["tcp_wmem_max"] = values[2]
    except:
        pass
    
    # 获取其他TCP参数
    try:
        data["tcp_timestamps"] = int(get_sysctl_value('net.ipv4.tcp_timestamps'))
        data["tcp_sack"] = int(get_sysctl_value('net.ipv4.tcp_sack'))
        data["tcp_fastopen"] = int(get_sysctl_value('net.ipv4.tcp_fastopen'))
    except:
        pass
    
    return data

# 辅助函数：获取单个sysctl值
def get_sysctl_value(param):
    result = subprocess.run(['sysctl', param], capture_output=True, text=True)
    return result.stdout.strip().split('=')[1].strip()
