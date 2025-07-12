from pyomo.environ import Constraint

def add_ev_min_departure_soc_constraint(self, name_prefix):
    """
    Adds the EV minimum SOC constraint before departure to the Pyomo model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    """
    model=self.model
    
    def EV_min_departure_SOC_rule(model, i, time):
        return model.EVsoc[i,  time] >= model.EV_SoC_min_overtime_param[i,time]
    constraint = Constraint(model.SEVbuses, model.STimes, rule=EV_min_departure_SOC_rule)
    self.register_constraint(name_prefix, constraint)
