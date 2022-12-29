from MAxPy import *
from testbench import testbench_run

circuit = maxpy.AxCircuit(top_name="adder4")#, synth_overwrite = True)
circuit.set_testbench_script(testbench_run)
circuit.set_synth_tool("yosys")
circuit.rtl2py(target="exact",log_opt=True, saif_opt=False)

    #circuit.parameters = {
#    "[[PARAM_K]]": ["1","2"],
#    "[[PARAM_ADDER01]]": ["copyA","copyB"],
#}

#circuit.rtl2py_param_loop(base="rtl_param", testbench_script=testbench_run)
#circuit.rtl2py_param_loop(base="rtl_param", synth_tool="yosys", testbench_script=testbench_run)
#circuit.rtl2py_param_loop(base="rtl_param", synth_tool="yosys")
#circuit.testbench_param_loop(testbench_script=testbench_run)
#circuit.rtl2py(target="veri", synth_tool="yosys")

