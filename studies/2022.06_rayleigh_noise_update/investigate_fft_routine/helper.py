import numpy as np
import ctypes
import array as array
import ROOT
import os 
from ROOT import gInterpreter, gSystem


ROOT.gSystem.Load(os.environ.get('ARA_UTIL_INSTALL_DIR')+"/lib/libAraEvent.so")
ROOT.gSystem.Load(os.environ.get('ARA_DEPS_INSTALL_DIR')+"/lib/libRootFftwWrapper.so")
gInterpreter.ProcessLine('#include "' + os.environ.get('ARA_DEPS_INSTALL_DIR') + '/include/FFTtools.h"')
gInterpreter.ProcessLine('#include "' + os.environ.get('ARA_DEPS_INSTALL_DIR') + '/include/FFTWComplex.h"')

# this version does the FFT and such using the python version

def convertGraphToArray(gr):
    wfLength = gr.GetN()
    t = []
    v = []
    for kk in range(0,wfLength):
      t.append(gr.GetX()[kk])
      v.append(gr.GetY()[kk])
    return np.array(t), np.array(v)

def do_with_python(graph):

    times, volts = convertGraphToArray(graph)
    length = len(volts)
    
    fft = np.sqrt(2.) * np.abs(np.fft.rfft(volts)) # no negative frequencies

    power_time = 0
    for i in range(length):
        power_time += pow(volts[i], 2.)
    print("Power in time domain {}".format(power_time))

    power_freq = 0
    for i in range(len(fft)):
        power_freq += pow(fft[i], 2.)
    power_freq/=length
    print("Power in freq domain {}".format(power_freq))

    print("-----")




# this version does the FFT and such using the FFTtools package

# def do_with_FFTtools(graph):

    
#     oldY = graph.GetY()
#     oldX = graph.GetX()
#     length = int(graph.GetN())
#     deltaT = ( oldX[1] - oldX[0]) * 1.E-9 # convert to seconds

#     theFFT = array.array(ROOT.FFTtools.FFTWComplex, [0]*length)
#     theFFT = ROOT.FFTtools.doFFT(length, oldY)
#     print(ROOT.FFTtools.doFFT(length, oldY))
    
#     newLength = int((length/2) + 1)
#     newY = array.array('d', [0]*newLength)
#     newX = array.array('d', [0]*newLength)
#     deltaF = 1./(deltaT * length) # in Hz
#     deltaF *= 1E-6 # from Hz to MHz



#     # tempF = 0
#     # for i in range(newLength):
#     #     print(theFFT[i])
#     #     newY[i] = np.sqrt(2) * ROOT.FFTtools.getAbs(theFFT[i])
#     #     newX = tempF
#     #     tempF += deltaF
    
#     # grSpectrum = ROOT.TGraph(newLength, newX, newY)


    

