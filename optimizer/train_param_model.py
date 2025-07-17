import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, r2_score

# === 加载数据 ===
data_path = "data/param_training_data.csv"
if not os.path.exists(data_path):
    print("❌ 找不到训练数据文件：", data_path)
    exit(1)

df = pd.read_csv(data_path)

# === 目标参数（要预测的系统参数） ===
target_cols = [
    "kernel_sched_latency_ns",
    "kernel_sched_migration_cost_ns",
    "vm_swappiness",
    "vm_dirty_ratio",
    "vm_dirty_expire_centisecs",
    "tcp_rmem_min",
    "tcp_rmem_default",
    "tcp_rmem_max"
]

# === 特征列（系统状态 + 负载类型）===
feature_cols = [
    "cpu_percent", "load_avg_1", "load_avg_5", "load_avg_15",
    "gpu_util", "gpu_mem_used", "gpu_temp", "gpu_power",
    "mem_percent", "mem_used", "swap_used", "swap_percent",
    "read_bytes", "write_bytes", "bytes_sent", "bytes_recv",
    "tcp_congestion_encoded"
]

# 加入 workload_type（OneHot 编码）
feature_cols_full = feature_cols + ["workload_type"]

# 分离特征和目标
X_raw = df[feature_cols_full]
Y = df[target_cols]

# OneHot 编码 workload_type
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), feature_cols),
        ("cat", OneHotEncoder(), ["workload_type"])
    ]
)

# 使用多输出回归模型
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42)))
])

# === 拆分训练集 & 测试集 ===
X_train, X_test, y_train, y_test = train_test_split(X_raw, Y, test_size=0.2, random_state=42)

# === 训练模型 ===
model.fit(X_train, y_train)
print("✅ 模型训练完成")

# === 保存模型 ===
joblib.dump(model, "optimizer/param_model.pkl")
print("💾 模型已保存为 optimizer/param_model.pkl")

# === 性能评估 ===
y_pred = model.predict(X_test)

# 评估每个目标的误差
mse_scores = {}
r2_scores = {}
for i, col in enumerate(target_cols):
    mse = mean_squared_error(y_test[col], y_pred[:, i])
    r2 = r2_score(y_test[col], y_pred[:, i])
    mse_scores[col] = mse
    r2_scores[col] = r2
    print(f"📊 {col} - MSE: {mse:.2f} | R²: {r2:.3f}")

# 可视化 R²
plt.figure(figsize=(10, 5))
plt.barh(target_cols, [r2_scores[c] for c in target_cols])
plt.xlabel("R² Score")
plt.title("Model Prediction Accuracy (R²)")
plt.tight_layout()
plt.savefig("optimizer/param_model_r2_scores.png")
print("📈 R² 可视化图已保存为 optimizer/param_model_r2_scores.png")

