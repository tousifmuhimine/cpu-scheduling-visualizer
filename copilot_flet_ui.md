# CPU Scheduling Visualizer — Flet UI

## Context
The backend is already fully built. Do NOT rewrite or modify any existing files.
All scheduling logic, metrics, and monitoring stay exactly as they are.

Existing files (read-only):
- `scheduler.py` — fcfs(), sjf(), srtf(), round_robin()
- `metrics.py`   — calculate(), show_table()
- `monitor.py`   — show_system_processes(), show_cpu_stats()
- `main.py`      — old terminal menu (keep it, don't touch)

---

## Install
```bash
pip install flet
```
Add `flet` to `requirements.txt`

---

## New File: `app.py`
This is the only file to create. Run it with:
```bash
python app.py
```

---

## App Layout

### Window
- Title: `CPU Scheduling Visualizer`
- Min size: 900 x 650
- Theme: dark mode (`ft.ThemeMode.DARK`)
- Background color: `#0f1117`

---

### Layout: Two columns side by side

**Left Panel (300px wide) — Controls**
- App title at top: "CPU Scheduler" bold, accent color `#2E75B6`
- Subtitle: "Visualizer + Monitor" small, gray

**Process Input section:**
- Three text fields in a row: PID, Arrival Time, Burst Time
- `Add Process` button (accent blue)
- A list/table below showing added processes with a small ✕ remove button per row

**Algorithm section:**
- Dropdown to select: FCFS / SJF / SRTF / Round Robin
- When Round Robin is selected, show a Quantum number input field (default 2)
- `Run` button (green, full width)
- `Clear All` button (red outline, full width)

---

**Right Panel (fills remaining space) — Output**

Three tabs at the top:
1. `Gantt Chart`
2. `Metrics`
3. `System Monitor`

---

## Tab 1: Gantt Chart

After running an algorithm, render the Gantt chart as colored rectangles.

**How to draw it:**
- Use `ft.Stack` or `ft.Row` with `ft.Container` blocks
- Each process block = `ft.Container` with:
  - `bgcolor` = unique color per PID (use a fixed color map, see below)
  - `width` = proportional to duration: `duration * 40` pixels
  - `height` = 60
  - `border_radius` = 6
  - Content: PID centered in white bold text, duration below in small gray text
- Blocks sit in a horizontal scrollable `ft.Row`
- Below the blocks, show time markers (start time of each block) as small gray text
  aligned under each block boundary

**Color map (assign in order as new PIDs appear):**
```python
COLORS = ["#2E75B6", "#27AE60", "#E74C3C", "#F39C12",
          "#8E44AD", "#16A085", "#E67E22", "#2980B9"]
```

**Below the chart, show:**
- `Context Switches: N` — only for SRTF
- Which algorithm was used: e.g. `Algorithm: Round Robin  |  Quantum: 2`

---

## Tab 2: Metrics

Show a styled data table using `ft.DataTable` with columns:
PID | Arrival | Burst | Start | Finish | Waiting | Turnaround

- Header row: accent blue background, white bold text
- Alternating row colors: `#1a1f2e` and `#141820`
- Below the table show three summary chips:
  ```
  Avg Waiting: 6.50     Avg Turnaround: 12.25     CPU Utilization: 87%
  ```
  Each as a rounded container with a subtle border

---

## Tab 3: System Monitor

Two sections stacked vertically:

**Top: Real Processes**
- A `ft.DataTable` showing top 10 real processes from `psutil`
- Columns: PID | Name | CPU% | Memory (MB) | Status
- Refresh automatically every 2 seconds using `page.update()` in a thread
- Add a manual `Refresh` button too

**Bottom: CPU Core Usage**
- For each core, show:
  - Core label: `Core 0`
  - A `ft.ProgressBar` with value = cpu_percent / 100
  - Percentage text next to it
- Color the progress bar:
  - Green if < 50%
  - Orange if 50–80%
  - Red if > 80%
- Refresh every 2 seconds alongside the process table

---

## Error Handling in UI

- If user clicks Run with no processes: show a red snackbar — `"Add at least one process first"`
- If PID field is empty: show snackbar — `"PID cannot be empty"`
- If Arrival or Burst is not a number: show snackbar — `"Arrival and Burst must be numbers"`
- If Burst = 0: show snackbar — `"Burst time must be greater than 0"`
- Wrap all psutil calls in try/except silently — skip inaccessible processes

---

## Behavior Notes

- Switching algorithms and clicking Run again should clear and redraw the Gantt chart
- Process list on left panel updates live as user adds/removes processes
- Tabs are always visible; System Monitor tab refreshes independently of Run
- Keep `main.py` working as before — `app.py` is a separate entry point

---

## Import Pattern in app.py
```python
import flet as ft
import copy
import threading
import psutil
from scheduler import fcfs, sjf, srtf, round_robin
from metrics import calculate
```
Do not import show_table() from metrics — the UI replaces that terminal output.

---

## Test Checklist
- [ ] App opens in a window (not browser)
- [ ] Add 4 processes: P1/0/8, P2/1/4, P3/2/9, P4/3/5
- [ ] Run SRTF → Gantt chart shows colored blocks, Context Switches: 4
- [ ] Metrics tab shows avg waiting = 6.50
- [ ] Switch to Round Robin quantum=2 → chart updates correctly
- [ ] System Monitor tab shows real processes and CPU bars refreshing
- [ ] Removing a process from the list works
- [ ] Run with empty list shows red snackbar
