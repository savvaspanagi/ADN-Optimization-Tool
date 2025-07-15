import math
from pyomo.environ import Var, NonNegativeReals

def initialize_power_variable(self, power_name_prefix, model_set):
    """
    Initialize grid power variables in the Pyomo model.
    """
    model = self.model

    power_var = Var(model_set, model.STimes)
    self.register_variable(power_name_prefix, power_var)
