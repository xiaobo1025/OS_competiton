import multiprocessing
import time

def validate_cores_input():
    """验证CPU核心数输入"""
    while True:
        cores = input("请输入使用的 CPU 核心数：")
        try:
            cores = int(cores)
            if cores <= 0:
                print("错误: 核心数必须大于 0")
                continue
            
            total_cores = multiprocessing.cpu_count()
            if cores > total_cores:
                print(f"警告: 请求的核心数 ({cores}) 超过系统可用核心数 ({total_cores})")
                print(f"将使用最大可用核心数: {total_cores}")
                return total_cores
            
            return cores
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

def is_prime(n):
    """判断素数的辅助函数"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def cpu_worker(duration):
    """CPU工作进程"""
    end_time = time.time() + duration
    while time.time() < end_time:
        for _ in range(1000):
            is_prime(999999999999)

def simulate_cpu_load():
    """模拟CPU密集型负载"""
    cores = validate_cores_input()
    duration = validate_duration_input()
    
    print(f"开始 CPU 负载模拟 - 核心数: {cores}, 持续时间: {duration}秒")
    
    processes = []
    for _ in range(cores):
        p = multiprocessing.Process(target=cpu_worker, args=(duration,))
        processes.append(p)
        p.start()

    # 倒计时
    for remaining in range(duration, 0, -1):
        mins, secs = divmod(remaining, 60)
        time_format = f"{mins:02d}:{secs:02d}"
        print(f"\r剩余时间: {time_format}", end='', flush=True)
        time.sleep(1)
    print("\r剩余时间: 00:00", end='', flush=True)
    print()

    for p in processes:
        p.join()
    print("CPU 负载模拟完成")

if __name__ == "__main__":
    simulate_cpu_load()