from pyomo.environ import Constraint

def add_power_ch_dp_ev_cons(self, name_prefix):
    """
    Adds the EV charging decision point constraint to the Pyomo model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    """
    model=self.model
    def power_ch_dp_ev_cons_rule(model, i,  time):
        """
        Tracks changes in charging power over time.
        """
        if time == 0:
            return model.ev_ch_dp[i,  time] == model.pEVch[i,  time]
        else:
            return model.ev_ch_dp[i,  time] ==  model.pEVch[i,  time] - model.pEVch[i,  time - 1]
    
    constraint = Constraint(model.SEVbuses,  model.STimes, rule=power_ch_dp_ev_cons_rule)
    self.register_constraint(name_prefix, constraint)