import streamlit as st
import pandas as pd
import time
from monitor.collector import collect_all_metrics
from optimizer.workload_classifier import predict_workload
from optimizer.param_recommender import recommend_params
from controller.param_applier import apply_sysctl_params

# 初始化
st.set_page_config(page_title="系统智能调优仪表盘", layout="wide")
st.title("🧠 基于 AI 的 Linux 系统参数调优平台")

# 缓存数据历史
if "history" not in st.session_state:
    st.session_state.history = []

# 实时采集
metrics = collect_all_metrics()
workload = predict_workload(metrics)
metrics["workload_type"] = workload
st.session_state.history.append(metrics)

# 数据展示
df = pd.DataFrame(st.session_state.history[-30:])  # 只保留最新30条
col1, col2, col3 = st.columns(3)
col1.metric("CPU 使用率", f"{metrics['cpu_percent']}%")
col2.metric("内存使用率", f"{metrics['mem_percent']}%")
col3.metric("识别负载类型", workload.upper())

st.line_chart(df[["cpu_percent", "mem_percent"]])
st.dataframe(df.tail(10))

# 一键智能调优按钮
if st.button("🚀 一键智能优化当前系统参数"):
    params = recommend_params(workload)
    apply_sysctl_params(params)
    st.success(f"✅ 已根据 {workload} 类型推荐并应用参数：{params}")

# 参数自定义调节区
with st.expander("🛠 自定义参数调节"):
    custom_param = st.text_input("sysctl 参数名（如 vm.swappiness）")
    custom_value = st.text_input("设置值（如 10）")
    if st.button("应用参数"):
        try:
            apply_sysctl_params({custom_param: custom_value})
            st.success(f"✅ 已应用 {custom_param}={custom_value}")
        except:
            st.error("❌ 应用失败，请检查参数名和值是否正确")

# 下载数据
st.download_button("📥 下载历史监控日志", data=df.to_csv(index=False), file_name="system_monitor_log.csv")

