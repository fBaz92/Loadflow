
class Branch:
    """
    Represents a transmission line or transformer branch in a power system.
    
    A Branch connects two buses (i and j) and can model either a transmission
    line or a transformer. The branch model includes series impedance (r, x),
    shunt charging susceptance (b), and transformer parameters (tap ratio and
    phase shift).
    
    Attributes
    ----------
    i : int
        From bus index (0-based).
    j : int
        To bus index (0-based).
    r : float
        Series resistance in per unit.
    x : float
        Series reactance in per unit.
    b : float
        Total line charging susceptance in per unit (default: 0.0).
    tap : float
        Transformer tap ratio magnitude, placed on bus i side (default: 1.0).
        For transmission lines, tap = 1.0.
    shift_deg : float
        Transformer phase shift angle in degrees, placed on bus i side (default: 0.0).
        For transmission lines, shift_deg = 0.0.
    """
    
    def __init__(self, i: int, j: int, r: float, x: float, b: float = 0.0, tap: float = 1.0, shift_deg: float = 0.0):
        """
        Initialize a Branch object.
        
        Parameters
        ----------
        i : int
            From bus index (0-based). The bus where the branch originates.
        j : int
            To bus index (0-based). The bus where the branch terminates.
        r : float
            Series resistance in per unit (pu). Must be non-negative.
        x : float
            Series reactance in per unit (pu). Typically positive for inductive
            branches, negative for capacitive branches.
        b : float, optional
            Total line charging susceptance in per unit (pu). Defaults to 0.0.
            This represents the shunt capacitance of the line, typically split
            equally between the two ends in the pi-model.
        tap : float, optional
            Transformer tap ratio magnitude. Defaults to 1.0.
            For transmission lines, use tap = 1.0.
            For transformers, tap represents the voltage ratio (V_i / V_j).
        shift_deg : float, optional
            Transformer phase shift angle in degrees. Defaults to 0.0.
            For transmission lines, use shift_deg = 0.0.
            For phase-shifting transformers, this is the phase angle shift.
        
        Notes
        -----
        The branch model uses a pi-equivalent circuit with:
        - Series impedance: z = r + j*x
        - Shunt admittance: y_shunt = j*b/2 (split at each end)
        - Transformer: represented by tap ratio and phase shift on bus i side
        
        Examples
        --------
        >>> # Transmission line
        >>> line = Branch(i=0, j=1, r=0.01, x=0.05, b=0.02)
        >>> 
        >>> # Transformer
        >>> transformer = Branch(i=0, j=1, r=0.001, x=0.01, tap=1.1, shift_deg=0.0)
        >>> 
        >>> # Phase-shifting transformer
        >>> pst = Branch(i=0, j=1, r=0.001, x=0.01, tap=1.0, shift_deg=5.0)
        """
        self.i = i
        self.j = j

        assert i >= 0 and j >= 0 and i != j, "Invalid bus indices"
        assert r >= 0 and x >= 0, "Invalid series impedance"
        assert b >= 0, "Invalid shunt admittance"
        assert tap >= 0, "Invalid transformer tap ratio"
        assert shift_deg >= 0 and shift_deg <= 360, "Invalid phase shift angle"

        self.r = r
        self.x = x
        self.b = b            # total line charging susceptance (pu)
        self.tap = tap        # transformer ratio (magnitude), placed on 'i' side
        self.shift_deg = shift_deg  # phase shift (deg) on 'i' side
