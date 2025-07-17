import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, confusion_matrix, ConfusionMatrixDisplay,
    classification_report
)
from sklearn.preprocessing import LabelEncoder

# 1. 加载数据
data_path = "data/workload_training_data.csv"
if not os.path.exists(data_path):
    print("❌ 数据文件不存在，请确认路径为 data/workload_training_data.csv")
    exit(1)

df = pd.read_csv(data_path)

# 2. 编码字符串类型特征（如 TCP 拥塞算法）
if 'tcp_congestion_control' in df.columns:
    le = LabelEncoder()
    df['tcp_congestion_encoded'] = le.fit_transform(df['tcp_congestion_control'])

# 3. 特征选择（CPU/GPU/内存/I/O/网络等）
features = [
    "cpu_percent", "load_avg_1", "load_avg_5", "load_avg_15",
    "gpu_util", "gpu_mem_used", "gpu_temp", "gpu_power",
    "mem_percent", "mem_used", "swap_used", "swap_percent",
    "read_bytes", "write_bytes", "bytes_sent", "bytes_recv"
]
if "tcp_congestion_encoded" in df.columns:
    features.append("tcp_congestion_encoded")

X = df[features]
y = df["workload_type"]

# 4. 数据集划分
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. 模型训练
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. 模型评估
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\n🎯 模型准确率：{acc:.4f}\n")

# 7. 分类报告输出
report = classification_report(y_test, y_pred, digits=3)
print("📋 分类报告：\n")
print(report)

# 8. 混淆矩阵保存
labels = ["cpu_bound", "io_bound", "memory_bound", "mixed"]
cm = confusion_matrix(y_test, y_pred, labels=labels)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix")
plt.savefig("optimizer/model_confusion_matrix.png")
print("📊 混淆矩阵已保存：optimizer/model_confusion_matrix.png")

# 9. 特征重要性图保存
plt.figure(figsize=(10, 6))
importance = pd.Series(model.feature_importances_, index=features)
importance.sort_values().plot(kind='barh')
plt.title("Feature Importance")
plt.tight_layout()
plt.savefig("optimizer/feature_importance.png")
print("📈 特征重要性图已保存：optimizer/feature_importance.png")

# 10. 保存模型
model_path = "optimizer/workload_model.pkl"
joblib.dump(model, model_path)
print(f"✅ 模型训练完成，已保存至 {model_path}")

# 11. 保存训练日志
with open("optimizer/train_log.txt", "w") as f:
    f.write("🌟 模型训练日志\n")
    f.write(f"模型类型：RandomForestClassifier(n_estimators=100)\n")
    f.write(f"准确率：{acc:.4f}\n\n")
    f.write("使用特征：\n" + "\n".join(features) + "\n\n")
    f.write("分类报告：\n" + report)

print("📝 日志已保存：optimizer/train_log.txt")
