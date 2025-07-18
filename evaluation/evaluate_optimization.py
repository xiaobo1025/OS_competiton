import sys
import os
import time
import importlib
import pandas as pd
import matplotlib.pyplot as plt
from threading import Thread

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from monitor.collector import collect_all_metrics
from optimizer.param_recommender import recommend_params
from controller.param_applier import apply_sysctl_params

# 配置
SAMPLE_INTERVAL = 1
SAMPLE_DURATION = 10  # 秒
OUTPUT_DIR = "evaluation"
SUPPORTED_WORKLOADS = ["cpu_bound", "io_bound", "memory_bound", "mixed"]

def sample_metrics_during_workload(tag, workload_func):
    data = []
    end_time = time.time() + SAMPLE_DURATION

    t = Thread(target=workload_func, args=(SAMPLE_DURATION,))
    t.start()

    while time.time() < end_time:
        metrics = collect_all_metrics()
        metrics["phase"] = tag
        data.append(metrics)
        time.sleep(SAMPLE_INTERVAL)

    t.join()
    return pd.DataFrame(data)

def main():
    if len(sys.argv) < 2:
        print("❌ 请指定负载类型，如：python3 evaluate_optimization.py cpu_bound")
        return

    workload_type = sys.argv[1]
    if workload_type not in SUPPORTED_WORKLOADS:
        print(f"❌ 不支持的负载类型：{workload_type}")
        print("✅ 支持：cpu_bound, io_bound, memory_bound, mixed")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 动态导入 workload
    workload_module = importlib.import_module(f"workloads.{workload_type}")

    print(f"\n📊 阶段 1：采集优化前性能数据（{workload_type}）...")
    df_before = sample_metrics_during_workload("before", workload_module.run)

    print("\n⚙️ 阶段 2：应用 AI 推荐参数...")
    metrics = collect_all_metrics()
    metrics["workload_type"] = workload_type
    param_dict = recommend_params(metrics)
    apply_sysctl_params(param_dict)

    print(f"\n📊 阶段 3：采集优化后性能数据（{workload_type}）...")
    df_after = sample_metrics_during_workload("after", workload_module.run)

    print("\n💾 正在保存数据和图表...")
    df_all = pd.concat([df_before, df_after], ignore_index=True)
    csv_path = f"{OUTPUT_DIR}/{workload_type}_eval_data.csv"
    df_all.to_csv(csv_path, index=False)

    # 性能提升评估
    print("\n📈 性能提升评估：")
    for metric in ["cpu_percent", "mem_percent", "write_bytes"]:
        before_avg = df_before[metric].mean()
        after_avg = df_after[metric].mean()
        unit = "%" if "percent" in metric else ("MB/s" if "bytes" in metric else "")

        if "bytes" in metric:
            before_avg /= 1024 ** 2
            after_avg /= 1024 ** 2

        delta = after_avg - before_avg
        pct = (delta / before_avg) * 100 if before_avg != 0 else float("inf")
        symbol = "提升" if pct >= 0 else "下降"

        print(f"- {metric}：{before_avg:.2f}{unit} ➜ {after_avg:.2f}{unit}（{symbol} {pct:+.1f}%）")

    # 绘图
    plt.figure(figsize=(12, 6))
    for metric in ["cpu_percent", "mem_percent", "write_bytes"]:
        plt.plot(df_all["timestamp"], df_all[metric], label=metric)
    plt.xticks(rotation=45)
    plt.title(f"{workload_type.upper()} Performance Comparison (Before vs After Tuning)")
    plt.xlabel("Timestamp")
    plt.ylabel("System Metric Value")
    plt.legend()
    plt.tight_layout()
    img_path = f"{OUTPUT_DIR}/{workload_type}_eval_plot.png"
    plt.savefig(img_path)

    print(f"✅ 图表已保存：{img_path}")
    print(f"✅ 数据已保存：{csv_path}")

if __name__ == "__main__":
    main()
