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


settings = {
    3: {'dt':3, 'N':700,  'interp': None , 'filt': False},
}

voltage_arrays = {
    
}

# get all the voltages
for this_set in settings:
    these_settings = settings[this_set]
    this_dt = these_settings['dt']
    this_N = these_settings['N']
    this_interp = these_settings['interp']
    this_filt = these_settings['filt']
    top_dir = '/home/brian/ARA/ara5_analysis/tools/AraSim/'
    sim_file = f'{top_dir}/AraOut.noise_setup_dt_{this_dt}_N_{this_N}.root'
    volts = helper.get_all_volts_from_AraSim_file(sim_file, 0, this_interp, this_filt)
    voltage_arrays[this_set] = volts

line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':','-', '--', '-.', ':']

the_stds = []
the_dts = []

fig, axs = plt.subplots(1,2,figsize=(10,5))
bins = np.linspace(-100, 100, 50)
for this_set in settings:

    these_settings = settings[this_set]
    this_dt = these_settings['dt']
    this_N = these_settings['N']
    this_interp = these_settings['interp']
    this_filt = these_settings['filt']

    axs[0].hist(voltage_arrays[this_set], bins=bins, histtype='step', density=True, ls=line_styles[this_set],
        label=r'Sim, dT={:.2f} ns, N = {}, LP Filter? {}, $\sigma$= {:.4e}'.format(
            this_dt*1E-10/1E-9, this_N, this_filt,
            np.std(voltage_arrays[this_set]))
        )
        
    the_dts.append(this_dt)
    the_stds.append(np.std(voltage_arrays[this_set]))

the_stds = np.asarray(the_stds)
the_dts = np.asarray(the_dts)

axs[0].set_xlabel('Voltage [mV]')
axs[0].set_ylabel('Norm Counts')
# axs[0].set_yscale('log')
axs[0].legend(
    loc='upper center',
    bbox_to_anchor=(0.5, 1.35)
)

axs[1].plot(the_dts*1E-10/1E-9, the_stds, 'o')
axs[1].set_xlabel('TIMESTEP [ns]')
axs[1].set_ylabel('RMS Noise')

plt.tight_layout()
fig.savefig('validate_rms.png')



    