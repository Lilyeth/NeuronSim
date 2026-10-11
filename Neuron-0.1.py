import numpy as np
from copy import deepcopy

class Gate:
    def __init__(
        self,
        alpha_func,
        beta_func,
        power=1,
        initial=0.0
    ):
        self.alpha_func = alpha_func
        self.beta_func = beta_func

        self.power = power
        self.value = initial

    def update(self, V, dt):
        a = self.alpha_func(V)
        b = self.beta_func(V)

        # The equation here is the Hodkin-Huxley voltage gated channel gate change equation in non-spesific form, returning dx for timestep   
        self.value += dt * (a * (1 - self.value) - b * self.value)
        
        self.value = np.clip(
            self.value,
            0.0,
            1.0
        )

class Channel:
    def __init__(self, g_max: int, E_rev: int, gates: list):
        self.g_max = g_max
        self.E_rev = E_rev 
        self.gates = gates
        
    def update_gates(self, V, dt):
        for gate in self.gates:
            gate.update(V, dt)
   
    # Calculating the channel current and conductance, being the I_channel = g_max * gates * (V_m - E_rev)
    def conductance(self):
        g = self.g_max
        for gate in self.gates:
            g *= gate.value ** gate.power
        return g

    def current(self, V):
        return self.conductance() * (V - self.E_rev)
    

# Channel settings
def alpha_m(V): return 0.1 * (V + 40) / (1 - np.exp(-(V + 40) / 10))
def beta_m(V):  return 4.0 * np.exp(-(V + 65) / 18)

def alpha_h(V): return 0.07 * np.exp(-(V + 65) / 20)
def beta_h(V):  return 1.0 / (1 + np.exp(-(V + 35) / 10))

def alpha_n(V): return 0.01*(V+55)/(1 - np.exp(-(V+55)/10))
def beta_n(V):  return 0.125*np.exp(-(V+65)/80)
