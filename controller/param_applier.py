import subprocess

def apply_sysctl_params(param_dict):
    for key, value in param_dict.items():
        try:
            cmd = f"sysctl -w {key}={value}"
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✅ 已应用参数：{key}={value}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 应用失败：{key}={value}，错误：{e}")

