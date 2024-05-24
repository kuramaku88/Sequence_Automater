import pandas as pd
import numpy as np

from py_pulse import Pulse, Pulse_Queue, Channel
from pulse_helper import (
    load_channels,
    on_time,
    off_time,
    channel_on_off,
    channel_plotter,
    df_load_channels,
)


file_name = "Pulse_Manager.xlsx"
sheet_1 = "Pulse_Queue"
sheet_2 = "Pulse_Definition"
sheet_3 = "Test_Pulse_Definition"

df = pd.read_excel(file_name, sheet_name=[sheet_1, sheet_2, sheet_3])
pulse_queue = Pulse_Queue(df[f"{sheet_1}"])
pulse_definition = df[f"{sheet_2}"]

pulse_names = pulse_definition.columns[1:]
pulse_list = [Pulse(name, pulse_definition[name]) for name in pulse_names]
pulse_dic = {name: Pulse(name, pulse_definition[name]) for name in pulse_names}

test = pd.merge(df[f"{sheet_1}"], df[f"{sheet_3}"], how="left", on="Pulse_Name")
bla = df_load_channels(test)

# TODO: Look at the df_load_channels function
channels = load_channels(pulse_queue, pulse_dic)

on = np.sort(np.array(list(on_time(channels).keys()), dtype=int))
off = np.sort(np.array(list(off_time(channels).keys()), dtype=int))

combined_on = np.array([[j, 1] for j in on])
combined_off = np.array([[j, 0] for j in off])
combined = np.vstack([combined_on, combined_off])
combined = combined[np.argsort(combined[:, 0])]

delay = 0
old = 0
for command in combined:
    i = command[0]
    if i - delay == 0:
        command_delay = 10
    else:
        command_delay = i - delay
    if command[1] == 1:
        print(
            channel_on_off(
                "Turn on channels",
                "DIO_1",
                str(on_time(channels)[str(i)]),
                "on",
                str(command_delay),
            )
        )
    else:
        print(
            channel_on_off(
                "Turn on channels",
                "DIO_1",
                str(off_time(channels)[str(i)]),
                "off",
                str(command_delay),
            )
        )
    delay = delay + command[0] - old
    old = command[0]

channel_plotter(channels, 5)

def sequence():
    print("HI")