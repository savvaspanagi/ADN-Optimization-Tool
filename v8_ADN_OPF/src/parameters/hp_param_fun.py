from pyomo.environ import Param
import math

def initialize_hp_params(self, min_power_prefix_name, max_power_prefix_name, min_temp_preference_prefix_name, max_temp_preference_prefix_name):
    
    """
    Define and initialize EV-related parameters in the Pyomo model.
    """
    model=self.model
    System_Data_HP=self.anc_Vars.system_data_hp
    
    # Min-Max power of HP inverter
    def hp_min_power_rule(model, bus):
        return System_Data_HP.set_index('HP_node').loc[bus,'P_min']
    hp_min_power = Param(model.SHPbuses,initialize=hp_min_power_rule ,mutable=True)
    self.register_parameter(min_power_prefix_name, hp_min_power)

    def hp_max_power_rule(model, bus):
        return System_Data_HP.set_index('HP_node').loc[bus,'P_max']
    hp_max_power = Param(model.SHPbuses,initialize=hp_max_power_rule ,mutable=True)
    self.register_parameter(max_power_prefix_name, hp_max_power)

    # Temp Preference power of HP inverter
    def temp_min_preference_rule(model, bus, time):
        return System_Data_HP.set_index('HP_node').loc[bus,'temp_preference'].loc[time, 'Tmin']
    temp_min_preference = Param(model.SHPbuses, model.STimes, initialize=temp_min_preference_rule ,mutable=True)
    self.register_parameter(min_temp_preference_prefix_name, temp_min_preference)

    def temp_max_preference_rule(model, bus, time):
        return System_Data_HP.set_index('HP_node').loc[bus,'temp_preference'].loc[time, 'Tmax']
    temp_max_preference = Param(model.SHPbuses, model.STimes, initialize=temp_max_preference_rule ,mutable=True)
    self.register_parameter(max_temp_preference_prefix_name, temp_max_preference)

    


    


    
    

