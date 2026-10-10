import numpy as np
import matplotlib.pyplot as plt
from Channels import Na_channel, K_channel, Ca_channel, KCa_channel, Leak

class Compartment:
    def __init__(self, name, x, V_init=-65.0,
                 length=100e-4, radius=1e-4, Ri=150.0, Cm=1.0):
        """
        name: identifier (e.g. 'soma', 'dend1')
        x: compartment position on theoretical neuron, proximal end position
        V_init: initial membrane potential (mV)
        length: cm (e.g. 100 µm = 100e-4 cm)
        radius: cm (e.g. 1 µm = 1e-4 cm)
        Ri: intracellular resistivity of cytosol (Ω·cm)
        Cm: membrane capacitance (µF/cm²)
        """

        # Geometry
        self.length = length
        self.radius = radius
        self.area = 2 * np.pi * radius * length   # cm²
        self.Ri = Ri
        self.x = x  # proximal end position

        # Electrical state
        self.V = V_init      # mV
        self.Cm = Cm         # µF/cm²
        self.ca = 0.05       # mM (resting Ca)
        
        # Components
        self.channels = []   # list of ion channel objects
        self.synapses = []   # list of synapse objects
        self.connections = []  # [(other_compartment, R_axial)]

        # Currents for bookkeeping
        self.I_axial = 0.0
        self.I_syn = 0.0

    # --- API methods ---
    def add_channel(self, channel):
        self.channels.append(channel)
    
    def add_synapse(self, synapse):
        """synapses should be at the end of nodes"""
        self.synapses.append(synapse)

    def calculate_axial_resistance(self, neighbor, distance_along_neighbor):
        """
        Returns axial resistance (ohms) between self and a connection point on neighbor
        """
        # Compute center-to-center distance
        center_self = self.x + self.length / 2
        center_neighbor = neighbor.x + distance_along_neighbor
        dx = abs(center_self - center_neighbor)

        # Average radius for current path
        r_avg = (self.radius + neighbor.radius) / 2

        # Axial resistance formula
        R_axial = self.Ri * dx / (np.pi * r_avg**2)
        return R_axial

    def add_connection(self, neighbor, x_connection=0.5):
        """
        neighbor: Compartment object to connect to
        """

    def update_channels(self, dt):
        V = self.V
        for ch in self.channels:
            ch.update_gates(V, dt, self.ca)

        I_Ca_total = sum(c.current(V, ca=self.ca) for c in self.channels if getattr(ch, "name", "").lower().startswith("ca"))
        self.ca += -I_Ca_total * self.ca_factor * dt - (self.ca - self.ca_rest) * dt / self.ca_tau

    def compute_axial_current(self):
        pass

    def step(self, dt):
        pass