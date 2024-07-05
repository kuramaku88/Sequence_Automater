import json
import numpy as np
import matplotlib.pyplot as plt

from trial_wo_classes import *

def Merge(dict1, dict2):
    # Check conflict before merging commands
    # for now dict1 is for pulses and dict2 is for sweeps
    key_delay_pairs_1 = [(key, value['delay']) for key, value in dict1.items()]
    key_delay_pairs_2 = [(key, value['delay']) for key, value in dict2.items()]
    # retrive 

    pprint(dict1)
    pprint(dict2)

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
    print(sorted_dict1)
    print(dict1)
    return sorted_dict1

def module_reset_sequence(command_dic, module_name):
    previous_delay = 0
    
    # Define file paths
    module_file_path = os.path.join(modules_path, f"{module_name}.txt")
    reset_file_path = os.path.join(reset_path, f'{module_name}_sweep_reset.txt')
    print(module_file_path, reset_file_path)
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
            print(reset_text)
            # Write the reset command to the reset file
            with open(reset_file_path, "a") as file:
                file.write("test\n")
            
            previous_delay = command_time

        # Write the command to the module file
        with open(module_file_path, 'a') as module_file:
            module_file.write(command_text + '\n')
        # with open(reset_file_path, 'a') as reset_file:
        #         reset_file.write("Hello" + '\n')

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

def script_gen(modules_path, templates_path, script_path, script_name):
    
    modules = os.listdir(modules_path)

    template_end_path = 'D:\MPQ\scripts\\templates\\template_end.txt'
    template_ini_path ='scripts\\templates\\template_ini_new.txt'
    sweep_reset_path = 'D:\MPQ\scripts\\reset\sweep_reset.txt'
    
    with open(template_ini_path, 'r') as file:
        template_ini = file.read()
    
    with open(template_end_path, 'r') as file:
        template_end = file.read()

    with open(sweep_reset_path, 'r') as file:
        sweep_reset = file.read()

    with open(script_path+script_name, 'w') as file:
        file.write(template_ini+'\n')
    
    with open(script_path+script_name, 'a') as file:
        file.write(sweep_reset+'\n')

    for module_sequence_path in modules:
        with open(modules_path + module_sequence_path, 'r') as file:
            module_sequence = file.read()
    
        with open(script_path+script_name, 'a') as file:
            file.write(module_sequence)
    
    with open(script_path+script_name, 'a') as file:
        file.write(template_end)
    
    print("python script generated \n")

# data = load_json("./sequences/test_json_arb.json")
data = load_json("./sequences/output.json")

delete_files_in_directory(modules_path)
delete_files_in_directory(reset_path)

for group in data["groups"]:

###########----------------For_Pulses----------------###########
    # Sorts all Pulses by the start time
    sorted_pulses_start = sorted(
        group["Pulses"].items(), key=lambda x: (x[1]["Start"], x[1]["Duration"])
    )
    print(group["name"])
    on_off_times = get_on_off(sorted_pulses_start)
    channel_list = get_all_channels(on_off_times)
    merged_on_off = merge_channels(on_off_times, channel_list, sorted_pulses_start)
    
    pulses_on_off = dict(sorted(merged_on_off.items(), key=lambda x: x))

###########----------------For_Sweeps----------------###########
    # Sorts sweeps by start time
    sorted_sweeps_start = sorted(
        group["Sweeps"].items(), key=lambda x: (x[1]["Start"])
    )
    sweeps_on = get_on_times(sorted_sweeps_start)

###########----------------Combine_Commands----------------###########
    final_command_dic = Merge(add_delay(pulses_on_off, "Pulses"), add_delay(sweeps_on, "Sweeps"))
    print("Merged the Dictionaries \n") 
    module_reset_sequence(final_command_dic, group["name"])

script_gen(modules_path, templates_path, script_path, "testttttt9.py")