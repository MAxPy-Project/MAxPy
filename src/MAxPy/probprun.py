import os
from numpy import linspace
from MAxPy import utility

def probprun_loop(axckt, ckt_list=None, maxlvl=10, step=1):
    if ckt_list is None:
        print("> probprun error: circuit list not provided, exiting!")
        return
    if type(ckt_list) is not list:
        print("> probprun error: \"ckt_list\" must be of type \"list\", exiting!")
        return
    print(">>> probprun loop init")
    print(f"  > step val: {step:.1f}%")
    print(f"  > max level: {maxlvl:.1f}%")
    ckt_str = ", ".join(x for x in ckt_list)
    print(f"  > circuits to prun: {ckt_str}")
    for current_circuit in ckt_list:
        # first compile the rtl level using the synth synth_tool
        if axckt.group_dir == "":
            base = f"{axckt.top_name}_{current_circuit}/rtl"
        else:
            base = f"{axckt.group_dir}/{axckt.top_name}_{current_circuit}/rtl"
        target = f"{current_circuit}_{axckt.synth_tool}"
        axckt.prun_netlist = False
        if axckt.rtl2py(base=base, target=target) != utility.ErrorCodes.OK:
            print("> probprun error: compiling \"{base}\" in netlist level was not successful. check log files. skipping to next circuit")
            continue
        # with the compiled module, run testbench to get node info from simulation
        axckt.run_testbench()
        # this flag must be turned on in the pruning loop so the synth do not run again
        axckt.prun_netlist = False
        # now run the each of the pruning levels
        for prun_level in list(linspace(step, maxlvl, num=int(maxlvl/step))):
            # get netlist input path from previous compilation
            # (the first one is outside the loop, then the following are the last from the loop)
            netlist_to_prun_path = axckt.netlist_target_path
            prun_level_str = f"{prun_level:.1f}".replace(".", "_")
            if axckt.group_dir == "":
                pruned_netlist_dir = f"{axckt.top_name}_{current_circuit}_probprun_{prun_level_str}/pruned_netlist"
            else:
                pruned_netlist_dir = f"{axckt.group_dir}/{axckt.top_name}_{current_circuit}_probprun_{prun_level_str}/pruned_netlist"
            os.makedirs(pruned_netlist_dir, exist_ok = True)
            print(f"> probprun: creating directory with pruned netlist: {pruned_netlist_dir}")
            pruned_netlist_path = f"{pruned_netlist_dir}/{axckt.top_name}.v"
            with open(netlist_to_prun_path, "r") as nl2prun_handle:
                netlist_text = nl2prun_handle.readlines()
            netlist_node_count = len(axckt.node_info)
            print(f"> probprun: evaluating {netlist_node_count} nodes")
            for node in axckt.node_info:
                if node["p0"] >= node["p1"]:
                    high_prob_value = node["p0"]
                    high_prob_logic_level = "p0"
                else:
                    high_prob_value = node["p1"]
                    high_prob_logic_level = "p1"
                node["high_prob_value"] = high_prob_value
                node["high_prob_logic_level"] = high_prob_logic_level
            sorted_node_list = sorted(axckt.node_info, key=lambda d: d["high_prob_value"], reverse=True)
            nodes_to_prun = int(float(netlist_node_count)*float(prun_level)/100.0)
            if nodes_to_prun == 0:
                nodes_to_prun = 1
            print("> probprun: pruning %d%% of the netlist nodes (%d/%d)" % (prun_level, nodes_to_prun, netlist_node_count))
            node_count = 0
            for node in sorted_node_list:
                output_gate_count = 0
                input_gate_count = 0
                for i in range(len(netlist_text)):
                    if node['node'] in netlist_text[i]:
                        if "Z" in netlist_text[i]:
                            output_gate_count += 1
                            netlist_text[i] = netlist_text[i].replace(node['node'], "")
                        elif "wire" in netlist_text[i]:
                            netlist_text[i] = ""
                        elif node['high_prob_logic_level'] == "p0":
                            input_gate_count += 1
                            netlist_text[i] = netlist_text[i].replace(node['node'], "1'b0")
                        elif node['high_prob_logic_level'] == "p1":
                            input_gate_count += 1
                            netlist_text[i] = netlist_text[i].replace(node['node'], "1'b1")
                print(f"  > node: {node['node']}, {node['high_prob_logic_level']}: {node['high_prob_value']}, gate outputs: {output_gate_count}, gate inputs: {input_gate_count}")
                node_count += 1
                if node_count >= nodes_to_prun:
                    break
            with open(pruned_netlist_path, "w") as prunnl_handle:
                prunnl_handle.write("".join(netlist_text))
            if axckt.rtl2py(base=pruned_netlist_dir, target=f"{current_circuit}_probprun_{prun_level_str}") != utility.ErrorCodes.OK:
                print("> probprun error: compiling \"{base}\" in netlist level was not successful. check log files. skipping to next circuit")
                break
            axckt.run_testbench()
            if axckt.prun_flag is False:
                print(f"> probprun: exiting loop at {prun_level:.1f}, further pruning not allowed by testbench expected quality")
                break
    print(">>> probprun loop end\n")
