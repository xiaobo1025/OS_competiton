import threading
import time
import os
import random

def validate_file_size_input():
    """验证文件大小输入"""
    while True:
        size = input("请输入每个文件的大小（MB）：")
        try:
            size = int(size)
            if size <= 0:
                print("错误: 文件大小必须大于 0")
                continue
            if size > 1024:  # 1GB
                print("警告: 文件大小设置较大 (超过 1GB)，可能导致磁盘空间不足")
            return size
        except ValueError:
            print("错误: 请输入有效的整数")

def validate_threads_input(prompt, max_value=None):
    """通用线程数验证函数"""
    while True:
        threads = input(prompt)
        try:
            threads = int(threads)
            if threads <= 0:
                print("错误: 线程数必须大于 0")
                continue
            if max_value and threads > max_value:
                print(f"错误: 线程数不能超过 {max_value}")
                continue
            return threads
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

def disk_write_worker(file_dir, file_size_mb, duration):
    """磁盘写工作线程"""
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            file_name = os.path.join(file_dir, f"disk_test_{random.randint(1, 10000)}.tmp")
            with open(file_name, 'w') as f:
                f.write('*' * (file_size_mb * 1024 * 1024))
        except Exception as e:
            if time.time() < end_time:  # 只在未超时的情况下打印错误
                print(f"写操作错误: {e}")

def disk_read_worker(file_dir, duration):
    """磁盘读工作线程"""
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            files = [f for f in os.listdir(file_dir) if f.startswith("disk_test_")]
            if not files:
                time.sleep(1)  # 没有文件可读取，等待
                continue
                
            file_name = os.path.join(file_dir, random.choice(files))
            with open(file_name, 'r') as f:
                f.read()
        except Exception as e:
            if time.time() < end_time:  # 只在未超时的情况下打印错误
                print(f"读操作错误: {e}")

def simulate_disk_load():
    """模拟磁盘密集型负载"""
    file_size_mb = validate_file_size_input()
    write_threads = validate_threads_input("请输入写操作线程数：")
    read_threads = validate_threads_input("请输入读操作线程数：")
    duration = validate_duration_input()
    
    file_dir = "disk_test_dir"
    if not os.path.exists(file_dir):
        try:
            os.makedirs(file_dir)
        except Exception as e:
            print(f"创建测试目录失败: {e}")
            return
    
    print(f"开始磁盘负载模拟 - 每个文件大小: {file_size_mb}MB, 写线程数: {write_threads}, 读线程数: {read_threads}, 持续时间: {duration}秒")

    # 启动写线程
    write_thread_list = []
    for _ in range(write_threads):
        t = threading.Thread(target=disk_write_worker, args=(file_dir, file_size_mb, duration))
        write_thread_list.append(t)
        t.start()

    # 等待一会儿让写线程先创建些文件
    time.sleep(2)

    # 启动读线程
    read_thread_list = []
    for _ in range(read_threads):
        t = threading.Thread(target=disk_read_worker, args=(file_dir, duration))
        read_thread_list.append(t)
        t.start()

    # 倒计时
    for remaining in range(duration, 0, -1):
        mins, secs = divmod(remaining, 60)
        time_format = f"{mins:02d}:{secs:02d}"
        print(f"\r剩余时间: {time_format}", end='', flush=True)
        time.sleep(1)
    print("\r剩余时间: 00:00", end='', flush=True)
    print()

    for t in write_thread_list:
        t.join()
    for t in read_thread_list:
        t.join()

    # 清理文件
    try:
        for f in os.listdir(file_dir):
            if f.startswith("disk_test_"):
                os.remove(os.path.join(file_dir, f))
        os.rmdir(file_dir)
    except Exception as e:
        print(f"清理测试文件失败: {e}")
    
    print("磁盘负载模拟完成")

if __name__ == "__main__":
    simulate_disk_load()