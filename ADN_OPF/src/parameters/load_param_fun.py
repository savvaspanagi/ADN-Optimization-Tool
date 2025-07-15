from pyomo.environ import Param

def load_profile_param(self, profiles, load_p_name_prefix, load_q_name_prefix):

    model = self.model
    net=self.net
    system_data_load=self.anc_Vars.system_data_load
    
    def P_Load_rule(model, bus,  time):
        return system_data_load.set_index('Bus').loc[bus,'Active_Power']*profiles.loc[time,'Load_Profile']

    Load_P = Param(model.SLoadbuses,model.STimes, initialize=P_Load_rule, mutable=True)
    self.register_parameter(load_p_name_prefix, Load_P)
    
    def Q_Load_rule(model, bus,  time):
        return system_data_load.set_index('Bus').loc[bus,'Reactive_Power']*profiles.loc[time,'Load_Profile']

    Load_Q = Param(model.SLoadbuses,model.STimes, initialize=Q_Load_rule, mutable=True)
    self.register_parameter(load_q_name_prefix, Load_Q)
