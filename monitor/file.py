import psutil


def get_file_info():
    """
    获取文件相关的监测信息，包括系统级文件打开数、各进程文件打开数统计等
    :return: 包含文件监测信息的字典
    """
    # 获取系统级别的文件描述符统计信息（部分系统可能无法精确获取，psutil会尽力尝试）
    # 这里获取的是系统当前整体的文件打开情况相关统计，不同系统实现有差异
    file_stats = psutil.net_if_stats()  # 这个不是文件相关，只是先占位，下面重新处理
    # 正确获取系统文件打开数思路：遍历进程，统计每个进程打开的文件数，再汇总或者取部分统计
    all_processes = psutil.process_iter()
    total_open_files = 0
    process_file_count = []
    for proc in all_processes:
        try:
            open_files = proc.open_files()
            file_count = len(open_files)
            total_open_files += file_count
            process_file_count.append(file_count)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # 简单计算进程文件打开数的一些统计值，比如均值、最大值等（可根据需求调整）
    avg_open_files_per_proc = sum(process_file_count) / len(process_file_count) if process_file_count else 0
    max_open_files_per_proc = max(process_file_count) if process_file_count else 0

    return {
        "total_open_files": total_open_files,  # 系统层面大致的总文件打开数（遍历进程统计）
        "avg_open_files_per_process": avg_open_files_per_proc,  # 进程平均打开文件数
        "max_open_files_per_process": max_open_files_per_proc  # 单个进程最大打开文件数
    }  