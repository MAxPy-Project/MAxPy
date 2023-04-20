from subprocess import Popen
from .utility import ErrorCodes
from .utility import get_time_stamp
import os
import sysconfig
from datetime import datetime


#os.environ['PYBIND_LIBS'] = get_python_lib() + '/pybind11/include/'
os.environ['PYBIND_LIBS'] = sysconfig.get_paths()['purelib'] + '/pybind11/include/'
os.environ['VERI_LIBS']   = os.getenv("HOME") + '/verilator/include/'
os.environ['VERI_FLAGS']  = '-O3 -Wall -shared -std=c++11 -fPIC $(python -m pybind11 --includes)'
os.environ['VERI_PATH']   = os.getenv("HOME") + '/verilator/bin/verilator'
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

    # if axckt.vcd_opt == True:
    #     compile_string = \
    #         'c++' + ' ' \
    #         + os.environ.get('VERI_FLAGS') + ' ' \
    #         +'-I' + os.environ.get('VERI_LIBS') + ' ' \
    #         + os.environ.get('VERI_LIBS') + 'verilated.cpp' + ' ' \
    #         + os.environ.get('VERI_LIBS') + 'verilated_vcd_c.cpp' + ' ' \
    #         + axckt.source_output_dir  + '*.cpp' + ' ' \
    #         + '-o ' + axckt.compiled_module_path
    # else:
    #     compile_string = \
    #         'c++' + ' ' \
    #         + os.environ.get('VERI_FLAGS') + ' ' \
    #         +'-I' + os.environ.get('VERI_LIBS') + ' ' \
    #         + axckt.source_output_dir  + '*.cpp' + ' ' \
    #         + os.environ.get('VERI_LIBS') + 'verilated.cpp' + ' ' \
    #         +'-o ' + axckt.compiled_module_path

    cmake_lists = axckt.res.template_cmake_pybind.replace("[[TOP_NAME]]", axckt.top_name)
    cmake_lists = cmake_lists.replace("[[VERILATOR_INCLUDE_PATH]]", os.environ.get('VERI_LIBS'))
    if axckt.vcd_opt == True:
        cmake_lists = cmake_lists.replace("[[VCD_OPT]]", "")
    else:
        cmake_lists = cmake_lists.replace("[[VCD_OPT]]", "# ")

    path = f"{axckt.source_output_dir}CMakeLists.txt"
    with open(f"{axckt.target_compile_dir}CMakeLists.txt", "w") as f:
        f.write(cmake_lists)

    cmake_cmd = f"cmake -G Ninja -B {axckt.target_compile_dir} -S {axckt.target_compile_dir}"
    ninja_cmd = f"ninja -C {axckt.target_compile_dir}"

    # create log file
    log_path = f"{axckt.target_compile_dir}compile.log"
    log_file = open(log_path, 'w')
    log_file.write('MAxPy: PYBIND COMPILATION LOG\n\n')
    log_file.write(f"Command line:\n\n{cmake_cmd}\n\n")
    log_file.write(f"Command line:\n\n{ninja_cmd}\n\n")
    log_file.write("Log from stdout and stderr:\n\n")
    # close file and then open it again to avoid concurrency problems with subprocess call below
    log_file.close()
    log_file = open(log_path, "a")

    start_time = datetime.now()

    # execute compilation command as subprocess
    # child = Popen(compile_string, stdout=log_file, stderr=log_file, shell=True)
    # child.communicate()
    # error_code = child.wait()

    child = Popen(cmake_cmd, stdout=log_file, stderr=log_file, shell=True)
    child.communicate()
    error_code = child.wait()

    child = Popen(ninja_cmd, stderr=log_file, shell=True)
    child.communicate()
    error_code = child.wait()

    end_time = datetime.now()

    # get difference
    delta = end_time - start_time

    print(f"  >> {delta.total_seconds():.1f} seconds")

    log_file.write('\n\n')
    log_file.write(get_time_stamp())
    log_file.write('\n\n')
    log_file.close()

    # removing CMakeFiles dir to save disk space!
    ##TODO: reuse verilator and maxpy object files to save compile time and disk space
    rm_cmd = f"rm -r {axckt.target_compile_dir}CMakeFiles"
    child = Popen(rm_cmd, shell=True)
    child.communicate()
    child.wait()

    if error_code != 0:
        ret_val = ErrorCodes.C2PY_COMPILE_ERROR
    else:
        ret_val = ErrorCodes.OK

    return ret_val
