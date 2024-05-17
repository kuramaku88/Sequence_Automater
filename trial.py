import pandas as pd
import numpy as np
from pprint import pprint

commands = {"lvds_on": "ON LVDS Channel", "lvds_off": "OFF LVDS Channel"}
channels = np.zeros(28)


class Pulse:
    def __init__(self, name, definition):
        self.name = name
        self.definition = definition

    # Returns a list with the channels and their states
    def channel_mode(self):
        channel = []
        for i in self.definition:
            if i == "Off":
                channel.append((0, 0))
            elif i == "On":
                channel.append((1, 0))
            elif i == "Sweep":
                channel.append((1, 1))
        return channel

    def pulse_on(self):
        print(commands["lvds_on"] + self.name)

    def pulse_off(self):
        print(commands["lvds_off"] + self.name)


class Channel:
    def __init__(self, timeline=np.array([]), sweep_timeline=np.array([])):
        self.timeline = timeline
        self.sweep_timeline = sweep_timeline

    def append_timeline(self, time, sweep_enable):
        if sweep_enable:
            self.sweep_timeline = np.append(self.sweep_timeline, time)
        else:
            self.timeline = np.append(self.timeline, time)


class Pulse_Queue:
    def __init__(self, definition):
        self.definition = definition

    # Return a list with the each pulses start and ed time
    def queue_list(self):
        queue = self.definition.to_numpy()
        return queue

    def time_line(self, mode):
        queue = self.queue_list()
        start = queue[queue[:, 1].argsort()][:, (0, 1)]
        stop = queue[queue[:, 2].argsort()][:, (0, 2)]

        if mode == "start":
            return start
        else:
            return stop


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

pprint(pulse_dic)

pprint(pulse_dic["Pulse_1"])
