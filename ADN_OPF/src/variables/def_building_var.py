import math
from pyomo.environ import Var, NonNegativeReals

def initialize_building_variables(self, model_type, Qhp_name_prefix, Tin_name_prefix, min_temp_preference_param, max_temp_preference_param, Te_name_prefix=None):
    """
    Initialize Building variables in the Pyomo model.
    """
    model = self.model
    system_data_hp = self.anc_Vars.system_data_hp
    
    def Tin_bounds_rule(model, bus, time):
        return min_temp_preference_param[bus,time], max_temp_preference_param[bus,time]
    
    if model_type=="3R2C":
        Qhp = Var(model.SHPbuses, model.STimes, domain=NonNegativeReals)
        Tin = Var(model.SHPbuses, model.STimes, bounds=Tin_bounds_rule )
        Te = Var(model.SHPbuses, model.STimes)
        
        self.register_variable(Qhp_name_prefix, Qhp)
        self.register_variable(Tin_name_prefix, Tin)
        self.register_variable(Te_name_prefix, Te)
        
        for hp in model.SHPbuses:
            getattr(self.model, Tin_name_prefix)[hp, 0].fix(system_data_hp.set_index('HP_node').loc[hp,'Initialization']['T_in'])
        
        for hp in model.SHPbuses:
            getattr(self.model, Te_name_prefix)[hp, 0].fix(system_data_hp.set_index('HP_node').loc[hp,'Initialization']['T_e'])
        
        
    