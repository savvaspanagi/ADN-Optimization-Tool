from pyomo.environ import Constraint, cos, sin

def add_amplitude_constraint_rule(self, x_var, y_var, amp_var,name_prefix):
    """
    Generic rule to constrain the amplitude of a 2D vector:
        amp^2 = x^2 + y^2
    Can be used for apparent power, current magnitude, velocity norm, etc.
    """

    model=self.model

    def amplitude_rule(model, i, t):
        return x_var[i, t]**2 + y_var[i, t]**2 == amp_var[i, t]**2

    constraint = Constraint(model.SGrid,model.STimes, rule=amplitude_rule)
    self.register_constraint(name_prefix, constraint)
    
    
