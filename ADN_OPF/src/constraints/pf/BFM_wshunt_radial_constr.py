from pyomo.environ import Constraint

def add_active_power_flow_bfm(self, pder_contrl_var, p_line_var,p_line_reverse_var, p_transformer_var,p_transformer_reverse_var, pgrid_var,ev_ch_p_var, name_prefix, p_hp_var=None):
    model = self.model

    def active_power_balance(model, j, time):
        return (
            sum(pder_contrl_var[bus, time] for bus in model.SDER_contr if bus == j)
                + sum(model.unctrl_PV_gen_P[bus, time] for bus in model.SDER_uncontr if bus == j)
                + sum(pgrid_var[bus, time] for bus in model.SGrid if bus == j)
                - sum(model.Load_P[bus, time] for bus in model.SLoadbuses if bus == j)
                - sum(ev_ch_p_var[bus, time] for bus in model.SEVbuses if bus == j)
                - sum(p_hp_var[bus, time] for bus in model.SHPbuses if bus == j)
            == sum(p_line_var[j, k, time] for k in model.Sdownstream[j])
            + sum(p_line_reverse_var[j, k, time] for k in model.Supstream[j])
            +sum(p_transformer_var[j, k, time] for k in model.Sdownstream_transformer[j])
            +sum(p_transformer_reverse_var[j, k, time] for k in model.Supstream_transformer[j])
        )

    constraint = Constraint(model.Sbuses, model.STimes, rule=active_power_balance)
    self.register_constraint(name_prefix, constraint)

def add_reactive_power_flow_bfm(self, qder_contr_var, q_line_var,q_line_reverse_var, q_transformer_var,q_transformer_reverse_var, qgrid_var, ev_q_var, name_prefix, q_hp_var=None):
    model = self.model

    def reactive_power_balance(model, j, time):
        return (0
            + sum(qder_contr_var[bus, time] for bus in model.SDER_contr if bus == j)
            + sum(model.unctrl_PV_gen_Q[bus, time] for bus in model.SDER_uncontr if bus == j)
            + sum(qgrid_var[bus, time] for bus in model.SGrid if bus == j)
            - sum(model.Load_Q[bus, time] for bus in model.SLoadbuses if bus == j)
            - sum(ev_q_var[bus, time] for bus in model.SEVbuses if bus == j)
            - sum(q_hp_var[bus, time] for bus in model.SHPbuses if bus == j)
            == sum(q_line_var[j, k, time] for k in model.Sdownstream[j])
            + sum(q_line_reverse_var[j, k, time] for k in model.Supstream[j])
            + sum(q_transformer_var[j, k, time] for k in model.Sdownstream_transformer[j])
            + sum(q_transformer_reverse_var[j, k, time] for k in model.Supstream_transformer[j])
        )

    constraint = Constraint(model.Sbuses, model.STimes, rule=reactive_power_balance)
    self.register_constraint(name_prefix, constraint)

def add_voltage_drop_bfm(self, line_set, line_reverse_set, voltage_var, p_line_var, p_reverse_line_par, q_line_var, q_reverse_line_par, current_line_var, curret_reverse_line_var, resistance_param, reactance_param, alpha_real, alpha_imag, name_prefix, name_reverse_prefix):
    model = self.model
    a_real = alpha_real
    a_imag = alpha_imag
    def voltage_drop_equation(model, i, j, time):
        r = resistance_param[i, j]
        x = reactance_param[i, j]
        z_ij_amplitude_square = (r**2 + x**2)
        aij_amplitude_square = (a_real[i, j]**2 + a_imag[i, j]**2)
        return (
            aij_amplitude_square*voltage_var[i, time] - voltage_var[j, time] ==
             2 * (a_real[i,j] * (r*p_line_var[i, j, time] + x * q_line_var[i, j, time]) - a_imag[i,j] * (r*q_line_var[i, j, time] + x * p_line_var[i, j, time])) 
             - z_ij_amplitude_square * current_line_var[i, j, time]
             )
    constraint = Constraint(line_set, model.STimes, rule=voltage_drop_equation)
    self.register_constraint(name_prefix, constraint)

    def voltage_drop_reverse_equation(model, i, j, time):
        key = (min(i, j), max(i, j))
        r = resistance_param[key]
        x = reactance_param[key]
        z_ij_amplitude_square = (r**2 + x**2)
        aij_amplitude_square = (a_real[key]**2 + a_imag[key]**2)
        return (
            aij_amplitude_square*voltage_var[i, time] - voltage_var[j, time] ==
             2 * (a_real[key] * (r*p_reverse_line_par[i, j, time] + x * q_reverse_line_par[i, j, time]) - a_imag[key] * (r*q_reverse_line_par[i, j, time] + x * p_reverse_line_par[i, j, time])) 
             - z_ij_amplitude_square * curret_reverse_line_var[i, j, time]
             )

    reverse_constraint = Constraint(line_reverse_set, model.STimes, rule=voltage_drop_reverse_equation)
    self.register_constraint(name_reverse_prefix, reverse_constraint)

def add_current_flow_bfm(self, line_set, line_reverse_set, p_line_var,p_reverse_line_par, q_line_var,q_reverse_line_par, current_var,curret_reverse_line_var, voltage_var, name_prefix, name_reverse_prefix):
    model = self.model

    def current_flow_equality(model, i, j, time):
        return (
            current_var[i, j, time] * voltage_var[i, time] ==
            p_line_var[i, j, time]**2 + q_line_var[i, j, time]**2
        )
    
    def current_flow_reverse_equality(model, i, j, time):
        return (
            curret_reverse_line_var[i, j, time] * voltage_var[i, time] ==
            p_reverse_line_par[i, j, time]**2 + q_reverse_line_par[i, j, time]**2
        )

    constraint = Constraint(line_set, model.STimes, rule=current_flow_equality)
    self.register_constraint(name_prefix, constraint)

    constraint = Constraint(line_reverse_set, model.STimes, rule=current_flow_reverse_equality)
    self.register_constraint(name_reverse_prefix, constraint)


def add_voltage_link_symmetric_constraint(self, line_set, voltage_var, p_line_var, p_reverse_line_par, q_line_var, q_reverse_line_par, resistance_param, reactance_param, alpha_real, alpha_imag, name_real_prefix, name_imag_prefix):
    model = self.model
    a_real = alpha_real
    a_imag = alpha_imag
    def voltage_link_symmetric_real(model, i, j, time):
        r = resistance_param[i, j]
        x = reactance_param[i, j]
        return (
            a_real[i,j] * voltage_var[i,time] - r * p_line_var[i,j,time] - x * q_line_var[i,j,time] == 
            a_real[i,j] * voltage_var[j,time] - r * p_reverse_line_par[j,i,time] - x * q_reverse_line_par[j,i,time] 
             )
    constraint = Constraint(line_set, model.STimes, rule=voltage_link_symmetric_real)
    self.register_constraint(name_real_prefix, constraint)

    def voltage_link_symmetric_imag(model, i, j, time):
        r = resistance_param[i, j]
        x = reactance_param[i, j]
        return (
            -a_imag[i,j] * voltage_var[i,time] - r * q_line_var[i,j,time] + x * p_line_var[i,j,time] == 
            a_imag[i,j] * voltage_var[j,time] + r * q_reverse_line_par[j,i,time] - x * p_reverse_line_par[j,i,time] 
             )

    reverse_constraint = Constraint(line_set, model.STimes, rule=voltage_link_symmetric_imag)
    self.register_constraint(name_imag_prefix, reverse_constraint)
