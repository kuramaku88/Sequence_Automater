
import wrapper.wrapper_hvi_sequence as hvis
from sequences.system_parameters import *

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
### Reset commands for Module_DIO_1

### Commands for Module_DIO_1
	hvis.dio_send_trigger('Turn on triggers', Module_DIO_1, ['A0', 'A6', 'A8'], 'on', 0.0)
	hvis.dio_send_trigger('Turn off triggers', Module_DIO_1, ['A0'], 'off', 15000.0)
	hvis.dio_send_trigger('Turn off triggers', Module_DIO_1, ['A6', 'A8'], 'off', 905500.0)
	hvis.dio_send_trigger('Turn on triggers', Module_DIO_1, ['A0', 'A9'], 'on', 1000.0)
	hvis.dio_send_trigger('Turn off triggers', Module_DIO_1, ['A0', 'A9'], 'off', 70000.0)
	hvis.dio_send_trigger('Turn on triggers', Module_DIO_1, ['A7'], 'on', 500.0)
	hvis.dio_send_trigger('Turn off triggers', Module_DIO_1, ['A7'], 'off', 7500.0)
### Commands for Module_DIO_2
	hvis.dio_send_trigger('Turn on triggers', Module_DIO_2, ['B0', 'B1'], 'on', 10000.0)
	hvis.dio_sweep('Sweeping ['B2', 'B3']', Module_DIO_2, ['B2', 'B3'], 1, 0, 0.01, 1000.0)
	hvis.dio_sweep('Sweeping ['B4']', Module_DIO_2, ['B4'], 2, 0, 0.01, 89000)
	hvis.dio_sweep('Sweeping ['B5']', Module_DIO_2, ['B5'], 3, 0, 0.01, 100000)
	hvis.dio_send_trigger('Turn off triggers', Module_DIO_2, ['B0', 'B1'], 'off', 810000.0)

    hvis.end_sync_multi_sequence_block()

    hvis.end_sync_while()