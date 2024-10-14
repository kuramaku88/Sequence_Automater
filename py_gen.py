import json
import numpy as np
import matplotlib.pyplot as plt
import os
import json_gen

from helper_methods import *
# from json_gen_2 import json_gen

file_path = 'FPGA_Manager.xlsx'  
output_file_path = "sequences_json/output_test.json"

# Generate the json_file
json_gen

# Load the JSON file
data = load_json("D:\MPQ\sequences_json\output_test.json")

# Clear previous the directories with different commands and resets 
delete_files_in_directory(modules_path)
delete_files_in_directory(reset_path)

# Loop through modules to generate the necessary commands
for module in data["modules"]:
    module_name = module["name"]

###########----------------For_Pulses----------------###########
    # Sorts all Pulses by the start time
    sorted_pulses_start = sorted(
        module["Pulses"].items(), key=lambda x: (x[1]["Start"], x[1]["Duration"])
    )
    on_off_times = get_on_off(sorted_pulses_start)
    channel_list = get_all_channels(on_off_times)
    merged_on_off = merge_channels(on_off_times, channel_list, sorted_pulses_start)
    
    pulses_on_off = dict(sorted(merged_on_off.items(), key=lambda x: x))
    # print(pulses_on_off)

###########----------------For_Sweeps----------------###########
    # Sorts sweeps by start time
    sorted_sweeps_start = sorted(
        module["Sweeps"].items(), key=lambda x: (x[1]["Start"])
    )
    sweeps_on = get_on_times(sorted_sweeps_start)

###########----------------Combine_Commands----------------###########
    final_command_dic = Merge(add_delay(pulses_on_off, "Pulses"), add_delay(sweeps_on, "Sweeps"))
    print(f"Merged the Dictionaries for moulde: {module_name}\n")
    # print(final_command_dic)
    module_reset_sequence(final_command_dic, module_name)

# Generate the python scriot by putting together the templates, commands and resets
script_gen(modules_path, reset_path, script_path, "KS_FPGA_py_script_test_4.py")