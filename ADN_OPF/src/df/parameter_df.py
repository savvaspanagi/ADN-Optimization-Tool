import pandas as pd
class parameter_df:
    def __init__(self,manager):
        self.manager=manager        
        # Initialize dataframes 
        # self.System_Data_Lines = self.define_lines()
        # self.Basic_Active_Load_Profile = pd.DataFrame()
        # self.Basic_Reactive_Load_Profile = pd.DataFrame()
        
        return  
    
    def list(self):
        """
        Returns a list of names of attributes that are pandas DataFrames.
        """
        df_list = [attr for attr in dir(self) 
                   if isinstance(getattr(self, attr), pd.DataFrame) and not attr.startswith("__")]
        return df_list
    
    def pyomo_par_to_dataframe(self, pyomo_var):
        """
        Converts a Pyomo variable into a pandas DataFrame.

        Parameters:
            pyomo_var: Pyomo variable, indexed by 1, 2, or 3 dimensions.

        Returns:
            pd.DataFrame: A DataFrame where:
                        - Rows are determined by the last index for 2D/3D variables.
                        - For 1D variables, it returns a single-column DataFrame.
        """
        data = {}
        last_index_set = set()

        # Check the number of dimensions of the Pyomo variable
        for index in pyomo_var:
            if not isinstance(index, tuple):
                # Handle single-parameter variables (e.g., model.p[1])
                index = (index,)  # Convert to a tuple for consistent processing

            *keys, last_index = index  # Unpack keys (first indices) and last index
            last_index_set.add(last_index)  # Collect unique last indices

            # Create a tuple for the column key (combination of first indices)
            column_key = tuple(keys)

            if column_key not in data:
                data[column_key] = []
            # Append the variable value
            data[column_key].append(pyomo_var[index].value)
        # Create a DataFrame from the dictionary
        df = pd.DataFrame(data)

        # Set the index (rows) based on unique values from the last dimension
        if len(last_index_set) > 1:
            # df.index = sorted(last_index_set)
            df.index.name = "Index"
        else:
            # If there's only one index, make it a single-column DataFrame
            df = df.rename(columns=lambda col: f"{'_'.join(map(str, col))}")
            df.index.name = "Index"

        # Rename columns to reflect multi-dimension keys
        if len(data.keys()) > 1:
            df.columns = [f"{'_'.join(map(str, col))}" for col in data.keys()]
        else:
            # If it's a single-column DataFrame, set a simple name
            df.columns = ["Value"]

        return df

    
    def wrapper_parameter_df(self):
        for i in self.manager.list_parameters():
            var = getattr(self.manager.model,i,None)
            df = self.pyomo_par_to_dataframe(var)
            setattr(self,i,df)

  