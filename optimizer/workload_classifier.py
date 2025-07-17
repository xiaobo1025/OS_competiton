import os
import joblib
import pandas as pd

# 模型路径
MODEL_PATH = "optimizer/workload_model.pkl"

# 模型训练时的特征顺序（必须保持一致）
FEATURE_COLUMNS = [
    "cpu_percent", "load_avg_1", "load_avg_5", "load_avg_15",
    "gpu_util", "gpu_mem_used", "gpu_temp", "gpu_power",
    "mem_percent", "mem_used", "swap_used", "swap_percent",
    "read_bytes", "write_bytes", "bytes_sent", "bytes_recv",
    "tcp_congestion_encoded"
]

# 全局模型缓存
_model = None

def load_model():
    global _model
    if not os.path.exists(MODEL_PATH):
        print(f"❌ 模型文件未找到：{MODEL_PATH}")
        return None
    try:
        _model = joblib.load(MODEL_PATH)
        print("✅ 模型加载成功")
    except Exception as e:
        print(f"❌ 模型加载失败：{e}")
        _model = None

# 用于外部热重载模型
def reload_model():
    load_model()

# 初始化加载
load_model()

def predict_workload(metrics: dict) -> str:
    if _model is None:
        return "unknown"  # 模型未加载时兜底

    # 构造特征行（缺失项填 0）
    row = {feature: metrics.get(feature, 0) for feature in FEATURE_COLUMNS}
    df = pd.DataFrame([row])

    try:
        prediction = _model.predict(df)[0]
    except Exception as e:
        print(f"❌ 预测失败：{e}")
        return "unknown"

    return prediction
