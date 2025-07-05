import subprocess

def get_gpu_info(gpu_id=0):
    try:
        cmd = f"nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu,power.draw --format=csv,noheader,nounits -i {gpu_id}"
        output = subprocess.check_output(cmd, shell=True).decode().strip()
        util, mem, temp, power = output.split(', ')
        return {
            "gpu_util": float(util),
            "gpu_mem_used": float(mem),
            "gpu_temp": float(temp),
            "gpu_power": float(power)
        }
    except:
        return {
            "gpu_util": -1,
            "gpu_mem_used": -1,
            "gpu_temp": -1,
            "gpu_power": -1
        }

