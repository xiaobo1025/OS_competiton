import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import threading

from monitor.collector import collect_all_metrics
from optimizer.workload_classifier import predict_workload
#from optimizer.param_recommender import recommend_params
from optimizer.predict_best_param import predict_best_param
from controller.param_applier import apply_sysctl_params

import workloads.cpu_bound as cpu_workload
import workloads.io_bound as io_workload
import workloads.memory_bound as mem_workload

# 页面配置
st.set_page_config(page_title="系统智能调优仪表盘", layout="wide")
st.title("🧠 基于 AI 的 Linux 系统参数调优平台")

import time
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=5000, key="auto_refresh")

# 初始化状态
MAX_HISTORY = 300
if "history" not in st.session_state:
    st.session_state.history = []
if "last_workload" not in st.session_state:
    st.session_state.last_workload = None
if "workload_running" not in st.session_state:
    st.session_state.workload_running = False
if "workload_finished_message" not in st.session_state:
    st.session_state.workload_finished_message = ""

# 实时采集 & 分类
metrics = collect_all_metrics()
workload = predict_workload(metrics)
metrics["workload_type"] = workload

# 保存历史数据
st.session_state.history.append(metrics)
if len(st.session_state.history) > MAX_HISTORY:
    st.session_state.history = st.session_state.history[-MAX_HISTORY:]

# 如果负载类型发生变化，执行智能优化
if st.session_state.last_workload != workload:
    st.markdown(f"⚙️ 检测到负载变化：**{st.session_state.last_workload} ➜ {workload}**")
    #params = recommend_params(workload)
    #params = recommend_params(metrics)

    top_df = predict_best_param(workload, top_k=1)
    if not top_df.empty:
        param_fields = [k for k in top_df.columns if k.startswith("kernel.") or k.startswith("vm.") or k.startswith("net.")]
        params = {k: top_df.iloc[0][k] for k in param_fields}
        for k, v in params.items():
            apply_sysctl_params({k: v})
            st.success(f"✅ 已应用参数：{k}={v}")
    else:
        st.warning("⚠️ 没有找到推荐参数组合")

# 系统指标面板
df = pd.DataFrame(st.session_state.history)
col1, col2, col3 = st.columns(3)
col1.metric("CPU 使用率", f"{metrics['cpu_percent']}%")
col2.metric("内存使用率", f"{metrics['mem_percent']}%")
col3.metric("识别负载", workload.upper())

st.subheader("📈 系统关键指标趋势")
st.line_chart(df[["cpu_percent", "mem_percent", "write_bytes"]])

st.subheader("📋 最近数据（最新 10 条）")
st.dataframe(df.tail(10))

# 一键优化按钮
if st.button("🚀 一键智能优化当前系统参数"):
    #params = recommend_params(workload)

    top_df = predict_best_param(workload, top_k=1)
    if not top_df.empty:
        param_fields = [k for k in top_df.columns if k.startswith("kernel.") or k.startswith("vm.") or k.startswith("net.")]
        params = {k: top_df.iloc[0][k] for k in param_fields}
        apply_sysctl_params(params)
        st.success(f"✅ 已根据 {workload} 类型应用参数：{params}")
    else:
        st.warning("⚠️ 没有找到推荐参数组合")

# 📥 下载
st.download_button("📥 下载完整监控日志", data=df.to_csv(index=False), file_name="system_monitor_log.csv")

# 🧪 模拟负载（侧边栏）
st.sidebar.title("🧪 模拟工作负载")
selected = st.sidebar.selectbox("选择负载类型", ["不运行", "CPU 密集型", "IO 密集型", "内存密集型"])
duration = st.sidebar.slider("运行时长（秒）", 5, 60, 10)

# 如果选择了负载并点击运行按钮
if st.sidebar.button("▶️ 启动负载任务"):
    if selected == "不运行":
        st.sidebar.warning("⚠️ 请先选择一种要运行的工作负载任务")
    elif st.session_state.workload_running:
        st.sidebar.warning(f"⚙️ 当前已有负载正在运行，请等待其完成")
    else:
        st.session_state.workload_running = True
        st.sidebar.success(f"⏳ 正在运行 {selected} 任务...")

        def run_workload():
            if selected == "CPU 密集型":
                cpu_workload.run(duration)
            elif selected == "IO 密集型":
                io_workload.run(duration)
            elif selected == "内存密集型":
                mem_workload.run(duration)

            st.session_state.workload_running = False
            st.session_state.workload_finished_message = f"✅ {selected} 任务已完成 🎉"

        threading.Thread(target=run_workload).start()

# 在任务结束后，主线程显示成功提示
if st.session_state.workload_finished_message:
    st.sidebar.success(st.session_state.workload_finished_message)
    st.session_state.workload_finished_message = ""

# 🛠 自定义参数设置
with st.expander("🛠 自定义参数调节"):
    custom_param = st.text_input("sysctl 参数名（如 vm.swappiness）")
    custom_value = st.text_input("设置值（如 10）")
    if st.button("应用参数"):
        try:
            apply_sysctl_params({custom_param: custom_value})
            st.success(f"✅ 已应用 {custom_param}={custom_value}")
        except:
            st.error("❌ 应用失败，请检查参数名和值是否正确")
