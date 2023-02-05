from errno import EROFS, errorcode
import os
import sys
import re
import sysconfig
import subprocess
import importlib
import itertools
import copy
from pandas import read_csv
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from .utility import *
from .resources import Resources
from .synth import synth
from .estimations import est_area, est_power_timing
from .verilate import verilate
from .wrapper import wrapper
from .compile import compile
from .check import check
from .results import ResultsTable
from .pareto import pareto_front


class AxCircuit:
    res = Resources()

    def __init__(self,
        top_name="",
        tech="NanGate15nm",
        xml_opt="verilator",
        clk_signal="",
        group_dir="",
        testbench_script=None,
        #dot_opt = 'verilator',
        #target_clk_period = 100000,
        ):

        # initial message
        print(f"MAxPy - Version {version}\n")

        self.res.load_tech(tech)

        self.top_name = top_name
        self.tech = tech
        self.xml_opt = xml_opt
        self.clk_signal = clk_signal
        self.parameters = {}
        self.group_dir = group_dir
        self.testbench_script = testbench_script
        self.prob_pruning_threshold = 0
        self.node_info = []
        self.prun_flag = False
        self.prun_netlist = False
        self.saif_opt = True
        self.vcd_opt = False
        self.log_opt = True
        self.synth_tool = None
        self.results_filename = ""

    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    # getters and setters

    def set_group(self, path):
        self.group_dir = path


    def set_testbench_script(self, testbench_script):
        self.testbench_script = testbench_script


    def set_synth_tool(self, synth_tool):
        self.synth_tool = synth_tool


    def set_prob_pruning_threshold(self, threshold):
        self.prob_pruning_threshold = threshold


    def set_results_filename(self, filename):
        if self.group_dir == "":
            self.results_filename = filename
        else:
            self.results_filename= f"{self.group_dir}/{filename}"



    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

    def rtl2py(self, base="", target=""):
        if base == "":
            base = "rtl"

        if target == "":
            target = "level_00"
            self.current_parameter = ""
        else:
            self.current_parameter = target

        self.class_name = f"{self.top_name}_{target}"

        print("------------------------------------------------------------------------------------")
        print(f">>> MAxPy rtl2py: converting Verilog RTL design \"{self.top_name}\" into Python module")
        print(f"> Base \"{base}\", Target \"{target}\"")

        print("> Start: " + get_time_stamp())

        if self.synth_tool is not None:
            if self.synth_tool in self.res.synth_tools:
                self.synth_opt = True
            else:
                self.synth_opt = False
        else:
            self.synth_opt = False

        if self.synth_opt is False:
            self.synth_tool = "yosys"

        self.base_path = f"{base}/*.v"
        if self.group_dir == "":
            self.target_compile_dir = f"{self.top_name}_{target}/"
            self.pymod_path = f"{self.top_name}_{target}"
        else:
            self.target_compile_dir = f"{self.group_dir}/{self.top_name}_{target}/"
            self.pymod_path = f"{self.group_dir}.{self.top_name}_{target}"
        self.target_netlist_dir = "{t}netlist_{s}/".format(t=self.target_compile_dir, s=self.synth_tool)
        self.source_output_dir = "{t}source/".format(t=self.target_compile_dir)

        self.compiled_module_path = "{t}{c}.so".format(t=self.target_compile_dir, c=self.top_name)
        self.netlist_target_path = "{d}{c}.v".format(d=self.target_netlist_dir, c=self.top_name)
        self.wrapper_cpp_path = "{d}verilator_pybind_wrapper.cpp".format(d=self.source_output_dir)
        self.wrapper_header_path = "{d}verilator_pybind_wrapper.h".format(d=self.source_output_dir)
        self.area_report_path = "{t}area_report.txt".format(t=self.target_compile_dir, c=self.top_name)
        self.power_report_path = "{t}power_report.txt".format(t=self.target_compile_dir, c=self.top_name)

        os.makedirs(self.target_compile_dir, exist_ok = True)
        os.makedirs(self.source_output_dir, exist_ok = True)
        os.makedirs(self.target_netlist_dir, exist_ok = True)

        self.trace_levels = 99  ##TODO: ???

        self.area = 0.0
        self.power = 0.0
        self.timing = 0.0

        # synth: synthesize RTL file
        if self.prun_netlist is False:
            err = synth(self)

            if self.synth_opt is False:
                self.synth_tool = None

            if err is not ErrorCodes.OK:
                print(">>> End: " + get_time_stamp())
                print(">>> MAxPy ERROR: synth process exited with error code \"{error}\". Please check log files".format(error=err))
                return err
            else:
                if self.synth_opt is True:
                    self.base_path = self.netlist_target_path

                self.working_netlist = self.netlist_target_path
        else:
            self.working_netlist = f"{base}/{self.top_name}.v"

        est_area(self)
        est_power_timing(self)

        print(f"  > Netlist estimated area: {self.area:.3f}")
        print(f"  > Netlist estimated power = {self.power:.3f} uW")
        print(f"  > Netlist estimated maximum delay = {self.timing:.3f} nS")

        task_list = [
            verilate,
            wrapper,
            compile,
            check
        ]

        for task in task_list:
            err = task(self)
            if err is not ErrorCodes.OK:
                print("> End: " + get_time_stamp())
                print(f">>> Error converting circuit \"{self.top_name}\"! (code: {err})")
                print("")
                return err

        print("> End: " + get_time_stamp())
        print(">>> Circuit \"{t}\" converted successfully!".format(t=self.top_name))
        print("")

        return ErrorCodes.OK

    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .


    def rtl2py_param_loop(self, base = ""):
        # change variable parameters in rtl source file
        file =  open(f"{base}/{self.top_name}.v", 'r')
        rtl_source_original = file.read()
        file.close()

        keys = self.parameters.keys()
        values = (self.parameters[key] for key in keys)
        combinations = [dict(zip(keys, combination)) for combination in itertools.product(*values)]

        count=len(combinations)
        print(f">>> Converting Verilog RTL design \"{self.top_name}\" into Python module with variable parameters")
        print(f">>> Iterating through {count} combinations")
        print("")

        for param_list in combinations:
            s = ""
            rtl_source_edit = rtl_source_original
            for key in param_list:
                value = param_list[key]
                if s != "":
                    s = s + "_"
                s = s + f"{value}"
                rtl_source_edit = rtl_source_edit.replace(key, value)

            if self.synth_tool is not None:
                s = s + "_" +  self.synth_tool

            if self.group_dir == "":
                base = f"{self.top_name}_{s}/rtl"
            else:
                base = f"{self.group_dir}/{self.top_name}_{s}/rtl"

            try:
                os.makedirs(base)

                target = f"{s}"
                file =  open(f"{base}/{self.top_name}.v", 'w')
                file.write(rtl_source_edit)
                file.close()

                err = self.rtl2py(base=base, target=target)

                if err is ErrorCodes.OK:
                    self.run_testbench()

            except FileExistsError:
                print(f">>> Skipping combination \"{s}\" because it already exists (dir: {base})")
                print("")

    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .


    def run_testbench(self):
        if self.testbench_script is not None:
            print("> Testbench init")
            mod_name = f"{self.pymod_path}.{self.top_name}"
            mod = importlib.import_module(mod_name, package=None)
            self.prun_flag, self.node_info = self.testbench_script(ckt=mod, results_filename=self.results_filename)
            print("> Testbench end\n")
            return ErrorCodes.OK

    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .


    def probprun(self, base, prun_level):
        print(f"> Probabilistic pruning (level {prun_level}%)")
        print(f"  > Original netlist: {self.netlist_target_path}")

        original_node_info = self.node_info.copy()
        original_netlist_target_path = self.netlist_target_path
        original_current_parameter = self.current_parameter

        prun_level_str = "%02d" % (prun_level)

        #if "_build" in base:
        #    base = base.split("_build")[0]

        if self.group_dir == "":
            probprun_netlist_path = f"{self.top_name}_{base}_probprun_{prun_level_str}/netlist"
        else:
            probprun_netlist_path = f"{self.group_dir}/{self.top_name}_{base}_probprun_{prun_level_str}/netlist"

        os.makedirs(probprun_netlist_path, exist_ok = True)

        print(f"  > Creating directory with pruned netlist: {probprun_netlist_path}")

        fhandle = open(self.netlist_target_path, "r")
        netlist_text = fhandle.readlines()
        fhandle.close()
        netlist_node_count = len(self.node_info)
        print(f"  > Evaluating {netlist_node_count} nodes")

        for node in self.node_info:
            if node["p0"] >= node["p1"]:
                high_prob_value = node["p0"]
                high_prob_logic_level = "p0"
            else:
                high_prob_value = node["p1"]
                high_prob_logic_level = "p1"
            node["high_prob_value"] = high_prob_value
            node["high_prob_logic_level"] = high_prob_logic_level

        sorted_node_list = sorted(self.node_info, key=lambda d: d["high_prob_value"], reverse=True)
        nodes_to_prun = int(float(netlist_node_count)*float(prun_level)/100.0)
        if nodes_to_prun == 0:
            nodes_to_prun = 1
        print("  > Pruning %d%% of the netlist nodes (%d/%d)" % (prun_level, nodes_to_prun, netlist_node_count))
        node_count = 0
        for node in sorted_node_list:
            output_gate_count = 0
            input_gate_count = 0
            for i in range(len(netlist_text)):
                if node['node'] in netlist_text[i]:
                    if "Z" in netlist_text[i]:
                        output_gate_count += 1
                        netlist_text[i] = netlist_text[i].replace(node['node'], "")
                    elif "wire" in netlist_text[i]:
                        netlist_text[i] = ""
                    elif node['high_prob_logic_level'] == "p0":
                        input_gate_count += 1
                        netlist_text[i] = netlist_text[i].replace(node['node'], "1'b0")
                    elif node['high_prob_logic_level'] == "p1":
                        input_gate_count += 1
                        netlist_text[i] = netlist_text[i].replace(node['node'], "1'b1")
            print(f"    > Node: {node['node']}, {node['high_prob_logic_level']}: {node['high_prob_value']}, gate outputs: {output_gate_count}, gate inputs: {input_gate_count}")
            node_count += 1
            if node_count >= nodes_to_prun:
                break

        pruned_netlist_path = f"{probprun_netlist_path}/{self.top_name}.v"
        fhandle = open(pruned_netlist_path, "w")
        fhandle.write("".join(netlist_text))
        fhandle.close()

        self.prun_netlist = True
        self.rtl2py(
            base=probprun_netlist_path,
            target=f"{self.current_parameter}_probprun_{prun_level_str}",
        )
        self.prun_netlist = False

        self.node_info = original_node_info.copy()
        self.netlist_target_path = original_netlist_target_path
        self.current_parameter = original_current_parameter

    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .


    def testbench_param_loop(self):
        if self.testbench_script is None:
            print("Error! Testbench script is None!\n")
            return

        keys = self.parameters.keys()
        values = (self.parameters[key] for key in keys)
        combinations = [dict(zip(keys, combination)) for combination in itertools.product(*values)]

        for param_list in combinations:
            target = ""
            for key in param_list:
                value = param_list[key]
                #key_name = key.split("[[PARAM_")[1].replace("]]", "")
                if target != "":
                    target = target + "_"
                target = target + f"{value}"

            if self.synth_tool is not None:
                target = target + "_" +  self.synth_tool

            if self.group_dir == "":
                self.target_compile_dir = f"{self.top_name}_{target}/"
                self.pymod_path = f"{self.top_name}_{target}"
            else:
                self.target_compile_dir = f"{self.group_dir}/{self.top_name}_{target}/"
                self.pymod_path = f"{self.group_dir}.{self.top_name}_{target}"

            self.target_netlist_dir = "{t}netlist_{s}/".format(t=self.target_compile_dir, s=self.synth_tool)
            self.netlist_target_path = "{d}{c}.v".format(d=self.target_netlist_dir, c=self.top_name)
            self.current_parameter = target

            self.run_testbench()

    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .


    def get_pareto_front(self, x_name, y_name):
        csv_data = read_csv(self.results_filename, delimiter=";")
        x_data = csv_data[x_name].tolist()
        y_data = csv_data[y_name].tolist()
        x_pareto, y_pareto, index = pareto_front(x_data, y_data)
        pareto_elements = []
        pareto_circuits = []
        print(f"> Pareto front for {self.top_name}:")
        for i in index:
            name = csv_data["circuit"][i]
            pareto_line = f"circuit: {name}, x: {x_data[i]}, y: {y_data[i]}"
            pareto_elements.append(pareto_line)
            pareto_circuits.append(name)
            print(f"  > {pareto_line}")
        if self.group_dir == "":
            pareto_filename = f"pareto_{x_name}_{y_name}.txt"
        else:
            pareto_filename = f"{self.group_dir}/pareto_{x_name}_{y_name}.txt"
        with open(pareto_filename, "w") as pareto_file:
            print(f"> Saving pareto list into file: {pareto_filename}")
            pareto_file.write("\n".join(x for x in pareto_elements))
        plt.scatter(x_data, y_data, color="blue", marker=".", label="_nolegend_")
        plt.scatter(x_pareto, y_pareto, 200, color="red", edgecolors="black", marker="*", label="_nolegend_")
        plt.plot(x_pareto, y_pareto, color='black', marker='.', linewidth=3, markersize=1, zorder=0)
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        if self.group_dir == "":
            pareto_image= f"pareto_{x_name}_{y_name}.pdf"
        else:
            pareto_image= f"{self.group_dir}/pareto_{x_name}_{y_name}.pdf"
        plt.savefig(pareto_image)
        plt.savefig(pareto_image.replace(".pdf", ".png"))
        plt.show()
        return pareto_circuits
