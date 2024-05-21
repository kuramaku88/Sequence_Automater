import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from py_pulse import *
from pulse_helper import *

file_name = "Pulse_Manager.xlsx"
sheet_1 = "Pulse_Queue"
sheet_2 = "Pulse_Definition"

# pulse_queue = pd.read_excel(file_name, sheet_name=sheet_1)
pulse_definition = pd.read_excel(file_name, sheet_name=sheet_2)
pulse_names = pulse_definition.columns[1:]
pulse_list = []
pulse_dic = {}
pulse_queue = Pulse_Queue(pd.read_excel(file_name, sheet_name=sheet_1))

for name in pulse_names:
    pulse_list.append(Pulse(name, pulse_definition[name]))
    pulse_dic.update({name: Pulse(name, pulse_definition[name])})

channels = load_channels(pulse_queue, pulse_dic, 28)

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
    if(i-delay==0):
        command_delay = 10
    else:
        command_delay = i - delay
    if command[1] == 1:
        print(channel_on_off("Turn on channels", "DIO_1", str(on_time(channels)[str(i)]), "on", str(command_delay)))
    else:
        print(channel_on_off("Turn on channels", "DIO_1", str(off_time(channels)[str(i)]), "off", str(command_delay)))
    delay = delay +command[0] - old
    old = command[0]

for j in combined:
    print(j)