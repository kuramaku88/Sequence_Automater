
import wrapper.wrapper_hvi_sequence as hvis
from sequences.system_parameters import *

Start_Delay1 = 200
Start_Delay2 = 0
Sweep_1 = {'channels': [8, 11], 'sweep_number': 1, 'RE_delay_init': Start_Delay1, 'FE_delay_init':Start_Delay1+ 10/3,
           'RE_delay_inc': 0, 'FE_delay_inc': 10}
Sweep_2 = {'channels': [9, 12, 14], 'sweep_number': 2, 'RE_delay_init': Start_Delay2, 'FE_delay_init': Start_Delay2+10,
           'RE_delay_inc': 0, 'FE_delay_inc': 20}

Counters_1 = {'channels': [2,3,4,5,6,7]}


# Below we define the different parameters for the sweep
total_length = 1e9
single_gate_length = 1e6

# Each increment corresponds to 10/3 ns (One cycle of 300 MHz)
number_iterations = int(total_length / single_gate_length)

def hvi_sequence():
    # To initialise the sweep set Enable High
    hvis.sync_multi_sequence_block("Initialising Sweep parameters", delay=500)
    hvis.dio_sweep_initializer('Initialize LVDS Channels', Module_DIO1, lvds_start=8)
    hvis.end_sync_multi_sequence_block()

    hvis.sync_while("Eternal loop", Module_DIO1, "State", "GREATER_THAN_OR_EQUAL_TO", 0, delay=1000)

    # Reset Sweepers in the sandbox, the gate HVIS register and the HVI FE,RE delay registers
    hvis.sync_multi_sequence_block("Initialize Sequence", delay=520)
    hvis.register_set("Set register <gate> as 0", Module_DIO1, "gate", 0, 30)
    hvis.dio_sweep_reset('Initialize sweep1 registers', Module_DIO1, Sweep_1)
    hvis.dio_sweep_reset('Initialize sweep2 registers', Module_DIO1, Sweep_2)
    hvis.end_sync_multi_sequence_block()

    hvis.sync_while_2registers("Gate loop", Module_DIO1, "gate", "LESS_THAN", number_iterations, Module_DIO1, "State", "EQUAL_TO", 0, delay=500)
		hvis.dio_output("Turn on channels",DIO_1,[0, 1, 4],"on", delay=10)
		hvis.dio_output("Turn on channels",DIO_1,[2],"on", delay=50)
		hvis.dio_output("Turn on channels",DIO_1,[3],"on", delay=10)
		hvis.dio_output("Turn off channels",DIO_1,[2],"off", delay=10)
		hvis.dio_output("Turn on channels",DIO_1,[2, 14],"on", delay=30)
		hvis.dio_output("Turn off channels",DIO_1,[3],"off", delay=20)
		hvis.dio_output("Turn off channels",DIO_1,[0, 4],"off", delay=20)
		hvis.dio_output("Turn on channels",DIO_1,[0, 4],"on", delay=50)
		hvis.dio_output("Turn off channels",DIO_1,[2, 14],"off", delay=110)
		hvis.dio_output("Turn on channels",DIO_1,[3],"on", delay=10)
		hvis.dio_output("Turn off channels",DIO_1,[0, 4],"off", delay=180)
		hvis.dio_output("Turn off channels",DIO_1,[3],"off", delay=220)
		hvis.dio_output("Turn off channels",DIO_1,[1],"off", delay=120)

    hvis.end_sync_multi_sequence_block()

    hvis.end_sync_while()