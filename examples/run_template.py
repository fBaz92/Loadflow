
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from powerflow.io.json import load_json_network
from powerflow.solver.newton_raphson import LoadFlow

def run(case_name):
    path = pathlib.Path(__file__).resolve().parents[1] / "networks" / f"{case_name}.json"
    net = load_json_network(str(path))
    res = LoadFlow(verbose=True).solve(net)
    Vm, Va = res["Vm"], res["Va"]
    print(f"\n=== RESULTS {case_name} ===")
    for i,(v,a) in enumerate(zip(Vm, Va)):
        print(f"Bus {i:3d}: |V|={v:.5f} pu, angle={a*180/3.141592653589793:.3f} deg")

if __name__ == "__main__":
    run("IEEE14.m")
