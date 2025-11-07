import re
import numpy as np
from powerflow.elements.bus import Bus, BusType
from powerflow.elements.branch import Branch
from powerflow.elements.shunt import Shunt
from powerflow.network.network import Network


def load_matpower(path):
    """
    Carica un file MATPOWER .m sia in formato:
      - mpc = {...} "script mode"
      - function mpc = caseXX ... end   "function mode"
    Convertendo automaticamente la funzione in script.
    """
    text = open(path, "r", encoding="utf-8").read()

    # --- Caso: file inizia con "function mpc = ..."
    if re.match(r"^\s*function\s+mpc\s*=", text, re.IGNORECASE):
        lines = text.splitlines()
        new = ["mpc = struct();"]
        started = False

        for line in lines:
            # salta la riga "function mpc = XXX"
            if re.match(r"^\s*function\s+mpc\s*=", line, re.IGNORECASE):
                started = True
                continue
            # interrompi a "end"
            if started and re.match(r"^\s*end\s*$", line, re.IGNORECASE):
                break
            if started:
                new.append(line)

        text = "\n".join(new)

    namespace = {"struct": dict}
    exec(text, namespace)

    if "mpc" not in namespace:
        raise ValueError("Il file MATPOWER non definisce mpc")

    mpc = namespace["mpc"]

    base_mva = float(mpc.get("baseMVA", 100.0))
    bus = np.array(mpc["bus"], float)
    branch = np.array(mpc["branch"], float)
    gen = np.array(mpc.get("gen", []), float)

    buses = []
    for row in bus:
        idx = int(row[0]) - 1
        type_code = int(row[1])
        Pd, Qd = row[2], row[3]
        Vm, Va = row[7], row[8]

        if type_code == 3: btype = BusType.SLACK
        elif type_code == 2: btype = BusType.PV
        else: btype = BusType.PQ

        buses.append(Bus(idx, btype, Vm, Va, P=-Pd/base_mva, Q=-Qd/base_mva))

    for row in gen:
        idx = int(row[0]) - 1
        Pg, Qg, Qmax, Qmin, Vset = row[1:6]
        buses[idx].P += Pg / base_mva
        buses[idx].Q += Qg / base_mva
        buses[idx].Qmax = Qmax / base_mva
        buses[idx].Qmin = Qmin / base_mva
        if buses[idx].type in (BusType.SLACK, BusType.PV):
            buses[idx].V = Vset

    branches = []
    for row in branch:
        i, j = int(row[0]) - 1, int(row[1]) - 1
        r, x, b = row[2], row[3], row[4]
        tap = row[8] if len(row) > 8 and row[8] != 0 else 1.0
        shift = row[9] if len(row) > 9 else 0.0
        branches.append(Branch(i, j, r, x, b, tap, shift))

    shunts = []
    for row in bus:
        k = int(row[0]) - 1
        Gs, Bs = row[4], row[5]
        if Gs != 0 or Bs != 0:
            shunts.append(Shunt(k, Gs/base_mva, Bs/base_mva))

    return Network(buses, branches, shunts, base_mva)
