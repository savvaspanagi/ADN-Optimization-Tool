from pyomo.environ import Constraint, cos, sin

def add_building_thermodynamic_constraint(self, Tin, Te, Qhp, Tout, Qsol, Q_dynamic_prefix_name, Te_dynamic_prefix_name):
    
    """
    Adds the constraint for real line flow (active power) to the model.

    Parameters:
    - model: Pyomo model where the constraint will be added.
    - Y_bus_df: The admittance matrix (DataFrame).
    """
    model=self.model
    system_data_hp = self.anc_Vars.system_data_hp

    def Q_hp_dynamic(model, bus,  time):
        
        if time == max(model.STimes):
            return Constraint.Skip
        return (
             Qhp[bus,time] == (Tin[bus,time+1] - Tin[bus,time]) / (self.delta*60*60) * 
             system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['C_in'] / system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['fh'] - 
             (Te[bus,time] - Tin[bus,time]) / (system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['R_in_e'] / system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['fh']) -
             (Tout[bus,time]-Tin[bus,time]) / (system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['R_in_a'] * system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['fh']) -
             (system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['Ain'] * Qsol[bus,time]) / system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['fh']            
        )

    constraint = Constraint(model.SHPbuses,  model.STimes, rule=Q_hp_dynamic)
    self.register_constraint(Q_dynamic_prefix_name, constraint)

    def T_e_dynamic(model, bus,  time):
        
        if time == max(model.STimes):
            return Constraint.Skip
        # print(Te[bus,time+1])
        return (
             Te[bus,time+1] == Te[bus,time] +  (self.delta*60*60) * (
             (Tin[bus,time] - Te[bus,time]) / (system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['C_e']* system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['R_in_e']) + 
             (Tout[bus,time] - Te[bus,time]) / (system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['C_e'] * system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['R_in_e']) +
             ((1-system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['fh'])* Qhp[bus,time]) / system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['C_e'] +
             (system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['Ae'] * Qsol[bus,time]) / system_data_hp.set_index('HP_node').loc[bus,'RC_Parameters']['C_e']  
        )
        )
    
    constraint = Constraint(model.SHPbuses,  model.STimes, rule=T_e_dynamic)
    self.register_constraint(Te_dynamic_prefix_name, constraint)