# ancillary_variables.py

import pandas as pd
import numpy as np
import math
class AdditionalData:
    def __init__(self,manager):
        
        net=manager.net
        self.net=net 
        # Ancillary DataFrames and constants
        self.f = 50  # Frequency in Hz
        self.S_Base = net.sn_mva
        V_base_list = np.sort(net.bus['vn_kv'].unique())
        self.V_Base = net.bus.iloc[-1,:]['vn_kv']
        self.Z_base = (self.V_Base ** 2) / self.S_Base
        self.I_base = (self.S_Base * 10**6) / (np.sqrt(3) * self.V_Base * 10**3) / 1000
        self.Y_base = self.S_Base / (self.V_Base ** 2)
        # Create DataFrame
        self.base_values = pd.DataFrame({
            'f': self.f,
            'S_base [MVA]': net.sn_mva,
            'V_base [kV]': V_base_list,
            'Z_base [Ohm]': (V_base_list ** 2) / net.sn_mva,
            'I_base [kA]': (net.sn_mva * 1e6) / (np.sqrt(3) * V_base_list * 1e3) / 1e3,
            'Y_base [S]': net.sn_mva / (V_base_list ** 2)
        })
        # Initialize dataframes
        self.System_Data_Nodes = self.define_nodes()
        self.System_Data_Lines = self.define_lines()
        self.System_Data_Transformers = self.define_transformer()
        self.System_Data_DER = self.define_der()
        self.System_Data_Grid = self.define_grid()
        self.system_data_load = self.define_load_data()

        self.system_data_ev = pd.DataFrame()
        self.system_data_ev_char = pd.DataFrame()
        self.system_data_hp=pd.DataFrame()

    def define_nodes(self):
        NB = len(self.net.bus)
        System_Data_Nodes = pd.DataFrame()
        System_Data_Nodes['Nodes'] = range(NB)
        System_Data_Nodes['min_v'] = self.net.bus['min_vm_pu']
        System_Data_Nodes['max_v'] = self.net.bus['max_vm_pu']
        System_Data_Nodes['name'] = self.net.bus['name']
        # Assign name of feeder. This is only for plotting convenience, can be ignored.
        def assign_category(name):
            if isinstance(name, str):  # Ensure name is a string
                if 'F1' in name:
                    return 'F1'
                elif 'F2' in name:
                    return 'F2'
                elif 'F3' in name:
                    return 'F3'
                return None
            return None  # Default value if name is not a string
        System_Data_Nodes['Feeder'] = self.net.bus['name'].astype(str).apply(assign_category)
        
        return System_Data_Nodes

    def define_lines(self):
        km = self.net.line['length_km']
        System_Data_Lines = pd.DataFrame()
        # System_Data_Lines['Voltage_Level'] = self.net.bus.loc[self.net.line['from_bus']]['vn_kv']
        System_Data_Lines['FROM'] = self.net.line['from_bus']
        System_Data_Lines['TO'] = self.net.line['to_bus']
        System_Data_Lines = System_Data_Lines.merge(self.net.bus[['vn_kv']], left_on='FROM', right_index=True)
        System_Data_Lines = System_Data_Lines.merge(
            self.base_values[['V_base [kV]', 'Z_base [Ohm]']],
            left_on='vn_kv',
            right_on='V_base [kV]',
            how='left')
        System_Data_Lines['R'] = self.net.line['r_ohm_per_km'] * km / System_Data_Lines['Z_base [Ohm]']
        System_Data_Lines['X'] = self.net.line['x_ohm_per_km'] * km / System_Data_Lines['Z_base [Ohm]']
        System_Data_Lines['Y'] = 2 * np.pi * self.f * self.net.line['c_nf_per_km'] * km * 1e-9 / self.Y_base
        System_Data_Lines['Imax_pu'] = self.net.line['max_i_ka'] / self.I_base
        return System_Data_Lines

    def define_transformer(self):
        System_Data_Transformer = pd.DataFrame()
        System_Data_Transformer['FROM'] = self.net.trafo['hv_bus']
        System_Data_Transformer['TO'] = self.net.trafo['lv_bus']
        System_Data_Transformer['Sn'] = self.net.trafo['sn_mva'] / self.S_Base # Convert MVA to base
        System_Data_Transformer['vn_hv_kv'] = self.net.trafo['vn_hv_kv'] 
        System_Data_Transformer['vn_lv_kv'] = self.net.trafo['vn_lv_kv']
        System_Data_Transformer['Inom_HV_A'] = (
        self.net.trafo['sn_mva'] * 1e3 / (np.sqrt(3) * System_Data_Transformer['vn_hv_kv']))
        System_Data_Transformer['Inom_LV_A'] = (
        self.net.trafo['sn_mva'] * 1e3 / (np.sqrt(3) * System_Data_Transformer['vn_lv_kv']))
        System_Data_Transformer = System_Data_Transformer.merge(self.base_values[['V_base [kV]', 'I_base [kA]']], left_on='vn_hv_kv', right_on='V_base [kV]', how='left')
        System_Data_Transformer['Imax_pu'] = (
        System_Data_Transformer['Inom_HV_A'] / (System_Data_Transformer['I_base [kA]']*1e3))
        System_Data_Transformer['R'] = self.net.trafo['vkr_percent'] / 100 * self.S_Base / System_Data_Transformer['Sn']
        System_Data_Transformer['X'] = (np.sqrt((self.net.trafo['vk_percent'] / 100) ** 2 - self.net.trafo['vkr_percent'] / 100 ** 2)) * self.S_Base / System_Data_Transformer['Sn']
        return System_Data_Transformer

    def define_der(self):
        NDER = len(self.net.sgen)
        if NDER != 0:
            System_Data_DER = pd.DataFrame()
            System_Data_DER['DER_node'] = self.net.sgen['bus']
            System_Data_DER['P_min'] = 0
            System_Data_DER['P_max'] = self.net.sgen['p_mw'] / self.S_Base
            System_Data_DER['Q_min'] = -abs(self.net.sgen['q_mvar']) / self.S_Base
            System_Data_DER['Q_max'] = abs(self.net.sgen['q_mvar']) / self.S_Base
            System_Data_DER['Controllable'] = False
        else:
            System_Data_DER = pd.DataFrame({'DER_node': [], 'P_min': [], 'P_max': [], 'Q_min': [], 'Q_max': [], 'Controllable': []})
        return System_Data_DER
    
    def define_grid(self):
        NGrid = len(self.net.ext_grid)
        if NGrid != 0:
            System_Data_Grid = pd.DataFrame()
            System_Data_Grid['Grid_node'] = self.net.ext_grid['bus']
        else:
            System_Data_Grid = pd.DataFrame({'Grid_node': [0]})
        return System_Data_Grid
    
    def define_load_data(self):
        System_Data_Load = pd.DataFrame()
        System_Data_Load['Bus'] = self.net.load['bus']  # Define the bus where the load is located
        System_Data_Load['Active_Power'] = self.net.load['p_mw'] / self.S_Base  # Define the maximum installed active power 
        # Usually the reactive power has a constant power factor value for example cosf=0.95
        System_Data_Load['Reactive_Power'] = self.net.load['q_mvar'] / self.S_Base  # Define the maximum allowable reactive power 
        
        # Assign name of feeder. This is only for plotting convenience, can be ignored.
        def assign_category(name):
            if isinstance(name, str):  # Ensure name is a string    
                if 'F1' in name:
                    return 'F1'
                elif 'F2' in name:
                    return 'F2'
                elif 'F3' in name:
                    return 'F3'
                else:
                    return None  # Default value if none of the conditions are met
            return None  # Default value if name is not a string
        
        System_Data_Load['Feeder'] = self.net.load['name'].apply(assign_category)
        return System_Data_Load
    
    #################################----------------- EV ---------------------############################# 

    def addEV(self, node, P_min_ch, P_max_ch, Qmin, Qmax, costh_EV, P_control, Q_control, V2G, EV_EC,EV_SoC_init,EV_SoC_end,EV_SoC_min,EV_SoC_max,EV_cons,arrival,departure,distance):
        """Add an EV to the system with user-defined parameters."""
        # Initialize an empty DataFrame if it's the first EV
        if self.system_data_ev.empty:
            self.system_data_ev = pd.DataFrame()
            self.system_data_ev_char = pd.DataFrame()
            

        # Define new EV data based on user input
        new_ev = pd.DataFrame({
            'EV_node': [node],  # Single node for this example (could be dynamic based on user input)
            'EV_Pmin_ch': [P_min_ch / 1000 / self.S_Base],  # Convert P_min to MW
            'EV_Pmax_ch': [P_max_ch / 1000 / self.S_Base],  # Convert P_max to MW
            'EV_Qmin': [Qmin / 1000 / self.S_Base],  # Calculate Qmin
            'EV_Qmax': [Qmax / 1000 / self.S_Base],  # Calculate Qmax
            'P_control': [P_control], 
            'Q_control': [Q_control],  
            'EV_costh': [costh_EV],  # costh
            'V2G': [V2G],  # costh
            'EV_EC': [EV_EC / 1000 / self.S_Base],  # Energy Capacity in MWh
            'EV_SOC_ini': [EV_SoC_init],  # Initial SOC in percentage
            'EV_SOC_end': [EV_SoC_end],  # End SOC in percentage
            'EV_SOC_min': [EV_SoC_min],  # Minimum SOC in percentage
            'EV_SOC_max': [EV_SoC_max],  # Maximum SOC in percentage
            'Consumption(MWh)_per_100km': [EV_cons / 1000 / self.S_Base],  # Consumption per 100 km in MWh
        })
        new_ev_char = pd.DataFrame({
            'EV_node': [node],  # Single node for this example (could be dynamic based on user input)
            'departure': [departure],  # Convert P_min to MW
            'arrival': [arrival],  # Convert P_max to MW
            'distance': [distance],  # Calculate Qmin
        })
        new_ev_char['trip_energy_needs'] = new_ev_char['distance'].apply(lambda x: [round(i * new_ev['Consumption(MWh)_per_100km'][0] / 100, 4) for i in x])
        new_ev_char['SoC_Needs_For_Trip(%)'] = new_ev_char['trip_energy_needs'].apply(lambda x: [round(i / new_ev['EV_EC'][0] * 100, 4) for i in x])
        new_ev_char['Min_SOC_Before_Departure(%)'] = new_ev_char['SoC_Needs_For_Trip(%)'].apply(lambda x: [round(max(i+new_ev['EV_SOC_min'][0],new_ev['EV_SOC_min'][0]), 4) for i in x])
        # Append new EV data to the existing EV DataFrame
        self.system_data_ev = pd.concat([self.system_data_ev, new_ev], ignore_index=True)
        self.system_data_ev_char = pd.concat([self.system_data_ev_char, new_ev_char], ignore_index=True)

        return
    
    #################################----------------- Flexible Building Heat Pump ---------------------############################# 


    def addFlexBuilding(self, node, P_min, P_max, RC_Parameters, Initialization, model_Type, time_interval, timeframe, temp_preference=None, COP=None, Qmin=None, Qmax=None, costh_HP=0.95, P_control="controllable", Q_control="constant_pf"):
        """
        Add a Heat Pump (HP) to the system with user-defined parameters.
        If COP is not provided, a default COP curve is generated as a function of outdoor temperature.
        """
        # Initialize DataFrame if not already present
        if not hasattr(self, 'system_data_hp') or self.system_data_hp.empty:
            self.system_data_hp = pd.DataFrame()

        if Qmin == None:
            Qmin=-P_max
        if Qmax == None:
            Qmax=P_max
            
        # Determine number of time steps
        num_steps = int((timeframe * 60) / time_interval)

        # Generate default temperature preference DataFrame if not provided
        if temp_preference is None:
            temp_preference = pd.DataFrame({
                'Tmin': [20.0] * num_steps,
                'Tmax': [22.0] * num_steps
            })
        else:
            # Validate input
            if not isinstance(temp_preference, pd.DataFrame):
                raise ValueError("Temperature preference must be a pandas DataFrame.")
            if list(temp_preference.columns) != ['Tmin', 'Tmax']:
                raise ValueError("Temperature preference DataFrame must have columns: ['Tmin', 'Tmax'].")
            if len(temp_preference) != num_steps:
                raise ValueError("Temperature preference length must match simulation time steps.")
            
        # Handle COP: if None, generate a default COP curve (example linear)
        if COP is None:
            # Example: COP = 2.5 + 0.1 * Tout for Tout in range -5 to 20°C
            tout_range = np.arange(-5, 21, 1)
            cop_values = 2.5 + 0.1 * tout_range
            COP = pd.DataFrame({'Tout': tout_range, 'COP': cop_values})

        # Create HP entry
        new_hp = pd.DataFrame({
            'HP_node': [node],
            'P_min': [P_min / 1000 / self.S_Base],
            'P_max': [P_max / 1000 / self.S_Base],
            'RC_Parameters': [RC_Parameters],
            'Initialization': [Initialization],
            'model_type': [model_Type],
            'temp_preference': [temp_preference],
            'COP_curve': [COP],  # DataFrame with COP vs Tout
            'Qmin': [Qmin / 1000 / self.S_Base],
            'Qmax': [Qmax / 1000 / self.S_Base],
            'costh_HP': [costh_HP],
            'P_control': [P_control],
            'Q_control': [Q_control]
        })

        self.system_data_hp = pd.concat([self.system_data_hp, new_hp], ignore_index=True)

        return
        
    
        
    