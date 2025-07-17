import time
def run(duration=10):
    start = time.time()
    while time.time() - start < duration:
        for _ in range(10**6):
            _ = sum(i * i for i in range(100))  # 占 CPU
