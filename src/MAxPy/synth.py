from subprocess import Popen
from os import remove
from .utility import ErrorCodes

def synth(axckt):

    print("> Synth")

    ## removed! check done in AxCkt class
    # if axckt.synth_tool not in axckt.res.synth_tools:
    #     print(f"> Invalid synth tool! ({axckt.synth_tool})")
    #     print(f"  Available tools:")
    #     for tool in axckt.res.synth_tools:
    #         print(f"    - {tool}:")

    # create log file
    log_path = f"{axckt.target_compile_dir}synth.log"
    log_file = open(log_path, "w")

    if axckt.synth_tool == "yosys":
        file_text = axckt.res.template_yosys_synth
        #file_text = file_text.replace("[[RTLFILENAME]]", f"{self.axlib_path} {self.base_path}") #TODO!
        file_text = file_text.replace("[[RTLFILENAME]]", f"{axckt.base_path}")
        file_text = file_text.replace("[[LIBFILENAME]]", axckt.res.path_tech_verilog)
        file_text = file_text.replace("[[TOPMODULE]]", axckt.top_name)
        file_text = file_text.replace("[[NETLIST]]", axckt.netlist_target_path)
        file_text = file_text.replace("[[LIBRARY]]", axckt.res.path_tech_lib)
        file_text = file_text.replace("[[LIBRARYABC]]", axckt.res.path_tech_lib)

        with open("synth.ys", "w") as f:
            f.write(file_text)

        yosys_cmd = "yosys synth.ys;"

        # initial information in log file
        log_file.write("MAxPy: SYNTHESIS USING YOSYS\n\n")
        log_file.write(f"Command line:\n\n{yosys_cmd}\n\n")
        log_file.write(f"Synth file:\n\n{file_text}\n\n")
        log_file.write("Log from stdout and stderr:\n\n")
        # close file and then open it again to avoid concurrency problems with subprocess call below
        log_file.close()
        log_file = open(log_path, "a")

        # execute compilation command as subprocess
        child = Popen(yosys_cmd, stdout=log_file, stderr=log_file, shell=True)
        child.communicate()
        error_code = child.wait()

        # close logfile
        log_file.write(f"Synth command exit code: {error_code}")
        log_file.close()

        if error_code != 0:
            ret_val = ErrorCodes.SYNTH_ERROR
        else:
            ret_val = ErrorCodes.OK

        remove ("synth.ys")

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

