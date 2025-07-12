import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def results_flexibility_plot(self,flex_up_result,flex_down_result,title=None,x_axes=None,y_axes=None,zero_axes=None , shading=None):

        timeframe=self.timeframe
        time_interval=self.time_interval
        time_labels = [f'{hour:02d}:{0:02d}' for hour in range(0,24,2)]  # 30-minute intervals (00:00, 00:30, ...)
        plt.figure(figsize=(6, 3))
        if zero_axes==None:
            plt.plot(flex_up_result, label="Upward Flexibility")
            plt.plot(flex_down_result, label="Downward Flexibility")
        elif shading=="Yes":
            plt.plot(flex_up_result, label="Upward Flexibility")
            plt.plot(flex_down_result, label="Downward Flexibility")
            plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
            # plt.fill_between(x, flex_up_result.values, 0, where=(flex_up_result.values >= 0), color='blue', alpha=0.5, label='Upward Flexibility')
            # plt.fill_between(x, flex_down_result.values, 0, where=(np.array(flex_down_result) <= 0), color='red', alpha=0.5, label='Downward Flexibility')
        if zero_axes=="Yes":
            plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
        if title is not None:
            plt.title(title)
        if x_axes is not None:
            plt.xlabel(x_axes)
        if y_axes is not None:
            plt.ylabel(y_axes)
        plt.xticks(range(0, int(timeframe/(time_interval/60)) ,4), time_labels*int(timeframe/24), rotation=90)    
        plt.tight_layout()  # Adjust layout for better readability
        plt.legend(loc='upper left', fontsize=8, title_fontsize=8,ncol=1)
        return