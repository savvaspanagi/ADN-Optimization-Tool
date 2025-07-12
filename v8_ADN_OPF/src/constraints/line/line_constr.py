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


def add_real_line_flow_constraint(self, line_flow_con_name_prefix, active_curr, voltage, phase_angle):
    """
    Adds the constraint for real line flow (active power) to the model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    - Y_bus_df: The admittance matrix (DataFrame).
    """
    model=self.model
    
    def real_line_flow_rule(model, k, t,  time):
        return (
            active_curr[k, t,  time] ==
            (voltage[k,  time] * cos(phase_angle[k,  time])
             - voltage[t,  time] * cos(phase_angle[t,  time])) * model.admitt_mat_Parm_real[k, t]
            - (voltage[k,  time] * sin(phase_angle[k,  time])
               - voltage[t,  time] * sin(phase_angle[t,  time])) * model.admitt_mat_Parm_imag[k, t]
        )

    constraint = Constraint(model.Slines,  model.STimes, rule=real_line_flow_rule)
    self.register_constraint(line_flow_con_name_prefix, constraint)

def add_reactive_line_flow_constraint(self, line_flow_con_name_prefix, reactive_curr, voltage, phase_angle):
    """
    Adds the constraint for reactive line flow to the model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    - Y_bus_df: The admittance matrix (DataFrame).
    """
    model=self.model
    def reactive_line_flow_rule(model, k, t,  time):
        return (
            reactive_curr[k, t,  time] ==
            (voltage[k,  time] * sin(phase_angle[k,  time])
             - voltage[t,  time] * sin(phase_angle[t,  time])) * model.admitt_mat_Parm_real[k, t]
            + (voltage[k,  time] * cos(phase_angle[k,  time])
               - voltage[t,  time] * cos(phase_angle[t,  time])) * model.admitt_mat_Parm_imag[k, t]
        )
    
    constraint = Constraint(model.Slines,  model.STimes, rule=reactive_line_flow_rule)
    self.register_constraint(line_flow_con_name_prefix, constraint)
    
def add_line_flow_constraint(self, line_flow_con_name_prefix, current, active_curr, reactive_curr):
    """
    Adds the constraint to calculate the magnitude of the line current to the model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    """
    model=self.model
    
    def line_flow_rule(model, k, t,  time):
        return (
            current[k, t,  time] ** 2 ==
            active_curr[k, t,  time] **
            2 + reactive_curr[k, t,  time] ** 2
        )

    constraint = Constraint(model.Slines,  model.STimes, rule=line_flow_rule)
    self.register_constraint(line_flow_con_name_prefix, constraint)
    

def add_line_flow_losses_constraint(self, current, line_flow_losses_con_name_prefix):
    """
    Adds the constraint to calculate active power losses for each line to the model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    """
    model=self.model
    def line_flow_losses_rule(model, k, t,  time):
        return (
            model.Line_losses[k, t,  time] ==
            current[k, t,  time] ** 2 * model.resistance_Parm[k, t]
        )

    constraint = Constraint(model.Slines,  model.STimes, rule=line_flow_losses_rule)
    self.register_constraint(line_flow_losses_con_name_prefix, constraint)

def add_line_flow_amplitude_losses_constraint(self, line_set, current_var, losses_var, line_flow_losses_con_name_prefix):
    """
    Adds the constraint to calculate active power losses for each line to the model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    """
    model=self.model
    def line_flow_losses_rule(model, k, t,  time):
        key = (min(k, t), max(k, t))
        return (
            losses_var[k, t,  time] ==
            current_var[k, t,  time] * model.resistance_Parm[key]
        )

    constraint = Constraint(line_set,  model.STimes, rule=line_flow_losses_rule)
    self.register_constraint(line_flow_losses_con_name_prefix, constraint)
