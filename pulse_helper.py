import numpy as np
from py_pulse import Pulse_Queue, Pulse, Channel
import matplotlib.pyplot as plt
from pandas import DataFrame
from typing import Optional


def timeline_merge(timeline: list[Optional[list[int]]]) -> list[Optional[list[int]]]:
    if len(timeline) > 1:
        timeline = timeline[timeline[:, 0].argsort()]
        merged = np.array([])
        for i in range(1, len(timeline)):
            if np.array_equal(merged, np.empty_like(merged)):
                start_o = timeline[i - 1][0]
                stop_o = timeline[i - 1][0] + timeline[i - 1][1]
                start_n = timeline[i][0]
                stop_n = timeline[i][0] + timeline[i][1]

                if start_n <= stop_o:
                    if stop_o > stop_n:
                        merged = np.array([[start_o, stop_o - start_o]])
                    else:
                        merged = np.array([[start_o, stop_n - start_o]])

                else:
                    merged = np.array([[start_o, stop_o - start_o]])
                    merged = np.vstack([merged, [start_n, stop_n - start_n]])

            else:
                start_o = merged[-1][0]
                stop_o = merged[-1][0] + merged[-1][1]
                start_n = timeline[i][0]
                stop_n = timeline[i][0] + timeline[i][1]

                if start_n <= stop_o:
                    merged[-1] = start_o, stop_n - start_o

                else:
                    merged = np.vstack([merged, [start_n, stop_n - start_n]])
    else:
        merged = timeline
    return merged


def load_channels(
    pulse_queue: Pulse_Queue, pulse_dic: dict[str:Pulse], ch_no=28
) -> list[Channel]:
    ch = 0
    channels = [Channel() for i in range(ch_no)]
    for name in pulse_queue.definition["Pulse_Name"]:
        for k in range(len(pulse_dic[name].channel_mode())):
            mode = pulse_dic[name].channel_mode()[k]
            start_time = pulse_queue.definition["Start Time"][ch]
            pulse_length = pulse_queue.definition["Pulse Length"][ch]
            if mode == 1:
                # print(j, "Channel", k, "On", start_time, pulse_length)
                channels[k].append_timeline(np.array([start_time, pulse_length]), 0)
            elif mode == 2:
                # print(j, "Channel", k, "Sweep", start_time, pulse_length)
                channels[k].append_timeline(np.array([start_time, pulse_length]), 1)
        ch = ch + 1
    return channels


def df_load_channels(comb_df: DataFrame) -> list[Channel]:
    num_channels = 28
    channels = [Channel() for _ in range(num_channels)]

    for i in range(num_channels):
        channel_col = f"Ch{i}"
        filtered_df = comb_df.query(f"{channel_col} != 'Off'")[
            ["Pulse_Name", "Start Time", "Pulse Length", channel_col]
        ]

        # print(filtered_df.head())
        on_condition = filtered_df[channel_col] == "On"
        sweep_condition = ~on_condition

        on_timeline = filtered_df.loc[
            on_condition, ["Start Time", "Pulse Length"]
        ].to_numpy()
        sweep_timeline = filtered_df.loc[
            sweep_condition, ["Start Time", "Pulse Length"]
        ].to_numpy()

        for timeline in on_timeline:
            channels[i].append_timeline(timeline, 0)

        for timeline in sweep_timeline:
            channels[i].append_timeline(timeline, 1)

    return channels


def channel_plotter(channels: list[Channel], n=28):
    ch_ct = 0
    # Creates a color map to ensure that each plot has a different color
    col_lin = np.linspace(0, 1, 50)
    np.random.seed(42)
    np.random.shuffle(col_lin)
    color = iter(plt.cm.rainbow(col_lin))

    fig, ax = plt.subplots(n, 1, sharex=True)
    # Remove horizontal space between axes
    fig.subplots_adjust(hspace=0)

    # Loops through each channel and plots the waveform for the channel
    # I have fixed it, but I think I can improve on how I have written it
    for ch in channels[:n]:
        c = next(color)
        print(timeline_merge(ch.timeline))
        for i in timeline_merge(ch.timeline):
            
            ax[ch_ct].plot([i[0], i[0] + i[1]], np.zeros_like(i) + 1, color=c)
            for ch_vert in (i[0], i[0] + i[1]):
                ax[ch_ct].axvline(ch_vert, 0.0, 0.91, color=c)
            ax[ch_ct].grid(True)
            ax[ch_ct].set_yticks([])
            ax[ch_ct].set_ylim(0, 1.1)
            ax[ch_ct].set_xlim(0, 1000)
            ax[ch_ct].set_ylabel("Ch_" + str(ch_ct), rotation = 0)
            # ax.set_title("Channel"+str(ch_ct-1))
        ch_ct += 1  # Append the channel number
    plt.savefig("Image.jpg")
    plt.show()
    


# TODO: rename this function and write documentation cuz gawddamn this name is confusing
def on_time(channels: list[Channel]) -> dict[str : list[int]]:
    ontime = {}
    ch = 0
    for j in channels:
        for i in timeline_merge(j.timeline):
            try:
                ontime[str(i[0])].append(ch)
            except:
                ontime.update({str(i[0]): [ch]})
        ch += 1
    return ontime


def off_time(channels: list[Channel]) -> dict[str : list[int]]:
    offtime = {}
    ch = 0
    for j in channels:
        for i in timeline_merge(j.timeline):
            try:
                offtime[str(i[0] + i[1])].append(ch)
            except:
                offtime.update({str(i[0] + i[1]): [ch]})
        ch += 1
    return offtime

# Fix the command
def channel_on_off(
    name: str, engine: str, channels: list[int], on_off: str, delay=10
) -> str:
    return f'hvis.dio_output("{name}",{engine},{channels},"{on_off}", delay={delay})'

def code_gen(
        channels: list[Channel], script_name: str
) -> None:
    
    on = np.sort(np.array(list(on_time(channels).keys()), dtype=int))
    off = np.sort(np.array(list(off_time(channels).keys()), dtype=int))

    combined_on = np.array([[j, 1] for j in on])
    combined_off = np.array([[j, 0] for j in off])
    combined = np.vstack([combined_on, combined_off])
    combined = combined[np.argsort(combined[:, 0])]

    # Reading the beginning and the ending of the file, which will stay the same for now
    with open("template_ini.txt", "r") as file:
        temp_ini = file.read()

    with open("template_end.txt", "r") as file:
        temp_end = file.read()

    # Write the initialisation section to the generated script
    with open(script_name, "w") as file: 
        file.write(temp_ini+'\n')

    delay = 0
    old = 0    

    for command in combined:
        i = command[0]
        
        if i - delay < 10:
            raise TypeError(f"-------Clash in On-Off timings at {delay}ns -------- \n [Note: Minimum possible delay between on and off commands are is 10 ns]")
        else:
            command_delay = i - delay
        
        if command[1] == 1:
            command_text = channel_on_off("Turn on channels", "DIO_1", str(on_time(channels)[str(i)]), "on", str(command_delay),)
            with open(script_name, "a") as file: 
                file.write('\t\t'+command_text+'\n') 

        else:
            command_text = channel_on_off("Turn off channels", "DIO_1", str(off_time(channels)[str(i)]), "off", str(command_delay))
            with open(script_name, "a") as file: 
                file.write('\t\t'+command_text+'\n') 

        delay = delay + command[0] - old
        old = command[0]

    with open(script_name, "a") as file: 
        file.write(temp_end)
