import pandas as pd
class var_results_df:
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
    
    def pyomo_var_to_dataframe(self,pyomo_var):
        """
        Converts a Pyomo variable into a pandas DataFrame.

        Parameters:
            pyomo_var: Pyomo variable, indexed by 2 or 3 dimensions.

        Returns:
            pd.DataFrame: A DataFrame where rows are determined by the last index,
                        and columns are determined by the first indices.
        """
        # Check the number of dimensions of the Pyomo variable
        data = {}
        last_index_set = set()

        for index in pyomo_var:
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
        
        # Set the last index (rows) based on unique values from the last dimension
        df.index = sorted(last_index_set)

        # Rename columns to reflect multi-dimension keys
        df.columns = [f"{'_'.join(map(str, col))}" for col in data.keys()]

        return df
    
    def wrapper_var_results(self):
        for i in self.manager.list_variables():
            var = getattr(self.manager.model,i,None)
            df = self.pyomo_var_to_dataframe(var)
            setattr(self,i,df)

  