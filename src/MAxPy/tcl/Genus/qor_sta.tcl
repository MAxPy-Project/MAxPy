include load_etc.tcl

set DESIGN [[TOPMODULE]]
set POW_EFF high
set SYN_EFF high
set MAP_EFF high

set _OUTPUTS_PATH outputs
set _REPORTS_PATH reports
set _LOG_PATH logs
set _RESULTS_PATH results

set_attribute library [[LIBRARY]]

set_attribute script_search_path ./ 
set_attribute hdl_search_path [[NETLISTFILEPATH]] /

set_attribute find_takes_multiple_names true

#HDL ERRORS
set_attribute hdl_error_on_blackbox true 
set_attribute hdl_error_on_latch true 
set_attribute hdl_error_on_negedge true 


set_attribute wireload_mode top 
set_attribute information_level 7 
set_attribute lp_power_unit uW 


set_attr interconnect_mode ple 
set_attribute lp_power_analysis_effort $POW_EFF

read_netlist [[NETLISTFILENAME]]

#[[READ_SDCFILE]]
#[[READ_STIMULI]]
#[[WRITE_SDF]]

report qor

#puts "Final Runtime & Memory."
#timestat FINAL

#[[REPORT_AREA]]
#[[REPORT_TIMING]]
#[[REPORT_POWER]]

puts "Synthesis Finished ........."

quit
