from pyomo.environ import Param

def alpha_bfm_param(self, alpha_line_real_prefix, alpha_line_imag_prefix, alpha_transformer_real_prefix, alpha_transformer_imag_prefix):
    """
    Initialize voltage variables in the Pyomo model.
    """
    model = self.model
    System_Data_Lines=self.anc_Vars.System_Data_Lines
    
    def alpha_real_rule(model, sfrom,sto):
        return 1-System_Data_Lines.set_index(['FROM', 'TO']).loc[sfrom,sto]['X']*System_Data_Lines.set_index(['FROM', 'TO']).loc[sfrom,sto]['Y']/2

    real_Parm = Param(model.Slines, initialize=alpha_real_rule, mutable=True)
    self.register_parameter(alpha_line_real_prefix, real_Parm)
    
    def alpha_imag_rule(model, sfrom,sto):
        return System_Data_Lines.set_index(['FROM', 'TO']).loc[sfrom,sto]['R']*System_Data_Lines.set_index(['FROM', 'TO']).loc[sfrom,sto]['Y']/2
    imag_Parm = Param(model.Slines, initialize=alpha_imag_rule, mutable=True)
    self.register_parameter(alpha_line_imag_prefix, imag_Parm)

    def alpha_transformer_real_rule(model, sfrom,sto):
        return 1

    real_Parm = Param(model.STransformers, initialize=alpha_transformer_real_rule, mutable=True)
    self.register_parameter(alpha_transformer_real_prefix, real_Parm)
    
    def alpha_transformer_imag_rule(model, sfrom,sto):
        return 0
    imag_Parm = Param(model.STransformers, initialize=alpha_transformer_imag_rule, mutable=True)
    self.register_parameter(alpha_transformer_imag_prefix, imag_Parm)