from MAxPy import *
from testbench import testbench_run

circuit = maxpy.AxCircuit(top_name="adder4")#, synth_overwrite = True)
circuit.set_testbench_script(testbench_run)

# basic flow rtl level
circuit.rtl2py(target="exact")


# basic flow gate level
circuit.set_synth_tool("yosys")
circuit.rtl2py(target="exact_yosys")


# parameter substituition loop "study no 1"
circuit.set_group("study_no_1")
circuit.set_synth_tool(None)
circuit.parameters = {
    "[[PARAM_K]]": ["1","2"],
    "[[PARAM_ADDER01]]": ["copyA","copyB"],
}
circuit.rtl2py_param_loop(base="rtl_param")
