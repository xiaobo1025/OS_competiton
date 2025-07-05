import subprocess

def get_tcp_congestion():
    try:
        result = subprocess.run(['sysctl', 'net.ipv4.tcp_congestion_control'], capture_output=True, text=True)
        algo = result.stdout.strip().split('=')[1].strip()
        return {"tcp_congestion_control": algo}
    except:
        return {"tcp_congestion_control": "unknown"}

