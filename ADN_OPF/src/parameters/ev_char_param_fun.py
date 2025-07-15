from pyomo.environ import Param
import math

def initialize_ev_char_params(self, ev_arrival_prefix_name, ev_departure_prefix_name, ev_distance_prefix_name, EV_SoC_min_departure_prefix_name, ev_trip_energy_needs_prefix_name, ev_availability_prefix_name):
    
    """
    Define and initialize EV-related parameters in the Pyomo model.
    """
    model=self.model
    System_Data_EV_char=self.anc_Vars.system_data_ev_char
    System_Data_EV=self.anc_Vars.system_data_ev

    ## Arrival Time for each EV 
    def ev_arrival_time_rule(model, bus,ind):
        len_arrival=len(System_Data_EV_char.set_index('EV_node').loc[bus,"arrival"])
        if ind<=(len_arrival-1):
            return System_Data_EV_char.set_index('EV_node').loc[bus,"arrival"][ind]
        else:
            return -1
    ev_arrival_param = Param(model.SEVbuses,model.SDistance_ind,initialize=ev_arrival_time_rule ,mutable=True)
    self.register_parameter(ev_arrival_prefix_name, ev_arrival_param)
    
    ## Departure Time for each EV 
    def ev_departure_time_rule(model, bus,ind):
        len_departure=len(System_Data_EV_char.set_index('EV_node').loc[bus,"departure"])
        if ind<=(len_departure-1):
            return System_Data_EV_char.set_index('EV_node').loc[bus,'departure'][ind]
        else:
            return -1
    ev_departure_param = Param(model.SEVbuses,model.SDistance_ind,initialize=ev_departure_time_rule ,mutable=True)
    self.register_parameter(ev_departure_prefix_name, ev_departure_param)
    
    ## Distance Travel for each EV 
    def ev_dist_rule(model, bus, ind):
        len_distance=len(System_Data_EV_char.set_index('EV_node').loc[bus,"distance"])
        if ind<=(len_distance-1):
            return System_Data_EV_char.set_index('EV_node').loc[bus,'distance'][ind]
        else:
            return -1
    ev_distance_param = Param(model.SEVbuses,model.SDistance_ind, initialize=ev_dist_rule ,mutable=True)
    self.register_parameter(ev_distance_prefix_name, ev_distance_param)
    
    ## Minumum departure SOC in pu for each EV 
    def EV_SOC_min_departure_rule(model, sEV,ind):
        len_departure=len(System_Data_EV_char.set_index('EV_node').loc[sEV,"departure"])
        if ind<=(len_departure-1):
            return System_Data_EV.set_index('EV_node')['EV_EC'][sEV]*System_Data_EV_char.set_index('EV_node').loc[sEV,'Min_SOC_Before_Departure(%)'][ind]/100
        else:
            return -1    
    EV_SoC_min_departure_param = Param(model.SEVbuses,model.SDistance_ind, initialize=EV_SOC_min_departure_rule, mutable=True)
    self.register_parameter(EV_SoC_min_departure_prefix_name, EV_SoC_min_departure_param)
    
    ## Trip energy needs
    def EV_trip_energy_need_rule(model, sEV,ind):
        len_trip=len(System_Data_EV_char.set_index('EV_node').loc[sEV,"trip_energy_needs"])
        if ind<=(len_trip-1):
            return System_Data_EV_char.set_index('EV_node').loc[sEV,'trip_energy_needs'][ind]
        else:
            return -1    
    EV_energy_drive_cons_param = Param(model.SEVbuses,model.SDistance_ind, initialize=EV_trip_energy_need_rule, mutable=True)
    self.register_parameter(ev_trip_energy_needs_prefix_name, EV_energy_drive_cons_param)
    
    # The times that EV is not located at the charging point charge and discharge power was equal to zero
    def ev_available_rule(model, i, time):
        condition_satisfied=any(dep <= time < arr for dep, arr in zip(System_Data_EV_char.set_index('EV_node')['departure'][i], System_Data_EV_char.set_index('EV_node')['arrival'][i]))
        if condition_satisfied:
            return 0
        else:
            return 1
    EV_available_param = Param(model.SEVbuses,model.STimes, initialize=ev_available_rule, mutable=True)
    self.register_parameter(ev_availability_prefix_name, EV_available_param)