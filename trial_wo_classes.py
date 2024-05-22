from typing import OrderedDict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

file_name = "Pulse_Manager.xlsx"
sheet_1 = "Pulse_Queue"


df = pd.read_excel(file_name, sheet_name=sheet_1)
sorted_df = df.sort_values("Start Time")


def read_pulses(df):
    sorted_df = df.sort_values("Start Time")
    pulses_in_queue = {}
    for index, row in sorted_df.iterrows():
        if row["Pulse_Name"] not in pulses_in_queue:
            pulses_in_queue[row["Pulse_Name"]] = {
                1: {"Start Time": row["Start Time"], "End Time": row["End Time"]}
            }
        else:
            last_index = list(pulses_in_queue[row["Pulse_Name"]].keys())[-1]
            pulses_in_queue[row["Pulse_Name"]][last_index + 1] = {
                "Start Time": row["Start Time"],
                "End Time": row["End Time"],
            }
    return pulses_in_queue

def plot_sequence(pulses_in_queue):
    max_end_time = max(pulse[sub_pulse]["End Time"] for pulse in pulses_in_queue.values() for sub_pulse in pulse)
    x_range = np.arange(0, max_end_time)
    
    offset = 1
    colormap = plt.get_cmap("tab20", len(pulses_in_queue.keys()))
    
    for pulse_idx, pulse in enumerate(pulses_in_queue.keys()):
        color = colormap(pulse_idx)
        sub_pulses = pulses_in_queue[pulse]
        sorted_sub_pulses = sorted(sub_pulses.values(), key=lambda sp: sp["Start Time"])

        for sub_pulse in sorted_sub_pulses:
            start_time = sub_pulse["Start Time"]
            end_time = sub_pulse["End Time"]
            
            x = np.arange(start_time, end_time)
            height = 1 + offset
            y = np.full((len(x)), height)
            
            plt.plot(x, y, label=f"Pulse {pulse}" if sub_pulse == sorted_sub_pulses[0] else "", color=color)
            plt.vlines(x=[x[0], x[-1]], ymin=height - 1, ymax=height, color=color)
            
            mid_x = (start_time + end_time) / 2
            plt.text(mid_x, height - 0.5, '1', ha='center', va='center', color=color, fontsize=12)
        
        previous_end = 0
        for sub_pulse in sorted_sub_pulses:
            start_time = sub_pulse["Start Time"]
            plt.hlines(y=height - 1, xmin=previous_end, xmax=start_time, color=color)
            previous_end = sub_pulse["End Time"]
        plt.hlines(y=height - 1, xmin=previous_end, xmax=max_end_time, color=color)

        offset += 2
    
    plt.plot(x_range, np.zeros(len(x_range)), color='black')

    x_ticks = np.linspace(start=min(x_range), stop=max(x_range), num=10)
    plt.xticks(x_ticks,['%d' % np.ceil(val) for val in x_ticks])
    plt.yticks([],[])

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc="lower right")
    
    plt.xlabel("Time")
    plt.ylabel("Channels")
    plt.title("Pulse Sequence Plot")
    
    plt.show()

pulses_in_queue = read_pulses(df)
plot_sequence(pulses_in_queue)
