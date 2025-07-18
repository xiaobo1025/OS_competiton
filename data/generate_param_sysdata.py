import os
import time
import pandas as pd
import subprocess
from threading import Thread

from monitor.collector import collect_all_metrics
from sysparams.collector import collect_all_sysparams
from controller.param_applier import apply_sysctl_params

import workloads.cpu_bound as cpu_workload
import workloads.io_bound as io_workload
import workloads.memory_bound as mem_workload
import workloads.mixed as mixed_workload

from itertools import product

# ✅ 参数组合空间（系统可调参数）
def generate_param_grid():
    latency = [6000000]
    migration = [500000]
    swap = [10, 30]
    dirty_ratio = [5]
    dirty_expire = [300]
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

# ✅ 工作负载类型
WORKLOADS = {
    "cpu_bound": cpu_workload.run,
    "io_bound": io_workload.run,
    "memory_bound": mem_workload.run,
    "mixed": mixed_workload.run
}

# ✅ 采样函数：收集系统参数 + 性能监控数据
def sample_metrics(duration, interval, workload_label):
    samples = []
    end_time = time.time() + duration
    while time.time() < end_time:
        metrics = collect_all_metrics()          # 性能数据
        sysparams = collect_all_sysparams()      # 当前系统参数
        row = {**metrics, **sysparams}
        row["workload_type"] = workload_label
        samples.append(row)
        time.sleep(interval)
    return samples

# ✅ 主逻辑
def generate_training_data():
    output_path = "data/sysparam_training_data.csv"
    os.makedirs("data", exist_ok=True)
    param_configs = list(generate_param_grid())

    for workload_label, workload_func in WORKLOADS.items():
        print(f"\n💼 工作负载：{workload_label}")
        for i, param_config in enumerate(param_configs):
            print(f"⚙️ 参数组合 {i+1}/{len(param_configs)}")
            apply_sysctl_params(param_config)

            try:
                print("▶ 启动工作负载...")
                t = Thread(target=workload_func, args=(10,))
                t.start()

                samples = sample_metrics(duration=2, interval=2, workload_label=workload_label)
                t.join()

                df = pd.DataFrame(samples)
                if os.path.exists(output_path):
                    df.to_csv(output_path, mode='a', index=False, header=False)
                else:
                    df.to_csv(output_path, index=False)

            except Exception as e:
                print(f"❌ 出错：{e}")
                continue

    print(f"\n✅ 所有采样完成，结果保存至：{output_path}")

if __name__ == "__main__":
    generate_training_data()

