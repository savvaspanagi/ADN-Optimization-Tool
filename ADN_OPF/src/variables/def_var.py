import math
from pyomo.environ import Var, NonNegativeReals

def add_variable(self, variable_name_prefix, variable_set):
    """
    Initialize grid power variables in the Pyomo model.
    """
    model = self.model

    power_var = Var(variable_set, model.STimes)
    self.register_variable(variable_name_prefix, power_var)

