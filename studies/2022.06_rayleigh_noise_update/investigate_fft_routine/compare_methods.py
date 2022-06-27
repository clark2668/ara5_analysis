import numpy as np
import ROOT
from ROOT import gInterpreter, gSystem
import numpy as np
import matplotlib.pyplot as plt
import os 
import helper as helper
import copy

ROOT.gSystem.Load(os.environ.get('ARA_UTIL_INSTALL_DIR')+"/lib/libAraEvent.so")
gInterpreter.ProcessLine('#include "' + os.environ.get('ARASIM_DIR') + '/Tools.h"')
tools = ROOT.Tools()

volts = np.random.normal(size=512)
volts_forfft = copy.deepcopy(volts)

spectra_np = np.fft.rfft(volts)
spectra_np = np.abs(spectra_np)
# print(len(spectra_np))
tools.realft(volts_forfft, 1, len(volts))

newLength = int(len(volts_forfft)/2)

spectra_arasim = np.zeros(newLength)
for i in range(newLength):
    spectra_arasim[i] = np.sqrt( volts_forfft[2*i]**2 + volts_forfft[2*i+1]**2 )

fig, axs = plt.subplots(1,2,figsize=(12,5),
    #gridspec_kw={'width_ratios':[1.5,1]}
    )

# time domain
axs[0].plot(spectra_np, label='np')
axs[0].plot(spectra_arasim, label='np', ls='--')
# axs[0].set_xlabel('Time [s]')
# axs[0].set_ylabel('Voltage [V]')
axs[0].legend(loc='upper right')
fig.savefig('compare.png')




