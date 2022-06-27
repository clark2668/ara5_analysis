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

file1 = '/home/brian/ARA/ara5_analysis/tools/AraSim/AraOut.noise_setup_2048.txt.run30000.root'
file2 = '/home/brian/ARA/ara5_analysis/tools/AraSim/AraOut.noise_setup_1024.txt.run20000.root'


the_norm = 'standard'
the_norm = 'dT'
# the_norm = 'dTdF'

print("The Norm is {} ".format(the_norm))
the_pad = None
gr1 = helper.get_single_event_AraSim(file1, 0, 0)
t1, v1 = helper.get_t_v_arrays(gr1)
freqs1, fft1 = helper.do_fft_with_python(gr1, norm=the_norm)

gr2 = helper.get_single_event_AraSim(file2, 0, 0)
t2, v2 = helper.get_t_v_arrays(gr2)
freqs2, fft2 = helper.do_fft_with_python(gr2, norm=the_norm)

dF1 = (freqs1[1] - freqs1[0])
dF2 = (freqs2[1] - freqs2[0])
dT1 = (t1[1] - t1[0])
dT2 = (t2[1] - t2[0])
fft1_ave = copy.deepcopy(fft1)
fft2_ave = copy.deepcopy(fft2)

# accumulate
numInSum = 200
for i in range (1, numInSum):
    print("Adding {} ...".format(i))
    temp_gr1 = helper.get_single_event_AraSim(file1, i, 0)
    temp_t1, temp_v1 = helper.get_t_v_arrays(gr1)
    temp_gr2 = helper.get_single_event_AraSim(file2, i, 0)
    t2, v2 = helper.get_t_v_arrays(gr2)

    temp_freqs1, temp_fft1 = helper.do_fft_with_python(temp_gr1, norm=the_norm)
    temp_freqs2, temp_fft2 = helper.do_fft_with_python(temp_gr2, norm=the_norm)

    fft1_ave+=temp_fft1
    fft2_ave+=temp_fft2

    del temp_gr1, temp_gr2

# make it an average
fft1_ave/=numInSum
fft2_ave/=numInSum

fig, axs = plt.subplots(1,2,figsize=(12,5),
    #gridspec_kw={'width_ratios':[1.5,1]}
    )

# time domain
axs[0].plot(t1, v1, label='{} samples'.format(len(v1)))
axs[0].plot(t2, v2, ls='--', label='{} samples'.format(len(v2)))
axs[0].set_xlabel('Time [s]')
axs[0].set_ylabel('Voltage [V]')
axs[0].legend(loc='upper right')
# axs[0].set_title('Time Domain')

# # histogram of samples (to check rms)
# bins = np.linspace(-150E-3, 150E-3, 50)
# axs[1][0].hist(v1, bins=bins, density=True, histtype='step',
#     label=r'$\sigma$ = {:.1e}'.format(np.std(v1)), )
# axs[1][0].hist(v2, bins=bins, density=True, histtype='step', ls='--',
#     label=r'$\sigma$ = {:.1e}'.format(np.std(v2)))
# axs[1][0].set_xlabel('Volts')
# axs[1][0].set_ylabel('Norm Counts')
# axs[1][0].legend()


# get the normalization factors right
if the_norm == 'standard':
    time_norm_1 = 1.
    time_norm_2 = 1.
    freq_norm_1 = 1.
    freq_norm_2 = 1.
    the_freq_ylabel = 'H   [V]'
if the_norm == 'dT':
    time_norm_1 = dT1
    time_norm_2 = dT2
    freq_norm_1 = 1.
    freq_norm_2 = 1.
    the_freq_ylabel = r'H   [V / $\sqrt{Hz}$]'
elif the_norm == 'dTdF':
    time_norm_1 = dT1
    time_norm_2 = dT2
    freq_norm_1 = dF1
    freq_norm_2 = dF2
    the_freq_ylabel = r'H   [V $\cdot$ s]'


# double check parseval's theorem ("time-integral squared amplitude version")
power_trace1 = 0.
for i in range(len(v1)):
    power_trace1+=np.power(v1[i], 2.)*time_norm_1
print("Power Time Trace 1 {:.3e}".format(power_trace1))
power_trace2 = 0.
for i in range(len(v2)):
    power_trace2+=np.power(v2[i], 2.)*time_norm_2
print("Power Time Trace 2 {:.3e}".format(power_trace2))

power_fft1 = 0.
for i in range(len(fft1_ave)):
    power_fft1+=np.power(fft1_ave[i], 2.)*freq_norm_1
print("Power Freq Spec 1 {:.3e}".format(power_fft1))
power_fft2 = 0.
for i in range(len(fft2_ave)):
    power_fft2+=np.power(fft2_ave[i], 2.)*freq_norm_2
print("Power Freq Spec 2 {:.3e}".format(power_fft2))

# print("Spec Power 1 over 2 is {:.2f}".format(power_fft1/power_fft2))

# spectra

axs[1].plot(freqs1, fft1_ave)
axs[1].plot(freqs2, fft2_ave, ls='--')

axs[1].set_xlabel('Frequency [Hz]')
axs[1].set_ylabel(the_freq_ylabel)
# axs[1].set_ylim([0,5E-18])
axs[1].set_title("'{}' normalization".format(the_norm))

plt.tight_layout(pad=5.)
fig.savefig('traces_norm_{}.pdf'.format(the_norm), bbox_inches='tight')
