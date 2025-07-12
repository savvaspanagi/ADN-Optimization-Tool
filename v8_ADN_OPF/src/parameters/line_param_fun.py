from pyomo.environ import Param

def line_param(self, Y_bus_df, resist_prefix, react_prefix, adm_real_prefix, adm_img_prefix):
    """
    Initialize voltage variables in the Pyomo model.
    """
    model = self.model
    System_Data_Lines=self.anc_Vars.System_Data_Lines
    
    def Line_Resistance_rule(model, sfrom,sto):
        return System_Data_Lines.set_index(['FROM', 'TO']).loc[sfrom,sto]['R']

    resistance_Parm = Param(model.Slines, initialize=Line_Resistance_rule, mutable=True)
    self.register_parameter(resist_prefix, resistance_Parm)
    
    def Line_Reactance_rule(model, sfrom,sto):
        return System_Data_Lines.set_index(['FROM', 'TO']).loc[sfrom,sto]['X']
    reactance_Parm = Param(model.Slines, initialize=Line_Reactance_rule, mutable=True)
    self.register_parameter(react_prefix, reactance_Parm)


    admitt_mat_Parm_real = Param(model.Sbuses, model.Sbuses, initialize=Y_bus_df.stack().map(lambda x: x.real).to_dict(), mutable=True)
    admitt_mat_Parm_imag = Param(model.Sbuses, model.Sbuses, initialize=Y_bus_df.stack().map(lambda x: x.imag).to_dict(), mutable=True)
    self.register_parameter(adm_real_prefix, admitt_mat_Parm_real)
    self.register_parameter(adm_img_prefix, admitt_mat_Parm_imag)
    