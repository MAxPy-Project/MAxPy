import enum
import datetime


version = '0.1.2-dev'


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



#----------------------------------------------------------------------------------------------------------------------
#	eof
#----------------------------------------------------------------------------------------------------------------------
