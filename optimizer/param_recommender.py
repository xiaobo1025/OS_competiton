def recommend_params(workload_type):
    """
    返回推荐系统参数组合，后续可用于 sysctl 或 echo 应用
    """
    if workload_type == "cpu_bound":
        return {
            "kernel.sched_migration_cost_ns": "5000000",
            "kernel.sched_latency_ns": "10000000"
        }
    elif workload_type == "io_bound":
        return {
            "vm.dirty_ratio": "10",
            "vm.dirty_background_ratio": "5",
            "vm.dirty_expire_centisecs": "500"
        }
    elif workload_type == "memory_bound":
        return {
            "vm.swappiness": "10",
            "vm.min_free_kbytes": "65536"
        }
    elif workload_type == "mixed":
        return {
            "kernel.sched_latency_ns": "20000000",
            "vm.swappiness": "30"
        }
    else:
        return {}  # 不调优

