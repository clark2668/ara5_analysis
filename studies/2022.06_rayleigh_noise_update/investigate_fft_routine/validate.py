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
    # 2: {'dt':3, 'N':500,  'interp': None  },
    # 6: {'dt':4, 'N':500,  'interp': None  },
    0: {'dt':5, 'N':500,  'interp': 0.5  },
    1: {'dt':5, 'N':500,  'interp': 0.9  },
    # 0: {'dt':5, 'N':500,  'interp': None  },
    # 5: {'dt':6, 'N':500,  'interp': None  },
    # 1: {'dt':7, 'N':500,  'interp': None  },
    # 3: {'dt':8, 'N':500,  'interp': None  },
    # 4: {'dt':9, 'N':500,  'interp': None  },
    # 3: {'dt':2, 'N':300,  'interp': None  }
}

voltage_arrays = {
    
}

# get all the voltages
for this_set in settings:
    these_settings = settings[this_set]
    this_dt = these_settings['dt']
    this_N = these_settings['N']
    this_interp = these_settings['interp']
    top_dir = '/home/brian/ARA/ara5_analysis/tools/AraSim/'
    sim_file = f'{top_dir}/AraOut.noise_setup_dt_{this_dt}_N_{this_N}.root'

    volts = helper.get_all_volts_from_AraSim_file(sim_file, 0, this_interp)
    voltage_arrays[this_set] = volts

line_styles = ['-', '--', '-.', ':', '-', '--', '-.']

fig, axs = plt.subplots(1,2,figsize=(10,5))
bins = np.linspace(-100, 100, 50)
for this_set in settings:

    these_settings = settings[this_set]
    this_dt = these_settings['dt']
    this_N = these_settings['N']
    this_interp = these_settings['interp']

    axs[0].hist(voltage_arrays[this_set], bins=bins, histtype='step', density=True, ls=line_styles[this_set],
        label=r'Sim, dT={:.2f} ns, N = {}, Interp={}, $\sigma$= {:.4e}'.format(
            this_dt*1E-10/1E-9, this_N, this_interp,
            np.std(voltage_arrays[this_set]))
        )

axs[0].set_xlabel('Voltage [mV]')
axs[0].set_ylabel('Norm Counts')
# axs[0].set_yscale('log')
axs[0].legend(
    loc='upper center',
    bbox_to_anchor=(0.5, 1.35)
)
plt.tight_layout()
fig.savefig('validate.png')



    