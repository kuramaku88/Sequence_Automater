import numpy as np
from py_pulse import *
import matplotlib.pyplot as plt

def timeline_merge(timeline):
    if len(timeline) > 1:
        timeline = timeline[timeline[:, 0].argsort()]
        merged = np.array([])
        for i in range(1, len(timeline)):
            if np.array_equal(merged, np.empty_like(merged)):
                j = 0
                start_o = timeline[i-1][0]
                stop_o = timeline[i-1][0] + timeline[i-1][1]
                start_n = timeline[i][0]
                stop_n = timeline[i][0] + timeline[i][1]
                
                if start_n <= stop_o:
                    if stop_o>stop_n:
                        merged = np.array([[start_o, stop_o-start_o]])
                    else:
                        merged = np.array([[start_o, stop_n-start_o]])

                else:
                    merged = np.array([[start_o, stop_o-start_o]])
                    merged = np.vstack([merged, [start_n, stop_n-start_n]])

            else:
                start_o = merged[-1][0]
                stop_o = merged[-1][0] + merged[-1][1]
                start_n = timeline[i][0]
                stop_n = timeline[i][0] + timeline[i][1]

                if start_n <= stop_o:
                    merged[-1] = start_o, stop_n-start_o

                else:
                    merged = np.vstack([merged, [start_n, stop_n-start_n]])
    
    else:
        merged = timeline

    return merged

def load_channels(pulse_queue, pulse_dic, ch_no=28):
    ch = 0
    channels = [Channel() for i in range(ch_no)]
    for name in pulse_queue.definition["Pulse_Name"]:
        for k  in range(len(pulse_dic[name].channel_mode())):
            mode = pulse_dic[name].channel_mode()[k]
            start_time = pulse_queue.definition["Start Time"][ch]
            pulse_length = pulse_queue.definition["Pulse Length"][ch]
            if mode == 1:
                # print(j, "Channel", k, "On", start_time, pulse_length)
                channels[k].append_timeline(np.array([start_time, pulse_length]), 0)
            elif mode ==2:
                # print(j, "Channel", k, "Sweep", start_time, pulse_length)
                channels[k].append_timeline(np.array([start_time, pulse_length]), 1)
        ch = ch+ 1
    return channels


# def channel_plotter(channels, n = 28):
#     fig = plt.figure(figsize=(12,2.5*n))
#     ch_ct = 1

#     # Creates a color map to ensure that each plot has a different color
#     col_lin = np.linspace(0, 1, n)
#     np.random.seed(42)
#     np.random.shuffle(col_lin)
#     color = iter(plt.cm.rainbow(col_lin))

#     # Loops through each channel and plots the waveform for the channel
#     # I have fixed it, but I think I can improve on how I have written it
#     for ch in channels[:n]:
#         ax = plt.subplot(n, 1, ch_ct)
#         c = next(color)
#         for i in timeline_merge(ch.timeline):
#             ax.plot([i[0], i[0]+i[1]], np.zeros_like(i)+1, color = c)
#             for ch_vert in (i[0], i[0]+i[1]):
#                 ax.axvline(ch_vert, 0.0, 0.91,  color = c)
#             ax.grid(True)
#             ax.set_ylim(0,1.1)
#             ax.set_xlim(0, 1000)
#             ax.set_ylabel("Ch_"+str(ch_ct-1))
#             # ax.set_title("Channel"+str(ch_ct-1))
#         ch_ct+=1 # Append the channel number
#     plt.show()

def channel_plotter(channels, n = 28):
    ch_ct = 0
    # Creates a color map to ensure that each plot has a different color
    col_lin = np.linspace(0, 1, n)
    np.random.seed(42)
    np.random.shuffle(col_lin)
    color = iter(plt.cm.rainbow(col_lin))

    fig, ax = plt.subplots(n, 1, sharex=True)
    # Remove horizontal space between axes
    fig.subplots_adjust(hspace=0)

    # Loops through each channel and plots the waveform for the channel
    # I have fixed it, but I think I can improve on how I have written it
    for ch in channels[:n]:

        # ax = plt.subplot(n, 1, ch_ct)
        c = next(color)
        for i in timeline_merge(ch.timeline):
            ax[ch_ct].plot([i[0], i[0]+i[1]], np.zeros_like(i)+1, color = c)
            for ch_vert in (i[0], i[0]+i[1]):
                ax[ch_ct].axvline(ch_vert, 0.0, 0.91,  color = c)
            ax[ch_ct].grid(True)
            ax[ch_ct].set_yticks([])
            ax[ch_ct].set_ylim(0,1.1)
            ax[ch_ct].set_xlim(0, 1000)
            ax[ch_ct].set_ylabel("Ch_"+str(ch_ct))
            # ax.set_title("Channel"+str(ch_ct-1))
        ch_ct+=1 # Append the channel number
    plt.show()

def on_time(channels):
    ontime = {}
    ch = 0
    for j in channels:
        for i in timeline_merge(j.timeline):
            try:
                a = ontime[str(i[0])]
                ontime[str(i[0])].append(ch)
            except:
                ontime.update({str(i[0]): [ch]})
        ch+=1
    return ontime

def off_time(channels):
    offtime = {}
    ch = 0
    for j in channels:
        for i in timeline_merge(j.timeline):
            try:
                a = offtime[str(i[0]+i[1])]
                offtime[str(i[0]+i[1])].append(ch)
            except:
                offtime.update({str(i[0]+i[1]): [ch]})
        ch+=1
    return offtime

def channel_on_off(name, engine, channels, on_off, delay=10):
    return "hvis.sync_while(\"" + name + "\"," + engine + "," + channels + ",\"" + on_off + "\", delay=" + delay+")"