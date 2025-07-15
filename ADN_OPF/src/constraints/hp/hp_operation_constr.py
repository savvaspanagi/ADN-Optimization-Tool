from pyomo.environ import Constraint, cos, sin
import numpy as np
def add_HP_operation_constraint(self, Tout_param, Qhp, php, qhp,  php_operation_prefix_name, qhp_operation_prefix_name):
    
    model=self.model
    system_data_hp = self.anc_Vars.system_data_hp

    def P_hp_operation_rule(model, bus,  time):
        
        if time == max(model.STimes):
            return Constraint.Skip
        T_rounded = round(float(Tout_param[bus, time]()))         
        COP = system_data_hp.set_index('HP_node').loc[bus, 'COP_curve'].set_index('Tout').loc[T_rounded, 'COP']
        return (
           php[bus,time] == (Qhp[bus,time]/1000)/COP/1000/self.anc_Vars.S_Base
        )

    constraint = Constraint(model.SHPbuses,  model.STimes, rule=P_hp_operation_rule)
    self.register_constraint(php_operation_prefix_name, constraint)

    def reactive_hp_operation_rule(model, bus,  time):
        
        if time == max(model.STimes):
            return Constraint.Skip
        q_type = system_data_hp.set_index('HP_node').loc[bus, 'Q_control']
        cosf=system_data_hp.set_index('HP_node').loc[bus,'costh_HP']

        if q_type=='constant_pf':
            phi_rad = np.arccos(system_data_hp.set_index('HP_node').loc[bus,'costh_HP'])
            return (
           qhp[bus,time] == php[bus,time]*np.tan(phi_rad)
            )

    constraint = Constraint(model.SHPbuses,  model.STimes, rule=reactive_hp_operation_rule)
    self.register_constraint(qhp_operation_prefix_name, constraint)