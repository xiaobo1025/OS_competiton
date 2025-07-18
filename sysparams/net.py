import os

# -------- 核心工具函数 --------
def read_net_param(path):
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except:
        return "N/A"

# -------- core 参数采集 --------
def get_net_core_params():
    base_path = "/proc/sys/net/core/"
    params = {
        "somaxconn": read_net_param(base_path + "somaxconn")
    }
    return params

# -------- ipv4 参数采集 --------
def get_net_ipv4_params():
    base_path = "/proc/sys/net/ipv4/"
    params = {
        "tcp_congestion_control": read_net_param(base_path + "tcp_congestion_control"),
        "tcp_fin_timeout": read_net_param(base_path + "tcp_fin_timeout"),
        "tcp_tw_reuse": read_net_param(base_path + "tcp_tw_reuse"),
        "tcp_syncookies": read_net_param(base_path + "tcp_syncookies"),
        "tcp_max_syn_backlog": read_net_param(base_path + "tcp_max_syn_backlog"),
        "tcp_rmem": read_net_param(base_path + "tcp_rmem"),  # 3 个值：min, default, max
        "tcp_wmem": read_net_param(base_path + "tcp_wmem")
    }
    return params

# -------- 合并获取所有网络参数 --------
def get_all_net_params():
    params = {}
    params.update(get_net_core_params())
    params.update(get_net_ipv4_params())
    return params

# -------- 调试运行 --------
if __name__ == "__main__":
    import json
    all_params = get_all_net_params()
    print(json.dumps(all_params, indent=2))
