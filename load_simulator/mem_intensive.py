import time
import sys

def validate_memory_input():
    """验证内存输入"""
    while True:
        memory_mb = input("请输入要占用的内存大小（MB）：")
        try:
            memory_mb = int(memory_mb)
            if memory_mb <= 0:
                print("错误: 内存大小必须大于 0")
                continue
            
            # 获取系统总内存
            with open('/proc/meminfo') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        total_memory_kb = int(line.split()[1])
                        total_memory_mb = total_memory_kb // 1024
                        break
            
            max_allowed = total_memory_mb * 0.9
            if memory_mb > max_allowed:
                print(f"错误: 请求的内存 ({memory_mb}MB) 超过系统可用内存的 90% ({int(max_allowed)}MB)")
                continue
            
            return memory_mb
        except ValueError:
            print("错误: 请输入有效的整数")
        except Exception as e:
            print(f"验证内存输入时发生未知错误: {e}")
            return None

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

def simulate_memory_load():
    """模拟内存密集型负载"""
    memory_mb = validate_memory_input()
    if memory_mb is None:
        print("内存验证失败，退出程序")
        return
    
    duration = validate_duration_input()
    
    print(f"开始内存负载模拟 - 占用内存: {memory_mb}MB, 持续时间: {duration}秒")
    
    try:
        # 分配内存
        data = b'X' * (memory_mb * 1024 * 1024)
        
        # 倒计时
        for remaining in range(duration, 0, -1):
            mins, secs = divmod(remaining, 60)
            time_format = f"{mins:02d}:{secs:02d}"
            print(f"\r剩余时间: {time_format}", end='', flush=True)
            time.sleep(1)
        print("\r剩余时间: 00:00", end='', flush=True)
        print()
        
        # 释放内存
        del data
        print("内存负载模拟完成")
    except MemoryError:
        print("错误: 无法分配请求的内存量，可能系统内存不足")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    simulate_memory_load()