from typing import Any
import numpy as np
import matplotlib.pyplot as plt
from powerflow.math.ybus import build_ybus
from powerflow.network.network import Network

class PowerFlowReport:
    def __init__(self, network: Network, Vm: np.ndarray, Va: np.ndarray, P: np.ndarray, Q: np.ndarray):
        """
        Initialize a PowerFlowReport object with power flow solution results.
        
        Parameters
        ----------
        network : Network
            The power system network object containing buses, branches, and shunts.
        Vm : array_like
            Voltage magnitudes in per unit (p.u.) for each bus.
            Length must match the number of buses in the network.
        Va : array_like
            Voltage angles in degrees for each bus.
            Length must match the number of buses in the network.
        P : array_like
            Active power injections (MW) for each bus.
            Length must match the number of buses in the network.
        Q : array_like
            Reactive power injections (MVAr) for each bus.
            Length must match the number of buses in the network.
        
        Notes
        -----
        All input arrays are converted to numpy arrays internally for computation.
        The arrays should be ordered by bus index (0-based).
        """
        self.net = network
        self.Vm = np.array(Vm)
        self.Va = np.array(Va)
        self.P = np.array(P)
        self.Q = np.array(Q)

    def plot_voltage_profile(self):
        """
        Plot the voltage magnitude profile across all buses.
        
        Creates a stem plot showing the voltage magnitude (in per unit) for each
        bus in the network. The plot helps visualize voltage levels and identify
        buses with low or high voltages.
        
        Notes
        -----
        The plot is created but not displayed. Call `show_all()` or `plt.show()`
        to display the figure.
        """
        plt.figure()
        plt.stem(range(len(self.Vm)), self.Vm)
        plt.xlabel("Bus index")
        plt.ylabel("|V| (p.u.)")
        plt.title("Voltage Profile")
        plt.grid(True)

    def plot_angle_profile(self):
        """
        Plot the voltage angle profile across all buses.
        
        Creates a stem plot showing the voltage phase angle (in degrees) for each
        bus in the network. The plot helps visualize the phase relationships
        between buses and identify angle differences.
        
        Notes
        -----
        The plot is created but not displayed. Call `show_all()` or `plt.show()`
        to display the figure.
        """
        plt.figure()
        plt.stem(range(len(self.Va)), self.Va)
        plt.xlabel("Bus index")
        plt.ylabel("Angle (deg)")
        plt.title("Voltage Angles")
        plt.grid(True)

    def plot_generation_pie(self):
        """
        Plot a pie chart showing the distribution of generator real power.
        
        Creates a pie chart displaying the percentage share of active power
        generation from each generator bus. Only buses with positive active
        power injection (P > 0) are included in the chart.
        
        Notes
        -----
        The plot is created but not displayed. Call `show_all()` or `plt.show()`
        to display the figure.
        If no generators are found (all P <= 0), the chart will be empty.
        """
        gens = [b for b in self.net.buses if b.P > 0]
        labels = [f"Bus {b.idx+1}" for b in gens]
        values = [b.P for b in gens]

        plt.figure()
        plt.pie(values, labels=labels, autopct="%1.1f%%")
        plt.title("Generator Real Power Share")

    def plot_branch_flows(self):
        """
        Plot active power flows for all branches in the network.
        
        Creates a bar chart showing the active power flow (P_ij) from bus i to
        bus j for each branch. Power flows are calculated using the Ybus matrix
        and the solved voltage profile.
        
        Notes
        -----
        The plot is created but not displayed. Call `show_all()` or `plt.show()`
        to display the figure.
        Power flows are displayed in MW (converted from per-unit using base_mva).
        Positive values indicate power flowing from bus i to bus j.
        """
        # calcolo flussi P_ij usando V e Ybus
        Y = build_ybus(self.net)
        S = np.zeros((len(self.net.branches), 2))  # P_ij, P_ji

        # Build complex voltage phasor vector: V = |V| * exp(j*theta)
        # Converts from polar form (magnitude + angle) to complex form
        V = np.array([self.Vm[k] * np.exp(1j * np.deg2rad(self.Va[k])) for k in range(len(self.Vm))])
        
        for k, br in enumerate(self.net.branches):
            i, j = br.i, br.j
            Vi = V[i]
            Vj = V[j]
            
            # Calculate current from i to j using Ybus
            # Iij = Y[i,j] * Vj (current injected at i due to j)
            # But we want the actual branch current, so we use the off-diagonal element
            if Y[i, j] != 0:
                # Current flowing from i to j through the branch
                Iij = -Y[i, j] * Vj  # Negative because Y[i,j] is negative of branch admittance
                Sij = Vi * np.conj(Iij)
                S[k, 0] = Sij.real * self.net.base_mva  # Convert to MW
                
                # Reverse flow
                Iji = -Y[j, i] * Vi
                Sji = Vj * np.conj(Iji)
                S[k, 1] = Sji.real * self.net.base_mva
            else:
                # Fallback for disconnected branches
                S[k, 0] = 0.0
                S[k, 1] = 0.0

        plt.figure()
        plt.bar(range(len(S)), S[:,0])
        plt.xlabel("Branch index")
        plt.ylabel("MW")
        plt.title("Active Power Flows (P_ij)")
        plt.grid(True)

    def print_branch_flows_table(self):
        """
        Print a detailed table of branch power flows and losses.
        
        Calculates and displays a formatted table showing for each branch:
        - Branch number, from bus, and to bus
        - Active power flow from i to j (P_ij) in MW
        - Reactive power flow from i to j (Q_ij) in MVAr
        - Active power flow from j to i (P_ji) in MW
        - Reactive power flow from j to i (Q_ji) in MVAr
        - Branch losses in MW
        
        The calculations use the correct branch model accounting for:
        - Series impedance (r, x)
        - Shunt admittance (b)
        - Transformer tap ratio and phase shift
        
        Notes
        -----
        Power flows are calculated using the branch pi-model with transformer
        representation. Losses are computed as P_ij + P_ji (always positive).
        The table also displays total system losses at the bottom.
        
        Examples
        --------
        >>> report.print_branch_flows_table()
        ========================================================================
        BRANCH POWER FLOWS
        ========================================================================
        Branch   From   From type   To     To type   Vi (p.u.)   Vj (p.u.)   P_ij (MW)   Q_ij (MVAr)  P_ji (MW)   Q_ji (MVAr)  Losses (MW)
        ...
        """

        
        # Build complex voltage phasor vector: V = |V| * exp(j*theta)
        # Converts from polar form (magnitude + angle) to complex form
        V = np.array([self.Vm[k] * np.exp(1j * np.deg2rad(self.Va[k])) for k in range(len(self.Vm))])

        print("\n" + "="*140)
        print("BRANCH POWER FLOWS")
        print("="*140)
        print(f"{'Branch':<8} {'From':<6} {'From type':<10} {'To':<6} {'To type':<10} {'Vi (p.u.)':<12} {'Vj (p.u.)':<12} {'P_ij (MW)':<12} {'Q_ij (MVAr)':<12} {'P_ji (MW)':<12} {'Q_ji (MVAr)':<12} {'Losses (MW)':<12}")
        print("-"*140)

        total_losses = 0.0

        for k, br in enumerate(self.net.branches):
            i, j = br.i, br.j

            y_series = 1 / (br.r + 1j * br.x)
            y_shunt = 1j * (br.b / 2)

            tap = br.tap if br.tap != 0 else 1.0
            tap_c = tap * np.exp(1j * np.deg2rad(br.shift_deg))

            Vi = V[i]
            Vj = V[j]

            Iij = ((Vi / tap_c) - Vj) * y_series + (Vi / tap_c) * y_shunt
            Sij = Vi * np.conj(Iij) * self.net.base_mva

            Iji = ((Vj - Vi / tap_c) * y_series) + (Vj * y_shunt)
            Sji = Vj * np.conj(Iji) * self.net.base_mva

            P_ij, Q_ij = Sij.real, Sij.imag
            P_ji, Q_ji = Sji.real, Sji.imag

            # losses are the difference between the injected power and the received power. Since one is the opposite of the other (minus the losses), adding them gives the losses.
            losses = P_ij + P_ji 
            total_losses += losses

            print(f"{k+1:<8} {i+1:<6} {self.net.buses[i].type:<10} {j+1:<6} {self.net.buses[j].type:<10} {Vi.real:>11.4f} {Vj.real:>11.4f} {P_ij:>11.4f} {Q_ij:>11.4f} {P_ji:>11.4f} {Q_ji:>11.4f} {losses:>11.4f}")

        print("-"*140)
        print(f"{'TOTAL LOSSES:':<20} {total_losses:>11.4f} MW")
        print("="*140 + "\n")

    def show_all(self):
        """
        Display all plots that have been created.
        
        Calls matplotlib's `plt.show()` to display all figures that have been
        created by the plotting methods (plot_voltage_profile, plot_angle_profile,
        plot_generation_pie, plot_branch_flows) but not yet displayed.
        
        Notes
        -----
        This method should be called after creating one or more plots to
        actually display them. In Jupyter notebooks, plots may display
        automatically depending on the matplotlib backend configuration.
        """
        plt.show()
