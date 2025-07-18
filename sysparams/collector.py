#import sys
#import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sysparams.kernel import get_kernel_params
from sysparams.vm import get_vm_params
from sysparams.net import get_all_net_params as get_net_params
from sysparams.io import get_io_params

def collect_all_sysparams():
    params = {}
    params.update(get_kernel_params())
    params.update(get_vm_params())
    params.update(get_net_params())

    # 展平 Net 参数中的 rmem/wmem 三元组（若存在）
    if "tcp_rmem" in params:
        rmem_parts = params.pop("tcp_rmem").split()
        if len(rmem_parts) == 3:
            params["tcp_rmem_min"] = int(rmem_parts[0])
            params["tcp_rmem_default"] = int(rmem_parts[1])
            params["tcp_rmem_max"] = int(rmem_parts[2])

    if "tcp_wmem" in params:
        wmem_parts = params.pop("tcp_wmem").split()
        if len(wmem_parts) == 3:
            params["tcp_wmem_min"] = int(wmem_parts[0])
            params["tcp_wmem_default"] = int(wmem_parts[1])
            params["tcp_wmem_max"] = int(wmem_parts[2])

    # 只采第一个 block 设备（如 sda）
    io_params = get_io_params()
    if io_params:
        first_disk = sorted(io_params.keys())[0]
        disk_params = io_params[first_disk]
        for key, value in disk_params.items():
            params[f"disk_{key}"] = value  # 扁平化

        # 可选：提取 scheduler 当前策略（去除中括号）
        if "disk_scheduler" in params:
            sched = params["disk_scheduler"]
            for opt in sched.split():
                if opt.startswith("[") and opt.endswith("]"):
                    params["disk_scheduler"] = opt.strip("[]")
                    break

    return params

if __name__ == "__main__":
    import json
    all_sysparams = collect_all_sysparams()
    print(json.dumps(all_sysparams, indent=2))
