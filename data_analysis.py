# File: data_analysis.py
# Author: Claudio David Lopez

import pandas as pd
import matplotlib.pyplot as plt

# load results from file
voltages = pd.DataFrame.from_csv(
    'res_prob_lf.csv', sep=',', index_col=None)

# show loaded results
print('Voltage magnitudes\n',
      voltages)

# calculate mean voltage at each bus
print('Mean voltage at each bus\n',
      voltages.mean(axis=0))

# calculate voltage standard deviation at each bus
print('\nStandard deviation of voltage\n',
      voltages.std(axis=0))

# generate statistical summary of voltages
print('\nStatistic summary of voltages\n',
      voltages.describe())

# find voltages higher than 1.03 p.u.
print('\nBuses with voltages higher than 1.03 p.u.\n',
      (voltages>1.03).any())

# create histograms for terminal voltages
voltages.hist(column=['Bus_230kV_4'], bins=50)
plt.show()
