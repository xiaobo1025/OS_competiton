'''
import psutil

def get_network_info():
    net = psutil.net_io_counters()
    return {
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv
    }
'''
  

import psutil
import socket

def get_network_info():
    """获取完整的网络信息，包括接口状态、带宽和连接数"""
    data = {
        # 原有指标
        "bytes_sent": 0,
        "bytes_recv": 0,
        
        # 新增指标：网络接口详细信息
        "interfaces": {},
        
        # 网络连接统计
        "connections": {
            "total": 0,
            "established": 0,
            "syn_sent": 0,
            "syn_recv": 0,
            "fin_wait1": 0,
            "fin_wait2": 0,
            "time_wait": 0,
            "close": 0,
            "close_wait": 0,
            "last_ack": 0,
            "listen": 0,
            "closing": 0
        },
        
        # 系统级网络统计
        "tcp_connections_count": 0,
        "udp_connections_count": 0,
        "socket_count": 0
    }
    
    # 获取全局网络IO统计（保持原有逻辑）
    try:
        net = psutil.net_io_counters()
        data.update({
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv
        })
    except:
        pass
    
    # 获取每个网络接口的详细信息
    try:
        for iface, addrs in psutil.net_if_addrs().items():
            iface_data = {
                "addresses": [],
                "status": "unknown",
                "mtu": -1,
                "speed": -1
            }
            
            # 收集IP地址和MAC地址
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    iface_data["addresses"].append({
                        "family": "IPv4",
                        "address": addr.address,
                        "netmask": addr.netmask
                    })
                elif addr.family == socket.AF_INET6:
                    iface_data["addresses"].append({
                        "family": "IPv6",
                        "address": addr.address,
                        "netmask": addr.netmask
                    })
                elif addr.family == psutil.AF_LINK:
                    iface_data["mac"] = addr.address
            
            # 获取接口状态和MTU
            try:
                with open(f"/sys/class/net/{iface}/operstate", "r") as f:
                    iface_data["status"] = f.read().strip()
                with open(f"/sys/class/net/{iface}/mtu", "r") as f:
                    iface_data["mtu"] = int(f.read().strip())
                # 获取网卡速度（仅对支持的接口有效）
                with open(f"/sys/class/net/{iface}/speed", "r") as f:
                    iface_data["speed"] = int(f.read().strip())  # Mbps
            except:
                pass
            
            data["interfaces"][iface] = iface_data
    except:
        pass
    
    # 获取网络连接统计
    try:
        conn_states = {}
        for conn in psutil.net_connections(kind='inet'):
            state = conn.status
            conn_states[state] = conn_states.get(state, 0) + 1
            data["connections"]["total"] += 1
        
        # 更新连接状态统计
        for state, count in conn_states.items():
            if state in data["connections"]:
                data["connections"][state] = count
    except:
        pass
    
    # 获取TCP/UDP连接总数和socket总数
    try:
        # TCP连接数（等效于 netstat -t | wc -l）
        with open("/proc/net/tcp", "r") as f:
            data["tcp_connections_count"] = len(f.readlines()) - 1  # 减去标题行
        
        # UDP连接数（等效于 netstat -u | wc -l）
        with open("/proc/net/udp", "r") as f:
            data["udp_connections_count"] = len(f.readlines()) - 1
        
        # 总socket数
        with open("/proc/net/sockstat", "r") as f:
            for line in f:
                if line.startswith("sockets:"):
                    data["socket_count"] = int(line.split()[1].split('=')[1])
                    break
    except:
        pass
    return data