import importlib

def testbench_run(mod, test):

    adder = mod.adder4()

    print(f">>> testbench init - circuit: {adder.name()}, area: {adder.area}, parameters: {adder.parameters}")

    for x in range(8):
        adder.A = x
        adder.B = x
        adder.eval()
        print("x = {x}, sum = {sum}".format(x=x, sum=adder.SUM))

    print(">>> testbench end")
    print("")

    return False, []




if __name__ == "__main__":

    mod = importlib.import_module(name="build_adder4_k1.adder4")
    testbench_run(mod)
    
    mod = importlib.import_module(name="build_adder4_k2.adder4")
    testbench_run(mod)

    
