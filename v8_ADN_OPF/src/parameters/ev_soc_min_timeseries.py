from pyomo.environ import Param
import math

"""
This module produces the minimum State of Charge (SOC) timeseries for electric vehicles (EVs)
used in the optimization model. The timeseries ensures that each EV maintains a minimum SOC
over time, considering charging needs and trip schedules.

For more details on the formulation and methodology, please refer to the PowerTech 2025 paper.
"""

def initialize_ev_min_soc_timeseries(self, EV_min_SOC_timeseries_prefix_name):
    model = self.model
    delta = self.delta

    def EV_SOC_min_overtime_rule(model, i, time):
        for ind in model.SDistance_ind:
            t_dep = model.ev_departure_time_param[i, ind]()
            t_arr = model.ev_arrival_time_param[i, ind]()
            soc_min = model.EV_SoC_min_param[i]()
            soc_at_departure = model.EV_SoC_min_departure_param[i, ind]()
            t_needed = math.ceil((soc_at_departure - soc_min) / (model.ev_max_ch_param[i]() * delta))
            t_start_charge = t_dep - t_needed - 1
            if time <= t_start_charge or (time >= t_dep and time < t_arr):
                return soc_min
            elif t_start_charge < time < t_dep:
                slope = (soc_min - soc_at_departure) / t_needed
                x = t_dep - (t_needed + 1) - time
                return (soc_min + x * slope) * model.EV_available_param[i, time]()
            # default: return base value
        return model.EV_SoC_min_param[i]()

    param_obj = Param(model.SEVbuses, model.STimes, rule=EV_SOC_min_overtime_rule, mutable=True)
    self.register_parameter(EV_min_SOC_timeseries_prefix_name, param_obj)
