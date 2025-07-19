import os
import joblib
import pandas as pd
from itertools import islice

from monitor.collector import collect_all_metrics
from sysparams.collector import collect_all_sysparams
from data.generate_param_sysdata import generate_param_grid  # 如果你把该函数放那里
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

def predict_best_param(workload_type="cpu_bound", top_k=5):
    # === 加载评分模型 ===
    model_path = "optimizer/perf_model.pkl"
    if not os.path.exists(model_path):
        print("❌ 找不到模型文件：", model_path)
        return

    model = joblib.load(model_path)
    print("✅ 已加载评分模型")

    # === 采集当前系统状态 ===
    system_metrics = collect_all_metrics()
    system_metrics["workload_type"] = workload_type
    system_metrics["exec_time"] = 0   # placeholder
    system_metrics["cpu_avg"] = system_metrics.get("cpu_percent", 0)  # 用当前值代替平均

    # 提取特征列
    feature_cols = [
        "cpu_percent", "load_avg_1", "load_avg_5", "load_avg_15",
        "gpu_util", "gpu_mem_used", "gpu_temp", "gpu_power",
        "mem_percent", "mem_used", "swap_used", "swap_percent",
        "read_bytes", "write_bytes", "bytes_sent", "bytes_recv",
        "tcp_congestion_encoded", "exec_time", "cpu_avg", "workload_type"
    ]

    base_row = {col: system_metrics.get(col, 0) for col in feature_cols}
    
    # === 构造每个参数组合对应的输入样本 ===
    #param_grid = list(generate_param_grid())
    param_grid = list(islice(generate_param_grid(), 100))  # 只用前 100 组
    candidates = []

    for param in param_grid:
        row = base_row.copy()
        row.update(param)  # 这些不会被模型用到，但可以存储
        candidates.append(row)

    df = pd.DataFrame(candidates)

    # 模型中只会使用特征列
    X_input = df[feature_cols]

    # === 预测性能分数 ===
    y_pred = model.predict(X_input)
    df["predicted_perf_score"] = y_pred

    # === 排序并选出最优参数组合 ===
    df_sorted = df.sort_values(by="predicted_perf_score", ascending=False)
    top_df = df_sorted.head(top_k)

    print(f"\n🏆 Top {top_k} 参数组合推荐（按预测性能分数降序）:")
    for idx, row in top_df.iterrows():
        print(f"\n🔹 得分：{row['predicted_perf_score']:.4f}")
        print({k: row[k] for k in param_grid[0].keys()})  # 打印调优参数

    return top_df

if __name__ == "__main__":
    predict_best_param("cpu_bound", top_k=1)
