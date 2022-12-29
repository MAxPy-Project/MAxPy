from subprocess import Popen
from .utility import ErrorCodes
from .utility import get_time_stamp
import os
import sysconfig

os.environ['PYBIND_LIBS'] = sysconfig.get_paths()['purelib'] + '/pybind11/include/'
os.environ['VERI_FLAGS']  = '-O3 -shared -std=c++11 -fPIC $(python -m pybind11 --includes)'
os.environ['VCD2SAIF_SNPS'] = '/lab215/tools/synopsys/design_compiler_L-2016.03/bin/vcd2saif'
os.environ['VCD2SAIF_CDNS'] = '/lab215/tools/cadence/INCISIVE152/tools.lnx86/simvision/bin/simvisdbutil'


def compile(axckt):

    print("> C++ compilation")

    # remove old compiled module
    rm_old_files_string = f"rm -f {axckt.compiled_module_path}*"
    child = Popen(rm_old_files_string, shell=True)
    child.communicate()
    child.wait()

    # to include VCD_files = verilated_vcd_c.h
    # https://zipcpu.com/blog/2017/06/21/looking-at-verilator.html

    # assemble terminal command for pybind compilation

    if axckt.vcd_opt == True:
        pybind_string = \
            'c++' + ' ' \
            + os.environ.get('VERI_FLAGS') + ' ' \
            + '-I' + os.environ.get('PYBIND_LIBS') + ' ' \
            + '-I /usr/share/verilator/include' + ' ' \
            + '/usr/share/verilator/include/verilated.cpp' + ' ' \
            + '/usr/share/verilator/include/verilated_vcd_c.cpp' + ' ' \
            + axckt.source_output_dir  + '*.cpp' + ' ' \
            + '-o ' + axckt.compiled_module_path
    else:
        pybind_string = \
            'c++' + ' ' \
            + os.environ.get('VERI_FLAGS') + ' ' \
            +'-I' + os.environ.get('PYBIND_LIBS') + ' ' \
            + '-I /usr/share/verilator/include' + ' ' \
            + '/usr/share/verilator/include/verilated.cpp' + ' ' \
            + axckt.source_output_dir  + '*.cpp' + ' ' \
            +'-o ' + axckt.compiled_module_path


    # create log file
    log_path = f"{axckt.target_compile_dir}compile.log"
    log_file = open(log_path, 'w')
    log_file.write('MAxPy: PYBIND COMPILATION LOG\n\n')
    log_file.write(f"Command line:\n\n{pybind_string}\n\n")
    log_file.write("Log from stdout and stderr:\n\n")
    # close file and then open it again to avoid concurrency problems with subprocess call below
    log_file.close()
    log_file = open(log_path, "a")

    # execute compilation command as subprocess
    child = Popen(pybind_string, stdout=log_file, stderr=log_file, shell=True)
    child.communicate()
    error_code = child.wait()

    log_file.write('\n\n')
    log_file.write(get_time_stamp())
    log_file.write('\n\n')
    log_file.close()

    if error_code != 0:
        ret_val = ErrorCodes.C2PY_COMPILE_ERROR
    else:
        ret_val = ErrorCodes.OK

    return ret_val
