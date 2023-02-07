from MAxPy import maxpy
from MAxPy import probprun
from testbench import testbench_run

circuit = maxpy.AxCircuit(top_name="adder4")#, synth_overwrite = True)
circuit.set_testbench_script(testbench_run)

basic flow rtl level
circuit.rtl2py(target="exact")


# basic flow gate level
circuit.set_synth_tool("yosys")
circuit.rtl2py(target="exact_yosys")


# parameter substituition loop "study no 1"
circuit.set_group("study_no_1")
circuit.set_synth_tool(None)
circuit.set_results_filename("output.csv")
circuit.parameters = {
    "[[PARAM_ADDER01]]": ["copyA","copyB", "eta1", "loa", "trunc0", "trunc1"],
    "[[PARAM_K]]": ["0", "1", "2", "3"],
}
circuit.rtl2py_param_loop(base="rtl_param")


# generate pareto front
circuit.set_synth_tool("yosys")
pareto_circuits = circuit.get_pareto_front("area", "mre")
probprun.probprun_loop(circuit, pareto_circuits)
