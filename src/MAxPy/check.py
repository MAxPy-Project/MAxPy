from subprocess import Popen
from .utility import ErrorCodes

def check(axckt):
    print("> Module check (should print module\'s name)")

    module_test_string = "python -c \""
    module_test_string += "from {m} import {n};".format(m=axckt.pymod_path, n=axckt.top_name)
    module_test_string += "print('  >', %s.top().name())\"" % (axckt.top_name)

    child = Popen(module_test_string, shell=True)
    child.communicate()
    error_code = child.wait()

    if error_code != 0:
        ret_val = ErrorCodes.CHECKPYMOD_ERROR
    else:
        ret_val = ErrorCodes.OK

    return ret_val
