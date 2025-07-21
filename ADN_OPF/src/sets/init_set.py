from pyomo.environ import Set

def initialize_sets(self):
    """
    Initializes sets in the Pyomo model using the Constraintself.

    Parameters:
    - self: An instance of Constraintself.
    - net: The Pandapower network data.
    - time: The number of time steps.
    """
    net = self.net
    
    # Initialize sets in the pyomo model
    Sbuses = Set(initialize=self.anc_Vars.System_Data_Nodes['Nodes'])
    SGrid = Set(initialize=self.anc_Vars.System_Data_Grid['Grid_node'])
    SDER_contr = Set(initialize=self.anc_Vars.System_Data_DER[self.anc_Vars.System_Data_DER['Controllable']==True]['DER_node'])
    SDER_uncontr = Set(initialize=self.anc_Vars.System_Data_DER[self.anc_Vars.System_Data_DER['Controllable']==False]['DER_node'])
    # load_bus_series = net.load['bus']  # Your current bus Series
    # load_bus_counts = load_bus_series.groupby(load_bus_series).cumcount() + 1 # Count how many times each bus appears
    # unique_bus_ids = [f"{bus}.{count}" for bus, count in zip(load_bus_series, load_bus_counts)]
    # SLoadbuses = Set(initialize=unique_bus_ids)
    SLoadbuses = Set(initialize=net.load['bus'])
    Slines = Set(initialize=list(zip(self.anc_Vars.System_Data_Lines['FROM'], self.anc_Vars.System_Data_Lines['TO'])))
    STransformers = Set(initialize=list(zip(self.anc_Vars.System_Data_Transformers['FROM'], self.anc_Vars.System_Data_Transformers['TO'])))
    STimes = Set(initialize=list(range(int(self.timeframe*60/self.time_interval))))

    # Register sets in the self class for easy access
    self.register_set("Sbuses", Sbuses)
    self.register_set("SGrid", SGrid)
    self.register_set("SDER_contr", SDER_contr)
    self.register_set("SDER_uncontr", SDER_uncontr)
    self.register_set("SLoadbuses", SLoadbuses)
    self.register_set("Slines", Slines)
    self.register_set("STransformers", STransformers)
    self.register_set("STimes", STimes)
    
    System_Data_EV=self.anc_Vars.system_data_ev
    System_Data_EV_char=self.anc_Vars.system_data_ev_char
    System_Data_HP = self.anc_Vars.system_data_hp
    
    # max indices represent the maximum length of the 'departure' list in System_Data_EV_char
    max_indices=System_Data_EV_char['departure'].apply(len).max() if not System_Data_EV_char.empty else 0
    SDistance_ind = Set(initialize=range(max_indices))
    EV_nodes = System_Data_EV['EV_node'] if 'EV_node' in System_Data_EV else []
    SEVbuses = Set(initialize=EV_nodes if len(EV_nodes) > 0 else [])
    
    self.register_set("SEVbuses", SEVbuses)
    self.register_set("SDistance_ind", SDistance_ind)

    HP_nodes = System_Data_HP['HP_node'] if 'HP_node' in System_Data_HP else []
    SHPbuses = Set(initialize=HP_nodes if len(HP_nodes) > 0 else [])

    self.register_set("SHPbuses", SHPbuses)
    
    # Downstream: for each bus j, the set of k such that (j, k) is a branch
    def downstream_init(model, j):
        return [k for (from_bus, k) in model.Slines if from_bus == j]
    downstream = Set(self.model.Sbuses, initialize=downstream_init)
    self.register_set("Sdownstream", downstream)

    # Upstream: for each bus j, the set of i such that (i, j) is a branch
    def upstream_init(model, j):
        return [i for (i, to_bus) in model.Slines if to_bus == j]
    upstream = Set(self.model.Sbuses, initialize=upstream_init)
    self.register_set("Supstream", upstream)

    # Downstream: for each bus j, the set of k such that (j, k) is a branch
    def downstream_trafo_init(model, j):
        return [k for (from_bus, k) in model.STransformers if from_bus == j]
    downstream = Set(self.model.Sbuses, initialize=downstream_trafo_init)
    self.register_set("Sdownstream_transformer", downstream)

    # Upstream: for each bus j, the set of i such that (i, j) is a branch
    def upstream_trafo_init(model, j):
        return [i for (i, to_bus) in model.STransformers if to_bus == j]
    upstream = Set(self.model.Sbuses, initialize=upstream_trafo_init)
    self.register_set("Supstream_transformer", upstream)

    def reverse_lines_init(model):
        """Generate all (to, from) pairs that correspond to the reverse
        direction of every (from, to) pair already was in the model.Slines."""
        for from_bus, to_bus in model.Slines:
            yield (to_bus, from_bus)

    reserve_lines = Set(dimen=2, initialize=reverse_lines_init)
    self.register_set("Sreverse_lines", reserve_lines)

    def reverse_transformer_init(model):
        """Generate all (to, from) pairs that correspond to the reverse
        direction of every (from, to) pair already was in the model.Slines."""
        for from_bus, to_bus in model.STransformers:
            yield (to_bus, from_bus)

    reserve_transformer = Set(dimen=2, initialize=reverse_transformer_init)
    self.register_set("Sreverse_transformers", reserve_transformer)