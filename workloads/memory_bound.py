import time
def run(duration=10):
    start = time.time()
    a = []
    while time.time() - start < duration:
        a.append("x" * 1024 * 1024)  # 每次加1MB
        time.sleep(0.1)
