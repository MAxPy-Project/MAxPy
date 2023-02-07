import os
from numpy import linspace
from MAxPy import utility

def probprun(axckt, ckt_list=None, maxlvl=10, step=1):
    if ckt_list is None:
        print("> probprun error: circuit list not provided, exiting!")
        return
    if type(ckt_list) is not list:
        print("> probprun error: \"ckt_list\" must be of type \"list\", exiting!")
        return
    for current_circuit in ckt_list:
        # first compile the rtl level using the synth synth_tool
        if axckt.group_dir == "":
            base = f"{axckt.top_name}_{current_circuit}/rtl"
        else:
            base = f"{axckt.group_dir}/{axckt.top_name}_{current_circuit}/rtl"
        target = f"{current_circuit}_{axckt.synth_tool}"
        if axckt.rtl2py(base=base, target=target) != utility.ErrorCodes.OK:
            print("> probprun error: compiling \"{base}\" in netlist level was not successful. check log files. skipping to next circuit")
            continue
        axckt.run_testbench()
        for prun_level in list(linspace(step, maxlvl, num=int(maxlvl/step))):
            netlist_to_prun_path = axckt.netlist_target_path
            prun_level_str = f"{prun_level:002.1f}"
            if axckt.group_dir == "":
                pruned_netlist_path = f"{axckt.top_name}_{current_circuit}_probprun_{prun_level_str}/pruned_netlist"
            else:
                pruned_netlist_path = f"{axckt.group_dir}/{axckt.top_name}_{current_circuit}_probprun_{prun_level_str}/pruned_netlist"
            os.makedirs(pruned_netlist_path, exist_ok = True)
            print(f"  > Creating directory with pruned netlist: {pruned_netlist_path}")
            with open(netlist_to_prun_path, "r") as nl2prun_handle:
                netlist_text = nl2prun_handle.readlines()
            netlist_node_count = len(axckt.node_info)
            print(f"  > Evaluating {netlist_node_count} nodes")
            exit(1)


            #last_target =



    #
    #
    #
    #
    # print(f"> Probabilistic pruning (level {prun_level}%)")
    # print(f"  > Original netlist: {self.netlist_target_path}")
    #
    # original_node_info = self.node_info.copy()
    # original_netlist_target_path = self.netlist_target_path
    # original_current_parameter = self.current_parameter
    #
    # prun_level_str = "%02d" % (prun_level)
    #
    # if self.group_dir == "":
    #     probprun_netlist_path = f"{self.top_name}_{base}_probprun_{prun_level_str}/pruned_netlist"
    # else:
    #     probprun_netlist_path = f"{self.group_dir}/{self.top_name}_{base}_probprun_{prun_level_str}/pruned_netlist"
    #
    # os.makedirs(probprun_netlist_path, exist_ok = True)
    #
    # print(f"  > Creating directory with pruned netlist: {probprun_netlist_path}")
    #
    # fhandle = open(self.netlist_target_path, "r")
    # netlist_text = fhandle.readlines()
    # fhandle.close()
    # netlist_node_count = len(self.node_info)
    # print(f"  > Evaluating {netlist_node_count} nodes")
    #
    # for node in self.node_info:
    #     if node["p0"] >= node["p1"]:
    #         high_prob_value = node["p0"]
    #         high_prob_logic_level = "p0"
    #     else:
    #         high_prob_value = node["p1"]
    #         high_prob_logic_level = "p1"
    #     node["high_prob_value"] = high_prob_value
    #     node["high_prob_logic_level"] = high_prob_logic_level
    #
    # sorted_node_list = sorted(self.node_info, key=lambda d: d["high_prob_value"], reverse=True)
    # nodes_to_prun = int(float(netlist_node_count)*float(prun_level)/100.0)
    # if nodes_to_prun == 0:
    #     nodes_to_prun = 1
    # print("  > Pruning %d%% of the netlist nodes (%d/%d)" % (prun_level, nodes_to_prun, netlist_node_count))
    # node_count = 0
    # for node in sorted_node_list:
    #     output_gate_count = 0
    #     input_gate_count = 0
    #     for i in range(len(netlist_text)):
    #         if node['node'] in netlist_text[i]:
    #             if "Z" in netlist_text[i]:
    #                 output_gate_count += 1
    #                 netlist_text[i] = netlist_text[i].replace(node['node'], "")
    #             elif "wire" in netlist_text[i]:
    #                 netlist_text[i] = ""
    #             elif node['high_prob_logic_level'] == "p0":
    #                 input_gate_count += 1
    #                 netlist_text[i] = netlist_text[i].replace(node['node'], "1'b0")
    #             elif node['high_prob_logic_level'] == "p1":
    #                 input_gate_count += 1
    #                 netlist_text[i] = netlist_text[i].replace(node['node'], "1'b1")
    #     print(f"    > Node: {node['node']}, {node['high_prob_logic_level']}: {node['high_prob_value']}, gate outputs: {output_gate_count}, gate inputs: {input_gate_count}")
    #     node_count += 1
    #     if node_count >= nodes_to_prun:
    #         break
    #
    # pruned_netlist_path = f"{probprun_netlist_path}/{self.top_name}.v"
    # fhandle = open(pruned_netlist_path, "w")
    # fhandle.write("".join(netlist_text))
    # fhandle.close()
    #
    # self.prun_netlist = True
    # self.rtl2py(
    #     base=probprun_netlist_path,
    #     target=f"{self.current_parameter}_probprun_{prun_level_str}",
    # )
    # self.prun_netlist = False
    #
    # self.node_info = original_node_info.copy()
    # self.netlist_target_path = original_netlist_target_path
    # self.current_parameter = original_current_parameter
