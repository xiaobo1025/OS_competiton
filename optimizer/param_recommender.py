"""
param_recommender.py
根据 workload 类型，返回推荐的 sysctl 调优参数字典。
"""
'''
def recommend_params(workload_type: str) -> dict:
    """
    根据 workload 类型返回推荐的 sysctl 参数组合。
    可用于 echo/set_sysctl 等方式动态调优。

    Args:
        workload_type (str): 当前识别的负载类型

    Returns:
        dict: 推荐的参数键值对
    """

    PARAMS_BY_WORKLOAD = {
        "cpu_bound": {
            # 增加迁移开销，降低频繁调度
            "kernel.sched_migration_cost_ns": "5000000",   # 默认 500000 (ns)
            "kernel.sched_latency_ns": "10000000"          # 默认 6000000 (ns)
        },
        "io_bound": {
            # 提高 dirty page 写出频率
            "vm.dirty_ratio": "10",                        # 脏页占比触发写回阈值
            "vm.dirty_background_ratio": "5",              # 后台写回开始阈值
            "vm.dirty_expire_centisecs": "500"             # 脏页过期时间
        },
        "memory_bound": {
            # 减少内存交换倾向
            "vm.swappiness": "10",                         # 倾向于不使用 swap
            "vm.min_free_kbytes": "65536"                  # 保留更多空闲内存
        },
        "mixed": {
            # 综合调优策略
            "kernel.sched_latency_ns": "20000000",         # 拉长调度周期
            "vm.swappiness": "30"                          # 允许适度 swap
        }
    }

    return PARAMS_BY_WORKLOAD.get(workload_type.lower(), {})  # 默认为空字典
'''
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
