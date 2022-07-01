import ROOT
from ROOT import gInterpreter, gSystem, TChain
import numpy as np
import matplotlib.pyplot as plt
import os 
import helper as helper
import copy

plt.rcParams.update({
    'xtick.labelsize': 14, 
    'ytick.labelsize': 14,
    'xtick.major.size': 5, 
    'ytick.major.size': 5,
    'axes.titlesize': 14,
    'axes.labelsize': 14
})

gSystem.Load('libAra.so')

data_file = '/disk20/users/brian/ARA/event_003315.root'
ped_file = '/disk20/users/brian/ARA/peds/2014/A2/reped_run_003315.dat.gz'
calibrator = ROOT.AraEventCalibrator.Instance()
calibrator.setAtriPedFile(ped_file, 2)

gr1 = helper.get_single_softevent_data(data_file, 0, 0)
t1, v1 = helper.get_t_v_arrays(gr1)

top_dir = '/disk20/users/brian/ARA/sim/'
sim_file = f'{top_dir}/AraOut.noise_setup_1024.txt.run40000.root'
gr2 = helper.get_single_event_AraSim(sim_file, 0, 0)
t2, v2 = helper.get_t_v_arrays(gr2)

fig, axs = plt.subplots(1,1,figsize=(7,5))

# time domain
axs.plot(t2, v2, ls='--', color='C1', label='Simulation')
axs.plot(t1, v1, label='Data', color='C0')

axs.set_xlabel('Time [s]')
axs.set_ylabel('Voltage [mV]')
axs.legend(loc='upper right')

plt.tight_layout(pad=5.)
fig.savefig('validate_traces.pdf', bbox_inches='tight')
