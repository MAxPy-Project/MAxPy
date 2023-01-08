# MAxPy Multi-layer Approximate Computing Python Framework

## Repository

[Link](https://github.com/ysba/maxpy)

## Build and install package

### Pre-requisites

* System packages:
  * cmake
  * clang
  * gcc
  * tcl
  * swig
  * bison
  * flex
  * pip
  * ninja

* Python packages:
  * build
  * matplotlib

```sh
python -m pip install --upgrade build
pip install matplotlib
```

* Yosys
https://github.com/YosysHQ/yosys

```sh
sudo pacman -S yosys
sudo apt-get install yosys
```

* OpenSta
https://github.com/The-OpenROAD-Project/OpenSTA
(installed from source)

* Verilator
https://github.com/verilator/verilator
```sh
sudo pacman -S verilator
```

* Pybind11
https://github.com/pybind/pybind11
```sh
sudo pacman -S pybind11
```



### First time: cloning package repository

```sh
git clone https://github.com/ysba/maxpy
```

### Installing

```sh
cd maxpy
python -m build
pip install --force-reinstall dist/maxpy-x.x.x-py3-none-any.whl
```

### Running test script
``` sh
python tests/test.py
```
