import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class plot_fun:
    def __init__(self,manager):
        self.manager=manager
        # Initialize dataframes
        # self.System_Data_Lines = self.define_lines()
        # self.Basic_Active_Load_Profile = pd.DataFrame()
        # self.Basic_Reactive_Load_Profile = pd.DataFrame()
        return
    
    def result_df_plot(self, result, title=None, x_axes_label=None, y_axes_label=None, label=None):

        manager=self.manager
        timeframe=manager.timeframe
        time_interval=manager.time_interval
        time_labels = [f'{hour:02d}:{0:02d}' for hour in range(0,24,2)]  # 30-minute intervals (00:00, 00:30, ...)
        plt.figure(figsize=(6, 3))
        for i in result:
            plt.plot(result.loc[:,i].values, label=f'{i}')
        if title is not 'None':
            plt.title(title)
        if x_axes_label is not None:
            plt.xlabel(x_axes_label)
        if y_axes_label is not None: 
            plt.ylabel(y_axes_label)
        plt.xticks(range(0, int(timeframe/(time_interval/60)) ,4), time_labels*int(timeframe/24), rotation=90)    
        plt.tight_layout()  # Adjust layout for better readability
        if label=="Yes":
            plt.legend(loc='upper left', fontsize=8, title_fontsize=8,ncol=2)
        return
    
    def param_plot(self,results,title=None,x_axes=None,y_axes=None):
        
        manager=self.manager
        timeframe=manager.timeframe
        time_interval=manager.time_interval
        time_labels = [f'{hour:02d}:{0:02d}' for hour in range(0,24,2)]  # 30-minute intervals (00:00, 00:30, ...)
        plt.figure(figsize=(6, 3))
        for i in results:
            plt.plot(results.loc[:,i], label=f'{i}')
        if title is not None:
            plt.title(title)
        if x_axes is not None:
            plt.xlabel(x_axes)
        if y_axes is not None:
            plt.ylabel(y_axes)
        plt.xticks(range(0, int(timeframe/(time_interval/60)) ,4), time_labels*int(timeframe/24), rotation=90)    
        plt.tight_layout()  # Adjust layout for better readability
        plt.legend(loc='upper left', fontsize=8, title_fontsize=8,ncol=2)
        return
    
    def sum_param_plot(self,result,title=None,x_axes=None,y_axes=None):
        
        manager=self.manager
        timeframe=manager.timeframe
        time_interval=manager.time_interval
        time_labels = [f'{hour:02d}:{0:02d}' for hour in range(0,24,2)]  # 30-minute intervals (00:00, 00:30, ...)
        sload=manager.anc_Vars.system_data_load
        model=manager.model
        plt.figure(figsize=(6, 3))
        plt.plot(sum(result.loc[:,i].values  for i in result))
        if title is not None:
            plt.title(title)
        if x_axes is not None:
            plt.xlabel(x_axes)
        if y_axes is not None:
            plt.ylabel(y_axes)
        plt.xticks(range(0, int(timeframe/(time_interval/60)) ,4), time_labels*int(timeframe/24), rotation=90)    
        plt.tight_layout()  # Adjust layout for better readability
        # plt.legend(loc='upper left', fontsize=8, title='DER', title_fontsize=8,ncol=2)
        return
        
    
    