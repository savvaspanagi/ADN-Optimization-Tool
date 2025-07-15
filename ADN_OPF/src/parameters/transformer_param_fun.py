from pyomo.environ import Param

def transformer_param(self, resist_prefix, react_prefix):
    """
    Initialize voltage variables in the Pyomo model.
    """
    model = self.model
    System_Data_Transformers=self.anc_Vars.System_Data_Transformers
    
    def Transformer_Resistance_rule(model, sfrom,sto):
        return System_Data_Transformers.set_index(['FROM', 'TO']).loc[sfrom,sto]['R']
    resistance_Parm = Param(model.STransformers, initialize=Transformer_Resistance_rule, mutable=True)
    self.register_parameter(resist_prefix, resistance_Parm)
    
    def Transformer_Reactance_rule(model, sfrom,sto):
        return System_Data_Transformers.set_index(['FROM', 'TO']).loc[sfrom,sto]['X']
    reactance_Parm = Param(model.STransformers, initialize=Transformer_Reactance_rule, mutable=True)
    self.register_parameter(react_prefix, reactance_Parm)
    