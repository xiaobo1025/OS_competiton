import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, r2_score

# === 加载数据 ===
data_path = "data/sysparam_training_data.csv"
if not os.path.exists(data_path):
    print("❌ 找不到训练数据文件：", data_path)
    exit(1)

df = pd.read_csv(data_path)

# === 目标列（评分指标）===
target_col = "perf_score"

# === 输入特征列 ===
feature_cols = [
    "cpu_percent", "load_avg_1", "load_avg_5", "load_avg_15",
    "gpu_util", "gpu_mem_used", "gpu_temp", "gpu_power",
    "mem_percent", "mem_used", "swap_used", "swap_percent",
    "read_bytes", "write_bytes", "bytes_sent", "bytes_recv",
    "tcp_congestion_encoded", "exec_time", "cpu_avg"
]

feature_cols_full = feature_cols + ["workload_type"]

# === 拆分特征 & 目标 ===
X_raw = df[feature_cols_full]
y = df[target_col]

# === 特征预处理 ===
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), feature_cols),
        ("cat", OneHotEncoder(), ["workload_type"])
    ]
)

# === 回归模型（单输出）===
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
])

# === 拆分训练集 & 测试集 ===
X_train, X_test, y_train, y_test = train_test_split(
    X_raw, y, test_size=0.2, random_state=42
)

# === 模型训练 ===
model.fit(X_train, y_train)
print("✅ 模型训练完成")

# === 保存模型 ===
os.makedirs("optimizer", exist_ok=True)
joblib.dump(model, "optimizer/perf_model.pkl")
print("💾 模型已保存为 optimizer/perf_model.pkl")

# === 性能评估 ===
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"\n📊 perf_score - MSE: {mse:.4f} | R²: {r2:.4f}")

# === 可视化实际 vs 预测 ===
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.6)
plt.xlabel("Actual perf_score")
plt.ylabel("Predicted perf_score")
plt.title("Actual vs Predicted Performance Score")
plt.grid(True)
plt.tight_layout()
plt.savefig("optimizer/perf_model_prediction.png")
print("📈 可视化图已保存：optimizer/perf_model_prediction.png")
