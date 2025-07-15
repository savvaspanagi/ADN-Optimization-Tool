import math
from pyomo.environ import Var, NonNegativeReals

def initialize_der_variables(self, power_control_name_prefix, power_curtail_prefix, reactive_prefix_name):
    """
    Initialize grid power variables in the Pyomo model.
    """
    model = self.model
    system_data_der = self.anc_Vars.System_Data_DER
    
    def DER_active_bounds_rule(model, sder, time):
        node_data = system_data_der.set_index('DER_node')
        return 0, model.ctrl_PV_gen_P[sder,time]

    def DER_init_rule(model, sder, time):
        node_data = system_data_der.set_index('DER_node')
        return model.ctrl_PV_gen_P[sder,time]

    def DER_reactive_bounds_rule(model, sder, time):
        node_data = system_data_der.set_index('DER_node')
        return node_data.loc[sder, 'Q_min'], node_data.loc[sder, 'Q_max']

    pder_contr = Var(model.SDER_contr, model.STimes, within=NonNegativeReals, initialize=DER_init_rule, bounds=DER_active_bounds_rule)
    pder_curtail_contr = Var(model.SDER_contr, model.STimes, within=NonNegativeReals, initialize=0, bounds=DER_active_bounds_rule)
    qder_contr = Var(model.SDER_contr, model.STimes, bounds=DER_reactive_bounds_rule)

    self.register_variable(power_control_name_prefix, pder_contr)
    self.register_variable(power_curtail_prefix, pder_curtail_contr)
    self.register_variable(reactive_prefix_name, qder_contr)
