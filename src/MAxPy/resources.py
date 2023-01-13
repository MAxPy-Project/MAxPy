import sys
import subprocess

if sys.version_info < (3, 9):
	import importlib_resources
else:
	import importlib.resources as importlib_resources


class Resources:

    default_techs= [
        "NanGate15nm",
        ]

    synth_tools = [
        "yosys",
        "genus"
        ]

    # load resources from MAxPy package
    pkg = importlib_resources.files("MAxPy")

    # load templates
    path = str(pkg / "tcl" / "Yosys" / "synth.ys")
    with open(path, "r") as f:
        template_yosys_synth = f.read()

    path = str(pkg / "tcl" / "Genus" / "synth.tcl")
    with open(path, "r") as f:
        template_genus_synth = f.read()

    path = str(pkg / "tcl" / "OpenSTA" / "cmd_file.sta")
    with open(path, "r") as f:
        template_opensta_cmd = f.read()

    path = str(pkg / "templates" / "verilator_pybind_wrapper.cpp")
    with open(path, "r") as f:
        template_pybind_wrapper_source = f.read()

    path = str(pkg / "templates" / "verilator_pybind_wrapper.h")
    with open(path, "r") as f:
        template_pybind_wrapper_header = f.read()

    path = str(pkg / "templates" / "instance_source.cpp")
    with open(path, "r") as f:
        template_instance_source = f.read()

    path = str(pkg / "templates" / "cmake_pybind.txt")
    with open(path, "r") as f:
        template_cmake_pybind = f.read()


    # load paths
    verilator_config_path = str(pkg / "tcl" / "Verilator" / "verilator_config.vlt")

    axarith_path = str(pkg / "vlib" / "AxArith")

    pwd = subprocess.Popen("pwd", shell=True, stdout=subprocess.PIPE).stdout.read().decode().strip('\n')


    def load_tech(self, tech):
        if tech in self.default_techs:
            self.path_tech_verilog = str(self.pkg / "pdk" / f"{tech}.v")
            self.path_tech_lib = str(self.pkg / "pdk" / f"{tech}.lib")
        else:
            self.path_tech_verilog = f"{tech}.v"
            self.path_tech_lib = f"{tech}.lib"
