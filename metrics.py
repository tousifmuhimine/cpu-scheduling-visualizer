from tabulate import tabulate


def calculate(processes):
    if not processes:
        return processes, 0, 0

    total_waiting = 0
    total_turnaround = 0

    for process in processes:
        process["turnaround"] = process["finish"] - process["arrival"]
        process["waiting"] = process["turnaround"] - process["burst"]
        total_waiting += process["waiting"]
        total_turnaround += process["turnaround"]

    avg_waiting = total_waiting / len(processes)
    avg_turnaround = total_turnaround / len(processes)
    return processes, avg_waiting, avg_turnaround


def show_table(processes, avg_waiting, avg_turnaround):
    rows = [
        [
            process["pid"],
            process["arrival"],
            process["burst"],
            process["start"],
            process["finish"],
            process["waiting"],
            process["turnaround"],
        ]
        for process in processes
    ]

    print(
        tabulate(
            rows,
            headers=[
                "PID",
                "Arrival",
                "Burst",
                "Start",
                "Finish",
                "Waiting",
                "Turnaround",
            ],
            tablefmt="grid",
            numalign="center",
            stralign="center",
        )
    )
    print(f"Average Waiting Time    : {avg_waiting:.2f}")
    print(f"Average Turnaround Time : {avg_turnaround:.2f}")
