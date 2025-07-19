import subprocess
import os

def apply_sysctl_params(param_dict):
    for key, value in param_dict.items():
        # 特殊处理 TCP 内存等空格参数加引号
        if isinstance(value, str) and " " in value:
            value_str = f'"{value}"'
        else:
            value_str = str(value)
        
        # 正常的 sysctl 参数处理
        try:
            cmd = f"sysctl -w {key}={value_str}"
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✅ 已应用参数：{key}={value}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 应用失败：{key}={value}，错误：{e}")
