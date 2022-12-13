# MAxPy Multi-layer Approximate Computing Python Framework

## Repository

[Link](https://github.com/ysba/maxpy)

## Build and install package

### Pre-requisites

* pacman -S python-pip
* python -m pip install --upgrade pip
* python -m pip install --upgrade build


* Packages:
cmake
clang
gcc
tcl
swig
bison
flex

* Yosys
https://github.com/YosysHQ/yosys
sudo pacman -S yosys
sudo apt-get install yosys

* OpenSta
https://github.com/The-OpenROAD-Project/OpenSTA
(installed from source)

* Verilator
https://github.com/verilator/verilator
sudo pacman -S verilator

* Pybind11
https://github.com/pybind/pybind11
sudo pacman -S pybind11



### First time: cloning package repository

* git clone https://github.com/ysba/maxpy

### Installing

* cd maxpy
* python -m build
* pip install --force-reinstall dist/maxpy-x.x.x-py3-none-any.whl

### Running test script

* python tests/test.py
