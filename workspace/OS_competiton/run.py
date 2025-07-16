'''
import pandas as pd
import time
from monitor.collector import collect_all_metrics

if __name__ == "__main__":
    all_data = []
    print("🔍 正在开始系统状态采集，按 Ctrl+C 停止...")
    try:
        while True:
            metrics = collect_all_metrics()
            print(f"[{metrics['timestamp']}] 收集成功：{metrics['cpu_percent']}% CPU, {metrics['gpu_util']}% GPU")
            all_data.append(metrics)
            time.sleep(5)
    except KeyboardInterrupt:
        print("⛔ 停止采集，正在保存数据...")
        df = pd.DataFrame(all_data)
        df.to_csv("system_metrics_log.csv", index=False)
        print("✅ 已保存到 system_metrics_log.csv")
'''

import pandas as pd
import time
from monitor.collector import collect_all_metrics
from optimizer.workload_classifier import predict_workload
from optimizer.param_recommender import recommend_params
from controller.param_applier import apply_sysctl_params

if __name__ == "__main__":
    all_data = []
    last_workload = None  # 用于追踪变化
    last_disk_io = (0, 0)  # 上一次磁盘IO值: (read_bytes, write_bytes)
    print("🔍 正在启动系统监控与智能调优，按 Ctrl+C 停止...")

    try:
        while True:
            # Step 1: 实时采集系统指标
            metrics = collect_all_metrics()
            
            # 计算磁盘IO增量
            current_read = metrics.get('read_bytes', 0)
            current_write = metrics.get('write_bytes', 0)
            delta_read = current_read - last_disk_io[0]
            delta_write = current_write - last_disk_io[1]
            last_disk_io = (current_read, current_write)
            
            # 将增量添加到metrics中
            metrics['delta_read_bytes'] = delta_read
            metrics['delta_write_bytes'] = delta_write

            # Step 2: 利用模型判断当前 workload 类型
            workload = predict_workload(metrics)
            metrics["workload_type"] = workload

            # Step 3: 如果负载类型发生变化 → 自动调优
            if workload != last_workload:
                print(f"\n⚙️ 检测到负载变化：{last_workload} ➜ {workload}")
                params = recommend_params(workload)
                if params:
                    print(f"🚀 推荐参数：{params}")
                    apply_sysctl_params(params)
                else:
                    print("ℹ️ 当前不建议修改系统参数")
                last_workload = workload

            # Step 4: 打印简要信息（使用增量值）
            print(
                f"[{metrics['timestamp']}] {workload.upper()} "
                f"| CPU: {metrics['cpu_percent']}% "
                f"| MEM: {metrics['mem_percent']}% "
                # 使用增量值并转换为MB显示（保留两位小数）
                f"| DISK: READ {delta_read/(1024**2):.2f}M/WRITE {delta_write/(1024**2):.2f}M "
                # 网络流量保持不变（如需增量需类似处理）
                f"| NET: REC {metrics.get('bytes_recv', 0)//1024}K/SENT {metrics.get('bytes_sent', 0)//1024}K "
                f"| FILES: {metrics.get('total_open_files', 0)} "
            )

            all_data.append(metrics)
            time.sleep(5)

    except KeyboardInterrupt:
        print("⛔ 用户终止，正在保存监控日志...")
        df = pd.DataFrame(all_data)
        df.to_csv("system_metrics_log_with_workload.csv", index=False)
        print("✅ 日志已保存到 system_metrics_log_with_workload.csv")


