import json
import numpy as np
import matplotlib.pyplot as plt
from colors import colors
from pprint import pprint
from colorama import Fore

from pulse_helper import timeline_merge


def calculate_difference(num1, num2):
    if num1 - num2 < 1:
        return round(num1 - num2, 2)
    else:
        return round(num1 - num2, 1)


def get_all_channels(pulses):
    channel_list = []
    for time, _ in pulses.items():
        for _, channels in pulses[time].items():
            if len(channels) == 0:
                continue
            for channel in channels:
                if channel not in channel_list:
                    channel_list.append(channel)
    return channel_list


def flatten(arr):
    fin_arr = []
    for i in range(len(arr)):
        fin_arr.extend(arr[i])
    return fin_arr


def load_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data


def get_filtered_on_off_times(on_off_times):
    filtered_on_off = {}
    for time in on_off_times:
        filtered_on_off[time] = {}
        for k, v in on_off_times[time].items():
            if len(v) != 0:
                filtered_on_off[time][k] = v

    filtered_items = {}

    for times in filtered_on_off:
        keys_for_time = list(filtered_on_off[times].keys())
        if len(keys_for_time) > 1:
            for i in list(filtered_on_off[times])[:-1]:
                raise TypeError(
                    f"-------Clash in On-Off timings at {
                        times}ns -------- \n [Note: Minimum possible delay between on and off commands are is 10 ns]"
                )
                # filtered_items[times + 0.010] = {i: filtered_on_off[times].pop(i)} # actually throw error here instead of appending another element (only throw error if the channels differ)
    merged = filtered_on_off | filtered_items
    return merged


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

    return get_filtered_on_off_times(on_off)


def merge_channels(on_off_times, channel_list, sorted_pulses):
    channel_dic = {}

    for pulse in sorted_pulses_start:
        start, duration, channels = pulse[1].keys()
        for channel in pulse[1][channels]:
            if channel in channel_list:
                try:
                    channel_dic[channel].append(
                        [pulse[1][start], pulse[1][duration]])
                except:
                    channel_dic.update(
                        {str(channel): [[pulse[1][start], pulse[1][duration]]]}
                    )

    try_sorted_on_off = {}
    for channel in channel_list:
        merged = timeline_merge(np.array(channel_dic[channel]))
        for current in merged:
            t_start = current[0]
            t_stop = current[1] + current[0]
            for start, seq in on_off_times.items():
                for command, channels in on_off_times[start].items():
                    if channel in channels:
                        if start != t_start and command == "on":
                            channels.remove(channel)
            try:
                try_sorted_on_off[t_start]["on"].append(channel)
            except:
                try_sorted_on_off.update({t_start: {"on": []}})
                try_sorted_on_off[t_start]["on"].append(str(channel))

            try:
                try_sorted_on_off[t_stop]["off"].append(channel)
            except:
                try_sorted_on_off.update({t_stop: {"off": []}})
                try_sorted_on_off[t_stop]["off"].append(str(channel))
    return try_sorted_on_off


def print_sequence(on_off_pulses):
    keys = list(on_off_pulses.keys())
    # print(on_off_pulses)
    for i in range(len(keys)):
        if i == 0:
            if keys[i] == 0.0:
                print(
                    Fore.YELLOW,
                    "Adjusted Sequence to start at 0.01 us due to time constrains",
                    Fore.RESET,
                )
            for k, v in reversed(on_off_pulses[keys[i]].items()):
                if len(v) != 0:
                    print(
                        f"hvis.dio_send_trigger('Turn {k} triggers', dio_module, {
                            v}, {k}, 0.010)"
                    )
        else:
            for k, v in reversed(on_off_pulses[keys[i]].items()):
                if len(v) != 0:
                    print(
                        f"hvis.dio_send_trigger('Turn {k} triggers', dio_module, {v}, {k}, {
                            calculate_difference(keys[i], keys[i-1])})"
                    )


def plot_pulses(pulses, group_name, duration, colors):
    if duration == 0.0:
        return
    c = 0
    offset = 1
    y_ticks = []
    y_text = []
    for pulse in pulses:
        off_x_1 = np.arange(0, pulse[1]["Start"])
        off_y_1 = np.zeros_like(off_x_1) + offset
        plt.plot(off_x_1, off_y_1, color=colors[c])
        plt.vlines(x=pulse[1]["Start"], ymin=offset,
                   ymax=offset + 1, color=colors[c])
        on_x = np.arange(pulse[1]["Start"], pulse[1]
                         ["Start"] + pulse[1]["Duration"])
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
        y_ticks.append(offset)
        y_text.append(f"{pulse[0]} ({pulse[1]["Channels"]})")
        offset += 2
        c += 1
    plt.plot(
        np.arange(0, duration), np.zeros_like(np.arange(0, duration)), color="black"
    )
    plt.yticks(y_ticks, y_text)
    plt.title(f"Pulse Sequence for {group_name}")
    plt.grid(True)
    plt.show()


data = load_json("./sequences/test_json.json")

for group in data["groups"]:
    # Sorts all Pulses by the start time
    sorted_pulses_start = sorted(
        group["Pulses"].items(), key=lambda x: (x[1]["Start"], x[1]["Duration"])
    )
    on_off_times = get_on_off(sorted_pulses_start)
    channel_list = get_all_channels(on_off_times)

    merged_on_off = merge_channels(
        on_off_times, channel_list, sorted_pulses_start)

    sorted_on_off = dict(sorted(merged_on_off.items(), key=lambda x: x))

    print_sequence(sorted_on_off)
    plot_pulses(group["Pulses"].items(), group["name"],
                group["Duration"], colors)
