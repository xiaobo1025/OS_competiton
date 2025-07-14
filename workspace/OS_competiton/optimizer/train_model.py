'''
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# 文件路径
data_path = "data/workload_training_data.csv"

if not os.path.exists(data_path):
    print("❌ 数据文件不存在，请确认路径为 data/workload_training_data.csv")
    exit(1)

# 读取数据
df = pd.read_csv(data_path)

# 选择特征列（可以按需调整）
features = ["cpu_percent", "write_bytes", "mem_percent"]
X = df[features]
y = df["workload_type"]

# 训练模型
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 保存模型
model_path = "optimizer/workload_model.pkl"
joblib.dump(model, model_path)
print(f"✅ 模型训练完成，已保存至 {model_path}")
'''

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 文件路径
data_path = "data/workload_training_data.csv"

if not os.path.exists(data_path):
    print("❌ 数据文件不存在，请确认路径为 data/workload_training_data.csv")
    exit(1)

df = pd.read_csv(data_path)

# 转换字符串列（如有）
if 'tcp_congestion_control' in df.columns:
    le = LabelEncoder()
    df['tcp_congestion_encoded'] = le.fit_transform(df['tcp_congestion_control'])

# 选择特征列（更全面）
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

# 数据集划分
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 模型训练
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 模型评估
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"🎯 模型准确率：{acc:.4f}")

# 混淆矩阵显示与保存
cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix")
plt.savefig("optimizer/model_confusion_matrix.png")
print("📊 混淆矩阵已保存：optimizer/model_confusion_matrix.png")

# 特征重要性图
plt.figure(figsize=(10, 6))
importance = pd.Series(model.feature_importances_, index=features)
importance.sort_values().plot(kind='barh')
plt.title("Feature Importance")
plt.tight_layout()
plt.savefig("optimizer/feature_importance.png")
print("📈 特征重要性图已保存：optimizer/feature_importance.png")

# 保存模型
model_path = "optimizer/workload_model.pkl"
joblib.dump(model, model_path)
print(f"✅ 模型训练完成，已保存至 {model_path}")
