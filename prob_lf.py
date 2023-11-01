# File: prob_lf.py
# Author: Claudio David Lopez

import csv
from pfsim import MontecarloLoadFlow


FOLDER_NAME = ''
PROJECT_NAME = '2A4G'
STUDY_CASE_NAME = 'Study Case'

N_SAMPLES = 2500
STD_DEV = 0.1 # 0.1 = 10%

# activate project and study case
sim = MontecarloLoadFlow(
    folder_name=FOLDER_NAME,
    project_name=PROJECT_NAME,
    study_case_name=STUDY_CASE_NAME)
# create montecarlo load flow iterable object
mcldf = sim.monte_carlo_loadflow(N_SAMPLES, STD_DEV)
# create a csv file for storing results
with open('res_prob_lf.csv', 'w', newline='') as csvfile:
    # iterate over mcldf object to get voltage magnitudes
    for row_index, voltages in enumerate(mcldf):
        # write file header (bus names)
        if row_index == 0:
            csvwriter = csv.DictWriter(
                csvfile, voltages.keys())
            csvwriter.writeheader()
        # write file rows (voltage magnitudes)
        csvwriter.writerow(voltages)

