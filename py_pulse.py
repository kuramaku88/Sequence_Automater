import numpy as np
from pandas import DataFrame


class Pulse:
    def __init__(self, name: str, definition: DataFrame):
        self.name = name
        self.definition = definition

    # Returns a list with the channels and their states
    def channel_mode(self):
        channel = []
        for i in self.definition:
            if i == "Off":
                channel.append(0)
            elif i == "On":
                channel.append(1)
            elif i == "Sweep":
                channel.append(2)
        return channel

    # def pulse_on(self):
    #     print(commands['lvds_on']+self.name)

    # def pulse_off(self):
    #     print(commands['lvds_off']+self.name)


class Pulse_Queue:
    def __init__(self, definition: DataFrame):
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


class Channel:
    def __init__(
        self, timeline: list() = np.array([]), sweep_timeline: list() = np.array([])
    ):
        self.timeline = timeline
        self.sweep_timeline = sweep_timeline

    def append_timeline(self, pulse_time, sweep_enable):
        """
        Appends a given tuple of start time and pulse length to the timeline of the channel, asserting sswep_enable adds to the sweep timeline
        """
        if sweep_enable:
            if np.array_equal(self.sweep_timeline, np.empty_like(self.sweep_timeline)):
                self.sweep_timeline = np.array([pulse_time])
            else:
                self.sweep_timeline = np.vstack([self.sweep_timeline, pulse_time])
        else:
            if np.array_equal(self.timeline, np.empty_like(self.timeline)):
                self.timeline = np.array([pulse_time])
            else:
                self.timeline = np.vstack([self.timeline, pulse_time])
