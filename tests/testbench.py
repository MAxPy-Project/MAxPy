import importlib

def testbench_run(mod):

    adder = mod.adder4()

    print(f">>> testbench init - circuit: {adder.name()}, area: {adder.area}, parameters: {adder.parameters}")

    for x in range(8):
        adder.set_A(x)
        adder.set_B(x)
        adder.eval()
        print("x = {x}, sum = {sum}".format(x=x, sum=adder.get_SUM()))#SUM))

    print(">>> testbench end")

    return False, []


if __name__ == "__main__":

    mod = importlib.import_module(name="adder4_exact_build.adder4")
    testbench_run(mod)
