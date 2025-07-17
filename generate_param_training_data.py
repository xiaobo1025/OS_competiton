import subprocess
import time
import pandas as pd
import os
from monitor.collector import collect_all_metrics
from controller.param_applier import apply_sysctl_params
import workloads.cpu_bound as cpu_workload
import workloads.io_bound as io_workload
import workloads.memory_bound as mem_workload
import workloads.mixed as mixed_workload

from itertools import product

# 自动生成参数组合（共约 36 个）
def generate_param_grid():
    latency = [6000000, 10000000, 20000000]
    migration = [500000, 5000000]
    swap = [10, 30]
    dirty_ratio = [5, 10]
    dirty_expire = [300, 500]
    tcp_rmems = [
        "4096 87380 6291456",
        "4096 65536 4194304"
    ]
    for combo in product(latency, migration, swap, dirty_ratio, dirty_expire, tcp_rmems):
        yield {
            "kernel.sched_latency_ns": combo[0],
            "kernel.sched_migration_cost_ns": combo[1],
            "vm.swappiness": combo[2],
            "vm.dirty_ratio": combo[3],
            "vm.dirty_expire_centisecs": combo[4],
            "net.ipv4.tcp_rmem": combo[5]
        }

WORKLOADS = {
    "cpu_bound": cpu_workload.run,
    "io_bound": io_workload.run,
    "memory_bound": mem_workload.run,
    "mixed": mixed_workload.run
}

def sample_metrics(duration, interval, label, param_config):
    samples = []
    end_time = time.time() + duration
    while time.time() < end_time:
        metrics = collect_all_metrics()
        metrics["workload_type"] = label
        for k, v in param_config.items():
            key = k.replace(".", "_")
            if "tcp_rmem" in k:
                parts = v.split()
                metrics["tcp_rmem_min"] = int(parts[0])
                metrics["tcp_rmem_default"] = int(parts[1])
                metrics["tcp_rmem_max"] = int(parts[2])
            else:
                metrics[key] = int(v)
        samples.append(metrics)
        time.sleep(interval)
    return samples

def generate_training_data():
    all_data = []
    param_configs = list(generate_param_grid())
    output_path = "data/param_training_data.csv"
    os.makedirs("data", exist_ok=True)

    for workload_type, workload_func in WORKLOADS.items():
        print(f"\n💼 工作负载：{workload_type}")
        for i, param_config in enumerate(param_configs):
            print(f"⚙️ 参数组合 {i+1}/{len(param_configs)}")
            apply_sysctl_params(param_config)

            # 启动 workload（在主线程）
            try:
                print("▶ 运行负载任务...")
                from threading import Thread
                t = Thread(target=workload_func, args=(10,))
                t.start()
                samples = sample_metrics(duration=10, interval=2, label=workload_type, param_config=param_config)
                t.join()
                all_data.extend(samples)
            except Exception as e:
                print(f"❌ 负载运行异常：{e}")
                continue

            # 立即保存
            df = pd.DataFrame(all_data)
            if os.path.exists(output_path):
                df.to_csv(output_path, index=False, mode='a', header=False)
            else:
                df.to_csv(output_path, index=False)
            all_data.clear()

    print(f"\n✅ 数据采集完成，已追加至 {output_path}")

if __name__ == "__main__":
    generate_training_data()
