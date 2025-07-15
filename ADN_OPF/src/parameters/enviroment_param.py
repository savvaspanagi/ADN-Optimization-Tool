from pyomo.environ import Param

def enviroment_profile_param(self, data, outdoor_temeprature_name_prefix, solar_irradiance_name_prefix):

    model = self.model
        
    def outdoor_temperature_rule(model, bus,  time):
        return data['Tout'].iloc[time]

    outdoor_temp = Param(model.SHPbuses,model.STimes, initialize=outdoor_temperature_rule, mutable=True)
    self.register_parameter(outdoor_temeprature_name_prefix, outdoor_temp)
    
    def solar_irradiance_rule(model, bus,  time):
        return data['Tout'].iloc[time]

    solar_irradiance = Param(model.SHPbuses,model.STimes, initialize=solar_irradiance_rule, mutable=True)
    self.register_parameter(solar_irradiance_name_prefix, solar_irradiance)
