from pyomo.environ import Param
import math

def initialize_ev_params(self, min_ch_prefix_name, max_ch_prefix_name, EV_init_SOC_prefix_name, EV_end_SOC_prefix_name, EV_min_SOC_prefix_name, EV_max_SOC_prefix_name, EV_Ene_Capa_prefix_name ):
    
    """
    Define and initialize EV-related parameters in the Pyomo model.
    """
    model=self.model
    System_Data_EV=self.anc_Vars.system_data_ev
    
    # Min-Max active charge power of inverter
    def ev_min_ch_rule(model, bus):
        return System_Data_EV.set_index('EV_node').loc[bus,'EV_Pmin_ch']
    ev_min_ch_param = Param(model.SEVbuses,initialize=ev_min_ch_rule ,mutable=True)
    self.register_parameter(min_ch_prefix_name, ev_min_ch_param)
    
    def ev_max_ch_rule(model, bus):
        return System_Data_EV.set_index('EV_node').loc[bus,'EV_Pmax_ch']
    ev_max_ch_param = Param(model.SEVbuses,initialize=ev_max_ch_rule ,mutable=True)
    self.register_parameter(max_ch_prefix_name, ev_max_ch_param)

    # EV initial and ending SOC
    def EV_SOC_ini_rule(model, sEV):
        return System_Data_EV.set_index('EV_node')['EV_EC'][sEV]*System_Data_EV.set_index('EV_node')['EV_SOC_ini'][sEV]/100
    EVinit_SOC = Param(model.SEVbuses, initialize=EV_SOC_ini_rule, mutable=True)
    self.register_parameter(EV_init_SOC_prefix_name, EVinit_SOC)
    
    def EV_SOC_end_rule(model, sEV):
        return System_Data_EV.set_index('EV_node')['EV_EC'][sEV]*System_Data_EV.set_index('EV_node')['EV_SOC_end'][sEV]/100
    EVend_SOC_param = Param(model.SEVbuses, initialize=EV_SOC_end_rule, mutable=True)
    self.register_parameter(EV_end_SOC_prefix_name, EVend_SOC_param)
    
    # Minimum and Maximum SOC 
    def EV_SOC_min_rule(model, sEV):
        return System_Data_EV.set_index('EV_node')['EV_EC'][sEV]*System_Data_EV.set_index('EV_node')['EV_SOC_min'][sEV]/100
    EV_SoC_min_pref_param = Param(model.SEVbuses, initialize=EV_SOC_min_rule, mutable=True)
    self.register_parameter(EV_min_SOC_prefix_name, EV_SoC_min_pref_param)
    
    def EV_SOC_max_rule(model, sEV):
        return System_Data_EV.set_index('EV_node')['EV_EC'][sEV]*System_Data_EV.set_index('EV_node')['EV_SOC_max'][sEV]/100
    EV_SoC_max_param = Param(model.SEVbuses, initialize=EV_SOC_max_rule, mutable=True)
    self.register_parameter(EV_max_SOC_prefix_name, EV_SoC_max_param)
    
    def EV_capacity_rule(model, sEV):
        return System_Data_EV.set_index('EV_node')['EV_EC'][sEV]
    EV_capacity_param = Param(model.SEVbuses, initialize=EV_capacity_rule, mutable=True)
    self.register_parameter(EV_Ene_Capa_prefix_name, EV_capacity_param)

