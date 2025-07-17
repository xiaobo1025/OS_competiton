'''
import psutil

def get_cpu_info():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "load_avg_1": psutil.getloadavg()[0],
        "load_avg_5": psutil.getloadavg()[1],
        "load_avg_15": psutil.getloadavg()[2]
    }
'''

import psutil
import os
import glob

def get_cpu_info():
    """获取完整的CPU监测信息，包括调度策略、亲和性和CFS参数"""
    data = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "load_avg_1": psutil.getloadavg()[0],
        "load_avg_5": psutil.getloadavg()[1],
        "load_avg_15": psutil.getloadavg()[2],
        "cpu_count": psutil.cpu_count(logical=False),  # 物理核心数
        "cpu_count_logical": psutil.cpu_count(logical=True),  # 逻辑核心数
    }
 
    # 1. 获取全局CFS调度器参数
    cfs_params = {}
    cfs_path = "/sys/fs/cgroup/cpu"
    for param_file in glob.glob(f"{cfs_path}/cpu.cfs_*"):
        param_name = os.path.basename(param_file)
        try:
            with open(param_file, "r") as f:
                cfs_params[param_name] = f.read().strip()
        except Exception as e:
            cfs_params[param_name] = f"ERROR: {str(e)}"
    data["cfs_scheduler"] = cfs_params

    # 2. 获取CPU亲和性掩码（系统级）
    try:
        with open("/proc/self/affinity", "r") as f:  # 读取当前进程的亲和性
            data["cpu_affinity_mask"] = f.read().strip()
    except:
        data["cpu_affinity_mask"] = "N/A"

    # 3. 获取每个CPU核心的频率和温度（如果可用）
    cpu_cores = []
    for i in range(psutil.cpu_count(logical=False)):
        core_data = {"core_id": i}
        # CPU频率
        try:
            with open(f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_cur_freq", "r") as f:
                core_data["frequency_khz"] = int(f.read().strip())
        except:
            core_data["frequency_khz"] = -1
        
        # CPU温度（需要lm-sensors支持）
        try:
            temp_file = glob.glob(f"/sys/class/thermal/thermal_zone*/temp")
            if temp_file:
                with open(temp_file[0], "r") as f:
                    core_data["temperature_c"] = float(f.read().strip()) / 1000.0
        except:
            core_data["temperature_c"] = -1
        
        cpu_cores.append(core_data)
    data["cpu_cores"] = cpu_cores

    # 4. 获取当前进程调度策略（示例：当前脚本进程）
    try:
        pid = os.getpid()
        with open(f"/proc/{pid}/sched", "r") as f:
            sched_content = f.read()
            policy_line = next(line for line in sched_content.split("\n") if "policy" in line)
            data["current_process_scheduler"] = policy_line.strip()
    except:
        data["current_process_scheduler"] = "N/A"

    return data

    

