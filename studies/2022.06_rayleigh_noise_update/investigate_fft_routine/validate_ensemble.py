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


fig, axs = plt.subplots(1,2,figsize=(10,5))
bins = np.linspace(-100, 100, 50)

# ##############
# ### Time Domain Check
# ##############

chID = 0

# data
data_volts, data_freqs, data_spec = helper.get_all_volts_from_data_file(data_file, chID, interp=0.5, the_filter=True)
axs[0].hist(data_volts, bins=bins, histtype='step', density=True, 
    label=r'Data, $\sigma$= {:.1f}'.format(np.std(data_volts)),
    linewidth=3, alpha=0.8
)
print("Starting the look at simulation")
# simulation
top_dir = '/disk20/users/brian/ARA/sim/'
sim_file = f'{top_dir}/AraOut.noise_setup_1024.txt.run40000.root'
sim_volts, sim_freqs, sim_spec = helper.get_all_volts_from_AraSim_file(sim_file, chID)

the_dt = 3
the_N = 700
axs[0].hist(sim_volts, bins=bins, histtype='step', density=True, ls='--',
    label=r'Sim, dT={:.1f} ns, N = {}, $\sigma$= {:.1f}'.format(
        the_dt*1E-10/1E-9, the_N, np.std(sim_volts)
        ),
        linewidth=3, alpha=0.8
    )
axs[0].set_xlabel('Voltage [mV]')
axs[0].set_ylabel('Norm Counts')
# axs[0].set_yscale('log')
axs[0].legend(
    loc='upper center',
    bbox_to_anchor=(0.5, 1.15)
)


##############
### Frequency Domain Check
##############

data_volts, data_freqs, data_spec = helper.get_all_volts_from_data_file(
    data_file, chID, 0.5, 1024, the_filter=True, do_freq_spec=True
    )
axs[1].plot(data_freqs/1E6, data_spec, label='Data', linewidth=2)


sim_volts, sim_freqs, sim_spec = helper.get_all_volts_from_AraSim_file(
    sim_file, chID, 0.5, 1024, the_filter=False, do_freq_spec=True
    )
axs[1].plot(sim_freqs/1E6, sim_spec, ls='--', label='Sim', linewidth=2)

axs[1].set_xlabel('Frequency [MHz]')
axs[1].set_ylabel(r'Average Spectrum [V/$\sqrt{Hz}$]')

# axs[1].legend()

plt.tight_layout()
fig.savefig('validate_rms.pdf')



    