from pyomo.environ import Constraint, cos, sin


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
