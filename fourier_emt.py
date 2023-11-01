# File: fourier_emt.py
# Author: Claudio David Lopez

# WARNING: This script is only valid for waveforms of fixed 
# step size. All events in non-real time simulations in 
# PowerFactory produce waveforms of variaable step size.
# In order to calculate the FFT of such a waveform, 
# the waveform must first be interpolated to produce a
# fixed step size equivalent.

import matplotlib.pyplot as plt
from scipy import fft, fftpack, sin, linspace, pi
from pfsim import PowerFactorySim


FOLDER_NAME = ''
PROJECT_NAME = '2A4G'
STUDY_CASE_NAME = 'Study Case'
STEP_SIZE = 0.0001
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
    step_size=STEP_SIZE,
    end_time=0.02)
# run EMT simulation
sim.run_dynamic_sim()
# retrieve line-to-line volages from one bus
t, ula = sim.get_dynamic_results(
            'Bus_20kV_1.ElmTerm', 'm:ul:A')
# calculate fft of voltage wave
ULA = abs(fft(ula))/len(ula)
# determine frequency for each harmonic in ULA 
f = fftpack.fftfreq(len(ula), STEP_SIZE)
# plot voltage waveform and its FFT
plt.subplot(211)
plt.plot(t, ula)
plt.xlabel('time [s]')
plt.ylabel('voltage [kV]')
plt.subplot(212)
plt.plot(f, ULA)
plt.xlabel('frequency [Hz]')
plt.ylabel('voltage amplitud [kV]')
plt.show()
