from subprocess import Popen
from .utility import get_time_stamp
from .utility import version
from .utility import ErrorCodes
import re
import os


def wrapper(axckt):

    print("> C++/Python Wrapper")

    # remove old source files
    rm_old_files_string = f"rm -f {axckt.wrapper_cpp_path} {axckt.wrapper_header_path}"
    child = Popen(rm_old_files_string, shell=True)
    child.communicate()
    child.wait()

    # get instance and nets structure
    axckt.parent_list = []
    header_filename = f"{axckt.class_name}.h"
    top_instance = parse_verilator_header(axckt, header_filename, axckt.top_name)

    # print log file
    log_path = f"{axckt.target_compile_dir}wrapper.log"
    log_file = open(log_path, "w")
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
            pybind_string += f"\t\t.def(\"{method}\", &MAxPy_{axckt.class_name}::{method})\n"

    pybind_string += "\n\t\t// getters and setters for inputs and outpus\n"

    last_name = ''
    for net in top_instance['nets']:
        if net['name'] != last_name:

            # todo: use corret type!
            s = net["short_name"]
            t = "int"
            c = axckt.class_name

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
    include_list = look4includes(axckt.source_output_dir + '%s__Syms.h' % axckt.class_name)

    # convert list of string to single string
    include_str = '\n'.join(include_list)

    # net structure
    #net_structure = write_net_structure('', top_instance, 0, 0)

    if axckt.saif_opt is True:
        axckt.parent_list = []
        write_instance_source_files(axckt, top_instance, skip_nets_first=True)

    # wrapper source file
    file_text = axckt.res.template_pybind_wrapper_source
    file_text = file_text.replace("[[MAXPY_VERSION]]", version)
    file_text = file_text.replace("[[MODULE_NAME]]", axckt.top_name)
    file_text = file_text.replace("[[CLASS_NAME]]", axckt.class_name)
    file_text = file_text.replace("[[TOP_INSTANCE_METHOD]]", 'maxpy_' + top_instance['name'])
    file_text = file_text.replace("[[PYTHON_BIDING]]", pybind_string)
    file_text = file_text.replace("[[GETTERS_AND_SETTERS_DEFINITION]]", getters_and_setters_definition)
    file_text = file_text.replace("[[DATE_TIME]]", get_time_stamp())
    file_text = file_text.replace("[[NETLIST_AREA]]", "%f" % (axckt.area))
    file_text = file_text.replace("[[NETLIST_POWER]]", "%f" % (axckt.power))
    file_text = file_text.replace("[[NETLIST_TIMING]]", "%f" % (axckt.timing))
    if axckt.current_parameter != "":
        file_text = file_text.replace("[[PARAMETERS]]", f"\"{axckt.current_parameter}\"")
    else:
        file_text = file_text.replace("[[PARAMETERS]]", "\"\"")


    if axckt.vcd_opt:
        file_text = file_text.replace("[[VCD_OPT_IN]]", '')
        file_text = file_text.replace("[[VCD_OPT_OUT]]", '')
    else:
        file_text = file_text.replace("[[VCD_OPT_IN]]", '/* ')
        file_text = file_text.replace("[[VCD_OPT_OUT]]", ' */')

    if axckt.saif_opt is True:
        file_text = file_text.replace("[[SAIF_OPT_IN]]", '')
        file_text = file_text.replace("[[SAIF_OPT_OUT]]", '')
    else:
        file_text = file_text.replace("[[SAIF_OPT_IN]]", '/* ')
        file_text = file_text.replace("[[SAIF_OPT_OUT]]", ' */')

    if axckt.saif_opt is True:
        file_text = file_text.replace("[[SAIF_OPT_VALUE]]", "true")
    else:
        file_text = file_text.replace("[[SAIF_OPT_VALUE]]", "false")

    # write to file
    with open(axckt.wrapper_cpp_path, "w") as f:
        f.write(file_text)

    # wrapper header file
    file_text = axckt.res.template_pybind_wrapper_header

    axckt.parent_list = []

    if axckt.saif_opt is True:
        file_text = file_text.replace("[[INSTANCE_METHODS]]", get_instance_methods(axckt, top_instance))
    else:
        file_text = file_text.replace("[[INSTANCE_METHODS]]", "")

    file_text = file_text.replace("[[MAXPY_VERSION]]", version)
    file_text = file_text.replace("[[HEADER_INCLUDE]]", include_str)
    file_text = file_text.replace("[[MODULE_NAME]]", axckt.top_name)
    file_text = file_text.replace("[[CLASS_NAME]]", axckt.class_name)
    file_text = file_text.replace("[[VERILATOR_PATH]]", os.environ.get('VERI_LIBS'))
    file_text = file_text.replace("[[GETTERS_AND_SETTERS_DECLARATION]]", getters_and_setters_declaration)

    if axckt.vcd_opt:
        file_text = file_text.replace("[[VCD_OPT_IN]]", '')
        file_text = file_text.replace("[[VCD_OPT_OUT]]", '')
    else:
        file_text = file_text.replace("[[VCD_OPT_IN]]", '/* ')
        file_text = file_text.replace("[[VCD_OPT_OUT]]", ' */')

    if axckt.saif_opt is True:
        file_text = file_text.replace("[[SAIF_OPT_IN]]", '')
        file_text = file_text.replace("[[SAIF_OPT_OUT]]", '')
    else:
        file_text = file_text.replace("[[SAIF_OPT_IN]]", '/* ')
        file_text = file_text.replace("[[SAIF_OPT_OUT]]", ' */')


    with open(axckt.wrapper_header_path, "w") as f:
        f.write(file_text)

    return ErrorCodes.OK


def parse_verilator_header(axckt, header_filename, instance_name):

    with open(f"{axckt.source_output_dir}{header_filename}", "r") as f:
        header_text = f.readlines()

    instance = {'name': '', 'nets': [], 'instances': [], 'methods': [], 'class': header_filename}

    # pass 1: get instance name
    instance['name'] = instance_name

    # pass 2: look for other declared classes
    class_names = look4classes(header_text)

    # pass 3: look for nets inside this instance
    if header_filename == "sub_" + axckt.top_name + ".h":
        instance['nets'] = look4nets(axckt, header_text, skip_ports=True)
    else:
        instance['nets'] = look4nets(axckt, header_text, skip_ports=False)

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


                    if class_name == "sub_" + axckt.top_name:
                        axckt.parent_list.append(name)
                        instance['instances'].append(parse_verilator_header(axckt, class_name + '.h', 	name))
                        axckt.parent_list = axckt.parent_list[:-1]

    # pass 5: look for methods
    instance['methods'] = look4methods(header_text)

    return instance


def look4nets(axckt, text, skip_ports):
    net_list = []
    private_flag = 0
    ports_flag = 0
    local_signals_flag = 0
    design_specific_state_flag = 0
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
            design_specific_state_flag = 0
        elif line.find('// LOCAL SIGNALS') == 0:
            local_signals_flag = 1
            ports_flag = 0
            design_specific_state_flag = 0
        elif line.find('// DESIGN SPECIFIC STATE') == 0:
            local_signals_flag = 0
            ports_flag = 0
            design_specific_state_flag = 1
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
                    for parent in axckt.parent_list:
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

        elif local_signals_flag or design_specific_state_flag:
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
                for parent in axckt.parent_list:
                    local_parent.append(parent)
                short_name = name
                replace_list = [
                        axckt.top_name,
                        "__",
                        "PVT",
                        "DOT",
                        "F1",
                        "DIV",
                        "dut",
                        "&",
                        "Vcellinp",
                        "Vcellout"
                    ]
                for item2replace in replace_list:
                    short_name = short_name.replace(item2replace, "")
                net = {'name': name, 'bit_mask': 0x40, 'short_name': short_name, 'parent': local_parent}
                net_list.append(net)
    return net_list


def write_instance_source_files(axckt, instance, skip_nets_first=False):

    name = instance['name']
    axckt.parent_list.append(name)

    hierarchical_name = ''
    for instance_name in axckt.parent_list:
        hierarchical_name += instance_name

    # open template file
    file_text = axckt.res.template_instance_source

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
    file_text = file_text.replace("[[CLASS_NAME]]", axckt.class_name)
    file_text = file_text.replace("[[INSTANCE_NAME]]", hierarchical_name)
    file_text = file_text.replace("[[INSTANCE_CODE]]", code)

    # write instance source code file
    file = open(axckt.source_output_dir + 'maxpy_' + hierarchical_name + '.cpp', 'w')
    file.write(file_text)
    file.close()

    # write files for sub instances
    for current_instance in instance['instances']:
        write_instance_source_files(axckt, current_instance)

    axckt.parent_list = axckt.parent_list[:-1]


def get_instance_methods(axckt, instance):

    axckt.parent_list.append(instance['name'])

    name = ''
    for instance_name in axckt.parent_list:
        name += instance_name

    #method_list = ('\t\tInstance* maxpy_%s();\n' % instance['name'])
    method_list = ('\t\tInstance* maxpy_%s();\n' % name)

    for current_instance in instance['instances']:
        method_list += get_instance_methods(axckt, current_instance)

    axckt.parent_list = axckt.parent_list[:-1]

    return method_list


def show_structure(instance, level):

	str = ''

	tab = ''
	for i in range(level):
		tab += '  '

	str += '%sinstance name: %s\n' % (tab, instance['name'])

	for net in instance['nets']:
		str += '%snet: %s\n' % (tab, net)

	for inst in instance['instances']:
		str += show_structure(inst, level+1)

	for method in instance['methods']:
		str += '%smethod: %s\n' % (tab, method)

	return str


def look4classes(text):
	search_pattern = 'class '
	class_list = []
	for line in text:
		line = line.strip(' \t\n\r')
		if line.find(search_pattern) == 0 and line.find('_VerilatedVcd') < 0 and line.find('__Syms') < 0:
			class_list.append(line.replace(search_pattern, '').replace(';',''))
	return class_list


def look4methods(text):
	method_list = []
	private_flag = 0
	for line in text:
		line = line.strip(' \t\n\r')
		if line.find('private') == 0:
			private_flag = 1
		elif line.find('public') == 0:
			private_flag = 0
		if private_flag == 1:
			continue

		search = re.search(r'^void [a-zA-Z]', line)
		if search is not None:
			start, method_start = search.span()
			method_start =  method_start - 1
			method_end = line.index('(')
			method = line[method_start:method_end]
			method_list.append(method)

	return method_list


def look4includes(header_path):
	header = open(header_path)
	header_text = header.readlines()
	header.close()
	include_list = []
	for line in header_text:
		line = line.strip(' \t\n\r')
		if line.find('#include') == 0:
			include_list.append(line)
	return include_list


def get_net_hierarchical_name(net):
	str_out = ''
	for name in net['parent']:
		str_out += (name + '->')
	str_out += net['name']
	return str_out


def write_net_structure(str, instance, level, instance_index):

	tab = '\t\t\t'
	for i in range(level):
		tab += '\t'

	if level == 0:
		str += ('%stop_instance = new Instance("%s", NULL);\n' % (tab, instance['name']))
		str += ('%spi = top_instance;\n' % (tab))
	else:

		if instance_index == 0:
			# se primeiro instance da lista:
			str += '%spi->head_instance = new Instance("%s", pi);\n' % (tab, instance['name'].replace('__PVT__', ''))
			str += '%spi = pi->head_instance;\n' % (tab)
		else:
			# se proximos instances
			str += '%spi->next = new Instance("%s", pi);\n' % (tab, instance['name'].replace('__PVT__', ''))
			str += '%spi = pi->next;\n' % (tab)

	#str += '%spn = pi->head_net;\n' % (tab)

	# primeiro net
	str += ('%s// instance "%s" from class in "%s"\n' % (tab, instance['name'], instance['class']))
	net = instance['nets'][0]
	str += ('%spi->head_net = new Net("%s", &%s, %d);\n' % (tab, net['short_name'], get_net_hierarchical_name(net), net['bit_mask']))
	str += ('%spn = pi->head_net;\n' % tab)
	#str += ('%spn = pn->next;\n' % tab)

	# nets intermediarios
	for net in instance['nets'][1:len(instance['nets'])-1]:
		str += ('%spn->next = new Net("%s", &%s, %d);\n' % (tab, net['short_name'], get_net_hierarchical_name(net), net['bit_mask']))
		str += ('%spn = pn->next;\n' % tab)

	# ultimo net
	net = instance['nets'][len(instance['nets'])-1]
	str += ('%spn->next = new Net("%s", &%s, %d);\n' % (tab, net['short_name'], get_net_hierarchical_name(net), net['bit_mask']))
	str += ('\n')

	# prepara proximo instance
	if instance_index != 0:
		str += '%spi = pi->parent;\n' % (tab)
		str += '%swhile(pi->next)\n' % (tab)
		str += '%s\tpi = pi->next;\n' % (tab)

	str += ('\n')

	# instances
	for index, inst in enumerate(instance['instances']):
		str = write_net_structure(str, inst, level + 1, index)

	return str
