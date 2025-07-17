import threading
import time
import os

def validate_threads_input():
    """验证线程数输入"""
    while True:
        threads = input("请输入使用的线程数：")
        try:
            threads = int(threads)
            if threads <= 0:
                print("错误: 线程数必须大于 0")
                continue
            if threads > 100:
                print("警告: 线程数设置较高 (超过 100)，可能导致系统资源耗尽")
            return threads
        except ValueError:
            print("错误: 请输入有效的整数")

def validate_file_size_input():
    """验证文件大小输入"""
    while True:
        size = input("请输入每次读写的文件大小（KB）：")
        try:
            size = int(size)
            if size <= 0:
                print("错误: 文件大小必须大于 0")
                continue
            if size > 10240:  # 10MB
                print("警告: 文件大小设置较大 (超过 10MB)，可能导致内存问题")
            return size
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

def io_worker(file_path, duration, file_size_bytes):
    """IO工作线程"""
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            with open(file_path, 'w') as f:
                f.write('*' * file_size_bytes)
            with open(file_path, 'r') as f:
                f.read()
        except Exception as e:
            print(f"IO操作错误: {e}")
            break

def simulate_io_load():
    """模拟IO密集型负载"""
    threads_num = validate_threads_input()
    file_size_kb = validate_file_size_input()
    duration = validate_duration_input()
    
    file_size_bytes = file_size_kb * 1024
    file_path = "io_test.tmp"
    
    # 预先创建文件
    try:
        with open(file_path, 'w') as f:
            f.write('*' * file_size_bytes)
    except Exception as e:
        print(f"创建测试文件失败: {e}")
        return
    
    print(f"开始 IO 负载模拟 - 线程数: {threads_num}, 每次读写大小: {file_size_kb}KB, 持续时间: {duration}秒")

    threads = []
    for _ in range(threads_num):
        t = threading.Thread(target=io_worker, args=(file_path, duration, file_size_bytes))
        threads.append(t)
        t.start()

    # 倒计时
    for remaining in range(duration, 0, -1):
        mins, secs = divmod(remaining, 60)
        time_format = f"{mins:02d}:{secs:02d}"
        print(f"\r剩余时间: {time_format}", end='', flush=True)
        time.sleep(1)
    print("\r剩余时间: 00:00", end='', flush=True)
    print()

    for t in threads:
        t.join()
    
    # 删除测试文件
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"删除测试文件失败: {e}")
    
    print("IO 负载模拟完成")

if __name__ == "__main__":
    simulate_io_load()