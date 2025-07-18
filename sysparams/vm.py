import os

def read_vm_param(name):
    path = f"/proc/sys/vm/{name}"
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except:
        return "N/A"

def get_vm_params():
    return {
        "swappiness": read_vm_param("swappiness"),
        "dirty_ratio": read_vm_param("dirty_ratio"),
        "dirty_background_ratio": read_vm_param("dirty_background_ratio"),
        "dirty_expire_centisecs": read_vm_param("dirty_expire_centisecs"),
        "dirty_writeback_centisecs": read_vm_param("dirty_writeback_centisecs"),
        "min_free_kbytes": read_vm_param("min_free_kbytes"),
        "overcommit_memory": read_vm_param("overcommit_memory"),
        "overcommit_ratio": read_vm_param("overcommit_ratio"),
        "vfs_cache_pressure": read_vm_param("vfs_cache_pressure")
    }

if __name__ == "__main__":
    import json
    vm_data = get_vm_params()
    print(json.dumps(vm_data, indent=1))
