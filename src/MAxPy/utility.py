import enum
import subprocess
import datetime
import re

class MainLoopFsm(enum.Enum):
	INIT = enum.auto()
	PREPARE_PATHS = enum.auto()
	SYNTH = enum.auto()
	VERI2C = enum.auto()
	C2PY_PARSE = enum.auto()
	C2PY_COMPILE = enum.auto()
	CHECK_PYMOD = enum.auto()
	TESTBENCH = enum.auto()
	VCD2SAIF = enum.auto()
	QOR_STA = enum.auto()
	VERI2XML = enum.auto()
	XML2DOT = enum.auto()
	EVALUATE_RESULTS = enum.auto()
	PRUNING = enum.auto()
	END = enum.auto()

class ErrorCodes(enum.Enum):
    OK = enum.auto()
    SYNTH_ERROR = enum.auto()
    VERI2C_ERROR = enum.auto()
    C2PY_PARSE_ERROR = enum.auto()
    C2PY_COMPILE_ERROR = enum.auto()
    CHECKPYMOD_ERROR = enum.auto()

def remove_old_files(path):
    rm_old_files_string = "rm -f {path}".format(path=path)
    child = subprocess.Popen(rm_old_files_string, shell=True)
    child.communicate()
    exit_code = child.wait()

    # if exit_code == 0:
    #     print('  > Removing files from last compilation... Ok!')
    # else:
    #     print('  > Removing files from last compilation... Error, return code %d' % exit_code)

    return exit_code

def get_time_stamp():
	now = datetime.datetime.now()
	year = '{:02d}'.format(now.year)
	month = '{:02d}'.format(now.month)
	day = '{:02d}'.format(now.day)
	hour = '{:02d}'.format(now.hour)
	minute = '{:02d}'.format(now.minute)
	second = '{:02d}'.format(now.second)
	date_string = '{}-{}-{} {}:{}:{}'.format(month, day, year, hour, minute, second)
	return date_string



#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------
# veri2c parser functions

def saif_indent_level(level):
	space = ''
	for i in range(level):
		space += '  '
	return space


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

#----------------------------------------------------------------------------------------------------------------------
#	eof
#----------------------------------------------------------------------------------------------------------------------
