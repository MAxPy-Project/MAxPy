import importlib
from MAxPy import results

def testbench_run(ckt=None, results_filename=None):

    adder = ckt.adder4()

    rst = results.ResultsTable(results_filename, ["mre", "mse"])

    print(f">>> testbench init - circuit: {adder.name()}, area: {adder.area}, parameters: {adder.parameters}")

    mre = 0
    mse = 0
    for x in range(8):
        for y in range(8):
            adder.set_A(x)
            adder.set_B(y)
            adder.eval()
            #print(f"x {x}, y {y}, sum {adder.get_SUM():02d}")
            exact = x + y
            if adder.get_SUM() != exact:
                mre += 1
                mse += 2

    rst.add(adder, {"mre": mre, "mse": mse})

    print(">>> testbench end")

    if mre < 30:
        prun_flag = True
    else:
        prun_flag = False

    return prun_flag, adder.node_info


if __name__ == "__main__":
    mod = importlib.import_module(name="study_no_1.adder4_copyA_0.adder4")
    testbench_run(ckt=mod, results_filename="test.csv")
