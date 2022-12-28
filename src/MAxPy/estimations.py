
def est_area(netlist_path, techlib_path):

    with open(techlib_path, "r") as f:
        techlib_lines = f.readlines()

    with open(netlist_path, "r") as f:
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

    print(f"Netlist estimated area: {area}")
    return area


def est_power_delay(axckt):
    pass
