# 🖥️ CPU Scheduling Visualizer

> **An interactive desktop application that brings Operating System scheduling algorithms to life — with real-time Gantt charts, performance metrics, and a live system process monitor.**

---

## 🎬 Demo Video

> **📺 YouTube Demo:** [▶ Watch the full demonstration here](https://www.youtube.com/watch?v=YOUR_LINK_HERE)
>
> *(Replace the link above with your actual YouTube URL after uploading)*

---

## 📌 Project Overview

CPU scheduling is one of the most fundamental — and often misunderstood — concepts in Operating Systems. Most students learn it through textbooks and static diagrams. This project changes that.

**CPU Scheduling Visualizer** is a full-stack desktop application (built with Python + Flet) that lets you:
- Input your own processes
- Choose a scheduling algorithm
- Watch the Gantt chart render in real time
- Compare performance metrics instantly
- Monitor your actual system processes and CPU cores — live

Whether you're a student trying to understand preemption, or a developer curious how your OS manages threads, this tool makes it visual and interactive.

---

## 🚀 Features

| Feature | Description |
|--------|-------------|
| 🎨 **Gantt Chart Visualization** | Color-coded, proportional blocks per process |
| 📊 **Performance Metrics Table** | Waiting, Turnaround, Start, Finish times per process |
| 📈 **Summary Statistics** | Avg Waiting Time, Avg Turnaround, CPU Utilization % |
| 🔁 **Context Switch Counter** | Displayed after SRTF runs |
| 🖥️ **Live System Monitor** | Top 10 real OS processes via psutil, auto-refreshed every 2s |
| ⚙️ **CPU Core Usage Bars** | Color-coded progress bars per core (green/orange/red) |
| ➕ **Dynamic Process Input** | Add/remove processes on the fly |
| 🧹 **Clear & Reset** | Reset everything with one click |

---

## 🧠 Scheduling Algorithms

| Algorithm | Type | Description |
|-----------|------|-------------|
| **FCFS** | Non-preemptive | First Come First Serve — simplest, in order of arrival |
| **SJF** | Non-preemptive | Shortest Job First — picks shortest burst from ready queue |
| **SRTF** | ✅ Preemptive | Shortest Remaining Time First — preempts on shorter arrival |
| **Round Robin** | ✅ Preemptive | Fixed time quantum, cyclic execution |

---

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **UI Framework:** [Flet](https://flet.dev/) (Flutter-powered desktop apps in Python)
- **System Monitoring:** `psutil`
- **Terminal Mode:** `colorama`, `tabulate`

---

## 📁 Project Structure

```
cpu-scheduler/
├── app.py          ← Flet GUI entry point
├── main.py         ← Terminal/CLI entry point
├── scheduler.py    ← FCFS, SJF, SRTF, Round Robin logic
├── metrics.py      ← Waiting/Turnaround calculations
├── monitor.py      ← Real system process monitor (terminal)
├── visualizer.py   ← Terminal Gantt chart (colorama)
└── requirements.txt
```

---

## ⚙️ How to Run

### Prerequisites
```bash
pip install -r requirements.txt
```

### Launch the GUI (Recommended)
```bash
python app.py
```

### Launch the Terminal Version
```bash
python main.py
```

---

## 📷 Usage Guide

1. **Add processes** — Enter PID, Arrival Time, and Burst Time, then click *Add Process*
2. **Select algorithm** — Choose from FCFS, SJF, SRTF, or Round Robin
3. **Set Quantum** *(Round Robin only)* — Enter the time quantum (default: 2)
4. **Click Run** — Gantt chart and metrics render instantly
5. **Switch tabs** — View the metrics table or the live system monitor
6. **Remove a process** — Hit the ✕ button next to any process in the list

---

## 🧪 Test Case for Verification

Use this input to verify SRTF correctness:

| PID | Arrival | Burst |
|-----|---------|-------|
| P1  | 0       | 8     |
| P2  | 1       | 4     |
| P3  | 2       | 9     |
| P4  | 3       | 5     |

**Expected Results (SRTF):**
- Average Waiting Time: **6.50**
- Context Switches: **~9**

---

## 🎯 Learning Outcomes

- Understand preemptive vs. non-preemptive scheduling
- Visualize how arrival time and burst time affect execution order
- See the tradeoff between context switches and waiting time
- Compare algorithm efficiency through real metrics

---

## 📄 Technical Report (STAR Format)

### 🔴 Situation
The primary challenge was implementing **SRTF (preemptive SJF)** correctly. At every clock tick, the algorithm must check all arrived processes, compare remaining burst times, and preempt the current process if a shorter one arrives — all while accurately tracking context switches and merging consecutive Gantt blocks of the same process.

A secondary challenge was building a **real-time system monitor** inside a GUI that refreshes automatically without freezing the UI thread.

### 🟡 Task
I was building on top of an existing terminal-based CPU scheduling simulator that only supported FCFS, SJF, and Round Robin. The goal was to add SRTF scheduling and a live process monitor — and then wrap everything in a fully interactive GUI using Flet.

### 🟢 Action
- Implemented `srtf()` in `scheduler.py` with a tick-by-tick simulation loop, maintaining `remaining` burst per process, tracking context switches by detecting PID changes, and merging consecutive Gantt blocks
- Handled edge cases: ties broken by arrival time, clock advancing to next arrival when no process is ready
- Used Python's `threading` module to run the system monitor refresh loop as a daemon thread, calling `page.update()` safely without blocking the main UI
- Designed the Flet UI with a fixed left control panel and a tabbed right panel, ensuring the Gantt chart, metrics table, and system monitor each had independent scroll and update logic

### ✅ Result
- SRTF produces the correct average waiting time of **6.50** on the reference test case
- The GUI renders full Gantt charts, performance tables, and CPU core usage bars in real time
- The system monitor refreshes every 2 seconds without any UI freezing
- Both the GUI (`app.py`) and the original terminal (`main.py`) entry points work independently

---

## 🤝 Contributing

Contributions are welcome! Fork the repo and submit a pull request for:
- Additional algorithms (Priority Scheduling, HRRN, Multilevel Queue)
- Animation/step-through mode for the Gantt chart
- Export Gantt chart as PNG or PDF

---

## 📄 License

This project is open-source under the **MIT License**.

---

## 👤 Author

**Tousif Muhimine**
- GitHub: [@tousifmuhimine](https://github.com/tousifmuhimine)
- Repository: [CPU-Scheduling-Visualizer](https://github.com/tousifmuhimine/CPU-Scheduling-Visualizer)
