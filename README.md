# MAxPy Multi-layer Approximate Computing Python Framework

**MAxPy** is a framework aimed for simulation and exploration of Approximate Computing techniques in VLSI designs. It is Ptyhon-based, free and *open-source*.

Check out our <a href="https://maxpy-project.github.io/MAxPy" target="_blank">documentation</a>!

MAxPy is part of the <a href="https://github.com/MAxPy-Project" target="_blank">MAxPy Project</a>.

## Installation
```sh
pip install MAxPy
```

## Examples
### Basic flow
#### RTL-level
```python
from MAxPy import maxpy
from testbench import testbench_run
circuit = maxpy.AxCircuit(top_name="adder4")
circuit.set_testbench_script(testbench_run)
circuit.rtl2py(target="exact")
```
#### Gate-level
```python
from MAxPy import maxpy
from testbench import testbench_run
circuit = maxpy.AxCircuit(top_name="adder4")
circuit.set_testbench_script(testbench_run)
circuit.set_synth_tool("yosys")
circuit.rtl2py(target="exact_yosys")
```
### Parameter exploration
```python
from MAxPy import maxpy
from testbench import testbench_run
circuit = maxpy.AxCircuit(top_name="adder4")
circuit.set_testbench_script(testbench_run)
circuit.set_group("study_no_1")
circuit.set_synth_tool(None)
circuit.set_results_filename("output.csv")
circuit.parameters = {
    "[[PARAM_ADDER01]]": ["copyA","copyB", "eta1", "loa", "trunc0", "trunc1"],
    "[[PARAM_K]]": ["0", "1", "2", "3"],
}
circuit.rtl2py_param_loop(base="rtl_param")
```
### Probabilist pruning
```python
from MAxPy import maxpy
from MAxPy import probprun
from testbench import testbench_run
circuit = maxpy.AxCircuit(top_name="adder4")
circuit.set_testbench_script(testbench_run)
circuit.set_synth_tool("yosys")
pareto_circuits = circuit.get_pareto_front("area", "mre")
probprun.probprun_loop(circuit, pareto_circuits)
```
