import os
import joblib
import pandas as pd

# 模型路径
MODEL_PATH = "optimizer/param_model.pkl"

# 特征列（必须与训练时一致）
FEATURE_COLUMNS = [
    "cpu_percent", "load_avg_1", "load_avg_5", "load_avg_15",
    "gpu_util", "gpu_mem_used", "gpu_temp", "gpu_power",
    "mem_percent", "mem_used", "swap_used", "swap_percent",
    "read_bytes", "write_bytes", "bytes_sent", "bytes_recv",
    "tcp_congestion_encoded", "workload_type"
]

# 加载模型（一次性）
_model = None
_encoder = None

def load_model():
    global _model
    if not os.path.exists(MODEL_PATH):
        print("❌ 参数推荐模型文件不存在：", MODEL_PATH)
        return
    try:
        _model = joblib.load(MODEL_PATH)
        print("✅ 参数推荐模型加载成功")
    except Exception as e:
        print(f"❌ 模型加载失败：{e}")
        _model = None

# 初始化加载
load_model()

def recommend_params(metrics: dict) -> dict:
    """
    根据当前系统状态（metrics）推理推荐的参数组合
    """
    if _model is None:
        print("⚠️ 模型未加载，返回空参数组合")
        return {}


    # 构造输入特征行（缺失填 0，确保为 float 类型）
    row = {}
    for feature in FEATURE_COLUMNS:
        val = metrics.get(feature, 0)
        try:
            row[feature] = float(val)
        except:
            row[feature] = 0.0

    # 构造输入特征行（缺失填 0）
    row = {feature: metrics.get(feature, 0) for feature in FEATURE_COLUMNS}

    # workload_type 保留原始文本格式（如 cpu_bound）
    df = pd.DataFrame([row])

    try:
        preds = _model.predict(df)[0]
        # 解析预测值为参数字典
        param_dict = {
            "kernel.sched_latency_ns": int(preds[0]),
            "kernel.sched_migration_cost_ns": int(preds[1]),
            "vm.swappiness": int(preds[2]),
            "vm.dirty_ratio": int(preds[3]),
            "vm.dirty_expire_centisecs": int(preds[4]),
            "net.ipv4.tcp_rmem": f"{int(preds[5])} {int(preds[6])} {int(preds[7])}"
        }
        return param_dict
    except Exception as e:
        print(f"❌ 推理失败：{e}")
        return {}
