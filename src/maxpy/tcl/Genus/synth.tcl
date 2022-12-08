include load_etc.tcl

set DESIGN [[TOPMODULE]]
set POW_EFF high
set SYN_EFF high
set MAP_EFF high

set _OUTPUTS_PATH outputs
set _REPORTS_PATH reports
set _LOG_PATH logs
set _RESULTS_PATH results

#set lef_svt_worst_1_0V "${DK_PATH}/LEF/cmos065_7m4x0y2z_Worst.lef \
#                        ${DK_PATH}/LEF/CORE65LPSVT.lef"                               
#set captables "${DK_PATH}/captable/cmos065_7m4x0y2z_Worst.captable"

set_attribute library [[LIBRARY]]
#set_attribute lef_library ${lef_svt_worst_1_0V}
#set_attribute cap_table_file ${captables}

set_attribute script_search_path ./ 
set_attribute hdl_search_path [[RTLFILEPATH]] 

set_attribute find_takes_multiple_names true

#set_attribute avoid true SDFFRNQ_X1

#PREVENT HDL ERRORS
set_attribute hdl_error_on_blackbox true 
set_attribute hdl_error_on_latch true 
set_attribute hdl_error_on_negedge true 

set_attribute wireload_mode top 
set_attribute information_level 7 
set_attribute lp_power_unit uW 

set_attr interconnect_mode ple 
set_attribute hdl_track_filename_row_col true 


read_hdl -v2001 [[RTLFILENAME]]
elaborate $DESIGN
check_design -unresolved
#read_sdc [[SDCFILE]]

report timing -lint

set_attribute lp_power_analysis_effort $POW_EFF

set_attr dp_perform_csa_operations false 

synthesize -to_generic -eff $SYN_EFF

timestat GENERIC

synthesize -to_mapped -eff $MAP_EFF 

#synthesize -to_mapped -eff $MAP_EFF -incr   

check_design -all


report qor

write_hdl -mapped > [[NETLIST]]

puts "Final Runtime & Memory."
timestat FINAL
puts "============================"
puts "Synthesis Finished ........."
puts "============================"

#report timing >timing.log
#report area   >area.log
#report power  >power.log

quit

