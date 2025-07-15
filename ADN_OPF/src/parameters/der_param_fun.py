from pyomo.environ import Param

def der_profile_param(self,profiles, unctr_DER_active_prefix, unctr_DER_reactive_prefix, cntr_DER_active_prefix, cntr_DER_reactive_prefix):
    
    model=self.model    
    system_data_DER=self.anc_Vars.System_Data_DER
    
    def P_gen_rule(model, bus,  time):
        return system_data_DER.set_index('DER_node').loc[bus,'P_max']*profiles.loc[time,'PV_Rooftop']

    PV_gen_P = Param(model.SDER_uncontr,model.STimes, initialize=P_gen_rule, mutable=True)
    self.register_parameter(unctr_DER_active_prefix, PV_gen_P)

    def P_gen_cntr_rule(model, bus,  time):
        return system_data_DER.set_index('DER_node').loc[bus,'P_max']*profiles.loc[time,'PV_Rooftop']

    PV_gen_P = Param(model.SDER_contr,model.STimes, initialize=P_gen_cntr_rule, mutable=True)
    self.register_parameter(cntr_DER_active_prefix, PV_gen_P)
    
    def Q_gen_rule(model, bus,  time):
        return system_data_DER.set_index('DER_node').loc[bus,'Q_max']*profiles.loc[time,'PV_Rooftop']

    PV_gen_Q = Param(model.SDER_uncontr,model.STimes, initialize=Q_gen_rule, mutable=True)
    self.register_parameter(unctr_DER_reactive_prefix, PV_gen_Q) 

    def Q_gen_cntrl_rule(model, bus,  time):
        return system_data_DER.set_index('DER_node').loc[bus,'Q_max']*profiles.loc[time,'PV_Rooftop']

    PV_gen_Q = Param(model.SDER_contr,model.STimes, initialize=Q_gen_cntrl_rule, mutable=True)
    self.register_parameter(cntr_DER_reactive_prefix, PV_gen_Q) 




