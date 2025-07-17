'''
import subprocess
def apply_sysctl_params(param_dict):
    for key, value in param_dict.items():
        try:
            cmd = f"sysctl -w {key}={value}"
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✅ 已应用参数：{key}={value}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 应用失败：{key}={value}，错误：{e}")
'''
import subprocess

def apply_sysctl_params(param_dict):
    for key, value in param_dict.items():
        try:
            # 如果参数值中包含空格（例如 "4096 87380 6291456"），加引号
            if isinstance(value, str) and " " in value:
                value = f'"{value}"'

            cmd = f"sysctl -w {key}={value}"
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✅ 已应用参数：{key}={value}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 应用失败：{key}={value}，错误：{e}")
