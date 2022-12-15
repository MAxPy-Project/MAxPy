from errno import EROFS, errorcode
import os
import sys
import re
import sysconfig
import subprocess
import itertools
import importlib
import copy

if sys.version_info < (3, 9):
	import importlib_resources
else:
	import importlib.resources as importlib_resources

version = '0.0.1'

from .utility import *

os.environ['PYBIND_LIBS'] = sysconfig.get_paths()['purelib'] + '/pybind11/include/'
os.environ['VERI_FLAGS']  = '-O3 -shared -std=c++11 -fPIC $(python -m pybind11 --includes)'
os.environ['VCD2SAIF_SNPS'] = '/lab215/tools/synopsys/design_compiler_L-2016.03/bin/vcd2saif'
os.environ['VCD2SAIF_CDNS'] = '/lab215/tools/cadence/INCISIVE152/tools.lnx86/simvision/bin/simvisdbutil'

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class AxCircuit:

	def __init__(self, 
		top_name="",
		tech="NanGate15nm",
		synth_tool=None,
		xml_opt="verilator",
		clk_signal="",
		group_dir="",
		testbench_script=None,
		#dot_opt = 'verilator',
		#target_clk_period = 100000,
		):

		# initial message
		print(f"MAxPy - Version {version}")
		print("")

		self.top_name = top_name	
		self.tech = tech
		self.xml_opt = xml_opt
		self.clk_signal = clk_signal
		self.parameters = {}
		self.group_dir = group_dir
		self.testbench_script = testbench_script
		self.synth_tool = synth_tool
		self.pwd = subprocess.Popen("pwd", shell=True, stdout=subprocess.PIPE).stdout.read().decode().strip('\n')
		pkg = importlib_resources.files("maxpy")
		self.library_path_v = str(pkg / "pdk" / "NanGate15nm.v")
		self.library_path_lib = str(pkg / "pdk" / "NanGate15nm.lib")
		self.yosys_synth_template_path = str(pkg / "tcl" / "Yosys" / "synth.ys")
		self.genus_synth_template_path = str(pkg / "tcl" / "Genus" / "synth.tcl")
		self.verilator_config_path = str(pkg / "tcl" / "Verilator" / "verilator_config.vlt")
		self.opensta_cmd_file_path = str(pkg / "tcl" / "OpenSTA" / "cmd_file.sta")
		self.wrapper_cpp_template = str(pkg / "templates" / "verilator_pybind_wrapper.cpp")
		self.wrapper_header_template = str(pkg / "templates" / "verilator_pybind_wrapper.h")
		self.instance_cpp_template = str(pkg / "templates" / "instance_source.cpp")
		self.axlib_path = str(pkg / "vlib" / "AxLib.v")
		self.prob_pruning_threshold = 0
		self.node_info = []
		self.prun_flag = False
		self.prun_netlist = False

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


	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .		
	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
				
	def rtl2py(
		self, 
		base="", 
		target="", 
		area_estimation=True, 
		log_opt=True,
		vcd_opt=False,
		saif_opt=True,
		):

		self.vcd_opt = vcd_opt
		self.log_opt = log_opt
		self.saif_opt = saif_opt

		if base == "":
			base = 'rtl'
		
		if target == "":
			target = "level_00"
			self.current_parameter = ""
		else:
			self.current_parameter = target

		self.class_name = f"{self.top_name}_{target}"
		
		print(f">>> Converting Verilog RTL design \"{self.top_name}\" into Python module, base \"{base}\", target \"{target}\"")
		
		print(">>> Start: " + get_time_stamp())
		print("")

		if self.synth_tool is not None:
			if self.synth_tool in synth_tools:
				self.synth_opt = True
			else:
				self.synth_opt = False
		else:
			self.synth_opt = False

		if area_estimation is True and self.synth_opt is False:
			self.synth_tool = "yosys"

		self.base_path = f"{base}/*.v"
		if self.group_dir == "":			
			self.target_compile_dir = f"{self.top_name}_{target}_build/"
			self.pymod_path = f"{self.top_name}_{target}_build"
		else:
			self.target_compile_dir = f"{self.group_dir}/{self.top_name}_{target}_build/"
			self.pymod_path = f"{self.group_dir}.{self.top_name}_{target}_build"
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
		
		if self.synth_opt is True or area_estimation is True: 
			os.makedirs(self.target_netlist_dir, exist_ok = True)

		self.trace_levels = 99  ##TODO: ???

		self.area = 0.0
		self.power = 0.0
		self.timing = 0.0

		# synth: synthesize RTL file (optional)
		if self.prun_netlist is False:
			if self.synth_opt is True or area_estimation is True:
				ret_val = self.synth()
				#print("  > End\n")
				if ret_val is not ErrorCodes.OK:
					print(">>> End: " + get_time_stamp())
					print(">>> MAxPy ERROR: synth process exited with error code \"{error}\". Please check log files".format(error=ret_val))
					return ret_val
				else:
					if self.synth_opt is True:
						self.base_path = self.netlist_target_path
					else:
						self.synth_tool = None
					
					self.get_area(self.netlist_target_path)
					self.get_power_and_timing(self.netlist_target_path)					
		else:
			self.get_area(f"{base}/{self.top_name}.v")
			self.get_power_and_timing(f"{base}/{self.top_name}.v")
			
		process_list = [
			self.veri2c,
			self.c2py_parse,
			self.c2py_compile,
			self.checkpymod,
			self.testbench
		]

		#process_list = [self.c2py_compile]

		for process in process_list:
			ret_val = process()
			#print("  > End\n")
			if ret_val is not ErrorCodes.OK:
				print(">>> End: " + get_time_stamp())
				print(">>> MAxPy ERROR: process exited with error code \"{error}\". Please check log files".format(error=ret_val))
				return ret_val

		print("")
		print(">>> End: " + get_time_stamp())
		print(">>> Circuit \"{t}\" compiled successfully!".format(t=self.top_name))
		print("")
		
		
		return ErrorCodes.OK


	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .


	def rtl2py_param_loop(self, base = '', area_estimation=True, saif_opt=True):

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
				base = f"{self.top_name}_{s}_rtl"
			else:
				base = f"{self.group_dir}/{self.top_name}_{s}_rtl"
			#os.makedirs(base, exist_ok = True)

			try:
				os.makedirs(base)

				target = f"{s}"
				file =  open(f"{base}/{self.top_name}.v", 'w')
				file.write(rtl_source_edit)
				file.close()
		
				ret_val = self.rtl2py(
					base=base, 
					target=target,
					area_estimation=area_estimation, 
					saif_opt=saif_opt
				)
				
				#if ret_val is ErrorCodes.OK:
				#	self.testbench()

			except FileExistsError:
				print(f">>> Skipping combination \"{s}\" because it already exists (dir: {base}")
				print("")

	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .


	def testbench(self):

		if self.testbench_script is not None:
			print("> Testbench init")
			mod_name = f"{self.pymod_path}.{self.top_name}"
			mod = importlib.import_module(mod_name, package=None)			
			self.prun_flag, self.node_info = self.testbench_script(mod, f"{self.target_compile_dir}log-testbench.txt", True)
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

		if "_build" in base:
			base = base.split("_build")[0]

		if self.group_dir == "":
			probprun_netlist_path = f"{self.top_name}_{base}_probprun_{prun_level_str}_netlist"
		else:
			probprun_netlist_path = f"{self.group_dir}/{self.top_name}_{base}_probprun_{prun_level_str}_netlist"

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
				self.target_compile_dir = f"{self.top_name}_{target}_build/"
				self.pymod_path = f"{self.top_name}_{target}_build"
			else:
				self.target_compile_dir = f"{self.group_dir}/{self.top_name}_{target}_build/"
				self.pymod_path = f"{self.group_dir}.{self.top_name}_{target}_build"

			self.target_netlist_dir = "{t}netlist_{s}/".format(t=self.target_compile_dir, s=self.synth_tool)
			self.netlist_target_path = "{d}{c}.v".format(d=self.target_netlist_dir, c=self.top_name)
			self.current_parameter = target

			self.testbench()


	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
	# synth

	def synth(self):
		
		print("> Synth")

		#if os.path.isfile(self.netlist_target_path) == True:
		#	print('\n  > There is already a netlist for the selected synth tool.\n    Do you want to run the syhtnesis option again and overwrite the existing netlist? (Y / N) + Enter')
		#	user = input()

		#	if user == 'n' or user == 'N' or user == 'No' or user == 'NO':
		#		print('  > Skipping synth step')
		#		return ErrorCodes.OK

		if self.log_opt:
			# create log file
			log_filename = "{d}log-synthesis.txt".format(d=self.target_compile_dir)
			#print('  > Creating log file: ' + log_filename)
			log_file = open(log_filename, 'w')

		if self.synth_tool == 'yosys':

			file = open(self.yosys_synth_template_path,'r')
			file_text = file.read()
			file.close()
			file_text = file_text.replace("[[RTLFILENAME]]", f"{self.axlib_path} {self.base_path}")
			file_text = file_text.replace("[[LIBFILENAME]]", f"{self.library_path_v}")
			file_text = file_text.replace("[[TOPMODULE]]", self.top_name)
			file_text = file_text.replace("[[NETLIST]]", self.netlist_target_path)
			file_text = file_text.replace("[[LIBRARY]]", self.library_path_lib)
			file_text = file_text.replace("[[LIBRARYABC]]", self.library_path_lib)
			file = open('synth.ys',"w")
			file.write(file_text)
			file.close()			

			# - - - - - - - - - - - - - - - Execute yosys - - - - - - - - - - - - - -

			yosys_cmd = 'yosys synth.ys;'
			
			# TODO: check exception
			
			if self.log_opt:
				# writing logfile
				# initial information in log file
				log_file.write('MAxPy: SYNTHESIS USING YOSYS\n\n')
				log_file.write('Command line:\n\n')
				log_file.write(yosys_cmd+'\n')
				log_file.write(file_text)
				log_file.write('\n\n')
				log_file.write('Terminal log:\n\n')

				# close file and then open it again to avoid concurrency problems with subprocess call below
				log_file.close()
				# reopen log file as append
				log_file = open(log_filename, 'a')

			#print('  > Running synth tool command: %s' % (yosys_cmd))

			# execute compilation command as subprocess		
			if self.log_opt:
				child = subprocess.Popen(yosys_cmd, stdout=log_file, stderr=subprocess.STDOUT, shell=True)
			else:
				child = subprocess.Popen(yosys_cmd, shell=True)

			child.communicate()
			error_code = child.wait()

			# close logfile
			if self.log_opt:
				log_file.write("Synth command exit code: {code}".format(code=error_code))

				log_file.close()

			if error_code != 0:
				ret_val = ErrorCodes.SYNTH_ERROR
			else:
				ret_val = ErrorCodes.OK
			
			# - - - - - - - - - - - - - Delete temporary Files - - - - - - - - - - - -
			os.remove ("synth.ys")
			
			#return self.error_code

			return ret_val

		# ##TODO	
		# elif(self.synth_tool == 'genus'):
	
		# 	template_tcl = 'tcl/Genus/synth.tcl'
		# 	file = open(template_tcl,'r')
		# 	file_text = file.read()
		# 	file.close()

		# 	genus_netlist_path = 'circuits/' + self.top_name + '/netlist/' + self.top_name + '_genus' '.v'
 
		# 	filenames = ' '.join(next(walk(os.path.dirname(self.synth_input_path)), (None, None, []))[2])

		# 	#RTL NAME TEM Q CONFERIR
		# 	file_text = file_text.replace("[[RTLFILENAME]]", filenames) 
		# 	file_text = file_text.replace("[[RTLFILEPATH]]", os.path.dirname(self.synth_input_path))
		# 	file_text = file_text.replace("[[TOPMODULE]]", self.top_name)
		# 	#file_text = file_text.replace("[[NETLIST]]", genus_netlist_path)
		# 	file_text = file_text.replace("[[NETLIST]]", self.netlist_path)
		# 	file_text = file_text.replace("[[LIBRARY]]", f"pdk/{self.tech}.lib")
		# 	file_text = file_text.replace("[[SDCFILE]]", "tcl/Genus/constraints.sdc")
		# 	file = open('synth.tcl',"w")
		# 	file.write(file_text)
		# 	file.close()
			
		# 	genus_cmd = 'genus -64 -legacy_ui -files synth.tcl'

		# 	if self.log_opt:
		# 		log_file.write('MAxPy: SYNTHESIS USING GENUS\n\n')
		# 		log_file.write('Command line:\n\n')
		# 		log_file.write(genus_cmd+'\n')
		# 		log_file.write(file_text)
		# 		log_file.write('\n\n')
		# 		log_file.write('Terminal log:\n\n')
		# 		# close file and then open it again to avoid concurrency problems with subprocess call below
		# 		log_file.close()
		# 		# reopen log file as append
		# 		log_file = open(log_filename, 'a')

		# 	print('  > Running compilation command: %s' % (genus_cmd))

		# 	if self.log_opt:
		# 		child = subprocess.Popen(genus_cmd, stdout=log_file, stderr=subprocess.STDOUT, shell=True)
		# 	else:
		# 		child = subprocess.Popen(genus_cmd, shell=True)

		# 	child.communicate()
		# 	self.error_code = child.wait()

		# 	if self.log_opt:
		# 		log_file.close()				# close log file
			
		# 	#os.remove ("synth.tcl")		
		# 	#os.remove("genus.log")
		# 	#os.remove("genus.cmd")

		# 	subprocess.Popen("rm synth.tcl", shell=True)
		# 	subprocess.Popen("rm genus.log", shell=True)
		# 	subprocess.Popen("rm genus.cmd", shell=True)
			
		# 	#self.adapt_genus_netlist()

		# 	if self.error_code != 0:
		# 		self.error_msg = 'Error runnin GENUS SYNTH command\nPlease check log file (%s)' % log_filename

		# 	return self.error_code

	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
	# veri2c

	def veri2c(self):

		print("> Verilator")

		if remove_old_files(self.source_output_dir + '*') != 0:
			return ErrorCodes.VERI2C_ERROR
				
		if self.synth_opt==True: 

			#verilator_string =	os.environ.get('VERI_PATH') + ' ' \
			verilator_string =	'verilator' + ' ' \
								+ '-Wall -Wno-UNUSED -cc -O0 -top ' + self.top_name + ' ' \
								+ '-Mdir ' + self.source_output_dir + ' ' \
								+ self.verilator_config_path + ' ' \
								+ self.base_path + ' ' \
								+ self.library_path_v + ' ' \
								+ self.axlib_path + ' ' \
								+ '--prefix ' + self.class_name + ' ' \
								+ '--mod-prefix sub'

		else:

			#verilator_string = 	os.environ.get('VERI_PATH') + ' ' \
			verilator_string =	'verilator' + ' ' \
								+ '-Wall -Wno-UNUSED -cc -top ' + self.top_name + ' ' \
								+ '-Mdir ' + self.source_output_dir + ' ' \
								+ self.verilator_config_path + ' ' \
								+ self.base_path + ' ' \
								+ self.library_path_v + ' ' \
								+ self.axlib_path + ' ' \
								+ '--prefix ' + self.class_name + ' ' \
								+ '--mod-prefix sub'

		print(verilator_string)


		if self.vcd_opt == True:
			verilator_string += ' --trace'

		if self.clk_signal != '':
			verilator_string += (' --clk ' + self.clk_signal)

		if self.log_opt:
			# create log file
			log_filename = self.target_compile_dir  + ('log-veri2c_compile.txt')
			#print('  > Creating log file: ' + log_filename)
			log_file = open(log_filename, 'w')

			# initial information in log file
			log_file.write('MAxPy: VERILATOR LOG\n\n')
			log_file.write('Command line:\n\n')
			log_file.write(verilator_string)
			log_file.write('\n\n')
			log_file.write(get_time_stamp())
			log_file.write('\n\n')
			log_file.write('Terminal log:\n\n')

			# close file and then open it again to avoid concurrency problems with subprocess call below
			log_file.close()
			# reopen log file as append
			log_file = open(log_filename, 'a')

		#print('  > Running verilation command')#: ' + verilator_string)

		# execute compilation command as subprocess		
		if self.log_opt:
			child = subprocess.Popen(verilator_string, stdout=log_file, stderr=subprocess.STDOUT, shell=True)
		else:
			child = subprocess.Popen(verilator_string, shell=True)

		child.communicate()
		error_code = child.wait()

		if self.log_opt:
			log_file.write('\n\n')
			log_file.write(get_time_stamp())
			log_file.write('\n\n')
			log_file.close()

		if error_code != 0:
			ret_val = ErrorCodes.VERI2C_ERROR
		else:
			ret_val = ErrorCodes.OK
		
		return ret_val

	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
	# c2py-parse

	def c2py_parse (self):

		print("> C++/Python Wrapper")

		if remove_old_files("{c} {h}".format(c=self.wrapper_cpp_path, h=self.wrapper_header_path)) != 0:
			return ErrorCodes.C2PY_PARSE

		# get instance and nets structure
		self.parent_list = []
		header_filename = f"{self.class_name}.h"
		top_instance = self.parse_verilator_header(header_filename, self.top_name)

		if self.log_opt:
			# create log file
			log_filename = self.target_compile_dir  + ('log-c2py_parse.txt')
			#print('  > Creating log file: ' + log_filename)
			log_file = open(log_filename, 'w')
			log_file.write('MAxPy: VERILATOR/PYBIND WRAPPER\n\n')
			log_file.write(show_structure(top_instance, 0))
			log_file.write('\n\n')
			log_file.write(get_time_stamp())
			log_file.write('\n\n')
			log_file.close()

		#prepare python biding string
		pybind_string = "\t\t// verilator model methods\n"
		getters_and_setters_declaration = ""
		getters_and_setters_definition = ""
		
		for method in top_instance["methods"]:
			if method != "trace":
				pybind_string += f"\t\t.def(\"{method}\", &MAxPy_{self.class_name}::{method})\n"

		pybind_string += "\n\t\t// getters and setters for inputs and outpus\n"

		last_name = ''
		for net in top_instance['nets']:
			if net['name'] != last_name:

				# todo: use corret type!
				s = net["short_name"]
				t = "int"
				c = self.class_name

				pybind_string += f"\t\t.def(\"get_{s}\", &MAxPy_{c}::get_{s})\n"
				pybind_string += f"\t\t.def(\"set_{s}\", &MAxPy_{c}::set_{s})\n"
				pybind_string += "\n"

				# int get_A();
				# void set_A(int val);
				getters_and_setters_declaration += f"\t\t{t} get_{s}();\n\t\tvoid set_{s}({t} val);\n\n"

				# int MAxPy_adder4_exact::get_SUM() {
				# 	return(adder4_exact::SUM);
				# }
				#
				# void MAxPy_adder4_exact::set_SUM(int val) {
				# 	adder4_exact::SUM = val;
				# }

				getters_and_setters_definition += f"{t} MAxPy_{c}::get_{s}() {{\n\treturn({c}::{s});\n}}\n\n"
				getters_and_setters_definition += f"void MAxPy_{c}::set_{s}({t} val) {{\n\t{c}::{s} = val;\n}}\n\n"

				last_name = net['name']

		# get include files
		include_list = look4includes(self.source_output_dir + '%s__Syms.h' % self.class_name)

		# convert list of string to single string
		include_str = '\n'.join(include_list)

		# net structure
		#net_structure = write_net_structure('', top_instance, 0, 0)

		if self.saif_opt is True:
			self.parent_list = []
			self.write_instance_source_files(top_instance, skip_nets_first=True)

		#.................................................................................
		# open template for wrapper file

		file = open(self.wrapper_cpp_template,'r')
		file_text = file.read()
		file.close()
		
		#.................................................................................
		# replace template data

		file_text = file_text.replace("[[MAXPY_VERSION]]", version)
		file_text = file_text.replace("[[MODULE_NAME]]", self.top_name)
		file_text = file_text.replace("[[CLASS_NAME]]", self.class_name)
		file_text = file_text.replace("[[TOP_INSTANCE_METHOD]]", 'maxpy_' + top_instance['name'])
		file_text = file_text.replace("[[PYTHON_BIDING]]", pybind_string)
		file_text = file_text.replace("[[GETTERS_AND_SETTERS_DEFINITION]]", getters_and_setters_definition)
		file_text = file_text.replace("[[DATE_TIME]]", get_time_stamp())
		file_text = file_text.replace("[[NETLIST_AREA]]", "%f" % (self.area))
		file_text = file_text.replace("[[NETLIST_POWER]]", "%f" % (self.power))
		file_text = file_text.replace("[[NETLIST_TIMING]]", "%f" % (self.timing))
		if self.current_parameter != "":
			file_text = file_text.replace("[[PARAMETERS]]", f"\"{self.current_parameter}\"")
		else:
			file_text = file_text.replace("[[PARAMETERS]]", "\"\"")


		if self.vcd_opt:
			file_text = file_text.replace("[[VCD_OPT_IN]]", '')
			file_text = file_text.replace("[[VCD_OPT_OUT]]", '')
		else:
			file_text = file_text.replace("[[VCD_OPT_IN]]", '/* ')
			file_text = file_text.replace("[[VCD_OPT_OUT]]", ' */')

		if self.saif_opt is True:
			file_text = file_text.replace("[[SAIF_OPT_IN]]", '')
			file_text = file_text.replace("[[SAIF_OPT_OUT]]", '')
		else:
			file_text = file_text.replace("[[SAIF_OPT_IN]]", '/* ')
			file_text = file_text.replace("[[SAIF_OPT_OUT]]", ' */')

		if self.saif_opt is True:
			file_text = file_text.replace("[[SAIF_OPT_VALUE]]", "true")
		else:
			file_text = file_text.replace("[[SAIF_OPT_VALUE]]", "false")

		file = open(self.wrapper_cpp_path, 'w')
		file.write(file_text)
		file.close()	

		#.................................................................................
		# open template for header file

		file = open(self.wrapper_header_template,'r')
		file_text = file.read()
		file.close()

		# edit header template file
		self.parent_list = []
		
		if self.saif_opt is True:
			file_text = file_text.replace("[[INSTANCE_METHODS]]", self.get_instance_methods(top_instance))
		else:
			file_text = file_text.replace("[[INSTANCE_METHODS]]", "")
		
		file_text = file_text.replace("[[MAXPY_VERSION]]", version)
		file_text = file_text.replace("[[HEADER_INCLUDE]]", include_str)
		file_text = file_text.replace("[[MODULE_NAME]]", self.top_name)
		file_text = file_text.replace("[[CLASS_NAME]]", self.class_name)
		file_text = file_text.replace("[[VERILATOR_PATH]]", "/usr/share/verilator/include/")
		file_text = file_text.replace("[[GETTERS_AND_SETTERS_DECLARATION]]", getters_and_setters_declaration)

		if self.vcd_opt:
			file_text = file_text.replace("[[VCD_OPT_IN]]", '')
			file_text = file_text.replace("[[VCD_OPT_OUT]]", '')
		else:
			file_text = file_text.replace("[[VCD_OPT_IN]]", '/* ')
			file_text = file_text.replace("[[VCD_OPT_OUT]]", ' */')

		if self.saif_opt is True:
			file_text = file_text.replace("[[SAIF_OPT_IN]]", '')
			file_text = file_text.replace("[[SAIF_OPT_OUT]]", '')
		else:
			file_text = file_text.replace("[[SAIF_OPT_IN]]", '/* ')
			file_text = file_text.replace("[[SAIF_OPT_OUT]]", ' */')

		#.................................................................................
		# write header file

		file = open(self.wrapper_header_path, 'w')
		file.write(file_text)
		file.close()	


		return ErrorCodes.OK

	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
	# c2py-compile

	def c2py_compile (self):

		print("> C++ compilation")
		

		# remove old files from previous compilation
		if remove_old_files(self.compiled_module_path) != 0:
			return ErrorCodes.C2PY_COMPILE

		# to include VCD_files = verilated_vcd_c.h
		# https://zipcpu.com/blog/2017/06/21/looking-at-verilator.html
		
		# assemble terminal command for pybind compilation

		if self.vcd_opt == True:
			pybind_string = \
				'c++' + ' ' \
				+ os.environ.get('VERI_FLAGS') + ' ' \
				+ '-I' + os.environ.get('PYBIND_LIBS') + ' ' \
				+ '-I /usr/share/verilator/include' + ' ' \
				+ '/usr/share/verilator/include/verilated.cpp' + ' ' \
				+ '/usr/share/verilator/include/verilated_vcd_c.cpp' + ' ' \
				+ self.source_output_dir  + '*.cpp' + ' ' \
				+ '-o ' + self.compiled_module_path 
		else:
			pybind_string = \
				'c++' + ' ' \
				+ os.environ.get('VERI_FLAGS') + ' ' \
				+'-I' + os.environ.get('PYBIND_LIBS') + ' ' \
				+ '-I /usr/share/verilator/include' + ' ' \
				+ '/usr/share/verilator/include/verilated.cpp' + ' ' \
				+ self.source_output_dir  + '*.cpp' + ' ' \
				+'-o ' + self.compiled_module_path

		if self.log_opt:
			# create log file
			log_filename = self.target_compile_dir + ('log-c2py_compile.txt')
			#print('  > Creating log file: ' + log_filename)
			log_file = open(log_filename, 'w')
			# initial information in log file
			log_file.write('MAxPy: PYBIND COMPILATION LOG\n\n')
			log_file.write('Command line:\n\n')
			log_file.write(pybind_string)
			log_file.write('\n\n')
			log_file.write('\n\n')
			log_file.write(get_time_stamp())
			log_file.write('\n\n')
			log_file.write('Terminal log:\n\n')

			# close file and then open it again to avoid concurrency problems with subprocess call below
			log_file.close()
			# reopen log file as append
			log_file = open(log_filename, 'a')

		#print('  > Running compilation command')#: ' + pybind_string)

		# execute compilation command as subprocess		
		if self.log_opt:
			child = subprocess.Popen(pybind_string, stdout=log_file, stderr=subprocess.STDOUT, shell=True)
		else:
			child = subprocess.Popen(pybind_string, shell=True)

		child.communicate()
		error_code = child.wait()

		if self.log_opt:
			log_file.write('\n\n')
			log_file.write(get_time_stamp())
			log_file.write('\n\n')
			log_file.close()
		
		if error_code != 0:
			ret_val = ErrorCodes.C2PY_COMPILE_ERROR
		else:
			ret_val = ErrorCodes.OK
		
		return ret_val

	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
	# checkpymod

	def checkpymod (self):

		print("> Module check (should print module\'s name)")
		
		#print('  > Runnin test script (should print module\'s name):')

		module_test_string = "python -c \""
		module_test_string += "from {m} import {n};".format(m=self.pymod_path, n=self.top_name)
		module_test_string += "print('  >', %s.%s().name())\"" % (self.top_name, self.top_name)

		#print(module_test_string)

		child = subprocess.Popen(module_test_string, shell=True)
		child.communicate()
		error_code = child.wait()

		if error_code != 0:
			ret_val = ErrorCodes.CHECKPYMOD_ERROR
		else:
			ret_val = ErrorCodes.OK

		return ret_val


	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

	# veri2c parser methods
	def parse_verilator_header(self, header_filename, instance_name):

		header = open(self.source_output_dir + header_filename)
		header_text = header.readlines()
		header.close()

		instance = {'name': '', 'nets': [], 'instances': [], 'methods': [], 'class': header_filename}

		# pass 1: get instance name
		instance['name'] = instance_name

		# pass 2: look for other declared classes
		class_names = look4classes(header_text)

		# pass 3: look for nets inside this instance
		if header_filename == "sub_" + self.top_name + ".h":
			instance['nets'] = self.look4nets(header_text, skip_ports=True)
		else:
			instance['nets'] = self.look4nets(header_text, skip_ports=False)

		# pass 4: look for instances inside this instance
		cells_flag = 0
		private_flag = 0
		for line in header_text:
			line = line.strip(' \t\n\r')

			if line.find('private') == 0:
				private_flag = 1
			elif line.find('public') == 0:
				private_flag = 0

			if private_flag:
				continue

			if line.find('// CELLS') == 0:
				cells_flag = 1
			elif line.find('// PORTS') == 0:
				cells_flag = 0
			elif line.find('// LOCAL SIGNALS') == 0:
				cells_flag = 0
			elif line.find('// LOCAL VARIABLES') == 0:
				cells_flag = 0
			elif line.find('// INTERNAL VARIABLES') == 0:
				cells_flag = 0
			elif line.find('// CONSTRUCTORS') == 0:
				cells_flag = 0
			elif line.find('// INTERNAL METHODS') == 0:
				cells_flag = 0

			if cells_flag:
				for class_name in class_names:
					try:
						class_compare = line.split()[0].replace('*', '')
					except:
						class_compare = ''

					if class_name == class_compare:
						name = line.split()[1].replace(';','')

						if name == 'const':
							name = line.split()[2].replace(';','')


						if class_name == "sub_" + self.top_name:	
							self.parent_list.append(name)		
							instance['instances'].append(self.parse_verilator_header(class_name + '.h', 	name))
							self.parent_list = self.parent_list[:-1]

		# pass 5: look for methods
		instance['methods'] = look4methods(header_text)

		return instance


	def look4nets(self, text, skip_ports):
		net_list = []
		private_flag = 0
		ports_flag = 0
		local_signals_flag = 0
		for line in text:
			line = line.strip(' \t\n\r')		
			if line.find('private') == 0:
				private_flag = 1
			elif line.find('public') == 0:
				private_flag = 0
			if private_flag == 1:
				continue

			if line.find('// PORTS') == 0 and skip_ports is False:
				ports_flag = 1
				local_signals_flag = 0
			elif line.find('// LOCAL SIGNALS') == 0:
				local_signals_flag = 1
				ports_flag = 0
			elif line.find('// LOCAL VARIABLES') == 0:
				local_signals_flag = 0
				ports_flag = 0
			elif line.find('// INTERNAL VARIABLES') == 0:
				ports_flag = 0
				local_signals_flag = 0
			elif line.find('// CONSTRUCTORS') == 0:
				ports_flag = 0
				local_signals_flag = 0
			elif line.find('// INTERNAL METHODS') == 0:
				ports_flag = 0
				local_signals_flag = 0
			elif line.find('// CELLS') == 0:
				ports_flag = 0
				local_signals_flag = 0


			if ports_flag:
				search = re.search(r'^VL_(SIG|IN|OUT|INOUT)', line)			
				if search is not None:			
					start, size_start = search.span()
					size_end = line.index('(')
					size = line[size_start:size_end]
					direction = line[line.index('_')+1:size_start]
					if len(size) > 0:
						try:
							size = int(size)
							type = 'single'
						except:
							type = 'array'
					else:
						size = 0
						type = 'single'
					
					name_start = size_end + 1
					name_end = line.index(',')
					name = line[name_start:name_end]

					name = name.replace('&', '')

					msb_start = name_end + 1
					msb_end = msb_start + line[msb_start:].index(',')
					msb = int(line[msb_start:msb_end])

					if size == 'W':
						lsb_start = msb_end + 1
						lsb_end = lsb_start + line[lsb_start:].index(',')
						lsb = int(line[lsb_start:lsb_end])

						array_start = lsb_end + 1
						array_end = array_start + line[array_start:].index(')')
						array = int(line[array_start:array_end])

					elif size == 0:
						size = msb + 1

					else:
						lsb_start = msb_end + 1
						lsb_end = lsb_start + line[lsb_start:].index(')')
						lsb = int(line[lsb_start:lsb_end])

					if type == 'single':

						# make a local copy of the input parent list so the parent list is not passed as reference
						# to the the nets. this way each net has its own parent list
						local_parent = []
						for parent in self.parent_list:
							local_parent.append(parent)


						short_name = name.replace('__PVT__','').replace('&', '')

						if msb == 0 and lsb == 0:
							net = {'name': name, 'bit_mask': 0x40, 'short_name': short_name, 'parent': local_parent}
							net_list.append(net)
						else:
							for bit in range(msb+1):
							#for bit in range(msb+1, 0, -1):	# reverse order
								#bit -= 1
								net = {'name': name, 'bit_mask': bit, 'short_name': short_name, 'parent': local_parent}
								net_list.append(net)
					
					#TODO: ADD biding code for array port
					#else:
					#	print('    port[name: %s (%s), size: %s[%d][%d:%d]] << %s >>' % (name, direction, size, array, msb, lsb, line))

			elif local_signals_flag:
				if 'CData' in line or 'SData' in line or 'IData' in line or 'WData' in line:
					
					name = line.split()[1].replace(';', '')

					if '[' in name:

						##TODO: add binding code for arrays
						#name = name[:name.index('[')]
						continue

					if '>' in name:
						#when type contains VlUnpacked directive
						name = line.split()[2].replace(';','')

					name = name.replace('&', '')

					local_parent = []
					for parent in self.parent_list:
						local_parent.append(parent)

					short_name = name

					if short_name.find(self.top_name) == 0:
						short_name = short_name.replace(self.top_name, '')

					if '__' in short_name:
						short_name = short_name.replace('__', '')

					if 'PVT' in short_name:
						short_name = short_name.replace('PVT', '')
						
					if 'DOT' in short_name:
						short_name = short_name.replace('DOT', '')

					if 'F1' in short_name:
						short_name = short_name.replace('F1', '')

					if 'DIV' in short_name:
						short_name = short_name.replace('DIV', '')

					if 'dut' in short_name:
						short_name = short_name.replace('dut', '')

					if '&' in short_name:
						short_name = short_name.replace('&', '')

					net = {'name': name, 'bit_mask': 0x40, 'short_name': short_name, 'parent': local_parent}

					
					net_list.append(net)


		return net_list


	def write_instance_source_files(self, instance, skip_nets_first=False):
		
		name = instance['name']
		self.parent_list.append(name)

		hierarchical_name = ''
		for instance_name in self.parent_list:
			hierarchical_name += instance_name

		# open template file
		file = open(self.instance_cpp_template,'r')
		file_text = file.read()
		file.close()

		# generate code for instance
		code = '\ttop = new Instance("%s");\n' % (name.replace('__PVT__',''))
		code += '\tpi = top;\n'

		# net initialization
		if len(instance['nets']) > 0 and skip_nets_first is False:
			# first net
			net = instance['nets'][0]
			code += ('\tpi->head_net = new Net("%s", &%s, %d);\n' % (net['short_name'], get_net_hierarchical_name(net), net['bit_mask']))
			code += ('\tpn = pi->head_net;\n')

			if len(instance['nets']) > 1:
				# intermediate nets
				for net in instance['nets'][1:len(instance['nets'])-1]:
					code += ('\tpn->next = new Net("%s", &%s, %d);\n' % (net['short_name'], get_net_hierarchical_name(net), net['bit_mask']))
					code += ('\tpn = pn->next;\n')

				# last net
				net = instance['nets'][len(instance['nets'])-1]
				code += ('\tpn->next = new Net("%s", &%s, %d);\n' % (net['short_name'], get_net_hierarchical_name(net), net['bit_mask']))
				code += ('\n')
			
			else:
				# last net
				net = instance['nets'][len(instance['nets'])-1]
				code += ('\tpn->next = new Net("%s", &%s, %d);\n' % (net['short_name'], get_net_hierarchical_name(net), net['bit_mask']))
				code += ('\n')


		# instance initialization

		qty = len(instance['instances'])

		if qty > 0:
			# first net
			current_instance = instance['instances'][0]
			code += ('\tpi->head_instance = maxpy_%s%s();\n' % (hierarchical_name, current_instance['name']))

			if qty > 1:

				if qty > 2:
					# intermediate nets
					for current_instance in instance['instances'][1:qty-1]:
						code += ('\tpi->next = maxpy_%s%s();\n' % (hierarchical_name, current_instance['name']))
						code += ('\tpi = pi->next;\n')

				# last net
				current_instance = instance['instances'][qty-1]
				code += ('\tpi->next = maxpy_%s%s();\n' % (hierarchical_name, current_instance['name']))
		
		# replace template data
		file_text = file_text.replace("[[CLASS_NAME]]", self.class_name)
		#file_text = file_text.replace("[[MODULE_NAME]]", self.top_name)
		file_text = file_text.replace("[[INSTANCE_NAME]]", hierarchical_name)
		file_text = file_text.replace("[[INSTANCE_CODE]]", code)

		# write instance source code file
		file = open(self.source_output_dir + 'maxpy_' + hierarchical_name + '.cpp', 'w')
		file.write(file_text)
		file.close()	

		# write files for sub instances
		for current_instance in instance['instances']:
			self.write_instance_source_files(current_instance)

		self.parent_list = self.parent_list[:-1]


	def get_instance_methods(self, instance):

		self.parent_list.append(instance['name'])

		name = ''
		for instance_name in self.parent_list:
			name += instance_name

		#method_list = ('\t\tInstance* maxpy_%s();\n' % instance['name'])
		method_list = ('\t\tInstance* maxpy_%s();\n' % name)

		for current_instance in instance['instances']:
			method_list += self.get_instance_methods(current_instance)

		self.parent_list = self.parent_list[:-1]

		return method_list


	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

	def get_area(self, netlist_path):
		self.area = report_area(self.library_path_lib, netlist_path)
		print(f"  > Netlist estimated area = {self.area}")

	# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
	# OpenSTA methods

	def get_power_and_timing(self, netlist_path):

		sta_cmd_file_path = "cmd_file.sta"
		power_report_path = f"opensta_{self.top_name}_power.rpt"
		timing_report_path = f"opensta_{self.top_name}_timing.rpt"

		file_handle = open(self.opensta_cmd_file_path, "r")
		cmd_file_text = file_handle.read()
		file_handle.close()
		cmd_file_text = cmd_file_text.replace("[[LIBRARY]]", self.library_path_lib)
		cmd_file_text = cmd_file_text.replace("[[NETLIST]]", netlist_path)
		cmd_file_text = cmd_file_text.replace("[[TOPMODULE]]", self.top_name)
		file_handle = open(sta_cmd_file_path, "w")
		file_handle.write(cmd_file_text)
		file_handle.close()
		sta_string = "sta cmd_file.sta"

		if self.log_opt:
			# create log file
			log_filename = self.target_compile_dir  + ('log-opensta.txt')
			log_file = open(log_filename, 'w')

			# initial information in log file
			log_file.write('MAxPy: OpenSTA LOG\n\n')
			log_file.write('Command line:\n\n')
			log_file.write(sta_string)
			log_file.write('\n\n')
			log_file.write(get_time_stamp())
			log_file.write('\n\n')
			log_file.write('Terminal log:\n\n')
			log_file.close()					# close file and then open it again to avoid concurrency problems with subprocess call below
			log_file = open(log_filename, 'a')	# reopen log file as append

		if self.log_opt:
			child = subprocess.Popen(sta_string, stdout=log_file, stderr=subprocess.STDOUT, shell=True)
		else:
			child = subprocess.Popen(sta_string, shell=True)

		child.communicate()
		child.wait()

		if self.log_opt:
			log_file.write('\n\n')
			log_file.write(get_time_stamp())
			log_file.write('\n\n')
			log_file.close()

		# get power report
		file_handle = open(power_report_path, "r")
		power_report_lines = file_handle.readlines()
		file_handle.close()
		self.power = 0.0
		for line in power_report_lines:
			line_items = line.rsplit()
			if len(line_items) < 1:
				continue
			if line_items[0] == "Total":
				self.power = float(line_items[4])
				break

		# get timing report
		file_handle = open(timing_report_path, "r")
		timing_report_lines = file_handle.readlines()
		file_handle.close()
		self.timing = 0.0
		if len(timing_report_lines) >= 3:
			data_line = timing_report_lines[2].rsplit()
			try:
				self.timing = float(data_line[-1])
			except:
				self.timing = 0.0

		print(f"  > Netlist estimated power = {self.power} W")
		print(f"  > Netlist estimated maximum delay = {self.timing} nS")

		os.remove(sta_cmd_file_path)
		os.remove(power_report_path)
		os.remove(timing_report_path)

		self.power *= 1e6 # convert to uWatts


#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------





#----------------------------------------------------------------------------------------------------------------------
#	end of file
#----------------------------------------------------------------------------------------------------------------------
