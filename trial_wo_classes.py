import json
import numpy as np
import matplotlib.pyplot as plt
from colors import colors


def flatten(arr):
    fin_arr = []
    for i in range(len(arr)):
        fin_arr.extend(arr[i])
    return fin_arr


def load_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data


def get_on_off(pulses):
    on_off = {}
    for pulse in pulses:
        start = pulse[1]["Start"]
        end = pulse[1]["Start"] + pulse[1]["Duration"]

        # Handle the "on" event
        if start not in on_off:
            on_off[start] = {"on": [], "off": []}
        on_off[start]["on"].extend(pulse[1]["Channels"])

        # Handle the "off" event
        if end not in on_off:
            on_off[end] = {"on": [], "off": []}
        for channel in pulse[1]["Channels"]:
            if channel not in on_off[end]["off"]:
                on_off[end]["off"].append(channel)
    return on_off


def print_sequence(on_off_pulses):
    keys = list(on_off_pulses.keys())

    for i in range(len(keys)):
        if i == 0:
            for k, v in reversed(on_off_pulses[keys[i]].items()):
                if len(v) != 0:
                    print(
                        f"hvis.dio_send_trigger('Turn {k} triggers', dio_module, {
                            v}, {k}, 0.010)"
                    )
        else:
            for k, v in reversed(on_off_pulses[keys[i]].items()):
                if len(v) != 0:
                    if k == "on" and len(on_off_pulses[keys[i]]["off"]) != 0:
                        print(
                            f"hvis.dio_send_trigger('Turn {k} triggers', dio_module, {
                                v}, {k}, 0.010)"
                        )
                    else:
                        print(
                            f"hvis.dio_send_trigger('Turn {k} triggers', dio_module, {
                                v}, {k}, {keys[i]-keys[i-1]})"
                        )


def plot_pulses(pulses, group_name, duration, colors):
    if duration == 0.0:
        return
    c = 0
    offset = 1
    for pulse in pulses:
        off_x_1 = np.arange(0, pulse[1]["Start"])
        off_y_1 = np.zeros_like(off_x_1) + offset
        plt.plot(off_x_1, off_y_1, color=colors[c])
        plt.vlines(x=pulse[1]["Start"], ymin=offset, ymax=offset + 1, color=colors[c])
        on_x = np.arange(pulse[1]["Start"], pulse[1]["Start"] + pulse[1]["Duration"])
        on_y = np.zeros_like(on_x) + offset + 1
        plt.plot(on_x, on_y, color=colors[c])
        off_x_2 = np.arange(pulse[1]["Start"] + pulse[1]["Duration"], duration)
        off_y_2 = np.zeros_like(off_x_2) + offset
        plt.plot(off_x_2, off_y_2, color=colors[c])
        plt.vlines(
            x=pulse[1]["Start"] + pulse[1]["Duration"],
            ymin=offset,
            ymax=offset + 1,
            color=colors[c],
        )
        offset += 2
        c += 1
    plt.plot(
        np.arange(0, duration), np.zeros_like(np.arange(0, duration)), color="black"
    )
    plt.title(f"Pulse Sequence for {group_name}")
    plt.grid(True)
    plt.show()


data = load_json("./sequences/test_json.json")

for group in data["groups"]:
    # Sorts all Pulses by the start time
    sorted_pulses_start = sorted(
        group["Pulses"].items(), key=lambda x: (x[1]["Start"], x[1]["Duration"])
    )

    on_off = get_on_off(sorted_pulses_start)
    sorted_on_off = dict(sorted(on_off.items(), key=lambda x: x))

    print_sequence(sorted_on_off)

    plot_pulses(group["Pulses"].items(), group["name"], group["Duration"], colors)
