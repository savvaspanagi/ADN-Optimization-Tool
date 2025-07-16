import math
from pyomo.environ import Var, NonNegativeReals

def initialize_ev_flexibility_variables(self, pup_flex_ev_name_prefix, pdown_flex_ev_name_prefix):
    
    """
    This module initializes the electric vehicle (EV) flexibility variables for the optimization model
    developed specifically for the PowerTech 2025 paper. It defines variables for EV charging power 
    deviation between each time period, slack variables for SOC limits, and upward/downward flexibility 
    margins. These variables are essential for accurately modeling the flexibility potential of EVs 
    in power system operation studies.

    For further details on the formulation and methodology, please refer to the PowerTech 2025 paper.
    """

    model = self.model

    pup_flex_ev=Var(model.SEVbuses, model.STimes,within=NonNegativeReals)
    pdown_flex_ev=Var(model.SEVbuses, model.STimes,within=NonNegativeReals)

    self.register_variable(pup_flex_ev_name_prefix, pup_flex_ev)
    self.register_variable(pdown_flex_ev_name_prefix, pdown_flex_ev)