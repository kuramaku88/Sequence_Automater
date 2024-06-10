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
    code_gen,
)

file_name = "Pulse_Manager.xlsx"
sheet_1 = "Pulse_Queue"
sheet_2 = "Pulse_Definition"
sheet_3 = "Test_Pulse_Definition"

df = pd.read_excel(file_name, sheet_name=[sheet_1, sheet_2, sheet_3])
merged_sheet = pd.merge(df[f"{sheet_1}"], df[f"{sheet_3}"], how="left", on="Pulse_Name")

# TODO: Look at the df_load_channels function
channels = df_load_channels(merged_sheet)
code_gen(channels, "try1.py")
channel_plotter(channels, 28)