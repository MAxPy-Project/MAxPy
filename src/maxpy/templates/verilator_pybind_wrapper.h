// MAxPy [[MAXPY_VERSION]]

#ifndef __MAXPY_WRAPPER__
#define __MAXPY_WRAPPER__

#include <pybind11/pybind11.h>
[[VCD_OPT_IN]]#include "[[VERILATOR_PATH]]verilated_vcd_c.h"[[VCD_OPT_OUT]]

[[HEADER_INCLUDE]]

namespace py = pybind11;

//---------------------------------------------------------------------------------------------------------------------
// "Net" class


[[SAIF_OPT_IN]]class Net {
	public:
		Net(const char* name_in, void *p_val, unsigned int bit_mask_in);
		void eval();
		void reset();
		unsigned int get_val();

		const char* name;
		int t0;
		int t1;
		int tc;
		int tx;
		int ig;
		float perc_high;
		float perc_low;
		unsigned int *val;
		unsigned int last_val;
		unsigned int bit_mask;
		bool first;
		Net *next;
};[[SAIF_OPT_OUT]]
//---------------------------------------------------------------------------------------------------------------------
// "Instance" class

[[SAIF_OPT_IN]]class Instance {
	public:
		Instance(const char* name_in);
		const char* name;
		Instance *head_instance;
		Instance *next;
		Net *head_net;
};[[SAIF_OPT_OUT]]
//---------------------------------------------------------------------------------------------------------------------
// "MAxPy_V[[CLASS_NAME]]" class

class MAxPy_[[CLASS_NAME]] : public [[CLASS_NAME]] {
	public:
		MAxPy_[[CLASS_NAME]](const char* name);
		~MAxPy_[[CLASS_NAME]]();
		void eval();

		// saif public methods
		[[SAIF_OPT_IN]]void eval_nets(Instance *pi);
		void reset_nets(Instance *pi);
        void saif_on_the_fly(int reset);
		void saif_print_instance(FILE *file_handler, Instance *pi, int level);
		void clear_memory();[[SAIF_OPT_OUT]]
		
		// vcd public methods
		[[VCD_OPT_IN]]void trace(const char* vcd_path);[[VCD_OPT_OUT]]

		//void show_nets(Instance *pi);

[[INSTANCE_METHODS]]
	private:
		// saif private properties
		[[SAIF_OPT_IN]]vluint64_t main_time;
		vluint64_t last_main_time;
		Instance *top_instance;[[SAIF_OPT_OUT]]
		
		// vcd private properties
		[[VCD_OPT_IN]]VerilatedVcdC* tfp;[[VCD_OPT_OUT]]
	public:
		float area;
		float power;
		float timing;
		std::string parameters;

		// saif public properties
		[[SAIF_OPT_IN]]std::string saif_path;
		py::list node_info;[[SAIF_OPT_OUT]]
};

//---------------------------------------------------------------------------------------------------------------------
#endif
//---------------------------------------------------------------------------------------------------------------------
//  EOF
//---------------------------------------------------------------------------------------------------------------------
