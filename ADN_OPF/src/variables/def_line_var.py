import math
from pyomo.environ import Var, NonNegativeReals

def initialize_line_variables(self, line_set, line_curr_name_prefix=None, line_rea_curr_name_prefix=None, line_act_curr_name_prefix=None, line_losses_name_prefix=None):
    """
    Initialize line-related variables in the Pyomo model.
    """
    model = self.model
    system_data_lines=self.anc_Vars.System_Data_Lines

    def Line_Curr_bounds_rule(model, sfrom, sto, time):
        line_data = system_data_lines.set_index(['FROM', 'TO'])
        imax = line_data.loc[(sfrom, sto), 'Imax']
        return -1 * imax, imax

    if line_curr_name_prefix is not None:
        Line_curr = Var(line_set, model.STimes, within=NonNegativeReals, bounds=Line_Curr_bounds_rule)
        self.register_variable(line_curr_name_prefix, Line_curr)

    if line_rea_curr_name_prefix is not None:
        Line_rea_curr = Var(line_set, model.STimes)
        self.register_variable(line_rea_curr_name_prefix, Line_rea_curr)

    if line_act_curr_name_prefix is not None:
        Line_act_curr = Var(line_set, model.STimes)
        self.register_variable(line_act_curr_name_prefix, Line_act_curr)

    if line_losses_name_prefix is not None:
        Line_losses = Var(line_set, model.STimes, within=NonNegativeReals, initialize=0)
        self.register_variable(line_losses_name_prefix, Line_losses)

def initialize_line_square_variables(self, line_set, line_curr_name_prefix=None):
    """
    Initialize line-related variables in the Pyomo model.
    """
    model = self.model
    system_data_lines=self.anc_Vars.System_Data_Lines

    def Line_Curr_bounds_rule(model, sfrom, sto, time):
        line_data = system_data_lines.set_index(['FROM', 'TO'])
        key = (min(sfrom, sto), max(sfrom, sto))
        imax = line_data.loc[key, 'Imax']
        return 0, imax**2

    if line_curr_name_prefix is not None:
        Line_curr = Var(line_set, model.STimes, within=NonNegativeReals, bounds=Line_Curr_bounds_rule)
        self.register_variable(line_curr_name_prefix, Line_curr)
