from subprocess import Popen
from .utility import ErrorCodes
from .utility import get_time_stamp


def verilate(axckt):
    print("> Verilator")

    # remove old source files
    rm_old_files_string = f"rm -f {axckt.source_output_dir}*"
    child = Popen(rm_old_files_string, shell=True)
    child.communicate()
    child.wait()

    if axckt.synth_opt is True:

        verilator_string =	'verilator' + ' ' \
                            + '-Wall -Wno-UNUSED -cc -O0 -top ' + axckt.top_name + ' ' \
                            + '-Mdir ' + axckt.source_output_dir + ' ' \
                            + axckt.res.verilator_config_path + ' ' \
                            + axckt.base_path + ' ' \
                            + axckt.res.path_tech_verilog + ' ' \
                            + '--prefix ' + axckt.class_name + ' ' \
                            + '--mod-prefix sub'

                        #+ axckt.axlib_path + ' ' \

    else:

        verilator_string =	'verilator' + ' ' \
                            + '-Wall -Wno-UNUSED -cc -top ' + axckt.top_name + ' ' \
                            + '-Mdir ' + axckt.source_output_dir + ' ' \
                            + axckt.res.verilator_config_path + ' ' \
                            + axckt.base_path + ' ' \
                            + axckt.res.path_tech_verilog + ' ' \
                            + '--prefix ' + axckt.class_name + ' ' \
                            + '--mod-prefix sub'

                        #+ axckt.axlib_path + ' ' \

    #print(verilator_string)


    if axckt.vcd_opt is True:
        verilator_string += " --trace"

    if axckt.clk_signal != "":
        verilator_string += f" --clk {axckt.clk_signal}"


    # create log file
    log_path = f"{axckt.target_compile_dir}verilate.log"
    #print('  > Creating log file: ' + log_filename)
    log_file = open(log_path, "w")

    # initial information in log file
    log_file.write("MAxPy: VERILATOR LOG\n\n")
    log_file.write(f"Command line:\n\n{verilator_string}\n\n")
    log_file.write("Log from stdout and stderr:\n\n")
    # close file and then open it again to avoid concurrency problems with subprocess call below
    log_file.close()
    log_file = open(log_path, "a")


    # execute verilator command as subprocess
    child = Popen(verilator_string, stdout=log_file, stderr=log_file, shell=True)
    child.communicate()
    error_code = child.wait()

    log_file.write('\n\n')
    log_file.write(get_time_stamp())
    log_file.write('\n\n')
    log_file.close()

    if error_code != 0:
        ret_val = ErrorCodes.VERI2C_ERROR
    else:
        ret_val = ErrorCodes.OK

    return ret_val
