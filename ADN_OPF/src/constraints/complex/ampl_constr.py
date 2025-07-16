from pyomo.environ import Constraint, cos, sin

def add_twoport_amplitude_constraint(self, x_var, y_var, amp_var,name_prefix,model_set):
    """
    Generic rule to constrxsain the amplitude of a 2D vector:
        amp^2 = x^2 + y^2
    Can be used for apparent power, current magnitude, velocity norm, etc.
    """

    model=self.model

    def current_amplitude_rule(model, k,t, time):
        return x_var[k,t,time]**2 + y_var[k,t,time]**2 == amp_var[k,t,time]**2

    constraint = Constraint(model_set,model.STimes, rule=current_amplitude_rule)
    self.register_constraint(name_prefix, constraint)

def add_oneport_amplitude_constraint(self, x_var, y_var, amp_var,name_prefix,model_set):
    """
    Generic rule to constrxsain the amplitude of a 2D vector:
        amp^2 = x^2 + y^2
    Can be used for apparent power, current magnitude, velocity norm, etc.
    """

    model=self.model

    def power_amplitude_rule(model, i, t):
        return x_var[i, t]**2 + y_var[i, t]**2 == amp_var[i, t]**2

    constraint = Constraint(model_set,model.STimes, rule=power_amplitude_rule)
    self.register_constraint(name_prefix, constraint)
    
    
