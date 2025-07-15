import math
from pyomo.environ import Var, NonNegativeReals

def initialize_ev_variables(self, pch_name_prefix, q_name_prefix, soc_name_prefix):
    """
    Initialize EV variables in the Pyomo model.
    """
    model = self.model
    system_data_ev = self.anc_Vars.system_data_ev
    
    def EV_charge_active_power_bounds_rule(model, sEV, time):
        node_data = system_data_ev.set_index('EV_node')
        return node_data.loc[sEV, 'EV_Pmin_ch'], node_data.loc[sEV, 'EV_Pmax_ch']

    def EV_reactive_power_bounds_rule(model, sEV, time):
        node_data = system_data_ev.set_index('EV_node')
        return node_data.loc[sEV, 'EV_Qmin'], node_data.loc[sEV, 'EV_Qmax']

    def EV_energy_bounds_rule(model, sEV, time):
        node_data = system_data_ev.set_index('EV_node')
        min_soc = node_data.loc[sEV, 'EV_EC'] * node_data.loc[sEV, 'EV_SOC_min'] / 100
        max_soc = node_data.loc[sEV, 'EV_EC'] * node_data.loc[sEV, 'EV_SOC_max'] / 100
        return min_soc, max_soc

    pEVch = Var(model.SEVbuses, model.STimes, bounds=EV_charge_active_power_bounds_rule)
    qEV = Var(model.SEVbuses, model.STimes, bounds=EV_reactive_power_bounds_rule)
    EVsoc = Var(model.SEVbuses, model.STimes, bounds=EV_energy_bounds_rule)
    
    self.register_variable(pch_name_prefix, pEVch)
    self.register_variable(q_name_prefix, qEV)
    self.register_variable(soc_name_prefix, EVsoc)
    