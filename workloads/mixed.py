import threading
import workloads.cpu_bound as cpu
import workloads.io_bound as io
import workloads.memory_bound as mem

def run(duration=10):
    t1 = threading.Thread(target=cpu.run, args=(duration,))
    t2 = threading.Thread(target=io.run, args=(duration,))
    t3 = threading.Thread(target=mem.run, args=(duration,))
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()

