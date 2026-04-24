# CPU Scheduling Visualizer — Copilot Build Guide

## What I'm Building
A terminal-based Python app that simulates CPU scheduling algorithms and prints
a color-coded Gantt chart in the terminal. Also shows performance metrics
(waiting time, turnaround time) in a table after each run.

---

## Tech Stack
- **Language:** Python 3.x
- **Libraries:** `colorama` (colors), `tabulate` (metrics table), `collections.deque` (Round Robin queue)
- **Install:** `pip install colorama tabulate`
- **Run:** `python main.py`

---

## Project Structure
```
cpu-scheduler/
├── main.py            ← entry point, menu loop
├── scheduler.py       ← FCFS, SJF, Round Robin algorithm functions
├── visualizer.py      ← Gantt chart renderer using colorama
└── metrics.py         ← waiting time, turnaround time, averages calculator
```

---

## Data Model
Each process is a dictionary:
```python
{
  "pid": "P1",        # process name
  "arrival": 0,       # arrival time (int)
  "burst": 5,         # burst time / CPU time needed (int)
  "remaining": 5,     # copy of burst, used by Round Robin
  "start": None,      # filled in by scheduler
  "finish": None,     # filled in by scheduler
  "waiting": None,    # calculated after scheduling
  "turnaround": None  # calculated after scheduling
}
```

The scheduler functions return a **timeline** — a list of tuples:
```python
timeline = [("P1", 0, 5), ("P2", 5, 8), ("P1", 8, 10), ...]
# each tuple: (pid, start_time, end_time)
```

---

## Files to Build

### 1. `scheduler.py`
Build three functions:

**`fcfs(processes)`**
- Sort by arrival time
- Execute in order, no preemption
- Return timeline + updated process list with start/finish times

**`sjf(processes)`**
- Non-preemptive
- At each step, among all arrived processes, pick the one with shortest burst
- Return timeline + updated process list

**`round_robin(processes, quantum)`**
- Use `collections.deque` as ready queue
- Add processes to queue as they arrive (sort by arrival first)
- Slice CPU time by `quantum`, re-queue unfinished processes
- Return timeline + updated process list

---

### 2. `metrics.py`
Build one function:

**`calculate(processes)`**
- `turnaround = finish - arrival`
- `waiting = turnaround - burst`
- Return updated process list + avg_waiting + avg_turnaround

---

### 3. `visualizer.py`
Build one function:

**`draw_gantt(timeline)`**
- Assign each unique PID a color from colorama (Fore.RED, Fore.GREEN, Fore.BLUE, etc.)
- Print a horizontal bar chart in the terminal like this:

```
| P1  | P2  | P1  | P3  |
0     5     8     10    13
```
- Each block width = proportional to duration (use spaces)
- Print time markers below each block boundary
- Use colorama to color each PID block differently

---

### 4. `metrics.py` display function
**`show_table(processes, avg_waiting, avg_turnaround)`**
- Use `tabulate` to print a table with columns:
  PID | Arrival | Burst | Start | Finish | Waiting | Turnaround
- Print averages below the table

---

### 5. `main.py`
Menu loop:
```
1. Add processes (input PID, arrival, burst)
2. View processes
3. Run FCFS
4. Run SJF
5. Run Round Robin (ask for quantum)
6. Clear processes
7. Exit
```
- After running any algorithm, call draw_gantt() then show_table()
- Use a deep copy of processes for each run so original list is preserved

---

## Example Expected Output
```
Running: Round Robin (Quantum = 2)

| P1   | P2   | P3   | P1   | P2   | P3   |
0      2      4      6      7      9      11

+-----+---------+-------+-------+--------+---------+-------------+
| PID | Arrival | Burst | Start | Finish | Waiting | Turnaround  |
+-----+---------+-------+-------+--------+---------+-------------+
| P1  |    0    |   4   |   0   |   7    |    3    |      7      |
| P2  |    1    |   3   |   2   |   9    |    5    |      8      |
| P3  |    2    |   5   |   4   |   11   |    4    |      9      |
+-----+---------+-------+-------+--------+---------+-------------+
Average Waiting Time    : 4.00
Average Turnaround Time : 8.00
```

---

## Copilot Tips
- Build and test `scheduler.py` first before touching the visualizer
- Test each algorithm with this sample input:
  - P1: arrival=0, burst=4
  - P2: arrival=1, burst=3
  - P3: arrival=2, burst=5
- For Round Robin, quantum=2 is a good test value
- Keep colorama's `init(autoreset=True)` at the top of `visualizer.py`
