import subprocess
import time
import pandas as pd
from monitor.collector import collect_all_metrics

def run_stress_cpu(duration=10):
    return subprocess.Popen(['stress', '--cpu', '4', '--timeout', str(duration)])

def run_stress_mem(duration=10):
    return subprocess.Popen(['stress', '--vm', '2', '--vm-bytes', '1G', '--timeout', str(duration)])

def run_stress_io(filename="tempfile", duration=10):
    return subprocess.Popen(['dd', 'if=/dev/zero', f'of={filename}', 'bs=1M', 'count=1024'])

def sample_metrics(label, duration=10, interval=2):
    data = []
    print(f"▶ 正在运行负载：{label}")
    end_time = time.time() + duration
    while time.time() < end_time:
        metrics = collect_all_metrics()
        metrics['workload_type'] = label
        data.append(metrics)
        time.sleep(interval)
    return data

def generate_all():
    all_data = []

    # CPU Bound
    cpu_proc = run_stress_cpu()
    all_data += sample_metrics("cpu_bound", duration=10)
    cpu_proc.wait()

    # IO Bound
    io_proc = run_stress_io()
    all_data += sample_metrics("io_bound", duration=10)
    io_proc.terminate()

    # Memory Bound
    mem_proc = run_stress_mem()
    all_data += sample_metrics("memory_bound", duration=10)
    mem_proc.wait()

    # Mixed
    cpu_proc = run_stress_cpu()
    mem_proc = run_stress_mem()
    all_data += sample_metrics("mixed", duration=10)
    cpu_proc.wait()
    mem_proc.wait()

    # 保存结果
    df = pd.DataFrame(all_data)
    df.to_csv("data/workload_training_data.csv", index=False)
    print("✅ 所有负载数据采集完成，已保存为 data/workload_training_data.csv")

if __name__ == "__main__":
    generate_all()

