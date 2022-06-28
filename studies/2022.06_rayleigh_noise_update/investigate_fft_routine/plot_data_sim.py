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

sim_file = '/home/brian/ARA/ara5_analysis/tools/AraSim/AraOut.noise_setup_1024.txt.run40000.root'

the_norm = 'standard'
# the_norm = 'dT'
# the_norm = 'dTdF'

evtNumber = 0
chID = 0 ## ONLY LOOK AT CHANNEL 0

# scan many channels

all_data_samples = []
all_sim_samples = []

do_ensemble = True
if do_ensemble:

    avg_data = None
    avg_sim = None
    freqs_data = None
    freqs_sim = None

    nev = 25
    pad = 1024

    for i in range(nev):

        print("on i {}".format(i))

        # data
        gr_data = helper.get_single_softevent_data(data_file, i, 0, pad=pad)
        freqs_data, fft_data = helper.do_fft_with_python(gr_data, norm='dTdF')

        if avg_data is None:
            avg_data = copy.deepcopy(fft_data)
            freqs_data = copy.deepcopy(freqs_data)
        else:
            avg_data+=fft_data

        gr_data_noint = helper.get_single_softevent_data(data_file, i, 0)
        t1_data_noint, v1_data_noint = helper.get_t_v_arrays(gr_data_noint)
        for j in range(len(v1_data_noint)):
            all_data_samples.append(v1_data_noint[j])
        del gr_data, gr_data_noint

        
        # sim
        gr_sim = helper.get_single_event_AraSim(sim_file, i, chID, pad=None)
        freqs_sim, fft_sim = helper.do_fft_with_python(gr_sim, norm='dTdF')

        if avg_sim is None:
            avg_sim = copy.deepcopy(fft_sim)
            freqs_sim = copy.deepcopy(freqs_sim)
        else:
            avg_sim+=fft_sim

        gr_sim_noint = helper.get_single_event_AraSim(sim_file, i, chID)
        t1_sim_noint, v1_sim_noint = helper.get_t_v_arrays(gr_sim_noint)
        dt = t1_sim_noint[1] - t1_sim_noint[0]
        print("The dT is {}, the N is {}".format(dt, len(t1_sim_noint)))
        for j in range(len(v1_sim_noint)):
            all_sim_samples.append(v1_sim_noint[j])
        del gr_sim, gr_sim_noint

    avg_data/=nev
    avg_sim/=nev

    fig, axs = plt.subplots(1,2,figsize=(10,5),
        #gridspec_kw={'width_ratios':[1.5,1]}
        )
    bins = np.linspace(-0.1, 0.1, 50)
    axs[0].hist(all_data_samples, bins=bins, histtype='step', density=True, 
        label=r'Data, $\mu$ = {:.2e}, $\sigma$ = {:.2e}'.format(np.mean(all_data_samples), np.std(all_data_samples)), )
    axs[0].hist(all_sim_samples, bins=bins, histtype='step', ls='--', density=True,
        label=r'Sim, $\mu$ = {:.2e}, $\sigma$ = {:.2e}'.format(np.mean(all_sim_samples), np.std(all_sim_samples)))
    axs[0].set_xlabel('Volts')
    axs[0].set_ylabel('Norm Counts')
    axs[0].legend()


    axs[1].plot(freqs_data, avg_data)
    axs[1].plot(freqs_sim, avg_sim)
    
    plt.tight_layout(pad=5.)
    fig.savefig('many_samples.png', bbox_inches='tight')

    print("Data RMS {:.3f}, Sim RMS {:.3f}, Ratio Sim/Data {:.3f}".format(
        np.std(all_data_samples), np.std(all_sim_samples),
        np.std(all_sim_samples)/np.std(all_data_samples)
        )
        )



do_single_event = False
if do_single_event:
    gr_data = helper.get_single_softevent_data(data_file, evtNumber, 0)
    t1_data, v1_data = helper.get_t_v_arrays(gr_data)
    print("Num data samples {}".format(len(v1_data)))
    print("Data dT is {}".format(t1_data[1] - t1_data[0]))
    freqs_data, fft_data = helper.do_fft_with_python(gr_data, norm='standard')

    gr_sim = helper.get_single_event_AraSim(sim_file, evtNumber, chID)
    t1_sim, v1_sim = helper.get_t_v_arrays(gr_sim)
    print("Number sim samples {}".format(len(t1_sim)))
    print("Sim dT is {}".format(t1_sim[1] - t1_sim[0]))
    freqs_sim, fft_sim = helper.do_fft_with_python(gr_sim, norm='standard')

    fig, axs = plt.subplots(1,3,figsize=(15,5))

    print("Data RMS {}".format(np.std(v1_data)))
    print("Sim RMS {}".format(np.std(v1_sim)))

    # time domain
    axs[0].plot(t1_sim, v1_sim, label='Sim')
    axs[0].plot(t1_data, v1_data, ls='--', label='Data')
    axs[0].set_xlabel('Time [s]')
    axs[0].set_ylabel('Voltage [V]')
    axs[0].legend(loc='upper right')
    # axs[0].set_xlim([0,1E-7])

    # histogram of samples (to check rms)
    bins = np.linspace(-0.1, 0.1, 50)
    axs[1].hist(v1_sim, bins=bins, density=True, histtype='step',
        label=r'$\sigma$ = {:.1e}'.format(np.std(v1_sim)), )
    axs[1].hist(v1_data, bins=bins, density=True, histtype='step', ls='--',
        label=r'$\sigma$ = {:.1e}'.format(np.std(v1_data)))
    axs[1].set_xlabel('Volts')
    axs[1].set_ylabel('Norm Counts')
    axs[1].legend()

    axs[2].plot(freqs_data, fft_data)
    axs[2].plot(freqs_sim, fft_sim)


    plt.tight_layout(pad=5.)
    fig.savefig('traces_data_and_sim_{}.png'.format(the_norm), bbox_inches='tight')
