
import numpy as np
from powerflow.elements.bus import BusType, Bus
from powerflow.elements.branch import Branch
from powerflow.elements.shunt import Shunt

class Network:
    """
    Represents a power system network for load flow analysis.
    
    A Network object contains all the components of a power system including
    buses, transmission lines/branches, and shunt elements. It provides methods
    to access different bus types and network properties.
    
    Attributes
    ----------
    buses : list of Bus
        List of bus objects in the network.
    branches : list of Branch
        List of branch (transmission line/transformer) objects.
    shunts : list of Shunt, optional
        List of shunt admittance elements. Defaults to empty list.
    base_mva : float, optional
        System base MVA for per-unit calculations. Defaults to 100.0 MVA.
    """
    
    def __init__(self, buses: list[Bus], branches: list[Branch], shunts: list[Shunt]=None, base_mva: float=100.0):
        """
        Initialize a Network object.
        
        Parameters
        ----------
        buses : list of Bus
            List of Bus objects representing the network buses.
            Each bus must have a unique index (idx) and a type (Slack, PV, or PQ).
        branches : list of Branch
            List of Branch objects representing transmission lines and transformers.
            Each branch connects two buses specified by indices i and j.
        shunts : list of Shunt, optional
            List of Shunt objects representing shunt admittances at buses.
            If None, defaults to an empty list.
        base_mva : float, optional
            System base MVA used for per-unit calculations. Defaults to 100.0 MVA.
        
        Examples
        --------
        >>> from powerflow.elements.bus import Bus, BusType
        >>> from powerflow.elements.branch import Branch
        >>> buses = [Bus(0, BusType.SLACK), Bus(1, BusType.PQ)]
        >>> branches = [Branch(0, 1, r=0.01, x=0.05)]
        >>> net = Network(buses, branches, base_mva=100.0)
        """
        self.buses = buses
        self.branches = branches
        self.shunts = shunts if shunts is not None else []
        self.base_mva = base_mva

    @property
    def nbus(self):
        """
        Get the number of buses in the network.
        
        Returns
        -------
        int
            Total number of buses in the network.
        """
        return len(self.buses)

    def slack_index(self):
        """
        Get the index of the slack (reference) bus.
        
        Returns
        -------
        int
            The 0-based index of the slack bus.
        
        Raises
        ------
        StopIteration
            If no slack bus is found in the network.
        
        Notes
        -----
        The network must have exactly one slack bus for load flow analysis.
        """
        return next(b.idx for b in self.buses if b.type == BusType.SLACK)

    def pv_indices(self):
        """
        Get the indices of all PV (voltage-controlled) buses.
        
        Returns
        -------
        list of int
            List of 0-based indices for all PV buses in the network.
        
        Notes
        -----
        PV buses have fixed voltage magnitude and active power injection,
        with reactive power determined by the load flow solution.
        """
        return [b.idx for b in self.buses if b.type == BusType.PV]

    def pq_indices(self):
        """
        Get the indices of all PQ (load) buses.
        
        Returns
        -------
        list of int
            List of 0-based indices for all PQ buses in the network.
        
        Notes
        -----
        PQ buses have fixed active and reactive power injections,
        with voltage magnitude and angle determined by the load flow solution.
        """
        return [b.idx for b in self.buses if b.type == BusType.PQ]
