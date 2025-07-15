from pyomo.environ import Constraint

def fix_ev_non_charging_times(self, model_ev_ch=None, model_ev_flex_up=None, model_ev_flex_down=None):
    """
    Fixes EV charging and discharging variables to 0 during non-charging times.

    Parameters:
    - model: Pyomo model where the variables will be fixed.
    """
    model=self.model
    
    for i in model.SEVbuses:
        for time in model.STimes:
            if model.EV_available_param[i,time]()==0:
                if model_ev_ch is not None:
                    model_ev_ch[i,  time].fix(0)
                    model.qEV[i,  time].fix(0)
                if model_ev_flex_up is not None:
                    model_ev_flex_up[i,  time].fix(0)
                if model_ev_flex_down is not None:
                    model_ev_flex_down[i,  time].fix(0)