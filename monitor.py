import psutil
import sys
from tabulate import tabulate


def _bar_characters():
    encoding = sys.stdout.encoding or "utf-8"
    try:
        "█░".encode(encoding)
        return "█", "░"
    except UnicodeEncodeError:
        return "#", "-"


def show_system_processes():
    processes = []

    for process in psutil.process_iter(["pid", "name", "memory_info", "status"]):
        try:
            cpu_percent = process.cpu_percent(interval=None)
            if cpu_percent is None:
                continue

            info = process.info
            memory_info = info.get("memory_info")
            memory_mb = memory_info.rss / (1024 * 1024) if memory_info else 0
            processes.append(
                [
                    info.get("pid"),
                    info.get("name") or "Unknown",
                    cpu_percent,
                    f"{memory_mb:.1f}",
                    info.get("status") or "Unknown",
                ]
            )
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda row: row[2], reverse=True)

    print(
        tabulate(
            processes[:10],
            headers=["PID", "Name", "CPU%", "Memory (MB)", "Status"],
            tablefmt="grid",
            numalign="center",
            stralign="center",
        )
    )
    print(
        "^ These are real OS processes. Your simulation above models how a\n"
        "  CPU scheduler would handle processes like these."
    )


def show_cpu_stats():
    try:
        usages = psutil.cpu_percent(interval=1, percpu=True)
    except psutil.Error as error:
        print(f"Could not read CPU stats: {error}")
        return

    filled_char, empty_char = _bar_characters()

    for index, usage in enumerate(usages):
        filled = round((usage / 100) * 20)
        empty = 20 - filled
        bar = filled_char * filled + empty_char * empty
        print(f"Core {index} [{bar}] {usage:.0f}%")
