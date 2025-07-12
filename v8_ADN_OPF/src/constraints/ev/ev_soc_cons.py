from pyomo.environ import Constraint

def add_ev_soc_constraint(self, name_prefix):
    """
    Adds the EV state of charge (SOC) constraint to the Pyomo model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    - delta: Time step duration for SOC calculation.
    """
    delta=self.delta
    model=self.model
    
    def EV_SOC_rule(model, i,  time):
        if time == 0:
            # Initial SOC at the beginning of the simulation
            return model.EVsoc[i,  time] == model.EVinit_SOC[i] + (model.pEVch[i,  time]) * delta
            
        else:
            for x in model.SDistance_ind: # SDistance_ind represent the length of the 'departure' list.
                if time == (model.ev_arrival_time_param[i, x]() - 1):
                    # SOC adjustment for EV arrival with matched x
                    return model.EVsoc[i, time] == \
                       model.EVsoc[i, time - 1] - model.EV_trip_energy_needs_param[i,x]
                       
            # SOC for regular time steps
            return model.EVsoc[i,  time] == model.EVsoc[i,  time - 1] + (model.pEVch[i,  time]) * delta

    constraint = Constraint(model.SEVbuses,  model.STimes, rule=EV_SOC_rule)
    self.register_constraint(name_prefix, constraint)
    