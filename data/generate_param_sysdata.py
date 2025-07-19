import os
import time
import subprocess
import pandas as pd
from itertools import islice

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
    # kernel params
    sched_latency_ns = [16000000, 24000000, 32000000]
    sched_migration_cost_ns = [250000, 500000, 750000]
    sched_wakeup_granularity_ns = [2000000, 4000000, 6000000]
    sched_min_granularity_ns = [1500000, 3000000, 4500000]
    sched_child_runs_first = [0, 1]
    sched_autogroup_enabled = [0, 1]
    sched_rr_timeslice_ms = [50, 100, 150]
    # vm params
    swappiness = [30, 60, 90]
    dirty_ratio = [5, 10, 15]
    dirty_background_ratio = [3, 5, 7]
    dirty_expire_centisecs = [1500, 3000, 4500]
    dirty_writeback_centisecs = [250, 500, 750]
    min_free_kbytes = [int(90112 * 0.5), 90112, int(90112 * 1.5)]
    overcommit_memory = [0, 1, 2]
    overcommit_ratio = [25, 50, 75]
    vfs_cache_pressure = [100, 200, 300]

    # net params
    somaxconn = [2048, 4096, 8192]
    tcp_fin_timeout = [30, 60, 90]
    tcp_tw_reuse = [0, 1, 2]
    tcp_syncookies = [0, 1]
    tcp_max_syn_backlog = [2048, 4096, 8192]
    tcp_rmems = [
        "4096 65536 2097152",
        "4096 131072 6291456",
        "8192 262144 8388608"
    ]
    tcp_wmems = [
        "4096 8192 2097152",
        "4096 16384 4194304",
        "8192 32768 8388608"
    ]
     
    for combo in product(
        sched_latency_ns, sched_migration_cost_ns, sched_wakeup_granularity_ns,
        sched_min_granularity_ns, sched_child_runs_first, sched_autogroup_enabled,
        sched_rr_timeslice_ms,
        swappiness, dirty_ratio, dirty_background_ratio,
        dirty_expire_centisecs, dirty_writeback_centisecs, min_free_kbytes,
        overcommit_memory, overcommit_ratio, vfs_cache_pressure,
        somaxconn, tcp_fin_timeout, tcp_tw_reuse, tcp_syncookies, tcp_max_syn_backlog,
        tcp_rmems, tcp_wmems
    ):
        yield {
            "kernel.sched_latency_ns": combo[0],
            "kernel.sched_migration_cost_ns": combo[1],
            "kernel.sched_wakeup_granularity_ns": combo[2],
            "kernel.sched_min_granularity_ns": combo[3],
            "kernel.sched_child_runs_first": combo[4],
            "kernel.sched_autogroup_enabled": combo[5],
            "kernel.sched_rr_timeslice_ms": combo[6],

            "vm.swappiness": combo[7],
            "vm.dirty_ratio": combo[8],
            "vm.dirty_background_ratio": combo[9],
            "vm.dirty_expire_centisecs": combo[10],
            "vm.dirty_writeback_centisecs": combo[11],
            "vm.min_free_kbytes": combo[12],
            "vm.overcommit_memory": combo[13],
            "vm.overcommit_ratio": combo[14],
            "vm.vfs_cache_pressure": combo[15],

            "net.core.somaxconn": combo[16],
            "net.ipv4.tcp_fin_timeout": combo[17],
            "net.ipv4.tcp_tw_reuse": combo[18],
            "net.ipv4.tcp_syncookies": combo[19],
            "net.ipv4.tcp_max_syn_backlog": combo[20],
            "net.ipv4.tcp_rmem": combo[21],
            "net.ipv4.tcp_wmem": combo[22],

        }

WORKLOADS = {
    "cpu_bound": cpu_workload.run,
    "io_bound": io_workload.run,
    "memory_bound": mem_workload.run,
    "mixed": mixed_workload.run
}

def sample_metrics(duration, interval, workload_label):
    samples = []
    start_time = time.time()
    end_time = start_time + duration

    cpu_usages = []

    while time.time() < end_time:
        runtime_metrics = collect_all_metrics()
        sysparams = collect_all_sysparams()
        combined = {**runtime_metrics, **sysparams}
        combined["workload_type"] = workload_label

        # 收集性能指标
        cpu_usages.append(runtime_metrics.get("cpu_percent", 0))

        samples.append(combined)
        time.sleep(interval)

    # 计算性能指标
    exec_time = time.time() - start_time
    cpu_avg = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0

    #print(cpu_avg)

    for row in samples:
        row["exec_time"] = round(exec_time, 2)
        row["cpu_avg"] = round(cpu_avg, 2)
        try:
            row["perf_score"] = round(
                0.6 * (1 / exec_time) +
                0.4 * (cpu_avg / 100.0), 2
            )
        except ZeroDivisionError:
            row["perf_score"] = 0.0

    return samples


def generate_sysparam_training_data():
    output_path = "data/sysparam_training_data.csv"
    os.makedirs("data", exist_ok=True)
    param_list = list(islice(generate_param_grid(), 100))  # 限制最多 100 组
    all_data = []

    for workload_type, workload_func in WORKLOADS.items():
        print(f"\n💼 工作负载：{workload_type}")
        for i, param_config in enumerate(param_list):
            print(f"⚙️ 应用参数组合 {i+1}/{len(param_list)}")
            apply_sysctl_params(param_config)

            try:
                print("▶ 运行负载任务...")
                from threading import Thread
                t = Thread(target=workload_func, args=(10,))
                t.start()
                samples = sample_metrics(duration=10, interval=2, workload_label=workload_type)
                t.join()
                all_data.extend(samples)
            except Exception as e:
                print(f"❌ 运行失败：{e}")
                continue

            # 保存阶段性数据
            df = pd.DataFrame(all_data)
            if os.path.exists(output_path):
                df.to_csv(output_path, mode="a", index=False, header=False)
            else:
                df.to_csv(output_path, index=False)
            all_data.clear()

    print(f"\n✅ 数据采集完成，结果保存至 {output_path}")

if __name__ == "__main__":
    generate_sysparam_training_data()