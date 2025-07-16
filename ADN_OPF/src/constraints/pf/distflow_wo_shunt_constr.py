from pyomo.environ import Constraint, cos, sin

def add_active_power_flow_df_wos_constraint(self, pder_contrl_var, pline_var, p_transformer_var, pgrid_var, ev_ch_p_var, line_current_var, transformer_current_var, name_prefix, p_hp_var=None):
    """
    Adds the active power flow constraint to the model using Constraintself.

    Parameters:
    - self: An instance of Constraintself.
    - model: Pyomo model.
    - Y_bus_df: Admittance matrix as a DataFrame.
    """
    
    model=self.model
    def branch_power_balance_active(model, j, time):
        return (
            sum(pder_contrl_var[bus, time] for bus in model.SDER_contr if bus == j)
                + sum(model.unctrl_PV_gen_P[bus, time] for bus in model.SDER_uncontr if bus == j)
                + sum(pgrid_var[bus, time] for bus in model.SGrid if bus == j)
                - sum(model.Load_P[bus, time] for bus in model.SLoadbuses if bus == j)
                - sum(ev_ch_p_var[bus, time] for bus in model.SEVbuses if bus == j)
                - sum(p_hp_var[bus, time] for bus in model.SHPbuses if bus == j)
                ==
            sum(pline_var[j, k, time] for k in model.Sdownstream[j])
            - sum((pline_var[i, j, time] - model.resistance_Parm[i, j] * line_current_var[i, j, time]) for i in model.Supstream[j])
            +sum(p_transformer_var[j, k, time] for k in model.Sdownstream_transformer[j])
            - sum((p_transformer_var[i, j, time] - model.transformer_resistance_Parm[i, j] * transformer_current_var[i, j, time]) for i in model.Supstream_transformer[j])
        ) 

    constraint = Constraint(model.Sbuses, model.STimes, rule=branch_power_balance_active)
    self.register_constraint(name_prefix, constraint)


def add_reactive_power_flow_df_wos_constraint(self, qder_contr_var, qline_var, q_transformer_var, qgrid_var, ev_ch_q_var, line_current_var, transformer_current_var, name_prefix, q_hp_var=None):
    """
    Adds the reactive power flow constraint to the model using Constraintself.

    Parameters:
    - self: An instance of Constraintself.
    - model: Pyomo model.
    - Y_bus_df: Admittance matrix as a DataFrame.
    """
    
    model=self.model
    
    def branch_power_balance_reactive(model, j, time):
        return (0
            + sum(qder_contr_var[bus, time] for bus in model.SDER_contr if bus == j)
            + sum(model.unctrl_PV_gen_Q[bus, time] for bus in model.SDER_uncontr if bus == j)
            + sum(qgrid_var[bus, time] for bus in model.SGrid if bus == j)
            - sum(model.Load_Q[bus, time] for bus in model.SLoadbuses if bus == j)
            - sum(ev_ch_q_var[bus, time] for bus in model.SEVbuses if bus == j)
            - sum(q_hp_var[bus, time] for bus in model.SHPbuses if bus == j)
            ==
            sum(qline_var[j, k, time] for k in model.Sdownstream[j])
            - sum((qline_var[i, j, time] - model.reactance_Parm[i, j] * line_current_var[i, j, time]) for i in model.Supstream[j])
            + sum(q_transformer_var[j, k, time] for k in model.Sdownstream_transformer[j])
            - sum((q_transformer_var[i, j, time] - model.transformer_reactance_Parm[i, j] * transformer_current_var[i, j, time]) for i in model.Supstream_transformer[j])
        )

    constraint = Constraint(model.Sbuses, model.STimes, rule=branch_power_balance_reactive)
    self.register_constraint(name_prefix, constraint)

def add_voltage_power_flow_df_wos_constraint(self, pline_var, qline_var, current_var, voltage_var, resistance_para, reactance_param, set,  name_prefix):
    
    model=self.model
    
    def branch_voltage_drop(model, i, j, time):
        return (
            voltage_var[j, time] ==
            voltage_var[i, time]
            - 2 * (resistance_para[i, j] * pline_var[i, j, time] + reactance_param[i, j] * qline_var[i, j, time])
            + (resistance_para[i, j]**2 + reactance_param[i, j]**2) * current_var[i, j, time]
        )
    
    constraint = Constraint(set, model.STimes, rule=branch_voltage_drop)
    self.register_constraint(name_prefix, constraint)

def add_brunch_current_flow_df_wos_equal_constraint(self, pline_var, qline_var, current_var, volage_var, set, name_prefix):
    
    model=self.model

    def branch_current_relation(model, i, j, time):
        return (
            current_var[i, j, time] * volage_var[i, time] ==
            pline_var[i, j, time]**2 + qline_var[i, j, time]**2
        )
    constraint = Constraint(set, model.STimes, rule=branch_current_relation)
    self.register_constraint(name_prefix, constraint)

def add_brunch_current_flow_df_wos_SOCP_constraint(self, pline_var, qline_var, current_var, volage_var, set, name_prefix):
    
    model=self.model

    def branch_current_relation(model, i, j, time):
        return (
            current_var[i, j, time] * volage_var[i, time] >=
            pline_var[i, j, time]**2 + qline_var[i, j, time]**2
        )
    constraint = Constraint(set, model.STimes, rule=branch_current_relation)
    self.register_constraint(name_prefix, constraint)
