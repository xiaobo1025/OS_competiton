import socket
import threading
import time
import random

def validate_port_input():
    """验证端口输入"""
    while True:
        port = input("请输入使用的端口号：")
        try:
            port = int(port)
            if port < 1024 or port > 65535:
                print("错误: 端口号必须在 1024-65535 范围内")
                continue
            
            # 检查端口是否可用
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.bind(('localhost', port))
            except OSError:
                print(f"错误: 端口 {port} 已被占用，请选择其他端口")
                continue
            
            return port
        except ValueError:
            print("错误: 请输入有效的整数")

def validate_packet_size_input():
    """验证数据包大小输入"""
    while True:
        size = input("请输入每个数据包的大小（KB）：")
        try:
            size = int(size)
            if size <= 0:
                print("错误: 数据包大小必须大于 0")
                continue
            if size > 1024:  # 1MB
                print("警告: 数据包大小设置较大 (超过 1MB)，可能导致网络拥塞")
            return size
        except ValueError:
            print("错误: 请输入有效的整数")

def validate_packet_rate_input():
    """验证数据包速率输入"""
    while True:
        rate = input("请输入每秒发送的数据包数量：")
        try:
            rate = int(rate)
            if rate <= 0:
                print("错误: 发包速率必须大于 0")
                continue
            if rate > 10000:
                print("警告: 发包速率设置较高 (超过 10000包/秒)，可能导致系统资源耗尽")
            return rate
        except ValueError:
            print("错误: 请输入有效的整数")

def validate_duration_input():
    """验证持续时间输入"""
    while True:
        duration = input("请输入负载持续时间（秒）：")
        try:
            duration = int(duration)
            if duration <= 0:
                print("错误: 持续时间必须大于 0")
                continue
            if duration > 3600:
                print("警告: 持续时间设置较长 (超过 1 小时)，请确保这是您想要的")
            return duration
        except ValueError:
            print("错误: 请输入有效的整数")

def show_countdown(duration):
    """显示倒计时"""
    for remaining in range(duration, 0, -1):
        mins, secs = divmod(remaining, 60)
        time_format = f"{mins:02d}:{secs:02d}"
        print(f"\r剩余时间: {time_format}", end='', flush=True)
        time.sleep(1)
    print("\r剩余时间: 00:00", end='', flush=True)
    print()

def tcp_server(port, packet_size_bytes, duration):
    """TCP服务器"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', port))
    server_socket.listen(1)
    
    print(f"TCP 服务器已启动，监听端口 {port}")
    
    end_time = time.time() + duration
    
    try:
        while time.time() < end_time:
            try:
                conn, addr = server_socket.accept()
                conn.settimeout(1)
                with conn:
                    while time.time() < end_time:
                        data = conn.recv(packet_size_bytes)
                        if not data:
                            break
            except socket.timeout:
                continue
            except Exception as e:
                if time.time() < end_time:
                    print(f"服务器错误: {e}")
    finally:
        server_socket.close()

def tcp_client(port, packet_size_bytes, packets_per_second, duration):
    """TCP客户端"""
    end_time = time.time() + duration
    packet_interval = 1.0 / packets_per_second
    data = b'X' * packet_size_bytes
    
    try:
        while time.time() < end_time:
            start_conn_time = time.time()
            
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    s.connect(('localhost', port))
                    
                    conn_remaining = end_time - time.time()
                    if conn_remaining <= 0:
                        break
                    
                    packets_to_send = int(conn_remaining * packets_per_second)
                    for _ in range(packets_to_send):
                        if time.time() >= end_time:
                            break
                        s.sendall(data)
                        time.sleep(packet_interval)
            except (socket.timeout, socket.error) as e:
                if time.time() < end_time:
                    time.sleep(0.1)
            
            elapsed = time.time() - start_conn_time
            if elapsed < 1.0 and time.time() < end_time:
                time.sleep(1.0 - elapsed)
    
    except KeyboardInterrupt:
        pass

def simulate_network_load():
    """模拟网络密集型负载"""
    port = validate_port_input()
    packet_size_kb = validate_packet_size_input()
    packets_per_second = validate_packet_rate_input()
    duration = validate_duration_input()
    
    packet_size_bytes = packet_size_kb * 1024
    
    print(f"开始网络（TCP）负载模拟 - 端口: {port}, 包大小: {packet_size_kb}KB, 发包速率: {packets_per_second}包/秒, 持续时间: {duration}秒")
    
    # 启动服务器线程
    server_thread = threading.Thread(target=tcp_server, 
                                    args=(port, packet_size_bytes, duration))
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(0.5)  # 等待服务器启动
    
    # 启动多个客户端线程
    num_clients = min(4, packets_per_second)  # 客户端数量，最多4个
    client_threads = []
    
    for _ in range(num_clients):
        t = threading.Thread(target=tcp_client, 
                            args=(port, packet_size_bytes, packets_per_second // num_clients, duration))
        t.daemon = True
        client_threads.append(t)
        t.start()
    
    show_countdown(duration)
    
    print("网络（TCP）负载模拟完成")

if __name__ == "__main__":
    simulate_network_load()