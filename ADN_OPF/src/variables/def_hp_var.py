import math
from pyomo.environ import Var, NonNegativeReals

def initialize_hp_variables(self, p_name_prefix, q_name_prefix):
    """
    Initialize HP variables in the Pyomo model.
    """
    model = self.model
    system_data_hp = self.anc_Vars.system_data_hp
    
    def HP_active_power_bounds_rule(model, sHP, time):
        node_data = system_data_hp.set_index('HP_node')
        return node_data.loc[sHP, 'P_min'], node_data.loc[sHP, 'P_max']

    def HP_reactive_power_bounds_rule(model, sHP, time):
        node_data = system_data_hp.set_index('HP_node')
        return node_data.loc[sHP, 'Qmin'], node_data.loc[sHP, 'Qmax']

    pHP = Var(model.SHPbuses, model.STimes, bounds=HP_active_power_bounds_rule)
    qHP = Var(model.SHPbuses, model.STimes, bounds=HP_reactive_power_bounds_rule)
    
    self.register_variable(p_name_prefix, pHP)
    self.register_variable(q_name_prefix, qHP)
    