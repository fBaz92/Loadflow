
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # add pack root to path

from powerflow.io.json import load_json_network
from powerflow.solver.newton_raphson import LoadFlow

if __name__ == "__main__":
    net = load_json_network(str(pathlib.Path(__file__).resolve().parents[1] / "networks" / "IEEE14.json"))
    res = LoadFlow(verbose=True, tol=1e-9).solve(net)
    Vm, Va = res["Vm"], res["Va"]
    print("\n=== RESULTS IEEE14 ===")
    for i,(v,a) in enumerate(zip(Vm, Va)):
        print(f"Bus {i:2d}: |V|={v:.5f} pu, angle={a*180/3.141592653589793:.3f} deg")
