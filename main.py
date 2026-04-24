from copy import deepcopy

from metrics import calculate, show_table
from monitor import show_cpu_stats, show_system_processes
from scheduler import fcfs, round_robin, sjf, srtf
from visualizer import draw_gantt


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


def read_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("Please enter a number greater than 0.")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")


def read_non_negative_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter 0 or a positive number.")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")


def add_processes(processes):
    count = read_positive_int("How many processes do you want to add? ")

    for _ in range(count):
        pid = input("PID: ").strip()
        while not pid:
            print("PID cannot be empty.")
            pid = input("PID: ").strip()

        arrival = read_non_negative_int("Arrival time: ")
        burst = read_positive_int("Burst time: ")
        processes.append(create_process(pid, arrival, burst))
        print(f"Added {pid}.")


def view_processes(processes):
    if not processes:
        print("No processes added yet.")
        return

    rows = [
        [process["pid"], process["arrival"], process["burst"]]
        for process in processes
    ]
    from tabulate import tabulate

    print(tabulate(rows, headers=["PID", "Arrival", "Burst"], tablefmt="grid"))


def run_algorithm(title, algorithm, processes, *args):
    if not processes:
        print("Add at least one process before running a scheduler.")
        return

    print(f"\nRunning: {title}\n")
    timeline, scheduled = algorithm(deepcopy(processes), *args)
    scheduled, avg_waiting, avg_turnaround = calculate(scheduled)
    draw_gantt(timeline)
    print()
    show_table(scheduled, avg_waiting, avg_turnaround)


def run_srtf(processes):
    if not processes:
        print("Add at least one process before running a scheduler.")
        return

    print("\nRunning: SRTF (Preemptive SJF)\n")
    timeline, scheduled, context_switches = srtf(deepcopy(processes))
    scheduled, avg_waiting, avg_turnaround = calculate(scheduled)
    draw_gantt(timeline)
    print()
    show_table(scheduled, avg_waiting, avg_turnaround)
    print(f"Context Switches: {context_switches}")


def print_menu():
    print("\n===== CPU Scheduling Visualizer =====")
    print("1. Add processes")
    print("2. View processes")
    print("3. Run FCFS")
    print("4. Run SJF (Non-Preemptive)")
    print("5. Run SRTF (Preemptive SJF)")
    print("6. Run Round Robin")
    print("7. Show real system processes")
    print("8. Show CPU core usage")
    print("9. Clear processes")
    print("0. Exit")


def main():
    processes = []

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_processes(processes)
        elif choice == "2":
            view_processes(processes)
        elif choice == "3":
            run_algorithm("FCFS", fcfs, processes)
        elif choice == "4":
            run_algorithm("SJF (Non-Preemptive)", sjf, processes)
        elif choice == "5":
            run_srtf(processes)
        elif choice == "6":
            quantum = read_positive_int("Quantum: ")
            run_algorithm(f"Round Robin (Quantum = {quantum})", round_robin, processes, quantum)
        elif choice == "7":
            show_system_processes()
        elif choice == "8":
            show_cpu_stats()
        elif choice == "9":
            processes.clear()
            print("Process list cleared.")
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Please choose an option from 0 to 9.")


if __name__ == "__main__":
    main()
