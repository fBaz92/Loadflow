
class Shunt:
    """
    Represents a shunt admittance element connected to a bus.
    
    A Shunt element models a constant admittance (conductance and/or susceptance)
    connected between a bus and ground. Shunt elements are commonly used to
    represent:
    - Capacitor banks (positive susceptance b > 0)
    - Inductor/reactor banks (negative susceptance b < 0)
    - Resistive loads (conductance g > 0)
    - Combined R-L or R-C loads
    
    Attributes
    ----------
    k : int
        Bus index (0-based) where the shunt is connected.
    g : float
        Conductance in per unit (p.u.). Defaults to 0.0.
        Positive for resistive loads, typically 0.0 for pure reactive shunts.
    b : float
        Susceptance in per unit (p.u.). Defaults to 0.0.
        Positive for capacitive shunts, negative for inductive shunts.
    """
    
    def __init__(self, k: int, g: float = 0.0, b: float = 0.0):
        """
        Initialize a Shunt object.
        
        Parameters
        ----------
        k : int
            Bus index (0-based) where the shunt element is connected.
            Must be a valid bus index in the network.
        g : float, optional
            Conductance in per unit (p.u.). Defaults to 0.0.
            Represents the real part of the shunt admittance Y = g + j*b.
            Positive for resistive loads.
        b : float, optional
            Susceptance in per unit (p.u.). Defaults to 0.0.
            Represents the imaginary part of the shunt admittance Y = g + j*b.
            - Positive b: capacitive shunt (injects reactive power)
            - Negative b: inductive shunt (absorbs reactive power)
            - Zero b: pure resistive or no reactive component
        
        Notes
        -----
        The shunt admittance Y = g + j*b is added to the diagonal element
        Y[k,k] of the Ybus matrix. The shunt current is I_shunt = Y * V_k.
        
        Examples
        --------
        >>> from powerflow.elements.shunt import Shunt
        >>> 
        >>> # Capacitor bank (injects reactive power)
        >>> capacitor = Shunt(k=5, b=0.1)
        >>> 
        >>> # Inductor/reactor (absorbs reactive power)
        >>> reactor = Shunt(k=3, b=-0.05)
        >>> 
        >>> # Resistive load
        >>> resistor = Shunt(k=2, g=0.02)
        >>> 
        >>> # Combined R-C load
        >>> rc_load = Shunt(k=1, g=0.01, b=0.05)
        """
        assert isinstance(k, int) and k >= 0, "Bus index k must be a non-negative integer"
        assert isinstance(g, (int, float)) and not (isinstance(g, bool)), "Conductance g must be a number"
        assert isinstance(b, (int, float)) and not (isinstance(b, bool)), "Susceptance b must be a number"
        self.k = k  # bus index (0-based)
        self.g = g  # conductance (pu)
        self.b = b  # susceptance (pu)
