import math
from pyomo.environ import Var, NonNegativeReals


def initialize_voltage_variables(self,voltage_name_prefix=None,angle_name_prefix=None):
    """
    Initialize voltage variables in the Pyomo model.
    """
    model = self.model
    def voltage_limits_rule(model, bus, time):
        return self.anc_Vars.System_Data_Nodes['min_v'].at[bus], self.anc_Vars.System_Data_Nodes['max_v'].at[bus]

    if voltage_name_prefix is not None:
        voltage_var = Var(model.Sbuses, model.STimes, bounds=voltage_limits_rule, initialize=1)
        self.register_variable(voltage_name_prefix, voltage_var)

    if angle_name_prefix is not None:
        angle_var = Var(model.Sbuses, model.STimes, bounds=(-math.pi, math.pi), initialize=0)
        self.register_variable(angle_name_prefix, angle_var)

def initialize_voltage_square_variables(self,voltage_name_prefix=None):
    """
    Initialize voltage variables in the Pyomo model.
    """
    model = self.model
    def voltage_limits_rule(model, bus, time):
        return (self.anc_Vars.System_Data_Nodes['min_v'].at[bus])**2, (self.anc_Vars.System_Data_Nodes['max_v'].at[bus])**2

    if voltage_name_prefix is not None:
        voltage_var = Var(model.Sbuses, model.STimes, bounds=voltage_limits_rule, initialize=1)
        self.register_variable(voltage_name_prefix, voltage_var)

