// C/C++ Includes
#include <iostream>
#include <cstdlib>
#include <sstream>
#include <fstream>
#include <stdio.h>
#include <vector>
#include <cmath>
#include <algorithm>

//AraRoot Includes
#include "RawAtriStationEvent.h"
#include "UsefulAtriStationEvent.h"
#include "FFTtools.h"

//ROOT Includes
#include "TTree.h"
#include "TFile.h"
#include "TGraph.h"
#include "TCanvas.h"

#include "helper.h"

RawAtriStationEvent *rawAtriEvPtr;

using namespace std;

int main(int argc, char **argv)
{

    TFile *fpIn = new TFile("/disk20/users/brian/ARA/event_003315.root");
    fpIn->cd();
    TTree *eventTree = (TTree*) fpIn->Get("eventTree");
    eventTree->SetBranchAddress("event", &rawAtriEvPtr);
    int numEntries = eventTree->GetEntries();
    std::cout<<"Num Entries "<<numEntries<<std::endl;

    for(int event=0; event<numEntries; event++){ //loop over those entries
        eventTree->GetEntry(event); //get the event
                
        if(rawAtriEvPtr->isSoftwareTrigger()){
            std::cout<<"On event "<<event<<std::endl;

            UsefulAtriStationEvent *realAtriEvPtr = new UsefulAtriStationEvent(rawAtriEvPtr, AraCalType::kLatestCalib);
            TGraph *grRaw = realAtriEvPtr->getGraphFromRFChan(0);
            TGraph *grInt = FFTtools::getInterpolatedGraph(grRaw, 0.5);
            TGraph *grPad = FFTtools::padWaveToLength(grInt, 1024);

            TGraph *grSpectrum = do_with_FFTtools(grPad);
                
            delete grSpectrum, grPad, grInt, grRaw;
            delete realAtriEvPtr;
        }

    }
    fpIn->Close();
    delete fpIn;
}
