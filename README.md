# MAxPy Multi-layer Approximate Computing Python Framework
## Preparation
Prior to running MAxPy, the following preparation needs to be done.
1. Install required system packages: ```make``` ```cmake``` ```clang``` ```gcc``` ```tcl``` ```swig``` ```bison``` ```flex``` ```pip``` ```ninja``` 
2. Install required Python packages: ```build``` ```matplotlib``` ```pandas``` ```numpy```
3. Install ```Yosys```
  * Option 1: from source 
    * [yosys on Github](https://github.com/YosysHQ/yosys)
  * Option 2: via ```apt-get```
    ```sh
    sudo apt-get install yosys
    ```
  * Option 3: via ```pacman```
    ```sh
    sudo pacman -S yosys
    ```
4. Install ```OpenSta```
  * Option 1: from source 
    * [OpenSTA on Github](https://github.com/The-OpenROAD-Project/OpenSTA)
5. Install ```Verilator```
  * Option 1: from system's package manager
    * Please check the Verilator package's version available in the repositories of the system package manager.
    * Versions equal or higher than ```v5.002``` are recommended.
  * Option 2: from source 
    * [Verilator on Github](https://github.com/verilator/verilator)
    * [Verilator installation instructions](https://verilator.org/guide/latest/install.html)
 6. Install ```pybind11```
  * Option 1: via ```apt-get```
    ```sh
    sudo apt-get install pybind11
    ```
  * Option 2: via ```pacman```
    ```sh
    sudo pacman -S pybind11
    ```
7. Install ```MAxPy```
  * Option 1: via ```pip```
    * ```> TO BE DONE```
    ```sh
    pip install MAxPy
    ```
  * Option 2: via ```wheel```
    * Download the ```wheel``` file from MaxPy's [latest release on Github](https://github.com/MAxPy-Project/MAxPy/releases/latest).
    * The file is in the ```MAxPy-x.x.x-py3-none-any.whl``` format, where the ```x.x.x``` sequence represents the current version.
    * Install the ```wheel``` file via ```pip```
      ```sh
      pip install [path_to_the_wheel_file]/MAxPy-x.x.x-py3-none-any.whl
      ```
    * At this point, ```MAxPy``` should be installed in the system as a Python module, being able to be imported from any Python script.
## Running
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
## Developing
1. Clone MAxPy's package repository
  ```sh
  git clone https://github.com/MAxPy-Project/MAxPy
  ```
2. Edit code as needed
3. Build the package
```sh
cd [path_to_maxpy_repo]/MAxPy
python -m build
```
4. Install package from ```wheel``` file
```sh
pip install --force-reinstall dist/maxpy-x.x.x-py3-none-any.whl
```
5. Run test script
``` sh
cd tests
python tests/run.py
```
6. Check the guidelines before making a ```pull request```
  * ```> TO BE DONE```
## Building documentation
1. Install system package ```python-sphinx```
2. In the MAxPy directory run the following command:
  ```sh
  sphinx-build -b html docs/source/ docs/build/html
  ```
3. The build HTML will be available at ```docs/build/html/```
