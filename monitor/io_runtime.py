import psutil

def get_disk_io():
    io = psutil.disk_io_counters()
    return {
        "read_bytes": io.read_bytes,
        "write_bytes": io.write_bytes
    }

