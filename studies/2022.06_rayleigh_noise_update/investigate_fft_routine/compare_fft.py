import ROOT
from ROOT import gInterpreter, gSystem
import numpy as np
import matplotlib.pyplot as plt
import os 
import helper as helper

ROOT.gSystem.Load(os.environ.get('ARA_UTIL_INSTALL_DIR')+"/lib/libAraEvent.so")
ROOT.gSystem.Load(os.environ.get('ARA_DEPS_INSTALL_DIR')+"/lib/libRootFftwWrapper.so")
gInterpreter.ProcessLine('#include "' + os.environ.get('ARA_DEPS_INSTALL_DIR') + '/include/FFTtools.h"')
# gInterpreter.ProcessLine('#include "/cvmfs/ara.opensciencegrid.org/trunk/centos7/source/ARA_cvmfs/build/include/FFTtools.h"')


file = ROOT.TFile.Open("/disk20/users/brian/ARA/event_003315.root")
eventTree = file.Get("eventTree")
rawEvent = ROOT.RawAtriStationEvent()
eventTree.SetBranchAddress("event", ROOT.AddressOf(rawEvent))

num_events = eventTree.GetEntries()
print("total events {}".format(num_events))

for event in range(num_events):

    eventTree.GetEntry(event)
    if(rawEvent.isSoftwareTrigger()):
        print("We have a software trigger on event {}".format(event))

        usefulEvent = ROOT.UsefulAtriStationEvent(rawEvent, ROOT.AraCalType.kLatestCalib)
        grRaw = usefulEvent.getGraphFromRFChan(0)
        grInt = ROOT.FFTtools.getInterpolatedGraph(grRaw, 0.5)
        grPad = ROOT.FFTtools.padWaveToLength(grInt, 1024)
        
        helper.do_fft_with_python(grPad)


        del grPad, grInt, grRaw, usefulEvent



        # c = ROOT.TCanvas()
        # c.cd()
        # grRaw.Draw("ALP")
        # grPad.Draw("Lsame")
        # grPad.SetLineColor(ROOT.kRed)
        # c.Print("root_waveform_{}.png".format(event))
