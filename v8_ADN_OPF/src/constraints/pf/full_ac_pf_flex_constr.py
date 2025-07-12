from pyomo.environ import Constraint, cos, sin

def add_active_power_flex_flow_constraint(self, pder_contrl_var, pgrid_var, ev_ch_p_var, ev_flex_p_var, voltage_v_var,voltage_pa_var, name_prefix,type):
    """
    Adds the active power flow constraint to the model using Constraintself.

    Parameters:
    - self: An instance of Constraintself.
    - model: Pyomo model.
    - Y_bus_df: Admittance matrix as a DataFrame.
    """
    
    model=self.model
    
    def active_power_flow_rule(model, k, time):
        return (
            sum(pder_contrl_var[bus, time] for bus in model.SDER_contr if bus == k)
            + sum(model.unctrl_PV_gen_P[bus, time] for bus in model.SDER_uncontr if bus == k)
            + sum(pgrid_var[bus, time] for bus in model.SGrid if bus == k)
            - sum(model.Load_P[bus, time] for bus in model.SLoadbuses if bus == k)
            - sum(ev_ch_p_var[bus, time] for bus in model.SEVbuses if bus == k)
            + (
                sum(ev_flex_p_var[bus, time] for bus in model.SEVbuses if bus == k)
                if type == "downward"
                else -sum(ev_flex_p_var[bus, time] for bus in model.SEVbuses if bus == k)
            )
            ==
            sum(
                voltage_v_var[k, time]
                * voltage_v_var[i, time]
                * (
                    model.admitt_mat_Parm_real[k, i] * cos(voltage_pa_var[k, time] - voltage_pa_var[i, time])
                    + model.admitt_mat_Parm_imag[k, i] * sin(voltage_pa_var[k, time] - voltage_pa_var[i, time])
                )
                for i in model.Sbuses
            )
        )

    constraint = Constraint(model.Sbuses, model.STimes, rule=active_power_flow_rule)
    self.register_constraint(name_prefix, constraint)


def add_reactive_power_flex_flow_constraint(self, qder_contr_var, qgrid_var, ev_ch_q_var, voltage_v_var, voltage_pa_var, name_prefix):
    """
    Adds the reactive power flow constraint to the model using Constraintself.

    Parameters:
    - self: An instance of Constraintself.
    - model: Pyomo model.
    - Y_bus_df: Admittance matrix as a DataFrame.
    """
    
    model=self.model
    
    def reactive_power_flow_rule(model, k, time):
        return (
            sum(qder_contr_var[bus, time] for bus in model.SDER_contr if bus == k)
            + sum(model.unctrl_PV_gen_Q[bus, time] for bus in model.SDER_uncontr if bus == k)
            + sum(qgrid_var[bus, time] for bus in model.SGrid if bus == k)
            - sum(model.Load_Q[bus, time] for bus in model.SLoadbuses if bus == k)
            - sum(ev_ch_q_var[bus, time] for bus in model.SEVbuses if bus == k)
            ==
            sum(
                voltage_v_var[k, time]
                * voltage_v_var[i, time]
                * (
                    model.admitt_mat_Parm_real[k, i] * sin(voltage_pa_var[k, time] - voltage_pa_var[i, time])
                    - model.admitt_mat_Parm_imag[k, i] * cos(voltage_pa_var[k, time] - voltage_pa_var[i, time])
                )
                for i in model.Sbuses
            )
        )

    constraint = Constraint(model.Sbuses, model.STimes, rule=reactive_power_flow_rule)
    self.register_constraint(name_prefix, constraint)
    
