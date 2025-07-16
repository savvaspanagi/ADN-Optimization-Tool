from sets import *
from df import *
from plot import *
from variables import *
from parameters import *
from constraints import *
from pyomo.environ import *
from types import MethodType
from admittance_matrix import *
class Manager:
    def __init__(self, net, model=None):
        
        # Create the Pyomo model if not provided
        if model is None:
            self.model = ConcreteModel()
            # self.model.dual = Suffix(direction=Suffix.IMPORT)  # This saves the dual variables and gives us information about how the constraints affect the solution
        
        # If a model is provided, use it
        else:
            self.model = model # Pyomo model
        
        self.net = net # pandapower network dataframe
        # Dictionaries for problem formulation constraints,variables, sets and parameters
        self.constraint_registry = {}
        self.set_registry = {}
        self.parameter_registry = {}
        self.variable_registry = {}

        # In the AncillaryData a hard transformarion of problem from pandapower to df, compatible to add them
        # into in the optimization 
        self.anc_Vars = AdditionalData(self)

        self.plot_fun=plot_fun(self) # Plot functions initialization
        self.results=var_results_df(self) # Results functions initialization
        self.parameter_df = parameter_df(self) # Parameters functions initialization
        
        # Registering set functions 
        set_fun = [initialize_sets]
        for func in set_fun:
            setattr(self, func.__name__, MethodType(func, self))

        # Registering variable functions 
        variable_fun = [addTime, initialize_voltage_variables,initialize_voltage_square_variables, add_variable, initialize_der_variables, initialize_line_variables,initialize_line_square_variables, initialize_ev_variables]
        for func in variable_fun:
            setattr(self, func.__name__, MethodType(func, self))
        
        # Registering ev flexibility variable functions 
        constrain_fun = [initialize_ev_flexibility_variables]
        for func in constrain_fun:
            setattr(self, func.__name__, MethodType(func, self))

        # Registering hp and building variable functions 
        constrain_fun = [initialize_hp_variables, initialize_building_variables]
        for func in constrain_fun:
            setattr(self, func.__name__, MethodType(func, self))

        # Registering parameter functions 
        param_fun = [der_profile_param, initialize_ev_params,initialize_ev_char_params, line_param, load_profile_param, transformer_param, alpha_bfm_param]
        for func in param_fun:
            setattr(self, func.__name__, MethodType(func, self))

        # Registering heatpumps parameter functions 
        param_fun = [initialize_hp_params, enviroment_profile_param]
        for func in param_fun:
            setattr(self, func.__name__, MethodType(func, self))

        # Registering some more parameter functions for ev 
        param_fun = [initialize_ev_min_soc_timeseries]
        for func in param_fun:
            setattr(self, func.__name__, MethodType(func, self))

        # Registering ev constraint functions 
        constrain_fun = [add_ev_soc_constraint, add_ev_min_departure_soc_constraint, add_power_up_flex_ev_cons, add_power_up_flex_max_cons, add_power_down_flex_ev_cons, add_power_down_flex_min_cons, add_power_ch_dp_ev_cons, fix_ev_non_charging_times]
        for func in constrain_fun:
            setattr(self, func.__name__, MethodType(func, self))

        # Registering hp constraint functions 
        constrain_fun = [add_building_thermodynamic_constraint, add_HP_operation_constraint]
        for func in constrain_fun:
            setattr(self, func.__name__, MethodType(func, self))
        
        # Registering line constraint functions 
        constrain_fun = [add_real_current_flow_constraint, add_reactive_current_flow_constraint, add_line_flow_losses_constraint, add_twoport_amplitude_constraint,add_oneport_amplitude_constraint, add_line_flow_amplitude_losses_constraint]
        for func in constrain_fun:
            setattr(self, func.__name__, MethodType(func, self))

        # Registering power flow constraint functions 
        constrain_fun = [add_active_power_flow_constraint,add_reactive_power_flow_constraint, add_active_power_flex_flow_constraint, add_reactive_power_flex_flow_constraint]
        for func in constrain_fun:
            setattr(self, func.__name__, MethodType(func, self))
        
        # Registering distflow without shunt power flow constraint functions 
        constrain_fun = [add_active_power_flow_df_wos_constraint,add_reactive_power_flow_df_wos_constraint, add_voltage_power_flow_df_wos_constraint, add_brunch_current_flow_df_wos_equal_constraint, add_brunch_current_flow_df_wos_SOCP_constraint]
        for func in constrain_fun:
            setattr(self, func.__name__, MethodType(func, self))
        
        # Registering branchflow with shunt power flow constraint functions 
        constrain_fun = [add_active_power_flow_bfm,add_reactive_power_flow_bfm, add_voltage_drop_bfm, add_current_flow_bfm, add_voltage_link_symmetric_constraint]
        for func in constrain_fun:
            setattr(self, func.__name__, MethodType(func, self))
        
        

        # Registering flexibility plot functions 
        flex_plot_fun = [results_flexibility_plot]
        for func in flex_plot_fun:
            setattr(self, func.__name__, MethodType(func, self))



    def register_constraint(self, name, constraint):
        """
        Registers a constraint in the model and the constraint registry.

        Parameters:
        - name: Name of the constraint group.
        - constraint: Pyomo Constraint object.
        """
        setattr(self.model, name, constraint)
        self.constraint_registry[name] = constraint

    def register_set(self, name, set_obj):
        """
        Registers a set in the set registry.

        Parameters:
        - name: Name of the set.
        - set_obj: Pyomo Set object.
        """
        setattr(self.model, name, set_obj)
        self.set_registry[name] = set_obj

    def register_variable(self, name, variable):
        """
        Registers a variable in the model and the variable registry.

        Parameters:
        - name: Name of the variable group.
        - variable: Pyomo Variable object.
        """
        setattr(self.model, name, variable)
        self.variable_registry[name] = variable
    
    def register_parameter(self, name, parameter):
        """
        Registers a variable in the model and the variable registry.

        Parameters:
        - name: Name of the variable group.
        - variable: Pyomo Variable object.
        """
        setattr(self.model, name, parameter)
        self.parameter_registry[name] = parameter

    def list_constraints(self):
        """
        Lists all registered constraints.
        """
        return list(self.constraint_registry.keys())

    def show_constraints(self, constraint_name):
        """
        Displays constraints by group name.
        """
        if constraint_name in self.constraint_registry:
            constraint = self.constraint_registry[constraint_name]
            for index in constraint:
                print(f"{constraint_name}[{index}]: {constraint[index].expr}")
        else:
            print(f"Constraint group '{constraint_name}' does not exist.")

    def list_sets(self):
        """
        Lists all registered sets.
        """
        return list(self.set_registry.keys())

    def show_set(self, set_name):
        """
        Displays the elements of a specific set.
        """
        if set_name in self.set_registry:
            set_obj = self.set_registry[set_name]
            print(f"Set {set_name}: {list(set_obj)}")
        else:
            print(f"Set '{set_name}' does not exist.")

    def list_variables(self):
        """
        Lists all registered variables.
        """
        return list(self.variable_registry.keys())

    def show_variable(self, variable_name):
        """
        Displays details of a specific variable.
        """
        if variable_name in self.variable_registry:
            variable = self.variable_registry[variable_name]
            print(f"Variable {variable_name}:")
            for index in variable:
                print(f"  {index},Initial: {variable[index].value}, ub:{variable[index].ub} ,lb:{variable[index].lb}")
        else:
            print(f"Variable '{variable_name}' does not exist.")
    
    def list_parameters(self):
        """
        Lists all registered variables.
        """
        return list(self.parameter_registry.keys())

    def show_parameter(self, parameter_name):
        """
        Displays details of a specific variable.
        """
        if parameter_name in self.parameter_registry:
            parameter = self.parameter_registry[parameter_name]
            print(f"Variable {parameter_name}:")
            for index in parameter:
                print(f"  {index}: {parameter[index].value}")
        else:
            print(f"Variable '{parameter_name}' does not exist.")
