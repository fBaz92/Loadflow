
from __future__ import annotations

import numpy as np
from typing import TypedDict
from powerflow.elements.bus import BusType
from powerflow.math.ybus import build_ybus
from powerflow.network.network import Network


class LoadFlowResult(TypedDict):
    """Typed container for the Newton-Raphson load-flow solution results."""

    Vm: np.ndarray
    Va: np.ndarray
    P: np.ndarray
    Q: np.ndarray
    iterations: int
    converged: bool


class LoadFlow:
    """
    Newton-Raphson load-flow solver.

    Parameters
    ----------
    tol : float, optional
        Convergence tolerance on the maximum power mismatch (p.u.). Defaults to ``1e-8``.
    max_iter : int, optional
        Maximum number of Newton iterations. Defaults to ``100``.
    verbose : bool, optional
        If ``True``, prints per-iteration convergence information. Defaults to ``False``.
    """

    def __init__(self, tol: float = 1e-8, max_iter: int = 100, verbose: bool = False) -> None:
        """Initialize the load-flow solver with algorithm settings."""
        self.tol = tol
        self.max_iter = max_iter
        self.verbose = verbose

    def solve(self, network: Network) -> LoadFlowResult:
        """
        Solve the load-flow problem for the provided network.

        Parameters
        ----------
        network : Network
            Power system network containing buses, branches, and shunts. Bus states
            (voltage magnitude, angle, injections, and limits) are taken from the
            ``network.buses`` collection.

        Returns
        -------
        LoadFlowResult
            Dictionary containing the solved voltages, injected powers, number of
            iterations, and a convergence flag. Voltage angles are returned in radians.

        Notes
        -----
        Implements the classical Newton-Raphson algorithm with PV reactive power
        limit enforcement. When a PV bus violates its ``Qmin``/``Qmax`` limits it is
        converted to PQ for the remainder of the solve. Convergence is declared when
        the maximum absolute power mismatch falls below ``tol``.
        """
        Y = build_ybus(network)
        G, B = Y.real, Y.imag

        n = network.nbus
        slack = network.slack_index()
        pv = network.pv_indices()
        pq = network.pq_indices()

        Vm = np.array([b.V for b in network.buses], float)
        Va = np.deg2rad([b.theta_deg for b in network.buses])

        P_spec = np.array([b.P for b in network.buses], float)
        # Q specified only for PQ; PV has variable Q, Slack is free
        Q_spec = np.array([b.Q if b.type == BusType.PQ else 0.0 for b in network.buses], float)

        PV_active = set(pv)  # PV with |V| fixed
        PV_conv = set()      # PV converted to PQ due to Q-limits

        for it in range(self.max_iter):
            V = Vm * np.exp(1j * Va)
            I = Y @ V
            S = V * np.conj(I)
            P = S.real
            Q = S.imag

            # Enforce PV Q-limits -> convert to PQ if necessary
            for k in list(PV_active):
                b = network.buses[k]

                if b.Qmin is not None and Q[k] < b.Qmin:
                    PV_active.remove(k) 
                    PV_conv.add(k) 
                    Q_spec[k] = b.Qmin
                    assert b.type == BusType.PV, "PV bus converted to PQ"
                    if self.verbose:
                        print(f"PV bus {k} converted to PQ due to Qmin limit")

                elif b.Qmax is not None and Q[k] > b.Qmax:
                    PV_active.remove(k)
                    PV_conv.add(k)
                    Q_spec[k] = b.Qmax
                    assert b.type == BusType.PV, "PV bus converted to PQ"
                    if self.verbose:
                        print(f"PV bus {k} converted to PQ due to Qmax limit")  

            p_rows = [k for k in range(n) if k != slack]
            q_rows = sorted(set(pq).union(PV_conv))

            dP = P_spec[p_rows] - P[p_rows]
            dQ = Q_spec[q_rows] - Q[q_rows]
            mismatch = np.r_[dP, dQ]

            if self.verbose:
                print(f"iter {it:02d} | max mismatch = {np.max(np.abs(mismatch)):.3e}")

            if np.max(abs(mismatch)) < self.tol:
                if self.verbose:
                    print(f"Converged in {it} iterations")
                return LoadFlowResult(
                    Vm=Vm.copy(),
                    Va=Va.copy(),
                    P=P.copy(),
                    Q=Q.copy(),
                    iterations=it,
                    converged=True,
                )

            theta_cols = p_rows
            V_cols = q_rows
            mP, mQ = len(p_rows), len(q_rows)

            H = np.zeros((mP, len(theta_cols)))
            N = np.zeros((mP, len(V_cols)))
            M = np.zeros((mQ, len(theta_cols)))
            L = np.zeros((mQ, len(V_cols)))

            Va_col = Va[:, None]
            dth = Va_col - Va_col.T
            c, s = np.cos(dth), np.sin(dth)

            # Build H and N (rows = P mismatch)
            for ri, k in enumerate(p_rows):
                Vk = Vm[k]
                # H diag and off-diag
                H[ri, theta_cols.index(k)] = -Q[k] - (Vk ** 2) * B[k, k]
                for m in theta_cols:
                    if m == k:
                        continue
                    H[ri, theta_cols.index(m)] = Vk * Vm[m] * (G[k, m] * s[k, m] - B[k, m] * c[k, m])
                # N diag and off-diag
                if k in V_cols:
                    N[ri, V_cols.index(k)] = (P[k] / max(Vk, 1e-12)) + Vk * G[k, k]
                for m in V_cols:
                    if m == k:
                        continue
                    N[ri, V_cols.index(m)] = Vk * (G[k, m] * c[k, m] + B[k, m] * s[k, m])

            # Build M and L (rows = Q mismatch)
            for ri, k in enumerate(q_rows):
                Vk = Vm[k]
                # M diag and off-diag
                M[ri, theta_cols.index(k)] = P[k] - (Vk ** 2) * G[k, k]
                for m in theta_cols:
                    if m == k:
                        continue
                    M[ri, theta_cols.index(m)] = -Vk * Vm[m] * (G[k, m] * c[k, m] + B[k, m] * s[k, m])
                # L diag and off-diag
                L[ri, V_cols.index(k)] = (Q[k] / max(Vk, 1e-12)) - Vk * B[k, k]
                for m in V_cols:
                    if m == k:
                        continue
                    L[ri, V_cols.index(m)] = Vk * (G[k, m] * s[k, m] - B[k, m] * c[k, m])

            J = np.block([[H, N], [M, L]])
            dx = np.linalg.solve(J, mismatch)

            Va[theta_cols] += dx[:mP]
            Vm[V_cols] += dx[mP:]

            # Re-impose |V| on PV still active
            for k in PV_active:
                Vm[k] = network.buses[k].V

        return LoadFlowResult(Vm=Vm, Va=Va, P=P, Q=Q, iterations=self.max_iter, converged=False)
