from typing import Optional


class BusType:
    """
    Bus type constants for power flow analysis.
    
    Defines the three standard bus types used in power flow calculations:
    - SLACK: Reference bus with fixed voltage magnitude and angle
    - PV: Voltage-controlled bus with fixed voltage magnitude and active power
    - PQ: Load bus with fixed active and reactive power injections
    
    Attributes
    ----------
    SLACK : str
        Constant for slack (reference) bus type.
    PV : str
        Constant for PV (voltage-controlled) bus type.
    PQ : str
        Constant for PQ (load) bus type.
    """
    SLACK = "Slack"
    PV = "PV"
    PQ = "PQ"


class Bus:
    """
    Represents a bus (node) in a power system network.
    
    A Bus object contains all the electrical parameters and constraints for a
    single bus in the power system. The bus type determines which quantities
    are fixed (specified) and which are calculated by the load flow solver.
    
    Attributes
    ----------
    idx : int
        Bus index (0-based) used to identify the bus in the network.
    type : str
        Bus type: BusType.SLACK, BusType.PV, or BusType.PQ.
    V : float
        Voltage magnitude in per unit (p.u.). Initial value, may be updated by solver.
    theta_deg : float
        Voltage phase angle in degrees. Initial value, may be updated by solver.
    P : float
        Net injected active power in per unit (p.u.) on system base.
        Positive for generation, negative for load.
    Q : float
        Net injected reactive power in per unit (p.u.).
        Positive for generation, negative for load.
    Qmin : float, optional
        Minimum reactive power limit for PV buses (p.u.). Defaults to None.
    Qmax : float, optional
        Maximum reactive power limit for PV buses (p.u.). Defaults to None.
    """
    
    def __init__(
        self,
        idx: int,
        type: str,
        V: float = 1.0,
        theta_deg: float = 0.0,
        P: float = 0.0,
        Q: float = 0.0,
        Qmin: Optional[float] = None,
        Qmax: Optional[float] = None
    ):
        """
        Initialize a Bus object.
        
        Parameters
        ----------
        idx : int
            Bus index (0-based). Must be unique within the network.
        type : str
            Bus type. Must be one of: BusType.SLACK, BusType.PV, or BusType.PQ.
            - SLACK: Fixed voltage magnitude and angle (reference bus)
            - PV: Fixed voltage magnitude and active power (generator bus)
            - PQ: Fixed active and reactive power (load bus)
        V : float, optional
            Initial voltage magnitude in per unit (p.u.). Defaults to 1.0.
            For SLACK and PV buses, this is the specified (fixed) value.
            For PQ buses, this is the initial guess for the solver.
        theta_deg : float, optional
            Initial voltage phase angle in degrees. Defaults to 0.0.
            For SLACK buses, this is the specified (fixed) value.
            For PV and PQ buses, this is the initial guess for the solver.
        P : float, optional
            Net injected active power in per unit (p.u.) on system base.
            Defaults to 0.0. Positive for generation, negative for load.
            For PV and PQ buses, this is the specified (fixed) value.
        Q : float, optional
            Net injected reactive power in per unit (p.u.). Defaults to 0.0.
            Positive for generation, negative for load.
            For PQ buses, this is the specified (fixed) value.
            For PV buses, this is calculated by the solver.
        Qmin : float, optional
            Minimum reactive power limit for PV buses (p.u.). Defaults to None.
            Used to enforce generator reactive power limits during load flow.
        Qmax : float, optional
            Maximum reactive power limit for PV buses (p.u.). Defaults to None.
            Used to enforce generator reactive power limits during load flow.
        
        Notes
        -----
        Bus type determines which quantities are fixed vs. calculated:
        - SLACK: V and theta_deg are fixed; P and Q are calculated
        - PV: V and P are fixed; theta_deg and Q are calculated (subject to Qmin/Qmax)
        - PQ: P and Q are fixed; V and theta_deg are calculated
        
        Examples
        --------
        >>> from powerflow.elements.bus import Bus, BusType
        >>> 
        >>> # Slack bus (reference)
        >>> slack = Bus(idx=0, type=BusType.SLACK, V=1.0, theta_deg=0.0)
        >>> 
        >>> # PV bus (generator)
        >>> gen = Bus(idx=1, type=BusType.PV, V=1.05, P=0.5, Qmin=-0.2, Qmax=0.3)
        >>> 
        >>> # PQ bus (load)
        >>> load = Bus(idx=2, type=BusType.PQ, P=-0.3, Q=-0.1)
        """
        self.idx = idx        # 0-based index
        self.type = type      # Slack, PV, PQ
        assert self.type in [BusType.SLACK, BusType.PV, BusType.PQ], "Invalid bus type"
        self.V = V            # voltage magnitude (pu)
        self.theta_deg = theta_deg  # angle (deg)
        self.P = P            # net injected active power (pu on system base)
        self.Q = Q            # net injected reactive power (pu)
        self.Qmin = Qmin      # reactive limits for PV (pu)
        self.Qmax = Qmax
