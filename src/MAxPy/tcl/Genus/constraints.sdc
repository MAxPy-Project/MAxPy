## SDC File Constraints ##
set sdc_version 1.5
set_load_unit -picofarads 1

# Define the circuit clock
#create_clock -name "CLK_IN" -add -period $::env(ENV_SYNTH_CLK_PERIOD) [dc::get_port {clk}]
create_clock -name "CLK_IN" -add -period 7.40 [dc::get_port {clk}]
#set_clock_gating_check -setup 0.0 

# Add some non-idealities to the clock
#set_clock_transition -rise 0.0000001 [get_clocks "CLK_IN"]
#set_clock_transition -fall 0.0000001 [get_clocks "CLK_IN"]
set_clock_uncertainty 0.000001 [dc::get_port {CLK}]

# Ignore timing for reset
set_false_path -from [get_ports rst]

## INPUTS
set_input_delay -clock CLK_IN 0.000001  [all_inputs]
#set_input_transition -min -rise 0.00000001   [all_inputs]
#set_input_transition -max -rise 0.0000001    [all_inputs]
#set_input_transition -min -fall 0.00000001   [all_inputs]
#set_input_transition -max -fall 0.0000001    [all_inputs]
#set_output_delay -clock CLK_IN  0.000001 [all_outputs]
 
## OUTPUTS
set_load 0.03 [all_outputs]
#set_load -max 0.32 [all_outputs]

