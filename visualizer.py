from colorama import Fore, Style, init


init(autoreset=True)

COLORS = [
    Fore.RED,
    Fore.GREEN,
    Fore.BLUE,
    Fore.YELLOW,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.WHITE,
]


def _colors_by_pid(timeline):
    pids = []
    for pid, _, _ in timeline:
        if pid not in pids:
            pids.append(pid)

    return {
        pid: COLORS[index % len(COLORS)]
        for index, pid in enumerate(pids)
    }


def draw_gantt(timeline):
    if not timeline:
        print("No timeline to display.")
        return

    colors = _colors_by_pid(timeline)
    block_widths = [
        max(5, (end - start) * 3)
        for _, start, end in timeline
    ]

    chart = ""
    markers = str(timeline[0][1])
    marker_position = len(markers)

    for index, (pid, _, end) in enumerate(timeline):
        width = block_widths[index]
        label = pid.center(width)
        chart += f"|{colors[pid]}{label}{Style.RESET_ALL}"

        boundary_position = len(_strip_color_codes(chart)) + 1
        spaces = max(1, boundary_position - marker_position - len(str(end)))
        markers += " " * spaces + str(end)
        marker_position = len(markers)

    chart += "|"
    print(chart)
    print(markers)


def _strip_color_codes(text):
    for color in COLORS + [Style.RESET_ALL]:
        text = text.replace(color, "")
    return text
