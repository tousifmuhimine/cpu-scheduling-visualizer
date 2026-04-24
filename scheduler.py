from collections import deque
from copy import deepcopy


def _prepare_processes(processes):
    return deepcopy(processes)


def _sort_by_arrival(processes):
    return sorted(processes, key=lambda process: (process["arrival"], process["pid"]))


def fcfs(processes):
    scheduled = _sort_by_arrival(_prepare_processes(processes))
    timeline = []
    current_time = 0

    for process in scheduled:
        current_time = max(current_time, process["arrival"])
        process["start"] = current_time
        current_time += process["burst"]
        process["finish"] = current_time
        process["remaining"] = 0
        timeline.append((process["pid"], process["start"], process["finish"]))

    return timeline, scheduled


def sjf(processes):
    scheduled = _prepare_processes(processes)
    pending = _sort_by_arrival(scheduled)
    completed = []
    timeline = []
    current_time = 0

    while pending:
        available = [
            process for process in pending if process["arrival"] <= current_time
        ]

        if not available:
            current_time = pending[0]["arrival"]
            available = [
                process for process in pending if process["arrival"] <= current_time
            ]

        process = min(available, key=lambda item: (item["burst"], item["arrival"], item["pid"]))
        pending.remove(process)

        process["start"] = current_time
        current_time += process["burst"]
        process["finish"] = current_time
        process["remaining"] = 0
        timeline.append((process["pid"], process["start"], process["finish"]))
        completed.append(process)

    return timeline, _sort_by_arrival(completed)


def srtf(processes):
    scheduled = _sort_by_arrival(_prepare_processes(processes))
    for process in scheduled:
        process["remaining"] = process["burst"]

    timeline = []
    completed_count = 0
    current_time = 0
    active_pid = None
    context_switches = 0

    while completed_count < len(scheduled):
        available = [
            process
            for process in scheduled
            if process["arrival"] <= current_time and process["remaining"] > 0
        ]

        if not available:
            next_arrival = min(
                process["arrival"]
                for process in scheduled
                if process["remaining"] > 0
            )
            current_time = max(current_time, next_arrival)
            active_pid = None
            continue

        process = min(
            available,
            key=lambda item: (item["remaining"], item["arrival"], item["pid"]),
        )

        if active_pid is not None and active_pid != process["pid"]:
            context_switches += 1
        active_pid = process["pid"]

        if process["start"] is None:
            process["start"] = current_time

        if timeline and timeline[-1][0] == process["pid"] and timeline[-1][2] == current_time:
            pid, start, _ = timeline[-1]
            timeline[-1] = (pid, start, current_time + 1)
        else:
            timeline.append((process["pid"], current_time, current_time + 1))

        process["remaining"] -= 1
        current_time += 1

        if process["remaining"] == 0:
            process["finish"] = current_time
            completed_count += 1

    return timeline, _sort_by_arrival(scheduled), context_switches


def round_robin(processes, quantum):
    if quantum <= 0:
        raise ValueError("Quantum must be greater than 0.")

    scheduled = _sort_by_arrival(_prepare_processes(processes))
    for process in scheduled:
        process["remaining"] = process["burst"]

    ready_queue = deque()
    timeline = []
    completed = []
    current_time = 0
    next_index = 0

    def add_arrived_processes():
        nonlocal next_index
        while next_index < len(scheduled) and scheduled[next_index]["arrival"] <= current_time:
            ready_queue.append(scheduled[next_index])
            next_index += 1

    while len(completed) < len(scheduled):
        add_arrived_processes()

        if not ready_queue:
            current_time = scheduled[next_index]["arrival"]
            add_arrived_processes()

        process = ready_queue.popleft()
        if process["start"] is None:
            process["start"] = current_time

        start_time = current_time
        run_time = min(quantum, process["remaining"])
        current_time += run_time
        process["remaining"] -= run_time
        timeline.append((process["pid"], start_time, current_time))

        add_arrived_processes()

        if process["remaining"] > 0:
            ready_queue.append(process)
        else:
            process["finish"] = current_time
            completed.append(process)

    return timeline, _sort_by_arrival(scheduled)
