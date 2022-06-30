import numpy as np
import ctypes
import array as array
import ROOT
import os 
from ROOT import gInterpreter, gSystem, TChain
import copy
import matplotlib.pyplot as plt


ROOT.gSystem.Load(os.environ.get('ARA_UTIL_INSTALL_DIR')+"/lib/libAraEvent.so")
ROOT.gSystem.Load(os.environ.get('ARA_DEPS_INSTALL_DIR')+"/lib/libRootFftwWrapper.so")
gInterpreter.ProcessLine('#include "' + os.environ.get('ARA_DEPS_INSTALL_DIR') + '/include/FFTtools.h"')
gInterpreter.ProcessLine('#include "' + os.environ.get('ARA_DEPS_INSTALL_DIR') + '/include/FFTWComplex.h"')

# this version does the FFT and such using the python version

# dump the graph x/y into np arrays
# and convert them to volts and seconds
def get_t_v_arrays(graph):
    t = []
    v = []
    for k in range(graph.GetN()):
        t.append(graph.GetX()[k]*1E-9) # convert to seconds
        v.append(graph.GetY()[k]*1E-3) # convert to volts
    t = np.asarray(t)
    v = np.asarray(v)
    return t, v


def do_fft_with_python(graph, norm='standard', grIntLength=1024):

    """

    Does the FFT of the graph
    Arguments:
        graph: a root TGraph
        norm: a string

            
            For 'norm', you have three options:
            
            1) 'standard'. Return the FFT spectral coefficients normalized by sqrt(2/N).
                This will satisfy Parseval's theorem for:
                sum(time_domain**2) = sum(freq_domain**2)
                Meaning the units of the fft are Volts.
                The user doesn't need to apply an additional normalization factors
                to get Parseval's theorem to work.
            
            2) 'dT'. Return the FFT spectral coefficients normalized by sqrt(2 * dT / N).
                This is the "time-integral squared amplitude".
                This will satisfy Parseval's theorem for:
                dT * sum(time_domain**2) = sum(freq_domain**2)
                Meaning the units of the fft are Volts/Sqrt(Hz).
                It is the user's job to multiply by dT on the time domain side.
            
            3) 'dTdF'. Return the FFT spectral coefficients normalized by sqrt(2 * dT / N / dF).
                That is, normalize the spectral coefficients 
                (the "time-integral squared amplitude) by the bin width.
                This will saisfy Parsevals' theorem for:
                dT * sum(time_domain**2) = dF * sum(freq_domain**2)
                Meaning the units of the fft are Volts*Seconds.
                It is the user's job to multiply by dT and dF,
                for the time domain and frequency domain sides, respectively.

    Returns:
        freqs: a numpy array of the frequencies for the FFT
        fft: the FFT
        the_extra_norm: a number
            
    Other: 
        Ryan Nichol's docs are very helpful: https://www.hep.ucl.ac.uk/~rjn/saltStuff/fftNormalisation.pdf

    """

    times, volts = get_t_v_arrays(graph)
    length = len(volts)
    dT = (times[1] - times[0])
    freqs = np.fft.rfftfreq(length, dT)
    freqs_old = np.fft.rfftfreq(grIntLength, dT)
    dF = (freqs[1] - freqs[0])
    dF_old = (freqs_old[1] - freqs_old[0])
    
    if norm not in ['standard', 'dT', 'dTdF', 'rayleigh']:
        raise Exception(f"requested normalization ({norm}) is not implemened")

    the_norm =1  # always start with this
    
    if norm=='standard':
        the_norm = np.sqrt(2./grIntLength)
    elif norm=='dT':
        the_norm = np.sqrt(2./grIntLength) * np.sqrt(dT)
    elif norm=='dTdF':
        the_norm = np.sqrt(2./grIntLength) * np.sqrt(dT / dF_old)
    elif norm=='rayleigh':
        the_norm = 1./(np.sqrt(dF_old) * grIntLength)

    fft = the_norm * np.abs(np.fft.rfft(volts)) # no negative frequencies

    # power_time = 0
    # for i in range(length):
    #     power_time += pow(volts[i], 2.)
    # print("Power in time domain {}".format(power_time))

    # power_freq = 0
    # for i in range(len(fft)):
    #     power_freq += pow(fft[i], 2.)
    # print("Power in freq domain {}".format(power_freq))

    return freqs, fft


def get_single_event_AraSim(rootFile, eventNumber, chID, pad=None):

    eventTree = TChain("eventTree")
    eventTree.AddFile(rootFile)
    realEvent = ROOT.UsefulAtriStationEvent()
    eventTree.SetBranchAddress("UsefulAtriStationEvent", ROOT.AddressOf(realEvent))
    eventTree.GetEntry(eventNumber)
    gr = realEvent.getGraphFromRFChan(chID)
    if pad is not None:
        gr = ROOT.FFTtools.padWaveToLength(gr, pad)
    return gr

def get_single_softevent_data(rootFile, softEventNumber, chID, pad=None):

    file = ROOT.TFile.Open(rootFile)
    eventTree = file.Get("eventTree")
    rawEvent = ROOT.RawAtriStationEvent()
    eventTree.SetBranchAddress("event", ROOT.AddressOf(rawEvent))
    numEvents = eventTree.GetEntries()
    numSoftEventsFound = 0
    for i in range(numEvents):
        eventTree.GetEntry(i)
        if(rawEvent.isSoftwareTrigger()):
            if(numSoftEventsFound==softEventNumber):
                usefulEvent = ROOT.UsefulAtriStationEvent(rawEvent, ROOT.AraCalType.kLatestCalib)
                gr = usefulEvent.getGraphFromRFChan(chID)
                if pad is not None:
                    grInt = ROOT.FFTtools.getInterpolatedGraph(gr, 0.25)
                    grPad = ROOT.FFTtools.padWaveToLength(grInt, pad)
                    del gr, grInt, usefulEvent
                    return grPad
                else:
                    del usefulEvent
                    return gr
            else:
                numSoftEventsFound+=1

def handle_wavform(gr, interp=None, pad=None, filter=False):
    
    # if we adjust the waveform, we always start with interpolation
    grIntLength = None
    if interp is not None:
        grInt = ROOT.FFTtools.getInterpolatedGraph(gr, interp)
        grIntLength = grInt.GetN()
        del gr
        gr = copy.deepcopy(grInt)
        del grInt
    
        # pad if requested
        if pad is not None:
            grPad = ROOT.FFTtools.padWaveToLength(gr, pad)
            del gr
            gr = copy.deepcopy(grPad)
            del grPad
        
        # filter if requested
        if filter is not None:
            filter.filterGraph(gr)
        
        # gr1 = ROOT.FFTtools.padWaveToLength(gr, 1024)
        # freqs, fft = do_fft_with_python(gr1)
        # fig, axs = plt.subplots(1,2,figsize=(10,5))
        # axs[0].plot(freqs, fft)
        # fig.savefig('demo_filter_{}.png'.format(filter))
        # del gr1
    
    return gr, grIntLength


def get_all_volts_from_data_file(rootFile, chID, interp=None, pad=None, the_filter=False, do_freq_spec=False):

    if the_filter:
        nyquist = 1./(2*interp*1E-9) # interp speed in ns
        freq_lowpass = 900E6/nyquist # lowpass filter at 900 MHz (comfortably in the ARA band)
        but = ROOT.FFTtools.ButterworthFilter(ROOT.FFTtools.LOWPASS, 5, freq_lowpass)
    else:
        but = None

    avg_freqs = None
    avg_spec = None
    all_volts = []

    file = ROOT.TFile.Open(rootFile)
    eventTree = file.Get("eventTree")
    rawEvent = ROOT.RawAtriStationEvent()
    eventTree.SetBranchAddress("event", ROOT.AddressOf(rawEvent))
    numEvents = eventTree.GetEntries()
    numEvents=1000
    numFound = 0
    for i in range(numEvents):
        eventTree.GetEntry(i)
        if(rawEvent.isSoftwareTrigger()):
            usefulEvent = ROOT.UsefulAtriStationEvent(rawEvent, ROOT.AraCalType.kLatestCalib)
            gr = usefulEvent.getGraphFromRFChan(chID)

            if interp or pad or the_filter or do_freq_spec:
                gr, grIntLength = handle_wavform(gr, interp, pad, but)

                if do_freq_spec:
                    freqs, fft = do_fft_with_python(gr, 'rayleigh', grIntLength)
                    if avg_freqs is None:
                        avg_freqs = copy.deepcopy(freqs)
                    if avg_spec is None:
                        avg_spec = copy.deepcopy(fft)
                    elif avg_spec is not None:
                        avg_spec += fft
                    numFound+=1

            volts = gr.GetY()
            for i in range(gr.GetN()):
                all_volts.append(volts[i])
            del gr
    file.Close()
    if do_freq_spec:
        avg_spec/=numFound
    return all_volts, avg_freqs, avg_spec



def get_all_volts_from_AraSim_file(rootFile, chID, interp=None, pad=None, the_filter=False, do_freq_spec=False):
    
    if the_filter:
        nyquist = 1./(2*interp*1E-9) # interp speed in ns
        freq_lowpass = 900E6/nyquist # lowpass filter at 900 MHz (comfortably in the ARA band)
        but = ROOT.FFTtools.ButterworthFilter(ROOT.FFTtools.LOWPASS, 2, freq_lowpass)
    else:
        but = None

    avg_freqs = None
    avg_spec = None
    all_volts = []
    
    file = ROOT.TFile.Open(rootFile)
    eventTree = file.Get("eventTree")
    realEvent = ROOT.UsefulAtriStationEvent()
    eventTree.SetBranchAddress("UsefulAtriStationEvent", ROOT.AddressOf(realEvent))
    numEvents = eventTree.GetEntries()
    numFound = 0
    for i in range(numEvents):
        eventTree.GetEntry(i)
        gr = realEvent.getGraphFromRFChan(chID)

        if interp or pad or the_filter or do_freq_spec:
            gr, grIntLength = handle_wavform(gr, interp, pad, but)
        
            if do_freq_spec:
                freqs, fft = do_fft_with_python(gr, 'rayleigh', grIntLength)
                if avg_freqs is None:
                    avg_freqs = copy.deepcopy(freqs)
                if avg_spec is None:
                    avg_spec = copy.deepcopy(fft)
                elif avg_spec is not None:
                    avg_spec += fft
                numFound+=1

        volts = gr.GetY()
        for i in range(gr.GetN()):
            all_volts.append(volts[i])
        del gr
    file.Close()
    if do_freq_spec:
        avg_spec/=numFound
    return all_volts, avg_freqs, avg_spec

