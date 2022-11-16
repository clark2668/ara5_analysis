////////////////////////////////////////////////////////////////////////////////
////	get_rms.cpp
////
////  Get RMS for various channels (both software and non-cal pulser RF triggers)
////////////////////////////////////////////////////////////////////////////////

// C/C++ Includes
#include <iostream>
#include <cstdlib>
#include <sstream>
#include <fstream>
#include <stdio.h>
#include <vector>
#include <algorithm>

//AraRoot Includes
#include "RawAtriStationEvent.h"
#include "UsefulAtriStationEvent.h"

//ROOT Includes
#include "TTree.h"
#include "TFile.h"
#include "TCanvas.h"

// custom
#include "helper.h"

RawAtriStationEvent *rawAtriEvPtr;

using namespace std;

int main(int argc, char **argv){

    if(argc<6){
        std::cout<<"Use is " << basename(argv[0]) << " <station> <year> <output_dir> <output_name> <data_file>" <<std::endl;
        return -1;
    }
    int station = atoi(argv[1]);
    int year = atoi(argv[2]);
    string outDir = argv[3];
    string outName = argv[4];

    int nGraphs = 16;

    // these are output objects for ROOT
    int numSoftTriggers = 0;
    int numRFTriggers = 0;
    
    // these are run local
    vector<double> RMS_SoftTrigger_total;
    RMS_SoftTrigger_total.resize(nGraphs);
    vector<double> RMS_RFTrigger_total;
    RMS_RFTrigger_total.resize(nGraphs);

    TFile *fpIn = new TFile(argv[5], "OLD");
    if(!fpIn){
        std::cerr << "Cannot open file " <<argv[5] << std::endl;
        return -1;
    }
    fpIn->cd();
    TTree *eventTree = (TTree*) fpIn -> Get("eventTree");
    if(!eventTree){
        std::cerr << "Can't find eventTree in file "<<argv[5]<<std::endl;
        return -1;
    }

    eventTree->SetBranchAddress("event", &rawAtriEvPtr);
    int runNum;
    eventTree->SetBranchAddress("run", &runNum);
    eventTree->GetEntry(0);
    char ped_file_name[400];
    sprintf(ped_file_name, "/mnt/scratch/baclark/ARA/peds/A%d/reped_run_%06d.dat.gz", station, runNum);
    printf("The Pedestal filename is %s\n", ped_file_name);
    AraEventCalibrator *calibrator = AraEventCalibrator::Instance();
    calibrator->setAtriPedFile(ped_file_name,station);

    int numEntries = eventTree->GetEntries();
    int numToFind = 20;
    int numFound = 0;
    int firstUnixTime = -1000;
    for(int event=0; event<numEntries; event++){
        if(numFound > numToFind) break;
        eventTree->GetEntry(event);

        std::cout<<"On event "<<event<<std::endl;
        if(numFound==0){
            firstUnixTime = rawAtriEvPtr->unixTime;
        }

        UsefulAtriStationEvent *realAtriEvPtr;
        if (station < 3){
            realAtriEvPtr = new UsefulAtriStationEvent(rawAtriEvPtr, AraCalType::kLatestCalib);
        }
        else{
            // have to use buggy version for A4 and A5 until we get the ADC loading fixed...
            realAtriEvPtr =  new UsefulAtriStationEvent(rawAtriEvPtr, AraCalType::kLatestCalib14to20_Bug);
        }
        
        std::vector<TGraph*> waveforms = makeGraphsFromRF(realAtriEvPtr, nGraphs);
        
        std::vector<double> vWaveformRMS; // container for the RMSs
        getRMS(waveforms, vWaveformRMS, 0); // get the RMSs

        bool isSoftwareTrigger = rawAtriEvPtr->isSoftwareTrigger();
        bool isCalpulser = rawAtriEvPtr->isCalpulserEvent();

        if(isSoftwareTrigger){ // for software triggers
            // fancy vector-wise addition
            transform(
                RMS_SoftTrigger_total.begin(), RMS_SoftTrigger_total.end(), 
                vWaveformRMS.begin(), RMS_SoftTrigger_total.begin(),  std::plus<double>());
            numSoftTriggers++;            
        }
        else if (!isSoftwareTrigger && !isCalpulser){ // for RF triggers that are not tagged cal triggers
            transform(
                RMS_RFTrigger_total.begin(), RMS_RFTrigger_total.end(), 
                vWaveformRMS.begin(), RMS_RFTrigger_total.begin(), std::plus<double>());
            numRFTriggers++;
        }

        for(int chan=0; chan<waveforms.size(); chan++) delete waveforms[chan];
        delete realAtriEvPtr;
        numFound++;

    }

    cout << numRFTriggers << " : ";
    for (int i = 0; i < nGraphs; i++){
        RMS_RFTrigger_total[i] = RMS_RFTrigger_total[i]/(double)numRFTriggers;
        cout << RMS_RFTrigger_total[i] << " : "; 
        RMS_SoftTrigger_total[i] = RMS_SoftTrigger_total[i]/(double)numSoftTriggers;
    }
    cout << endl;

    // copy to output destination (arrays, cuz reasons...)
    double RMS_SoftTrigger[nGraphs];
    double RMS_RFTrigger[nGraphs];
    copy(RMS_RFTrigger_total.begin(), RMS_RFTrigger_total.begin()+nGraphs, RMS_RFTrigger);
    copy(RMS_SoftTrigger_total.begin(), RMS_SoftTrigger_total.begin()+nGraphs, RMS_SoftTrigger);

    // write to file
    char output_file_name[500];
    // sprintf(output_file_name, "%s/rms_run_%06d.root", outDir.c_str(), runNum);
    sprintf(output_file_name, "%s/%s", outDir.c_str(), outName.c_str());
    TFile *outputFile = TFile::Open(output_file_name, "RECREATE");
    TTree *outputTree = new TTree("rms_tree", "rms_tree");
    std::cout<<"runNum "<<runNum<<std::endl;
    outputTree->Branch("runNumber", &runNum, "runNumber/I");
    outputTree->Branch("unixTime", &firstUnixTime, "unixTime/I");
    outputTree->Branch("numSoftTriggers", &numSoftTriggers, "numSoftTriggers/I");
    outputTree->Branch("numRFTriggers", &numRFTriggers, "numRFTriggers/I");
    outputTree->Branch("RMS_SoftTrigger", &RMS_SoftTrigger, "RMS_SoftTrigger[16]/D");
    outputTree->Branch("RMS_RFTrigger", &RMS_RFTrigger, "RMS_RFTrigger[16]/D");
    outputTree->Fill();
    outputFile->Write();
    outputFile->Close();
    delete outputFile;

    fpIn->Close();
    delete fpIn;

}