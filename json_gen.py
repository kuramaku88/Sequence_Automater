import pandas as pd
import json

# Load the Excel file
file_path = 'FPGA_Manager.xlsx'  # Replace with your file path
modules_df = pd.read_excel(file_path, sheet_name='Modules')
pulses_df = pd.read_excel(file_path, sheet_name='Pulses')
sweeps_df = pd.read_excel(file_path, sheet_name='Sweeps')
lookup_df = pd.read_excel(file_path, sheet_name='Channel Lookup')

# Create a lookup dictionary for channels to module names and channel names
channel_to_module = {}
channel_to_name = {}
for _, lookup_row in lookup_df.iterrows():
    channel = lookup_row['Channel']
    module_name = lookup_row['Module Name']
    channel_name = lookup_row['Channel Name']
    channel_to_module[channel] = module_name
    channel_to_name[channel] = channel_name

# Initialize the output JSON structure
output_json = {"modules": []}

# Function to find the module name from channels
def find_module_from_channels(channels):
    for channel in channels:
        if channel in channel_to_module:
            return channel_to_module[channel]
    return None

# Function to generate tag from channels
def generate_tag_from_channels(channels):
    return ', '.join([channel_to_name[channel] for channel in channels if channel in channel_to_name])

# Construct a dictionary to hold module data temporarily
module_data = {name: {"name": name, "Duration": duration, "Pulses": {}, "Sweeps": {}} for name, duration in modules_df.values}

# Populate pulses
for _, pulse_row in pulses_df.iterrows():
    pulse_name = pulse_row['Pulse Name']
    channels = pulse_row['Channels'].split(', ')
    module_name = find_module_from_channels(channels)
    
    if module_name:
        module_data[module_name]['Pulses'][pulse_name] = {
            "Start": pulse_row['Start'],
            "Duration": pulse_row['Duration'],
            "Channels": channels,
            "Tag": generate_tag_from_channels(channels)
        }

# Populate sweeps
for _, sweep_row in sweeps_df.iterrows():
    sweep_name = sweep_row['Sweep Name']
    channels = sweep_row['Channels'].split(', ')
    module_name = find_module_from_channels(channels)
    
    if module_name:
        module_data[module_name]['Sweeps'][sweep_name] = {
            "Start": sweep_row['Start'],
            "Sweep_Reg_Number": sweep_row['Sweep Reg Number'],
            "Rising_Edge_Delay": sweep_row['Rising Edge Delay'],
            "Falling_Edge_Delay": sweep_row['Falling Edge Delay'],
            "Rising_Edge_Increment": sweep_row['Rising Edge Increment'],
            "Falling_Edge_Increment": sweep_row['Falling Edge Increment'],
            "Channels": channels,
            "Tag": generate_tag_from_channels(channels)
        }

# Convert module_data to list for JSON output
output_json['modules'] = list(module_data.values())

# Convert to JSON and save
output_json_str = json.dumps(output_json, indent=4)
with open('output.json', 'w') as json_file:
    json_file.write(output_json_str)

print("JSON conversion completed successfully!")
