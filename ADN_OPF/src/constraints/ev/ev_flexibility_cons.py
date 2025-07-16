from pyomo.environ import Constraint

### Please refer to PowerTech 2025 paper for the mathematical formulation of the constraints ###

def add_power_up_flex_ev_cons(self, name_prefix):
    
    """
    Adds the EV upward flexibility constraint based on SOC to the Pyomo model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    - delta: Time step duration for SOC calculation.
    """
    delta=self.delta
    model=self.model
    
    def power_up_flex_ev_cons_rule(model, i,  time):
        """
        Limits the upward flexibility based on SOC.
        """
        if time == 0:
            # SOC constraint for the first day and time step
            return model.EVinit_SOC[i] + (model.pup_flex_ev[i,  time] + model.pEVch[i,  time]) * delta <= model.EV_SoC_max_param[i]
        else:
            # SOC constraint for regular time steps
            return model.EVsoc[i,  time - 1] + (model.pup_flex_ev[i,  time] + model.pEVch[i,  time]) * delta <= model.EV_SoC_max_param[i]

    constraint = Constraint(model.SEVbuses,  model.STimes, rule=power_up_flex_ev_cons_rule)
    self.register_constraint(name_prefix, constraint)

def add_power_up_flex_max_cons(self,name_prefix):
    """
    Adds the EV upward flexibility constraint based on max charger capability to the Pyomo model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    """
    model=self.model
    
    def power_up_flex_max_cons_rule(model, i,  time):
        """
        Limits the upward flexibility based on the maximum charger capability.
        """
        return model.pup_flex_ev[i,  time] + model.pEVch[i,  time] <= model.ev_max_ch_param[i]

    constraint = Constraint(model.SEVbuses,  model.STimes, rule=power_up_flex_max_cons_rule)
    self.register_constraint(name_prefix, constraint)
    
def add_power_down_flex_ev_cons(self, name_prefix):
    """
    Adds the EV downward flexibility constraint based on SOC to the Pyomo model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    - delta: Time step duration for SOC calculation.
    """
    delta=self.delta
    model=self.model
    
    def power_down_flex_ev_cons_rule(model, i,  time):
        """
        Limits the downward flexibility based on SOC.
        """
        if time == 0:
            # Initial SOC constraint
            return model.EVinit_SOC[i] + (model.pEVch[i,  time] - model.pdown_flex_ev[i,  time]) * delta  >= model.EV_SoC_min_overtime_param[i,  time]
        else:
            # Regular SOC constraint
            return model.EVsoc[i,  time - 1] + (model.pEVch[i,  time] - model.pdown_flex_ev[i,  time]) * delta  >= model.EV_SoC_min_overtime_param[i,  time]

    constraint = Constraint(model.SEVbuses,  model.STimes, rule=power_down_flex_ev_cons_rule)
    self.register_constraint(name_prefix, constraint)

def add_power_down_flex_min_cons(self,name_prefix):
    """
    Adds the downward flexibility constraint based on charger capability to the Pyomo model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    """
    model=self.model
    
    def power_down_flex_min_cons_rule(model, i,  time):
        """
        Limits the downward flexibility based on minimum charger capability.
        """
        return model.pdown_flex_ev[i,  time] <= model.pEVch[i,  time]

    constraint = Constraint(model.SEVbuses,  model.STimes, rule=power_down_flex_min_cons_rule)
    self.register_constraint(name_prefix, constraint)






