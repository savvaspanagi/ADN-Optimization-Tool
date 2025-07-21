import numpy as np
import pandas as pd
def get_zbase_from_net(net, bus_idx):
    """
    Computes the base impedance (Z_base) for a given bus using net.sn_mva and bus voltage.

    Parameters
    ----------
    net : pandapowerNet
        The pandapower network.
    bus_idx : int
        Index of the bus.

    Returns
    -------
    z_base : float
        The base impedance in Ohms for the bus.
    """
    V_base = net.bus.loc[bus_idx, 'vn_kv']  # in kV
    S_base = net.sn_mva                     # in MVA
    return (V_base ** 2) / S_base           # in Ohms

def add_line_admittance(net, Ybus):
    """
    Adds the series admittance contributions of each transmission line to the Ybus matrix.

    Each line has series impedance:
        z = r + jx

    The series admittance is:
        y = 1 / z

    For each line between buses i and j:
        Y_ii += y
        Y_jj += y
        Y_ij -= y
        Y_ji -= y

    Parameters
    ----------
    net : pandapowerNet
        The pandapower network containing line data.

    Ybus : np.ndarray
        The bus admittance matrix being assembled.
    """
    for _, row in net.line.iterrows():
        fb = net.bus.index.get_loc(row['from_bus'])
        tb = net.bus.index.get_loc(row['to_bus'])
        length = row['length_km']
        r = row['r_ohm_per_km'] * length
        x = row['x_ohm_per_km'] * length
        z = complex(r, x)
        y_series = 1 / z
        z_base = get_zbase_from_net(net, row['from_bus'])
        y_pu = y_series * z_base

        Ybus[fb, fb] += y_pu
        Ybus[tb, tb] += y_pu
        Ybus[fb, tb] -= y_pu
        Ybus[tb, fb] -= y_pu

def add_line_shunt_admittance(net, Ybus, f_hz=50):
    """
    Adds the shunt admittance contributions of each line to the diagonal of the Ybus matrix.

    The shunt admittance per line is modeled using:
        g = g_us_per_km * length / 1e6    (in Siemens)
        b = 2 * pi * f * c_nf_per_km * length / 1e9    (in Siemens)

    The total shunt admittance y_sh = g + jb is split equally at both ends:
        Y_ii += y_sh / 2
        Y_jj += y_sh / 2

    Parameters
    ----------
    net : pandapowerNet
        The pandapower network containing line data.

    Ybus : np.ndarray
        The bus admittance matrix being assembled.

    f_hz : float, optional
        Frequency in Hz (default is 50 Hz).
    """
    for _, row in net.line.iterrows():
        fb = net.bus.index.get_loc(row['from_bus'])
        tb = net.bus.index.get_loc(row['to_bus'])
        length = row['length_km']
        g_us = row.get('g_us_per_km', 0)
        c_nf = row.get('c_nf_per_km', 0)
        g = g_us * length / 1e6  # μS to S
        b = 2 * np.pi * f_hz * c_nf * length / 1e9  # nF to F to S
        y_shunt = complex(g, b)
        z_base = get_zbase_from_net(net, row['from_bus'])
        y_sh_pu = y_shunt * z_base

        Ybus[fb, fb] += y_sh_pu / 2
        Ybus[tb, tb] += y_sh_pu / 2

def add_trafo_admittance(net, Ybus):
    """
    Adds the transformer admittance contributions to the Ybus matrix,
    considering tap ratio, shift degree, and nominal voltage scaling.

    Parameters
    ----------
    net : pandapowerNet
        The pandapower network containing transformer data.
    Ybus : np.ndarray
        The complex bus admittance matrix being assembled (in Ohms⁻¹).
    """
    S_base = net.sn_mva  # MVA

    for _, row in net.trafo.iterrows():
        fb = net.bus.index.get_loc(row['hv_bus'])  # High voltage bus index
        tb = net.bus.index.get_loc(row['lv_bus'])  # Low voltage bus index

        # Base values
        V_base_hv = row['vn_hv_kv']
        V_base_lv = row['vn_lv_kv']
        s_n_trafo = row['sn_mva']

        # Transformer impedance (Ohms)
        r_pu = row['vkr_percent'] / 100
        x_pu = np.sqrt((row['vk_percent'] / 100) ** 2 - r_pu ** 2)
        z_tr = complex(r_pu, x_pu)
        z_tr_new = z_tr * (S_base / s_n_trafo)  # Ohmic scaling to system base
        y_tr_new = 1 / z_tr_new

        # Nominal transformer ratio
        base_ratio = V_base_hv / V_base_lv

        # Tap changer adjustment
        tap = row.get('tap_side', 'hv')
        tap_pos = row.get('tap_pos', 0)
        tap_neutral = row.get('tap_neutral', 0)
        tap_step = row.get('tap_step_percent', 0)
        tap_ratio = 1.0 
        if tap in ['hv', 'lv']:
            tap_multiplier = 1 + ((tap_pos - tap_neutral) * tap_step / 100)
            tap_ratio = tap_multiplier if tap == 'hv' else 1 / tap_multiplier

        a = tap_ratio 
        # Phase shift in degrees to radians
        shift_deg = row.get('shift_degree', 0)
        angle_rad = np.deg2rad(shift_deg)
        phase_shift = np.exp(1j * angle_rad)  # complex rotation factor
        # Ybus matrix updates considering shift and asymmetry
        Ybus[fb, fb] += y_tr_new / a**2
        Ybus[tb, tb] += y_tr_new 
        Ybus[fb, tb] -= y_tr_new / a / np.conj(phase_shift)
        Ybus[tb, fb] -= y_tr_new / a / phase_shift
        # Core loss modeling: i0_percent and pfe_kw (approximate)
        i0_percent = row.get('i0_percent', 0)
        pfe_kw = row.get('pfe_kw', 0)
        if i0_percent > 0 or pfe_kw > 0:
            print("yes")
            # Add shunt admittance to LV side
            g_pfe = pfe_kw / (V_base_lv * 1e3)**2  # conductance from core loss
            print(g_pfe)
            b_mag = i0_percent / 100 / (V_base_lv * 1e3)**2  # susceptance estimate
            Ybus[tb, tb] += complex(g_pfe, b_mag)

    return Ybus

def build_ybus(net, f_hz=50):
    """
    Builds the full bus admittance matrix (Ybus) by assembling:
    - Series admittances from transmission lines:      y = 1 / (r + jx)
    - Shunt admittances from line capacitance & conductance: y_sh = g + jb
    - Transformer admittances with tap ratio:          ideal transformer model

    Final matrix entries follow:
        Y_ii += Σ y_ij + y_sh/2
        Y_ij = -y_ij (series and trafo coupling)

    Parameters
    ----------
    net : pandapowerNet
        The pandapower network to process.

    f_hz : float, optional
        Frequency in Hz (default: 50 Hz).

    Returns
    -------
    Ybus : np.ndarray
        Complex bus admittance matrix (in Siemens).
    """
    n_buses = len(net.bus)
    Ybus = np.zeros((n_buses, n_buses), dtype=complex)

    add_line_admittance(net, Ybus)
    add_line_shunt_admittance(net, Ybus, f_hz)
    if hasattr(net, 'trafo') and not net.trafo.empty:
        add_trafo_admittance(net, Ybus)
    Y_bus_df = pd.DataFrame(Ybus)

    # Add bus indices as labels
    Y_bus_df.index = net.bus.index
    Y_bus_df.columns = net.bus.index
    return Y_bus_df
