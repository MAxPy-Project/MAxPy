from subprocess import Popen
from os import remove

def est_area(axckt):

    with open(axckt.res.path_tech_lib, "r") as f:
        techlib_lines = f.readlines()

    with open(axckt.working_netlist, "r") as f:
        netlist_lines = f.readlines()

    dictAreas = {}
    for line in techlib_lines:
        splitLine = line.rstrip().split()
        if len(splitLine) > 0:
            if "cell" in splitLine[0]:
                cellName = splitLine[1][1:-1]
            elif "area" in splitLine[0]:
                area = float(splitLine[2][:-1])
                dictAreas[cellName] = area

    area = 0.0
    state = 0

    for line in netlist_lines:
        # look for cell name
        if state == 0:
            splitLine = line.rstrip().split()
            if len(splitLine) > 0:
                cell_type = splitLine[0]
                if cell_type in dictAreas.keys():
                    cell_area_value = dictAreas[cell_type]
                    empty_output_flag = False
                    state = 1
         # look for cell end
        if state == 1:
            if "()" in line:
                empty_output_flag = True
            if ";" in line:
                if empty_output_flag is False:
                    area += cell_area_value
                state = 0

    axckt.area = area


def est_power_timing(axckt):

    sta_cmd_file_path = "cmd_file.sta"
    power_report_path = "power.rpt"
    timing_report_path = "timing.rpt"

    cmd_file_text = axckt.res.template_opensta_cmd
    cmd_file_text = cmd_file_text.replace("[[LIBRARY]]", axckt.res.path_tech_lib)
    cmd_file_text = cmd_file_text.replace("[[NETLIST]]", axckt.working_netlist)
    cmd_file_text = cmd_file_text.replace("[[TOPMODULE]]", axckt.top_name)
    cmd_file_text = cmd_file_text.replace("[[POWER_REPORT_PATH]]", power_report_path)
    cmd_file_text = cmd_file_text.replace("[[TIMING_REPORT_PATH]]", timing_report_path)
    with open(sta_cmd_file_path, "w") as f:
        f.write(cmd_file_text)
    sta_cmd= f"sta {sta_cmd_file_path}"

    # create log file
    log_path = f"{axckt.target_compile_dir}opensta.log"
    log_file = open(log_path, 'w')
    # initial information in log file
    log_file.write("MAxPy: OpenSTA LOG\n\n")
    log_file.write(f"Command line:\n\n{sta_cmd}\n\n")
    log_file.write(f"OpenSTA file:\n\n{cmd_file_text}\n\n")
    log_file.write("Log from stdout and stderr:\n\n")
    # close file and then open it again to avoid concurrency problems with subprocess call below
    log_file.close()
    log_file = open(log_path, "a")

    child = Popen(sta_cmd, stdout=log_file, stderr=log_file, shell=True)
    child.communicate()
    child.wait()

    # get power report
    with open(power_report_path, "r") as f:
        power_report_lines = f.readlines()
    log_file.write(f"Power report:\n\n{power_report_lines}\n\n")
    power = 0.0
    for line in power_report_lines:
        line_items = line.rsplit()
        if len(line_items) < 1:
            continue
        if line_items[0] == "Total":
            power = float(line_items[4])
            break

    # get timing report
    with open(timing_report_path, "r") as f:
        timing_report_lines = f.readlines()
    log_file.write(f"Timing report:\n\n{timing_report_lines}\n\n")
    timing = 0.0
    if len(timing_report_lines) >= 3:
        data_line = timing_report_lines[2].rsplit()
        try:
            timing = float(data_line[-1])
        except:
            timing = 0.0

    log_file.close()

    power *= 1e6 # convert to uWatts

    remove(sta_cmd_file_path)
    remove(power_report_path)
    remove(timing_report_path)

    axckt.power = power
    axckt.timing = timing


