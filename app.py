import copy
import threading
import time

import flet as ft
import psutil

from metrics import calculate
from scheduler import fcfs, round_robin, sjf, srtf


COLORS = [
    "#2E75B6",
    "#27AE60",
    "#E74C3C",
    "#F39C12",
    "#8E44AD",
    "#16A085",
    "#E67E22",
    "#2980B9",
]

BG = "#0f1117"
PANEL = "#141820"
PANEL_ALT = "#1a1f2e"
TEXT_MUTED = "#9aa4b2"
ACCENT = "#2E75B6"
GREEN = "#27AE60"
RED = "#E74C3C"
ORANGE = "#F39C12"


def create_process(pid, arrival, burst):
    return {
        "pid": pid,
        "arrival": arrival,
        "burst": burst,
        "remaining": burst,
        "start": None,
        "finish": None,
        "waiting": None,
        "turnaround": None,
    }


def main(page: ft.Page):
    page.title = "CPU Scheduling Visualizer"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 0
    page.window.min_width = 900
    page.window.min_height = 650

    processes = []
    last_run = {
        "timeline": [],
        "scheduled": [],
        "avg_waiting": 0,
        "avg_turnaround": 0,
        "cpu_utilization": 0,
        "algorithm": "",
        "quantum": None,
        "context_switches": None,
    }

    pid_field = ft.TextField(label="PID", dense=True, expand=1)
    arrival_field = ft.TextField(label="Arrival", dense=True, expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    burst_field = ft.TextField(label="Burst", dense=True, expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    quantum_field = ft.TextField(
        label="Quantum",
        value="2",
        dense=True,
        keyboard_type=ft.KeyboardType.NUMBER,
        visible=False,
    )
    algorithm_dropdown = ft.Dropdown(
        label="Algorithm",
        value="FCFS",
        options=[
            ft.dropdown.Option("FCFS"),
            ft.dropdown.Option("SJF"),
            ft.dropdown.Option("SRTF"),
            ft.dropdown.Option("Round Robin"),
        ],
    )

    process_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
    gantt_content = ft.Column(spacing=16, expand=True, scroll=ft.ScrollMode.AUTO)
    metrics_content = ft.Column(spacing=16, expand=True, scroll=ft.ScrollMode.AUTO)
    process_monitor_content = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
    cpu_monitor_content = ft.Column(spacing=8)

    def show_error(message):
        page.snack_bar = ft.SnackBar(
            ft.Text(message, color="white"),
            bgcolor=RED,
        )
        page.snack_bar.open = True
        page.update()

    def pid_color_map(timeline):
        pids = []
        for pid, _, _ in timeline:
            if pid not in pids:
                pids.append(pid)
        return {pid: COLORS[index % len(COLORS)] for index, pid in enumerate(pids)}

    def make_label(text, size=12, color=TEXT_MUTED, weight=None):
        return ft.Text(text, size=size, color=color, weight=weight)

    def reset_results():
        last_run.update(
            {
                "timeline": [],
                "scheduled": [],
                "avg_waiting": 0,
                "avg_turnaround": 0,
                "cpu_utilization": 0,
                "algorithm": "",
                "quantum": None,
                "context_switches": None,
            }
        )

    def update_process_list():
        process_list.controls.clear()
        if not processes:
            process_list.controls.append(
                ft.Container(
                    content=make_label("No processes added", color=TEXT_MUTED),
                    padding=12,
                    bgcolor=PANEL,
                    border_radius=6,
                )
            )
        else:
            process_list.controls.append(
                ft.Row(
                    [
                        make_label("PID", weight=ft.FontWeight.BOLD, color="white"),
                        make_label("Arrival", weight=ft.FontWeight.BOLD, color="white"),
                        make_label("Burst", weight=ft.FontWeight.BOLD, color="white"),
                        ft.Container(width=36),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
            for index, process in enumerate(processes):
                process_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(process["pid"], width=58, weight=ft.FontWeight.BOLD),
                                ft.Text(str(process["arrival"]), width=58),
                                ft.Text(str(process["burst"]), width=52),
                                ft.IconButton(
                                    icon=ft.icons.CLOSE,
                                    icon_size=16,
                                    width=32,
                                    height=32,
                                    tooltip="Remove process",
                                    data=index,
                                    on_click=remove_process,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        bgcolor=PANEL_ALT if index % 2 == 0 else PANEL,
                        border_radius=6,
                    )
                )
        page.update()

    def remove_process(event):
        index = event.control.data
        if index is None or index >= len(processes):
            return

        processes.pop(index)
        reset_results()
        update_process_list()
        render_gantt()
        render_metrics()

    def add_process(_):
        pid = (pid_field.value or "").strip()
        if not pid:
            show_error("PID cannot be empty")
            return

        arrival_text = arrival_field.value or ""
        burst_text = burst_field.value or ""
        try:
            arrival = int(arrival_text)
            burst = int(burst_text)
        except (TypeError, ValueError):
            show_error("Arrival and Burst must be numbers")
            return

        if burst <= 0:
            show_error("Burst time must be greater than 0")
            return
        if arrival < 0:
            show_error("Arrival and Burst must be numbers")
            return

        processes.append(create_process(pid, arrival, burst))
        pid_field.value = ""
        arrival_field.value = ""
        burst_field.value = ""
        update_process_list()

    def clear_all(_):
        processes.clear()
        reset_results()
        update_process_list()
        render_gantt()
        render_metrics()

    def on_algorithm_change(_):
        quantum_field.visible = algorithm_dropdown.value == "Round Robin"
        page.update()

    def run_selected(_):
        if not processes:
            show_error("Add at least one process first")
            return

        algorithm = algorithm_dropdown.value
        context_switches = None
        quantum = None

        try:
            if algorithm == "FCFS":
                timeline, scheduled = fcfs(copy.deepcopy(processes))
            elif algorithm == "SJF":
                timeline, scheduled = sjf(copy.deepcopy(processes))
            elif algorithm == "SRTF":
                timeline, scheduled, context_switches = srtf(copy.deepcopy(processes))
            else:
                quantum = int(quantum_field.value or "2")
                if quantum <= 0:
                    show_error("Burst time must be greater than 0")
                    return
                timeline, scheduled = round_robin(copy.deepcopy(processes), quantum)
        except ValueError:
            show_error("Arrival and Burst must be numbers")
            return

        scheduled, avg_waiting, avg_turnaround = calculate(scheduled)
        total_burst = sum(process["burst"] for process in scheduled)
        finish_time = max((end for _, _, end in timeline), default=0)
        start_time = min((start for _, start, _ in timeline), default=0)
        elapsed = finish_time - start_time
        cpu_utilization = (total_burst / elapsed * 100) if elapsed else 0

        last_run.update(
            {
                "timeline": timeline,
                "scheduled": scheduled,
                "avg_waiting": avg_waiting,
                "avg_turnaround": avg_turnaround,
                "cpu_utilization": cpu_utilization,
                "algorithm": algorithm,
                "quantum": quantum,
                "context_switches": context_switches,
            }
        )
        render_gantt()
        render_metrics()
        page.update()

    def render_gantt():
        gantt_content.controls.clear()
        timeline = last_run["timeline"]
        if not timeline:
            gantt_content.controls.append(
                ft.Container(
                    content=ft.Text("Run an algorithm to draw the Gantt chart.", color=TEXT_MUTED),
                    padding=18,
                    bgcolor=PANEL,
                    border_radius=8,
                )
            )
            page.update()
            return

        colors = pid_color_map(timeline)
        blocks = []
        markers = []
        for pid, start, end in timeline:
            duration = end - start
            width = max(52, duration * 40)
            blocks.append(
                ft.Container(
                    width=width,
                    height=60,
                    bgcolor=colors[pid],
                    border_radius=6,
                    content=ft.Column(
                        [
                            ft.Text(pid, color="white", weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(f"{duration}", color="#d8dee9", size=11),
                        ],
                        spacing=0,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )
            markers.append(
                ft.Container(width=width, content=ft.Text(str(start), size=11, color=TEXT_MUTED))
            )
        markers.append(ft.Text(str(timeline[-1][2]), size=11, color=TEXT_MUTED))

        gantt_content.controls.extend(
            [
                ft.Row(blocks, spacing=4, scroll=ft.ScrollMode.AUTO),
                ft.Row(markers, spacing=4, scroll=ft.ScrollMode.AUTO),
            ]
        )

        details = f"Algorithm: {last_run['algorithm']}"
        if last_run["quantum"] is not None:
            details += f"  |  Quantum: {last_run['quantum']}"
        gantt_content.controls.append(ft.Text(details, color=TEXT_MUTED))
        if last_run["context_switches"] is not None:
            gantt_content.controls.append(
                ft.Text(
                    f"Context Switches: {last_run['context_switches']}",
                    color="white",
                    weight=ft.FontWeight.BOLD,
                )
            )
        page.update()

    def metric_chip(label, value):
        return ft.Container(
            content=ft.Text(f"{label}: {value}", color="white", size=13),
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            border=ft.border.all(1, "#2a3142"),
            border_radius=20,
            bgcolor=PANEL,
        )

    def render_metrics():
        metrics_content.controls.clear()
        scheduled = last_run["scheduled"]
        if not scheduled:
            metrics_content.controls.append(
                ft.Container(
                    content=ft.Text("Metrics will appear after a run.", color=TEXT_MUTED),
                    padding=18,
                    bgcolor=PANEL,
                    border_radius=8,
                )
            )
            page.update()
            return

        columns = ["PID", "Arrival", "Burst", "Start", "Finish", "Waiting", "Turnaround"]
        rows = []
        for index, process in enumerate(scheduled):
            values = [
                process["pid"],
                process["arrival"],
                process["burst"],
                process["start"],
                process["finish"],
                process["waiting"],
                process["turnaround"],
            ]
            rows.append(
                ft.DataRow(
                    color=PANEL_ALT if index % 2 == 0 else PANEL,
                    cells=[ft.DataCell(ft.Text(str(value))) for value in values],
                )
            )

        metrics_content.controls.extend(
            [
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text(column, color="white", weight=ft.FontWeight.BOLD))
                        for column in columns
                    ],
                    rows=rows,
                    heading_row_color=ACCENT,
                    border_radius=6,
                    column_spacing=20,
                ),
                ft.Row(
                    [
                        metric_chip("Avg Waiting", f"{last_run['avg_waiting']:.2f}"),
                        metric_chip("Avg Turnaround", f"{last_run['avg_turnaround']:.2f}"),
                        metric_chip("CPU Utilization", f"{last_run['cpu_utilization']:.0f}%"),
                    ],
                    wrap=True,
                ),
            ]
        )
        page.update()

    def process_rows():
        rows = []
        for process in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "status"]):
            try:
                info = process.info
                cpu_percent = info.get("cpu_percent")
                if cpu_percent is None:
                    continue
                memory_info = info.get("memory_info")
                memory_mb = memory_info.rss / (1024 * 1024) if memory_info else 0
                rows.append(
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
        rows.sort(key=lambda row: row[2], reverse=True)
        return rows[:10]

    def progress_color(usage):
        if usage > 80:
            return RED
        if usage >= 50:
            return ORANGE
        return GREEN

    def refresh_monitor(_=None):
        try:
            rows = process_rows()
            cpu_usage = psutil.cpu_percent(interval=None, percpu=True)
        except psutil.Error:
            return

        process_monitor_content.controls.clear()
        process_monitor_content.controls.append(
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text(column, color="white", weight=ft.FontWeight.BOLD))
                    for column in ["PID", "Name", "CPU%", "Memory (MB)", "Status"]
                ],
                rows=[
                    ft.DataRow(
                        color=PANEL_ALT if index % 2 == 0 else PANEL,
                        cells=[ft.DataCell(ft.Text(str(value))) for value in row],
                    )
                    for index, row in enumerate(rows)
                ],
                heading_row_color=ACCENT,
                column_spacing=20,
                border_radius=6,
            )
        )

        cpu_monitor_content.controls.clear()
        for index, usage in enumerate(cpu_usage):
            cpu_monitor_content.controls.append(
                ft.Row(
                    [
                        ft.Text(f"Core {index}", width=70, color="white"),
                        ft.ProgressBar(
                            value=usage / 100,
                            color=progress_color(usage),
                            bgcolor="#2a3142",
                            expand=True,
                        ),
                        ft.Text(f"{usage:.0f}%", width=48, text_align=ft.TextAlign.RIGHT),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        page.update()

    def monitor_loop():
        while True:
            time.sleep(2)
            try:
                refresh_monitor()
            except Exception:
                pass

    left_panel = ft.Container(
        width=300,
        bgcolor="#10141d",
        padding=18,
        content=ft.Column(
            [
                ft.Text("CPU Scheduler", size=26, weight=ft.FontWeight.BOLD, color=ACCENT),
                ft.Text("Visualizer + Monitor", size=12, color=TEXT_MUTED),
                ft.Divider(height=24, color="#273044"),
                ft.Text("Process Input", weight=ft.FontWeight.BOLD),
                ft.Row([pid_field, arrival_field, burst_field], spacing=8),
                ft.ElevatedButton(
                    "Add Process",
                    icon=ft.icons.ADD,
                    bgcolor=ACCENT,
                    color="white",
                    on_click=add_process,
                    width=260,
                ),
                ft.Container(height=180, content=process_list),
                ft.Divider(height=24, color="#273044"),
                ft.Text("Algorithm", weight=ft.FontWeight.BOLD),
                algorithm_dropdown,
                quantum_field,
                ft.ElevatedButton(
                    "Run",
                    icon=ft.icons.PLAY_ARROW,
                    bgcolor=GREEN,
                    color="white",
                    on_click=run_selected,
                    width=260,
                ),
                ft.OutlinedButton(
                    "Clear All",
                    icon=ft.icons.DELETE_OUTLINE,
                    style=ft.ButtonStyle(color=RED, side=ft.BorderSide(1, RED)),
                    on_click=clear_all,
                    width=260,
                ),
            ],
            spacing=12,
        ),
    )

    tabs = ft.Tabs(
        selected_index=0,
        expand=True,
        tabs=[
            ft.Tab(
                text="Gantt Chart",
                content=ft.Container(content=gantt_content, padding=20, expand=True),
            ),
            ft.Tab(
                text="Metrics",
                content=ft.Container(content=metrics_content, padding=20, expand=True),
            ),
            ft.Tab(
                text="System Monitor",
                content=ft.Container(
                    padding=20,
                    expand=True,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("Real Processes", size=18, weight=ft.FontWeight.BOLD),
                                    ft.ElevatedButton(
                                        "Refresh",
                                        icon=ft.icons.REFRESH,
                                        bgcolor=ACCENT,
                                        color="white",
                                        on_click=refresh_monitor,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            process_monitor_content,
                            ft.Divider(color="#273044"),
                            ft.Text("CPU Core Usage", size=18, weight=ft.FontWeight.BOLD),
                            cpu_monitor_content,
                        ],
                        spacing=14,
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
            ),
        ],
    )

    algorithm_dropdown.on_change = on_algorithm_change
    page.add(ft.Row([left_panel, ft.Container(content=tabs, expand=True)], spacing=0, expand=True))

    update_process_list()
    render_gantt()
    render_metrics()
    refresh_monitor()
    threading.Thread(target=monitor_loop, daemon=True).start()


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
