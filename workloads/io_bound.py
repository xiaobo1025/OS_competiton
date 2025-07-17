'''
import time
def run(duration=10):
    start = time.time()
    with open("/tmp/io_test_file", "w") as f:
        while time.time() - start < duration:
            f.write("x" * 1024 * 1024)  # 写 1MB
            f.flush()
'''

import os
import time

def run(duration):
    """
    模拟 IO 密集型任务，持续进行磁盘写入操作，写入一定大小后循环覆盖。
    duration: 持续运行的秒数
    """
    path = "/tmp/io_test_file"
    block_size_kb = 512  # 每次写入 512KB
    max_file_size_mb = 200  # 控制最大写入文件大小
    max_file_size_bytes = max_file_size_mb * 1024 * 1024

    start_time = time.time()
    written_bytes = 0

    try:
        with open(path, "wb") as f:
            while time.time() - start_time < duration:
                f.write(b"x" * block_size_kb * 1024)
                f.flush()
                written_bytes += block_size_kb * 1024

                if written_bytes >= max_file_size_bytes:
                    f.seek(0)  # 回到文件开头重写（避免文件无限大）
                    written_bytes = 0
    except Exception as e:
        print(f"❌ IO bound workload error: {e}")
    finally:
        if os.path.exists(path):
            os.remove(path)
            print("🧹 IO 测试文件已清理")
