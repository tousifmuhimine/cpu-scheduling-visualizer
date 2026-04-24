# CPU Scheduling Visualizer — Level Up Update

## What's Already Built
The base project is complete with:
- `main.py` — menu loop and process input
- `scheduler.py` — FCFS, non-preemptive SJF, Round Robin
- `metrics.py` — waiting/turnaround calculations and table display
- `visualizer.py` — colorized Gantt chart using colorama

Do NOT rewrite existing code. Only add the two features below.

---

## Feature 1 — Preemptive SJF (SRTF)

### Add to `scheduler.py`

**`srtf(processes)`** — Shortest Remaining Time First
- Preemptive version of SJF
- At every clock tick, check all arrived processes and pick the one
  with the shortest **remaining** burst time
- If a new process arrives with shorter remaining time than the current
  one running, preempt immediately
- Track context switches (how many times CPU switches process)
- Return the same format as other schedulers:
  - `timeline` as list of `(pid, start, end)` tuples — merge consecutive
    blocks of the same PID into one tuple
  - Updated process list with `start`, `finish` filled in

### Add to `main.py` menu
```
5. Run SRTF (Preemptive SJF)
```
Shift Round Robin to option 6.

---

## Feature 2 — Real Process Monitor

### New file: `monitor.py`

**`show_system_processes()`**
- Use `psutil` to fetch the top 10 real running processes on the machine
- Sort by CPU percent descending
- Display using `tabulate` with columns:
  PID | Name | CPU% | Memory (MB) | Status
- After the table, print a note:
  ```
  ^ These are real OS processes. Your simulation above models how a
    CPU scheduler would handle processes like these.
  ```

**`show_cpu_stats()`**
- Use `psutil.cpu_percent(interval=1, percpu=True)` to get per-core usage
- Print a simple bar for each core using block characters (█) scaled to 20 chars
- Example:
  ```
  Core 0 [████████████░░░░░░░░] 61%
  Core 1 [██████░░░░░░░░░░░░░░] 31%
  ```

### Add to `main.py` menu
```
7. Show real system processes
8. Show CPU core usage (live)
```

### Install
```bash
pip install psutil
```
Add `psutil` to `requirements.txt`

---

## Add to `main.py` — Context Switch Counter

After running SRTF, print:
```
Context Switches: 5
```
Pull this from the return value of `srtf()`. Add it as a third return value:
```python
return timeline, processes, context_switches
```

---

## Edge Cases to Handle

In `scheduler.py` for SRTF:
- If two processes have the same remaining time, pick the one that arrived first
- If no process has arrived yet, advance clock to the next arrival time
  (don't loop forever on an empty ready queue)

In `monitor.py`:
- Wrap psutil calls in try/except — some processes deny access on Windows
- Skip processes where `cpu_percent()` returns `None`

---

## Updated Menu (main.py)
```
===== CPU Scheduling Visualizer =====
1. Add processes
2. View processes
3. Run FCFS
4. Run SJF (Non-Preemptive)
5. Run SRTF (Preemptive SJF)      ← new
6. Run Round Robin
7. Show real system processes      ← new
8. Show CPU core usage             ← new
9. Clear processes
0. Exit
```

---

## Test Input for SRTF
Use this to verify correctness:
- P1: arrival=0, burst=8
- P2: arrival=1, burst=4
- P3: arrival=2, burst=9
- P4: arrival=3, burst=5

Expected order (roughly): P1 runs 1 tick → P2 preempts → P4 joins →
P2 finishes → P4 runs → P1 resumes → P3 last.
Average waiting time should be **6.5**.
