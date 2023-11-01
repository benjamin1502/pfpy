# File: emt.py
# Author: Claudio David Lopez

import csv
from pfsim import PowerFactorySim


FOLDER_NAME = ''
PROJECT_NAME = '2A4G'
STUDY_CASE_NAME = 'Study Case'
MONITORED_VARIABLES = {
    'G1.ElmSym': ['s:phi', 's:speed', 's:fe'],
    '*.ElmTerm': ['m:ul:A', 'm:ul:B', 'm:ul:C']
}

# activate project and study case
sim = PowerFactorySim(
    folder_name=FOLDER_NAME,
    project_name=PROJECT_NAME,
    study_case_name=STUDY_CASE_NAME)
# prepare EMT simulation
sim.prepare_dynamic_sim(
    monitored_variables=MONITORED_VARIABLES,
    sim_type='ins',
    start_time=0.0,
    step_size=0.0001,
    end_time=0.02)
# run EMT simulation
sim.run_dynamic_sim()
# retrieve line-to-line volages from one bus
t, ula = sim.get_dynamic_results(
            'Bus_20kV_1.ElmTerm', 'm:ul:A')
_, ulb = sim.get_dynamic_results(
            'Bus_20kV_1.ElmTerm', 'm:ul:B')
_, ulc = sim.get_dynamic_results(
            'Bus_20kV_1.ElmTerm', 'm:ul:C')
# store line-to-line volages in csv file
with open('res_emt.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['t', 'ula', 'ulb', 'ulc'])
    for row in zip(t, ula, ulb, ulc):
        csvwriter.writerow(row)
