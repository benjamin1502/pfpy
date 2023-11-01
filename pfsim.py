# File: pfsim.py
# Author: Claudio David Lopez

import sys
sys.path.append(
    r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.11')
import powerfactory as pf

import datetime
import random
import os
import time
import warnings
from math import sqrt, cos, log, pi


def print_progress(current, total, start_time):
    """
    Print progress in percent and elapsed simulation
    time
    """
    # calculate progress
    progress = str(round(100*current/total, 1))
    # calculate elapsed time and convert to h:m:s format
    elapsed_time = str(datetime.timedelta(
        seconds=round(time.time()-start_time)))
    # create string with the progress/time message for printing
    message = '\rSimulation progress: ' +  progress + \
        ' %    Elapsed time: ' + elapsed_time + ' [h:m:s]'
    # print message
    sys.stdout.write(message)
    sys.stdout.flush()
    # print empty line at the end of simulation
    if current == total:
        print()


class PowerFactorySim(object):
    def __init__(self, folder_name='', project_name='Project',
                 study_case_name='Study Case'):
        # start PowerFactory
        self.app = pf.GetApplication()
        # activate project
        self.project = self.app.ActivateProject(
            os.path.join(folder_name, project_name))
        # activate study case
        study_case_folder = self.app.GetProjectFolder('study')
        study_case = study_case_folder.GetContents(
            study_case_name+'.IntCase')[0]
        self.study_case = study_case[0]
        self.study_case.Activate

    def prepare_loadflow(self, ldf_mode='balanced'):
        # translate load flow mode keyword to its int equivalent
        modes = {'balanced': 0, 'unbalanced': 1, 'dc': 2}
        # retrieve load-flow object
        self.ldf = self.app.GetFromStudyCase('ComLdf')
        # set load flow mode
        self.ldf.iopt_net = modes[ldf_mode]

    def run_loadflow(self):
        return bool(self.ldf.Execute())

    def get_bus_voltages(self):
        voltages = {}
        # collect all bus elements
        buses = self.app.GetCalcRelevantObjects('*.ElmTerm')
        # store voltage of each bus in a dictionary
        for bus in buses:
            voltages[bus.loc_name] = bus.GetAttribute('m:u')

        return voltages

    def prepare_dynamic_sim(self, monitored_variables,
                            sim_type='rms', start_time=0.0,
                            step_size=0.01, end_time=10.0):
        # get result file
        self.res = self.app.GetFromStudyCase('*.ElmRes')
        # select results variables to monitor
        for elm_name, var_names in monitored_variables.items():
            # get all network elements that match 'elm_name'
            elements = self.app.GetCalcRelevantObjects(elm_name)
            # select variables to monitor for each element
            for element in elements:
                self.res.AddVars(element, *var_names)
        # retrieve initial conditions and time domain sim. objects
        self.inc = self.app.GetFromStudyCase('ComInc')
        self.sim = self.app.GetFromStudyCase('ComSim')
        # set simulation type: 'rms' or 'ins' (for EMT)
        self.inc.iopt_sim = sim_type
        # set start time, step size and end time
        self.inc.tstart = start_time
        self.inc.dtgrd = step_size
        self.sim.tstop = end_time
        # set initial conditions
        self.inc.Execute()

    def run_dynamic_sim(self):
        return bool(self.sim.Execute())

    def get_dynamic_results(self, elm_name, var_name):
        # get network element of interest
        element = self.app.GetCalcRelevantObjects(elm_name)[0]
        # load results from file
        self.app.ResLoadData(self.res)
        # find colum in results file that holds result of interest
        col_index = self.app.ResGetIndex(
            self.res, element, var_name)
        # get number of rows (points in time) in the result file
        n_rows = self.app.ResGetValueCount(self.res, 0)
        # read results and time and store them in lists
        time = []
        var_values = []
        for i in range(n_rows):
            time.append(self.app.ResGetData(self.res, i, -1)[1])
            var_values.append(
                self.app.ResGetData(self.res, i, col_index)[1])

        return time, var_values

    def get_all_loads_pq(self):
        # collect all load elements
        loads = self.app.GetCalcRelevantObjects('*.ElmLod')
        # store active and reactive load values in dictionary
        p_load = {}
        q_load = {}
        for load in loads:
            p_load[load.loc_name] = load.plini
            q_load[load.loc_name] = load.qlini

        return p_load, q_load

    def set_all_loads_pq(self, p_load, q_load):
        # collect all load elements
        loads = self.app.GetCalcRelevantObjects('*.ElmLod')
        # set active and reactive load values
        for load in loads:
            load.plini = p_load[load.loc_name]
            load.qlini = q_load[load.loc_name]

    def toggle_out_of_service(self, elm_name):
        # collect all elements that match elm_name
        elms = self.app.GetCalcRelevantObjects(elm_name)
        # if elm is out of service, switch to in service, else,
        # switch to out of service
        for elm in elms:
            elm.outserv = 1 - elm.outserv

    def toggle_switches(self, elm_name):
        # collect all elements that match elm_name
        elms = self.app.GetCalcRelevantObjects(elm_name)
        # collect all switches
        sws = self.app.GetCalcRelevantObjects('*.StaSwitch')
        # find switches corresponding to each elm and toggle them
        for elm in elms:
            cubs = elm.GetCubicle(0) + elm.GetCubicle(1)
            for sw in sws:
                if sw.fold_id in cubs:
                    sw.on_off = 1 - sw.on_off

    def create_short_circuit(self, target_name, time,
                             duration=None, name='sc'):
        # get element where the  short circuit will be applied
        target = self.app.GetCalcRelevantObjects(target_name)[0]
        # get the events folder from active study case
        evt_folder = self.app.GetFromStudyCase('IntEVt')
        # create an empty event of type EvtShc (short circuit)
        evt_folder.CreateObject('EvtShc', name)
        # get the newly created event
        sc = evt_folder.GetContents(name+'.EvtShc')[0][0]
        # set time, target and type of short circuit (3-phase)
        sc.time = time
        sc.p_target = target
        sc.i_shc = 0
        # set clearing event if required
        if duration is not None:
            # create an empty event of type EvtShc (short circuit)
            evt_folder.CreateObject('EvtShc', name+'_clear')
            # get the newly created event
            scc = evt_folder.GetContents(
                name+'_clear'+'.EvtShc')[0][0]
            # set time, target and type of event (clearing)
            scc.time = time + duration
            scc.p_target = target
            scc.i_shc = 4

    def delete_short_circuit(self, name='sc'):
        # get the events folder from active study case
        evt_folder = self.app.GetFromStudyCase('IntEVt')
        # find the short circuit and clear event to delete
        sc = evt_folder.GetContents(name+'.EvtShc')[0]
        scc = evt_folder.GetContents(name+'_clear'+'.EvtShc')[0]
        # delete short circuit and clear events if they exist
        if sc:
            sc[0].Delete()
        if scc:
            scc[0].Delete()


class MontecarloLoadFlow(PowerFactorySim):
    def gen_normal_loads_pq(self, p_total, q_total,
                            p_base, q_base, std_dev=0.1):
        # generate 2 random numbers from uniform distribution
        rand1 = random.uniform(0, 1)
        rand2 = random.uniform(0, 1)
        # sample normally distributed load
        p_total_rand = p_total*(
            1 + std_dev*sqrt(-2*log(rand1))*cos(2*pi*rand2))
        q_total_rand = q_total*(
            1 + std_dev*sqrt(-2*log(rand1))*cos(2*pi*rand2))
        # collect all load elements
        loads = self.app.GetCalcRelevantObjects('*.ElmLod')
        # store normally distributed load values in dictionary
        p_normal = {}
        q_normal = {}
        for load in loads:
            p_normal[load.loc_name] = (p_base[load.loc_name]
                                       /p_total*p_total_rand)
            q_normal[load.loc_name] = (q_base[load.loc_name]
                                       /q_total*q_total_rand)

        return p_normal, q_normal

    def monte_carlo_loadflow(self, n_samples, std_dev,
                             max_attempts=10):
        # set up the load flow object
        self.prepare_loadflow()
        # get base (initial) load values
        p_base, q_base = self.get_all_loads_pq()
        # calculate total base system load
        p_total = sum(p_base.values())
        q_total = sum(q_base.values())
        # sample load flow 'n_samples' times
        for sample in range(n_samples):
            # re-attempt load flow in case of non-convergence
            for attempt in range(max_attempts):
                # generate random normally distributed loads
                p_normal, q_normal = self.gen_normal_loads_pq(
                    p_total, q_total, p_base, q_base, 
                    std_dev=std_dev)
                # set network loads to random load values
                self.set_all_loads_pq(p_normal, q_normal)
                # run load flow with normally dist. loads
                failed = self.run_loadflow()
                if failed:
                    warnings.warn(
                        "Sample " + str(sample)
                        + " didn't converge, re-attempt "
                        + str(attempt+1) + " out of " 
                        + str(max_attempts))
                else:
                    break

            # yield load flow results
            yield self.get_bus_voltages()

        # restore network to base load (initial) values
        self.set_all_loads_pq(p_base, q_base)
