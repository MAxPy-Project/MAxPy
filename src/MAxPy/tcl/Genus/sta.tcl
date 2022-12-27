include load_etc.tcl

set DESIGN SAD
set POW_EFF high
set SYN_EFF high
set MAP_EFF high

set _OUTPUTS_PATH outputs
set _REPORTS_PATH reports
set _LOG_PATH logs
set _RESULTS_PATH results

#shell rm -rf logs/ outputs/ rc.* reports/ results/


set lib_synth "${DK_PATH}/${LIB_SYNTH}"

#set lef_svt_worst_1_0V "${DK_PATH}/LEF/cmos065_7m4x0y2z_Worst.lef \
#                        ${DK_PATH}/LEF/CORE65LPSVT.lef"
                                 
#set captables "${DK_PATH}/captable/cmos065_7m4x0y2z_Worst.captable"

set_attribute library ${lib_synth}
#set_attribute lef_library ${lef_svt_worst_1_0V}
#set_attribute cap_table_file ${captables}

set_attribute script_search_path ${ENV_SCRIPT_PATH} /
set_attribute hdl_search_path ${ENV_RTL_PATH} /

set_attribute find_takes_multiple_names true

#HDL ERRORS
set_attribute hdl_error_on_blackbox true 
set_attribute hdl_error_on_latch true 
set_attribute hdl_error_on_negedge true 


set_attribute wireload_mode top 
set_attribute information_level 7 
set_attribute lp_power_unit uW 


set_attr interconnect_mode ple 
set_attribute hdl_track_filename_row_col true 

puts "$ENV_SCRIPT_PATH"
puts "$ENV_RTL_PATH"
puts "$ENV_SDC_FILE"


read_netlist netlist.v
read_sdc $ENV_SDC_FILE
write_sdf  -recrem split -setuphold split -edges check_edge -timescale ps  >  sta.sdf

puts "Final Runtime & Memory."
timestat FINAL
puts "============================"
puts "Synthesis Finished ........."
puts "============================"

report timing >timing.log
report area   >area.log
report power  >power.log

quit

