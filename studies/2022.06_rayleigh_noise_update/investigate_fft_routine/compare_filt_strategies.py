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


fig, axs = plt.subplots(1,1,figsize=(8,5))


##############
### Frequency Domain Check
##############

chID = 0

data_volts, data_freqs, data_spec = helper.get_all_volts_from_data_file(
    data_file, chID, 0.5, 1024, apply_filters='none', do_freq_spec=True
    )
axs.plot(data_freqs/1E6, data_spec, label='raw', linewidth=2)

data_volts, data_freqs, data_spec = helper.get_all_volts_from_data_file(
    data_file, chID, 0.5, 1024, apply_filters='bandpass', do_freq_spec=True
    )
axs.plot(data_freqs/1E6, data_spec, label='bandpassed (2nd order, Fmin = 90 MHz, Fmax = 900 MHz', linewidth=2, ls='--')
axs.legend()

axs.set_xlabel('Frequency [MHz]')
axs.set_ylabel(r'Average Spectrum [V/$\sqrt{Hz}$]')

plt.tight_layout()
fig.savefig('compare_spec.png')



    