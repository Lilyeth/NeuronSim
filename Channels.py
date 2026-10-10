import numpy as np
from copy import deepcopy

class IonChannel:
    def __init__(self, g_max, E_rev, gates=None, name="ion"):
        self.g_max = g_max
        self.E_rev = E_rev
        self.name = name
        self.gates = {}
        gates = gates or {}
        for gname, cfg in gates.items():
            self.gates[gname] = {
                "value": cfg.get("init", 0.0),
                "p": cfg.get("p", 1),
                "alpha": cfg.get("alpha"),
                "beta": cfg.get("beta")
            }

    def init_gates(self, V, ca=None):
        for gate in self.gates.values():
            a = gate["alpha"](V, ca) if gate["alpha"] else 0.0
            b = gate["beta"](V, ca) if gate["beta"] else 0.0
            gate["value"] = a / (a + b) if (a + b) != 0 else gate["value"]

    def update_gates(self, V, dt, ca=None):
        for gate in self.gates.values():
            a = gate["alpha"](V, ca) if gate["alpha"] else 0.0
            b = gate["beta"](V, ca) if gate["beta"] else 0.0
            x = gate["value"]
            dxdt = a * (1 - x) - b * x
            gate["value"] += dt * dxdt
            gate["value"] = np.clip(gate["value"], 0.0, 1.0)

    def conductance(self):
        g = self.g_max
        for gate in self.gates.values():
            g *= gate["value"] ** gate["p"]
        return g

    def current(self, V, ca=None):
        return self.conductance() * (V - self.E_rev)
    
    def clone(self):
        return deepcopy(self)
    
class VoltageGatedCaChannel(IonChannel):
    def __init__(self, g_max=1.0, E_rev=120.0, name="Ca"):
        gates = {
            "m": {"p": 2, "alpha": default_alpha_m_ca, "beta": default_beta_m_ca},
            "h": {"p": 1, "alpha": default_alpha_h_ca, "beta": default_beta_h_ca}
        }
        super().__init__(g_max=g_max, E_rev=E_rev, gates=gates, name=name)

class CaActivatedKChannel:
    def __init__(self, g_bar=10.0, E_rev=-90.0, kd=0.3, n=4.0, name="KCa"):
        """
        g_bar: maximal conductance (mS/cm^2)
        E_rev: K reversal (mV)
        kd: half-activation Ca concentration (µM)
        n: Hill coefficient
        """
        self.g_bar = g_bar
        self.E_rev = E_rev
        self.kd = kd
        self.n = n
        self.name = name
        # store current activation (for diagnostics)
        self.activation = 0.0
    

    def update(self, ca):
        # Hill equation
        ca_n = ca ** self.n
        kd_n = self.kd ** self.n
        self.activation = ca_n / (ca_n + kd_n) if (ca_n + kd_n) != 0 else 0.0

    def conductance(self):
        return self.g_bar * self.activation

    def current(self, V, ca=None):
        return self.conductance() * (V - self.E_rev)
    
# Channel settings
def alpha_m(V, ca=None): return 0.1 * (V + 40) / (1 - np.exp(-(V + 40) / 10))
def beta_m(V, ca=None):  return 4.0 * np.exp(-(V + 65) / 18)

def alpha_h(V, ca=None): return 0.07 * np.exp(-(V + 65) / 20)
def beta_h(V, ca=None):  return 1.0 / (1 + np.exp(-(V + 35) / 10))

def alpha_n(V, ca=None): return 0.01*(V+55)/(1 - np.exp(-(V+55)/10))
def beta_n(V, ca=None):  return 0.125*np.exp(-(V+65)/80)

# Calcium Control

def default_alpha_m_ca(V, ca=None):
    denom = 1 - np.exp(-(V + 25) / 10)
    denom = denom if abs(denom) > 1e-9 else 1e-9
    return 0.1 * (V + 25) / denom

def default_beta_m_ca(V, ca=None):
    return 4.0 * np.exp(-(V + 55) / 18)

def default_alpha_h_ca(V, ca=None):
    return 0.07 * np.exp(-(V + 50) / 20)

def default_beta_h_ca(V, ca=None):
    return 1.0 / (1 + np.exp(-(V + 20) / 10))


Ca_channel = VoltageGatedCaChannel(g_max=1.0, E_rev=120.0)
KCa_channel = CaActivatedKChannel(g_bar=10.0, E_rev=-90.0, kd=0.3, n=4.0)

Na_channel = IonChannel(
    g_max=120.0,
    E_rev=50.0,
    gates={
        "m": {"p": 3, "alpha": alpha_m, "beta": beta_m},
        "h": {"p": 1, "alpha": alpha_h, "beta": beta_h}
    },
    name="Na"
)

K_channel = IonChannel(
    g_max=36,
    E_rev=-77,
    gates={
        'n': {"p": 4, 'alpha':alpha_n, 'beta':beta_n}
    },
    name="K"
)


Leak = IonChannel(
    g_max=0.3,
    E_rev=-65,
    gates={},
    name='Leak'
)