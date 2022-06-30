# importing pandas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'xtick.labelsize': 14, 
    'ytick.labelsize': 14,
    'xtick.major.size': 5, 
    'ytick.major.size': 5,
    'axes.titlesize': 14,
    'axes.labelsize': 14
})

# Frequency,Channel,Fit,ChiSquare
def remove_outliers(the_dataframe):
    the_dataframe.loc[the_dataframe.Fit > 50, 'Fit'] = np.nan
    the_dataframe.loc[the_dataframe.Fit < 0, 'Fit'] = np.nan
    mask = np.isnan(the_dataframe.Fit)
    the_dataframe.Fit[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), the_dataframe.Fit[~mask])

# a plot
fig, axs = plt.subplots(1,2,figsize=(7,5))

# data
base = pd.read_csv('sigmavsfreq_ch0_pad1024.txt')
base.sort_values(by='Frequency', inplace=True)
remove_outliers(base)
freqs = base['Frequency']
fits = base['Fit']
axs[0].plot(freqs, fits, '--', label='Data (dT=0.5ns, padTo=1024)')

# data with 2048 inter samples (no longer needed)
# base = pd.read_csv('sigmavsfreq_ch0_pad2048.txt')
# base.sort_values(by='Frequency', inplace=True)
# remove_outliers(base)
# freqs_2048 = base['Frequency']
# fits_2048 = base['Fit']

base = pd.read_csv('sigmavsfreq_ch0_simpad1024.txt')
base.sort_values(by='Frequency', inplace=True)
remove_outliers(base)
freqs_sim = base['Frequency']
fits_sim = base['Fit']
axs[0].plot(freqs_sim, fits_sim, label='Sim (dT=0.5ns, padTo=1024)')

axs[0].legend()
axs[0].set_xlabel('Frequency [MHz]')
axs[0].set_ylabel(r'Sigma [V/$\sqrt{Hz}$]')
# axs.set_yscale('log')
# axs.set_ylim([1E-7, 2E-6])

axs[1].plot(freqs, fits/fits_sim)
# axs[1].set_xlim([0,850])
axs[1].set_ylim([0.6, 1.4])
axs[1].axhline(1.)
axs[1].set_xlabel('Frequency [MHz]')
axs[1].set_ylabel('Sim/Data')
fig.savefig('ch0_rayleigh_fits.png')

