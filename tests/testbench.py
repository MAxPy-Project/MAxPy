import importlib
from MAxPy import results

def testbench_run(mod):

    adder = mod.adder4()

    rst = results.ResultsTable("output.csv", ["mre", "mse"])

    rst.add(adder, {"mre": 123, "mse": 456})

    print(f">>> testbench init - circuit: {adder.name()}, area: {adder.area}, parameters: {adder.parameters}")

    for x in range(8):
        for y in range(8):
            adder.set_A(x)
            adder.set_B(y)
            adder.eval()
            print(f"x {x}, y {y}, sum {adder.get_SUM():02d}")

    print(">>> testbench end")

    return False, []


if __name__ == "__main__":
    mod = importlib.import_module(name="adder4_exact.adder4")
    testbench_run(mod)
