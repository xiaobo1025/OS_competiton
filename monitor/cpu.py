import psutil

def get_cpu_info():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "load_avg_1": psutil.getloadavg()[0],
        "load_avg_5": psutil.getloadavg()[1],
        "load_avg_15": psutil.getloadavg()[2]
    }

