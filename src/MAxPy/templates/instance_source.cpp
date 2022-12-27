#include "verilator_pybind_wrapper.h"

Instance* MAxPy_[[CLASS_NAME]]::maxpy_[[INSTANCE_NAME]]() {

    Instance *top, *pi;
	Net *pn;

[[INSTANCE_CODE]]
    return(top);
}
