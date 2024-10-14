import pandas as pd
import json

def json_gen(input_filepath, output_filepath):
    # Load the Excel file
    pulses_df = pd.read_excel(input_filepath, sheet_name='Pulses')
    sweeps_df = pd.read_excel(input_filepath, sheet_name='Sweeps')
    lookup_df = pd.read_excel(input_filepath, sheet_name='Channel Lookup')

    # Print the columns for debugging purposes
    print("Pulses columns:", pulses_df.columns)
    print("Sweeps columns:", sweeps_df.columns)
    print("Channel Lookup columns:", lookup_df.columns)

    # Ensure the expected column names are present
    expected_pulse_columns = ['Pulse Name', 'Start', 'Duration', 'Channel Names']
    expected_sweep_columns = ['Sweep Name', 'Start', 'Sweep Reg Number', 'Rising Edge Delay', 'Falling Edge Delay', 'Rising Edge Increment', 'Falling Edge Increment', 'Channel Names']
    expected_lookup_columns = ['Channel', 'Module Name', 'Channel Name']

    for column in expected_pulse_columns:
        if column not in pulses_df.columns:
            raise KeyError(f"Missing expected column '{column}' in Pulses sheet")

    for column in expected_sweep_columns:
        if column not in sweeps_df.columns:
            raise KeyError(f"Missing expected column '{column}' in Sweeps sheet")

    for column in expected_lookup_columns:
        if column not in lookup_df.columns:
            raise KeyError(f"Missing expected column '{column}' in Channel Lookup sheet")

    # Create a lookup dictionary for channel names to module names and channels
    channel_name_to_module = {}
    channel_name_to_channel = {}
    for _, lookup_row in lookup_df.iterrows():
        channel = lookup_row['Channel']
        module_name = lookup_row['Module Name']
        channel_name = lookup_row['Channel Name']
        channel_name_to_module[channel_name] = module_name
        channel_name_to_channel[channel_name] = channel

    # Initialize the output JSON structure
    output_json = {"modules": []}

    # Function to get module and channels mapping from channel names
    def get_module_and_channels_mapping(channel_names):
        module_channels = {}
        for channel_name in channel_names:
            if channel_name not in channel_name_to_channel:
                raise KeyError(f"Channel name '{channel_name}' not found in Channel Lookup sheet")
            module_name = channel_name_to_module[channel_name]
            channel = channel_name_to_channel[channel_name]
            if module_name not in module_channels:
                module_channels[module_name] = []
            module_channels[module_name].append(channel)
        return module_channels

    # Construct a dictionary to hold module data temporarily
    module_data = {}

    # Populate pulses
    for _, pulse_row in pulses_df.iterrows():
        pulse_name = pulse_row['Pulse Name']
        channel_names = pulse_row['Channel Names'].split(', ')
        module_channels = get_module_and_channels_mapping(channel_names)

        for module_name, channels in module_channels.items():
            if module_name not in module_data:
                module_data[module_name] = {"name": module_name, "Pulses": {}, "Sweeps": {}}

            module_data[module_name]['Pulses'][pulse_name] = {
                "Start": pulse_row['Start'],
                "Duration": pulse_row['Duration'],
                "Channels": channels,
                "Tag": ', '.join([name for name in channel_names if channel_name_to_module[name] == module_name])
            }

    # Populate sweeps
    for _, sweep_row in sweeps_df.iterrows():
        sweep_name = sweep_row['Sweep Name']
        channel_names = sweep_row['Channel Names'].split(', ')
        module_channels = get_module_and_channels_mapping(channel_names)

        for module_name, channels in module_channels.items():
            if module_name not in module_data:
                module_data[module_name] = {"name": module_name, "Pulses": {}, "Sweeps": {}}

            module_data[module_name]['Sweeps'][sweep_name] = {
                "Start": sweep_row['Start'],
                "Sweep_Reg_Number": sweep_row['Sweep Reg Number'],
                "Rising_Edge_Delay": sweep_row['Rising Edge Delay'],
                "Falling_Edge_Delay": sweep_row['Falling Edge Delay'],
                "Rising_Edge_Increment": sweep_row['Rising Edge Increment'],
                "Falling_Edge_Increment": sweep_row['Falling Edge Increment'],
                "Channels": channels,
                "Tag": ', '.join([name for name in channel_names if channel_name_to_module[name] == module_name])
            }

    # Convert module_data to list for JSON output
    output_json['modules'] = list(module_data.values())

    # Convert to JSON and save
    output_json_str = json.dumps(output_json, indent=4)
    with open(output_filepath, 'w') as json_file:
        json_file.write(output_json_str)

    print("JSON conversion completed successfully!")
