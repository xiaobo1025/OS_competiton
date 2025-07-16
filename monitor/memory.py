'''
import psutil

def get_memory_info():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "mem_total": mem.total,
        "mem_available": mem.available,
        "mem_used": mem.used,
        "mem_percent": mem.percent,
        "swap_total": swap.total,
        "swap_used": swap.used,
        "swap_percent": swap.percent
    }
'''

import psutil
import os
import subprocess

def get_memory_info():
    # 基础内存和交换分区信息（保留原逻辑）
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    data = {
        # 原有指标
        "mem_total": mem.total,
        "mem_available": mem.available,
        "mem_used": mem.used,
        "mem_percent": mem.percent,
        "swap_total": swap.total,
        "swap_used": swap.used,
        "swap_percent": swap.percent,
        
        # 1. 虚拟内存回收策略（swappiness）
        "vm_swappiness": get_swappiness(),
        
        # 2. 内存页大小（默认页大小和大页信息）
        "page_size": get_page_size(),
        "hugepage_info": get_hugepage_info(),
        
        # 3. 缓存管理（页缓存、slab缓存）
        "cache_stats": get_cache_stats()
    }
    return data

# 辅助函数：获取虚拟内存回收策略（swappiness）
def get_swappiness():
    try:
        with open("/proc/sys/vm/swappiness", "r") as f:
            return int(f.read().strip())  # 值范围0-100，越小越倾向于回收缓存而非交换
    except:
        return -1  # 表示获取失败

# 辅助函数：获取内存页大小
def get_page_size():
    try:
        # 默认页大小（字节）
        return os.sysconf("SC_PAGESIZE")
    except:
        return -1

# 辅助函数：获取大页（HugePage）信息
def get_hugepage_info():
    try:
        # 大页大小（通常为2MB或1GB）
        with open("/proc/meminfo", "r") as f:
            meminfo = f.read()
            hugepage_size = int([line for line in meminfo.split("\n") if "Hugepagesize" in line][0].split()[1]) * 1024  # 转换为字节
            return {"hugepage_size": hugepage_size}
    except:
        return {"hugepage_size": -1}
  
# 辅助函数：获取缓存管理信息（页缓存、slab缓存）
def get_cache_stats():
    try:
        with open("/proc/meminfo", "r") as f:
            meminfo = f.read()
            # 页缓存（Cached）：磁盘文件的内存缓存
            cached = int([line for line in meminfo.split("\n") if "Cached" in line][0].split()[1]) * 1024  # 转换为字节
            # Slab缓存：内核对象（如inode、dentry）的缓存
            slab = int([line for line in meminfo.split("\n") if "Slab" in line][0].split()[1]) * 1024
            return {
                "page_cache": cached,
                "slab_cache": slab
            }
    except:
        return {"page_cache": -1, "slab_cache": -1}
