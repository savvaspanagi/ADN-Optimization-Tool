from pyomo.environ import Constraint, cos, sin

"""
Computation of Active and Reactive Current Flow (I_ij) between two buses i and j

Given:
- Line admittance: Y_ij = G + jB
- Voltages: V_i = |V_i| ∠ θ_i,   V_j = |V_j| ∠ θ_j

The complex current from bus i to bus j is:
    I_ij = (G + jB) * (|V_i| * e^{jθ_i} - |V_j| * e^{jθ_j})

Expanding into real and imaginary parts:

Active current (real part):
    I_ij_active = G*(|V_i| * cos(θ_i) - |V_j| * cos(θ_j))
                - B*(|V_i| * sin(θ_i) - |V_j| * sin(θ_j))

Reactive current (imaginary part):
    I_ij_reactive = G*(|V_i| * sin(θ_i) - |V_j| * sin(θ_j))
                  + B*(|V_i| * cos(θ_i) - |V_j| * cos(θ_j))
"""


def add_real_current_flow_constraint(self, current_flow_constr_name_prefix, active_curr_var, voltage_var, phase_angle_var):
    """
    Adds the constraint for real line flow (active power) to the model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    - Y_bus_df: The admittance matrix (DataFrame).
    """
    model=self.model
    
    def real_current_flow_rule(model, k, t,  time):
        return (
            active_curr_var[k, t,  time] ==
            (voltage_var[k,  time] * cos(phase_angle_var[k,  time])
             - voltage_var[t,  time] * cos(phase_angle_var[t,  time])) * model.admitt_mat_Parm_real[k, t]
            - (voltage_var[k,  time] * sin(phase_angle_var[k,  time])
               - voltage_var[t,  time] * sin(phase_angle_var[t,  time])) * model.admitt_mat_Parm_imag[k, t]
        )

    constraint = Constraint(model.Slines,  model.STimes, rule=real_current_flow_rule)
    self.register_constraint(current_flow_constr_name_prefix, constraint)

def add_reactive_current_flow_constraint(self, reactive_flow_constr_name_prefix, reactive_curr_var, voltage_var, phase_angle_var):
    """
    Adds the constraint for reactive line flow to the model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    - Y_bus_df: The admittance matrix (DataFrame).
    """
    model=self.model
    def reactive_line_flow_rule(model, k, t,  time):
        return (
            reactive_curr_var[k, t,  time] ==
            (voltage_var[k,  time] * sin(phase_angle_var[k,  time])
             - voltage_var[t,  time] * sin(phase_angle_var[t,  time])) * model.admitt_mat_Parm_real[k, t]
            + (voltage_var[k,  time] * cos(phase_angle_var[k,  time])
               - voltage_var[t,  time] * cos(phase_angle_var[t,  time])) * model.admitt_mat_Parm_imag[k, t]
        )
    
    constraint = Constraint(model.Slines,  model.STimes, rule=reactive_line_flow_rule)
    self.register_constraint(reactive_flow_constr_name_prefix, constraint)
