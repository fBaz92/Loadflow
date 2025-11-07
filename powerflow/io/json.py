import json
from powerflow.elements.bus import Bus, BusType
from powerflow.elements.branch import Branch
from powerflow.elements.shunt import Shunt
from powerflow.network.network import Network
import numpy as np


def load_json_network(path, random_noise=False):
    """
    Carica una rete dal formato JSON standardizzato
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    base_mva = data.get("base_mva", 100.0)

    # --- Buses
    buses = []
    for b in data["buses"]:
        if b["type"].lower() == "slack":
            t = BusType.SLACK
        elif b["type"].lower() == "pv":
            t = BusType.PV
        else:
            t = BusType.PQ

        if random_noise:
            V = b["V"] + np.random.uniform(-0.1, 0.1) if t != BusType.SLACK else b["V"]
            theta_deg = b["theta_deg"] + np.random.uniform(-5, 5) if t != BusType.SLACK else b["theta_deg"]
        else:
            V = b["V"]
            theta_deg = b["theta_deg"]

        buses.append(
            Bus(
                b["id"],
                t,
                V,
                theta_deg,
                P=b["P"],
                Q=b["Q"],
                Qmin=b.get("Qmin", None),
                Qmax=b.get("Qmax", None),
            )
        )

    # --- Branches
    branches = []
    for br in data["branches"]:
        branches.append(
            Branch(
                br["i"], br["j"],
                br["r"], br["x"], br["b"],
                br.get("tap", 1.0),
                br.get("shift_deg", 0.0),
            )
        )

    # --- Shunts
    shunts = []
    for sh in data.get("shunts", []):
        shunts.append(
            Shunt(
                sh["bus"],
                sh["g"],
                sh["b"],
            )
        )

    return Network(buses, branches, shunts, base_mva)
