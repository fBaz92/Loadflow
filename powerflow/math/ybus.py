
import numpy as np
from powerflow.network.network import Network

def build_ybus(network: Network) -> np.ndarray:
    """Build the bus admittance matrix (Ybus) for the given network.

    Parameters
    ----------
    network : Network
        The power system network containing buses, branches, and shunt elements.

    Returns
    -------
    numpy.ndarray
        The complex bus admittance matrix (Ybus) of shape (nbus, nbus), where
        ``nbus`` is the number of buses in the network.

    Notes
    -----
    The Ybus matrix is constructed by summing contributions from all branches
    and shunts:

    * Each branch is modeled using its series impedance ``z = r + jx``, line
      charging susceptance ``b`` (split equally at both ends), and transformer
      tap ratio/phase shift ``tap`` and ``shift_deg``.
    * Off-diagonal elements ``Y[i, j]`` and ``Y[j, i]`` are populated with the
      negative of the branch admittance scaled by the transformer ratio.
    * Diagonal elements accumulate the self-admittance including shunt charging
      and shunt elements connected to each bus.
    """
    n = network.nbus
    Y = np.zeros((n, n), dtype=complex)

    for br in network.branches:
        z = complex(br.r, br.x)
        y = 1 / z
        ysh = 1j * br.b / 2.0
        t = br.tap * np.exp(1j * np.deg2rad(br.shift_deg))
        i, j = br.i, br.j

        Y[i, i] += (y + ysh) / (abs(t) ** 2)
        Y[j, j] += (y + ysh)
        Y[i, j] += -y / np.conj(t)
        Y[j, i] += -y / t

    for sh in network.shunts:
        Y[sh.k, sh.k] += complex(sh.g, sh.b)

    return Y
