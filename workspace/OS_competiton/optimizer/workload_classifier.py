'''
import joblib
import numpy as np
import pandas as pd

model = joblib.load("optimizer/workload_model.pkl")

def predict_workload(metrics: dict) -> str:
    df = pd.DataFrame([{
        "cpu_percent": metrics["cpu_percent"],
        "write_bytes": metrics["write_bytes"],
        "mem_percent": metrics["mem_percent"]
    }])
    return model.predict(df)[0]
'''

import joblib
import pandas as pd

# 加载模型
model = joblib.load("optimizer/workload_model.pkl")

# 模型训练时使用的完整特征列表（必须保持一致）
FEATURE_COLUMNS = [
    "cpu_percent", "load_avg_1", "load_avg_5", "load_avg_15",
    "gpu_util", "gpu_mem_used", "gpu_temp", "gpu_power",
    "mem_percent", "mem_used", "swap_used", "swap_percent",
    "read_bytes", "write_bytes", "bytes_sent", "bytes_recv", "tcp_congestion_encoded"
]

def predict_workload(metrics: dict) -> str:
    # 构造带完整特征的数据行
    row = {feature: metrics.get(feature, 0) for feature in FEATURE_COLUMNS}
    df = pd.DataFrame([row])
    return model.predict(df)[0]
