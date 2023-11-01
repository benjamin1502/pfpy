# File: rms_sc.py
# Author: Claudio David Lopez

from pfsim import PowerFactorySim


FOLDER_NAME = ''
PROJECT_NAME = '2A4G'
STUDY_CASE_NAME = 'Study Case'
MONITORED_VARIABLES = {
    'G1.ElmSym': ['s:phi', 's:speed', 's:fe'],
    '*.ElmTerm': ['m:u']
}

# activate project and study case
sim = PowerFactorySim(
    folder_name=FOLDER_NAME,
    project_name=PROJECT_NAME, 
    study_case_name=STUDY_CASE_NAME)
# get all buses in network
buses = sim.app.GetCalcRelevantObjects('*.ElmTerm')
# create result dictionaries
t = {}
f = {}
for bus in buses:
    # create short circuit on every bus
    sim.create_short_circuit(
        target_name=bus.loc_name+'.ElmTerm',
        time=2.0,
        duration=0.15)
    # prepare RMS simulation
    sim.prepare_dynamic_sim(
        monitored_variables=MONITORED_VARIABLES)
    # run RMS simulation
    sim.run_dynamic_sim()
    # get and store generator response
    t[bus.loc_name], f[bus.loc_name] = \
        sim.get_dynamic_results('G1.ElmSym', 's:fe')
    # delete old short circuit before new one
    sim.delete_short_circuit()