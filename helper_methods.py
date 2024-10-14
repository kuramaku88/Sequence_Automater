import json
import numpy as np
import matplotlib.pyplot as plt
import os
import copy

from colors import colors
from pprint import pprint
from colorama import Fore
from typing import Optional
# from pulse_helper import timeline_merge

modules_path = "./scripts/modules/"
templates_path = "./scripts/templates/"
script_path = "./scripts/py_scripts/"
reset_path = "./scripts/reset/"

def delete_files_in_directory(directory_path):
   try:
     files = os.listdir(directory_path)
     for file in files:
       file_path = os.path.join(directory_path, file)
       if os.path.isfile(file_path):
         os.remove(file_path)
     print(f"Directory cleared: {directory_path} \n")
   except OSError:
     print("Error occurred while deleting files.")

def calculate_difference(num1, num2):
    if num1 - num2 < 1:
        return round(num1 - num2, 2)
    else:
        return round(num1 - num2, 1)

def get_all_channels(pulses):
    channel_list = []
    for time , _ in pulses.items():
        for _ , channels in pulses[time].items():
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

# Method to load json file into a python variable
def load_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data

# Method that returns a list of on_off_times
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
                raise TypeError(f"-------Clash in On-Off timings at {times}ns -------- \n [Note: Minimum possible delay between on and off commands are is 10 ns]")
                # filtered_items[times + 0.010] = {i: filtered_on_off[times].pop(i)} # actually throw error here instead of appending another element (only throw error if the channels differ)
    merged = filtered_on_off | filtered_items
    return merged

# Get a list of on_off times from pulses
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

def get_on_times(commands):
    on = {}

    for command in commands:
        start = command[1]["Start"]
        Sweep_Reg_Number = command[1]["Sweep_Reg_Number"]
        Rising_Edge_Delay = command[1]["Rising_Edge_Delay"]
        Falling_Edge_Delay = command[1]["Falling_Edge_Delay"]
        Rising_Edge_Increment = command[1]["Rising_Edge_Increment"]
        Falling_Edge_Increment = command[1]["Falling_Edge_Increment"]
        Channels = command[1]["Channels"]

        if start in on:
            raise TypeError(f"-------Sweeps of different configurations starting at the same time -------- \n [Note: There is a delay between initialising different sweeps]")
        else: 
            on[start] = {"Sweep": [Sweep_Reg_Number, Rising_Edge_Delay, Falling_Edge_Delay, Rising_Edge_Increment, Falling_Edge_Increment, Channels]}
    return on


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


# Method that merges the timeslines for each channel from different pulses in the same module
def merge_channels(on_off_times, channel_list, sorted_pulses):
    channel_dic = {}

    for pulse in sorted_pulses:
        start, duration, channels, tags = pulse[1].keys()
        for channel in pulse[1][channels]:
            if channel in channel_list:
                try:
                    channel_dic[channel].append([pulse[1][start], pulse[1][duration]])
                except:
                    channel_dic.update({str(channel): [[pulse[1][start], pulse[1][duration]]]})
    
    try_sorted_on_off = {}
    # print(channel_dic)
    for channel in channel_list:
        merged = timeline_merge(np.array(channel_dic[str(channel)]))
        for current in merged:
            t_start = current[0]
            t_stop = current[1] + current[0]
            for start, seq in on_off_times.items():
                for command, channels in on_off_times[start].items():
                    if channel in channels:
                        if start!=t_start and command=="on":
                            channels.remove(channel)
            try:
                try_sorted_on_off[t_start]['on'].append(str(channel))
            except:
                try_sorted_on_off.update({t_start: {'on': []}})
                try_sorted_on_off[t_start]['on'].append(str(channel))

            try:
                try_sorted_on_off[t_stop]['off'].append(str(channel))
            except:
                try_sorted_on_off.update({t_stop: {'off': []}})
                try_sorted_on_off[t_stop]['off'].append(str(channel))

    return try_sorted_on_off

def add_delay(command_dic, command_type):
    command_dic = copy.deepcopy(command_dic)

    if command_type == "Pulses":
        for key in command_dic:
            command_dic[key]["delay"] = 10/1000

    if command_type == "Sweeps":
        for key in command_dic:
            sweep_ch_no = len(command_dic[key]['Sweep'][-1])
            delay = (50+sweep_ch_no*30)/1000
            if key<delay:
                raise TypeError(f"-------Clash in Sweep delay and Sweep Start timings at {key}us -------- \n ", key)
            command_dic[key]["delay"] = delay
            
    return command_dic


# def Merge(dict1, dict2):
#     # Check conflict before merging commands
#     key_delay_pairs_1 = [(key, value['delay']) for key, value in dict1.items()]
#     key_delay_pairs_2 = [(key, value['delay']) for key, value in dict2.items()]
    
#     # retrive 

#     for pair1 in key_delay_pairs_1:
#         for pair2 in key_delay_pairs_2:
#             if abs(pair1[0]-pair2[0]) <  0.01:
#                 time = pair1[0]
#                 raise TypeError(f"-------Clash in command timings at {time}us -------- \n ")
            
#     print(key_delay_pairs_1)
#     print(key_delay_pairs_2)
#     print("Hello")
#     dict1.update(dict2)
#     return dict1


def Merge(dict1, dict2):
    # Check conflict before merging commands
    # for now dict1 is for pulses and dict2 is for sweeps
    key_delay_pairs_1 = [(key, value['delay']) for key, value in dict1.items()]
    key_delay_pairs_2 = [(key, value['delay']) for key, value in dict2.items()]
    # retrive 

    for pair1 in key_delay_pairs_1:
        for pair2 in key_delay_pairs_2:
            if abs(pair1[0]-pair2[0]) <  0.01:
                time = pair1[0]
                raise TypeError(f"-------Clash in command timings at {time}us -------- \n ")
    
    for pair1 in key_delay_pairs_1:
        for pair2 in key_delay_pairs_2:
            if pair1[0] < pair2[0] and pair1[0] > pair2[0]-pair2[1]:
                time = pair1[0]
                raise TypeError(f"-------Clash in command timings at {time}us -------- \n ")

    dict1.update(dict2)
    sorted_dict1 = dict(sorted(dict1.items()))
    return sorted_dict1

def module_reset_sequence(command_dic, module_name):
    previous_delay = 0
    
    # Define file paths
    module_file_path = os.path.join(modules_path, f"{module_name}.txt")
    reset_file_path = os.path.join(reset_path, f'{module_name}_sweep_reset.txt')
    # Initialize the command and reset files
    os.makedirs(os.path.dirname(module_file_path), exist_ok=True)
    with open(module_file_path, 'w') as module_file:
        module_file.write("### Commands for " + module_name + '\n')
        module_file.close()
    os.makedirs(os.path.dirname(reset_file_path), exist_ok=True)
    with open(reset_file_path, 'w') as reset_file:
        reset_file.write("### Reset commands for " + module_name + '\n')
        reset_file.close()
    
    for command_time in sorted(command_dic.keys()):
        details = command_dic[command_time]
        delay = details.get("delay", 0)
        command_type_keys = [key for key in details.keys() if key != "delay"]
        
        if len(command_type_keys) != 1:
            print("Error: Command should have exactly one type ('on', 'off', 'Sweep')")
            continue
        
        command_type = command_type_keys[0]
        calc_delay = (command_time - previous_delay) * 1000
        
        if command_type == "on" or command_type == "off":
            command_channels = details[command_type]
            command_channels = list(map(int, command_channels))
            print(command_type)
            print("Command channels", command_channels)
            command_text = (
                f"\thvis.dio_send_trigger('Turn {command_type} triggers', "
                f"{module_name}, {command_channels}, '{command_type}', {calc_delay})"
            )
            previous_delay = command_time

        elif command_type == "Sweep":
            Sweep_Reg_Number, Rising_Edge_Delay, Falling_Edge_Delay, \
            Rising_Edge_Increment, Falling_Edge_Increment, command_channels = details[command_type]
            
            command_text = (
                f"\thvis.dio_sweep('Sweeping {command_channels}', {module_name}, {command_channels}, "
                f"{Sweep_Reg_Number}, {Rising_Edge_Increment}, {Falling_Edge_Increment}, {calc_delay})"
            )

            reset_text = (
                f"\thvis.dio_sweep_reset('Reset sweeping {command_channels}', {module_name}, {command_channels}, "
                f"{Sweep_Reg_Number}, {Rising_Edge_Delay}, {Falling_Edge_Delay})"
            )
            # Write the reset command to the reset file
            with open(reset_file_path, "a") as file:
                file.write(reset_text+"\n")
            
            previous_delay = command_time

        # Write the command to the module file
        with open(module_file_path, 'a') as module_file:
            module_file.write(command_text + '\n')

# Method that saves the sequence for each module in a separate file in the modules folder
# def print_sequence(on_off_pulses, module_name):
#     keys = list(on_off_pulses.keys())
    
#     with open(modules_path+module_name+'.txt','w') as file:
#         file.write("### Commands for " + module_name+'\n')

#     for i in range(len(keys)):
#         if i == 0:
#             if keys[i] == 0.0:
#                 print(module_name)
#                 print(
#                     Fore.YELLOW,
#                     "Adjusted Sequence to start at 0.01 us due to time constrains",
#                     Fore.RESET,
#                 )
#             for k, v in reversed(on_off_pulses[keys[i]].items()):
#                 if len(v) != 0:
#                     tag = str(v).replace('\'', '')
#                     command_text = f"\t\thvis.dio_send_trigger('Turn {k} triggers: {tag}', {module_name}, {v}, {k}, 10)"

#                     with open(modules_path+module_name+'.txt', 'a') as file:
#                         file.write(command_text+'\n')
#         else:
#             for k, v in reversed(on_off_pulses[keys[i]].items()):
#                 if len(v) != 0:
#                     tag = str(v).replace('\'', '')
#                     command_text = f"\t\thvis.dio_send_trigger('Turn {k} triggers {tag}', {module_name}, {v}, {k}, {calculate_difference(keys[i], keys[i-1])*1000})"

#                     with open(modules_path+module_name+'.txt', 'a') as file:
#                         file.write(command_text+'\n')


def print_sequence(on_off_pulses, module_name):
    keys = list(on_off_pulses.keys())
    
    with open(modules_path+module_name+'.txt','w') as file:
        file.write("### Commands for " + module_name+'\n')

    for i in range(len(keys)):
        if i == 0:
            if keys[i] == 0.0:
                print(module_name)
                print(
                    Fore.YELLOW,
                    "Adjusted Sequence to start at 0.01 us due to time constrains",
                    Fore.RESET,
                )
            for k, v in reversed(on_off_pulses[keys[i]].items()):
                if len(v) != 0:
                    tag = str(v).replace('\'', '')
                    command_text = f"\t\thvis.dio_send_trigger('Turn {k} triggers: {tag}', {module_name}, {v}, {k}, 10)"

                    with open(modules_path+module_name+'.txt', 'a') as file:
                        file.write(command_text+'\n')
        else:
            for k, v in reversed(on_off_pulses[keys[i]].items()):
                if len(v) != 0:
                    tag = str(v).replace('\'', '')
                    command_text = f"\t\thvis.dio_send_trigger('Turn {k} triggers {tag}', {module_name}, {v}, {k}, {calculate_difference(keys[i], keys[i-1])*1000})"

                    with open(modules_path+module_name+'.txt', 'a') as file:
                        file.write(command_text+'\n')

# Method to generate timing plots for pulses 
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

# Method that generates the script
def script_gen(modules_path, sweep_reset_path, script_path, script_name):
    
    modules = os.listdir(modules_path)
    resets = os.listdir(sweep_reset_path)

    
    template_ini_path ='scripts\\templates\\template_ini.txt'
    template_mid_path ='scripts\\templates\\template_mid.txt'
    template_end_path = 'D:\MPQ\scripts\\templates\\template_end.txt'

    with open(template_ini_path, 'r') as file:
        template_ini = file.read()

    with open(template_mid_path, 'r') as file:
        template_mid = file.read()
    
    with open(template_end_path, 'r') as file:
        template_end = file.read()

    with open(script_path+script_name, 'w') as file:
        file.write(template_ini+'\n')
    
    for reset_path in resets:
        with open(sweep_reset_path + reset_path, 'r') as file:
            reset_commands = file.read()
        
        with open(script_path+script_name, 'a') as file:
            file.write(reset_commands)
    
    with open(script_path+script_name, 'a') as file:
        file.write(template_mid+'\n')

    for module_sequence_path in modules:
        with open(modules_path + module_sequence_path, 'r') as file:
            module_sequence = file.read()
    
        with open(script_path+script_name, 'a') as file:
            file.write(module_sequence)
    
    with open(script_path+script_name, 'a') as file:
        file.write(template_end)
    
    print("python script generated \n")

######################################################################################
###############################---MAIN BODY---########################################
######################################################################################
