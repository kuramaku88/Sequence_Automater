
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
### Commands for Module_DIO_1
		hvis.dio_send_trigger('Turn on triggers: Hello', Module_DIO_1, ['A0', 'A6', 'A8'], on, 0.0)
		hvis.dio_send_trigger('Turn off triggers: Hello', Module_DIO_1, ['A0'], off, 15000.0)
		hvis.dio_send_trigger('Turn off triggers: Hello', Module_DIO_1, ['A6', 'A8'], off, 905500.0)
		hvis.dio_send_trigger('Turn on triggers: Hello', Module_DIO_1, ['A0', 'A9'], on, 1000.0)
		hvis.dio_send_trigger('Turn off triggers: Hello', Module_DIO_1, ['A0', 'A9'], off, 70000.0)
		hvis.dio_send_trigger('Turn on triggers: Hello', Module_DIO_1, ['A7'], on, 500.0)
		hvis.dio_send_trigger('Turn off triggers: Hello', Module_DIO_1, ['A7'], off, 7500.0)
### Commands for Module_DIO_2
		hvis.dio_sweep('Sweeping [10, 0.0, 10, ['B2', 'B3']]: Hello', Module_DIO_2, [10, 0.0, 10, ['B2', 'B3']], off, 890.0)
		hvis.dio_send_trigger('Turn on triggers: Hello', Module_DIO_2, ['B0', 'B1'], on, 9000.0)
		hvis.dio_sweep('Sweeping [10, 0.0, 10, ['B4']]: Hello', Module_DIO_2, [10, 0.0, 10, ['B4']], off, 89920.0)
		hvis.dio_send_trigger('Turn off triggers: Hello', Module_DIO_2, ['B0', 'B1'], off, 910000.0)

    hvis.end_sync_multi_sequence_block()

    hvis.end_sync_while()