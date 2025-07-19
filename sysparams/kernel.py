import os

def read_kernel_param(name):
    path = f"/proc/sys/kernel/{name}"
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except:
        return "N/A"

def get_kernel_params():
    return {
        "sched_latency_ns": read_kernel_param("sched_latency_ns"),
        "sched_migration_cost_ns": read_kernel_param("sched_migration_cost_ns"),
        "sched_wakeup_granularity_ns": read_kernel_param("sched_wakeup_granularity_ns"),
        "sched_min_granularity_ns": read_kernel_param("sched_min_granularity_ns"),
        "sched_child_runs_first": read_kernel_param("sched_child_runs_first"),
        "sched_autogroup_enabled": read_kernel_param("sched_autogroup_enabled"),
        "sched_rr_timeslice_ms": read_kernel_param("sched_rr_timeslice_ms")
    }
if __name__ == "__main__":
    import json
    kernel_data = get_kernel_params()
    print(json.dumps(kernel_data, indent=2))
