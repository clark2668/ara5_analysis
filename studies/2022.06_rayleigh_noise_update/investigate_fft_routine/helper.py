import numpy as np
import ctypes
import array as array
import ROOT
import os 
from ROOT import gInterpreter, gSystem, TChain


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


def do_fft_with_python(graph, norm='standard'):

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
    dF = (freqs[1] - freqs[0])
    
    if norm not in ['standard', 'dT', 'dTdF']:
        raise Exception(f"requested normalization ({norm}) is not implemened")

    the_norm = np.sqrt(2./length) # always start with this
    the_extra_norm = 1.
    
    if norm=='standard':
        the_extra_norm = 1.
    elif norm=='dT':
        the_extra_norm = np.sqrt(dT)
    elif norm=='dTdF':
        the_extra_norm = np.sqrt(dT / dF)
    
    the_norm *= the_extra_norm

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