////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
////	save_fft.cxx
////
////	March 2019,  clark.2668@osu.edu
////	Make an FFT of every soft trigger and save the spectral coefficient
////////////////////////////////////////////////////////////////////////////////

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
#include "AraGeomTool.h"
#include "AraQualCuts.h"

//ROOT Includes
#include "TTree.h"
#include "TFile.h"
#include "TGraph.h"
#include "TCanvas.h"

RawAtriStationEvent *rawAtriEvPtr;
UsefulAtriStationEvent *realAtriEvPtr;

using namespace std;

TGraph *makeFreqV_MilliVoltsNanoSeconds ( TGraph *grWave );

int main(int argc, char **argv)
{
    if(argc<5) {  // Check to make sure there are enough arguments to do something meaningful
        std::cout << "Usage requires you to provide input parameter of the form " << basename(argv[0]) << " <output_dir> <data_file> <is_simulation> <run_number>" << std::endl;
        return -1;
    }

    int isSimulation = atoi(argv[3]);
    int runNumber = atoi(argv[4]);

    TFile *fpIn = new TFile(argv[2], "OLD"); //we're going to open the data file
    if(!fpIn){
        std::cerr<< "Can not open the old file: " <<argv[2]<<endl;
        return -1;
    } //throw a warning if you can't open it
    fpIn->cd(); //go into that file
    TTree *eventTree = (TTree*) fpIn->Get("eventTree"); //load in the event free for this file
    if(!eventTree){
        std::cerr<<"Can't find eventTree in file" <<argv[2]<<endl;
        return -1;
    } //throw a warning if you can't open it


    if(isSimulation){
        eventTree->SetBranchAddress("UsefulAtriStationEvent", &realAtriEvPtr);
        printf("Doing Simulation \n");
    }
    else{
        eventTree->SetBranchAddress("event", &rawAtriEvPtr);
        printf("Doing Data \n");
        int runNum;
        eventTree->SetBranchAddress("run",&runNum);
        eventTree->GetEntry(0);
        int station=rawAtriEvPtr->stationId;
        int unixtime = rawAtriEvPtr->unixTime;
        time_t test_time = unixtime;
        tm *time = gmtime( &test_time );
        int year = time->tm_year+1900;

        printf("Filter Run Number %d \n", runNum);
        char ped_file_name[400];
        sprintf(ped_file_name, "/disk20/users/brian/ARA/peds/%d/A%d/reped_run_%06d.dat.gz", year, station, runNum);
        printf("The Pedestal filename is %s\n", ped_file_name);

        AraEventCalibrator *calibrator = AraEventCalibrator::Instance();
        calibrator->setAtriPedFile(ped_file_name,station); //because someone had a brain (!!), this will error handle itself if the pedestal doesn't exist
        
        runNumber = runNum;
    }

    char outfile_name[400];
    sprintf(outfile_name,"%s/fft_run%d.root",argv[1],runNumber);
    TFile *fpOut = TFile::Open(outfile_name, "RECREATE");
    TTree* outTree = new TTree("outTree", "outTree");
    double chan_spec[16][512]={{0}};
    double freqs[16][512]={0};
    outTree->Branch("chan_spec", &chan_spec, "chan_spec[16][512]/D");
    outTree->Branch("freqs", &freqs, "freqs[16][512]/D");

    fpIn->cd();
    double numEntries = eventTree -> GetEntries(); //get the number of entries in this file

    AraQualCuts *qual = AraQualCuts::Instance();
    int num_found=0;
    std::cout<<"Num Entries "<<numEntries<<std::endl;
    numEntries/=5;
    for(int event=0; event<numEntries; event++){ //loop over those entries
        eventTree->GetEntry(event); //get the event
        
        bool isSoftTrigger;
        if(isSimulation){
            // simulation is always software trigger
            isSoftTrigger=true;
        }
        else{
            // otherwise actually check
            isSoftTrigger = rawAtriEvPtr->isSoftwareTrigger();
        }
        
        if(isSoftTrigger){
            std::cout<<"On event "<<event<<std::endl;

            // if we're working with data, then we actually need to instantiate the real pointer
            if(!isSimulation){
                realAtriEvPtr = new UsefulAtriStationEvent(rawAtriEvPtr, AraCalType::kLatestCalib);
            }

            bool theQual;
            if(isSimulation){
                theQual = true;
            }
            else{
                theQual = qual->isGoodEvent(realAtriEvPtr);
            }


            if(theQual){

                std::vector<TGraph*> waveforms;
                std::vector<TGraph*> spectra;

                for(int chan=0; chan<16; chan++){
                    TGraph *grRaw = realAtriEvPtr->getGraphFromRFChan(chan);
                    TGraph *grInt = FFTtools::getInterpolatedGraph(grRaw, 0.5);
                    TGraph *grPad = FFTtools::padWaveToLength(grInt,1024);
                    TGraph *spec = makeFreqV_MilliVoltsNanoSeconds(grPad);
                    for(int samp=0; samp<512; samp++){
                        chan_spec[chan][samp]=spec->GetY()[samp];
                        freqs[chan][samp]=spec->GetX()[samp];
                    }
                    waveforms.push_back((TGraph*) grInt->Clone());
                    spectra.push_back((TGraph*) spec->Clone());

                    delete spec;
                    delete grPad;
                    delete grInt;
                    delete grRaw;
                }
                outTree->Fill();
                num_found++;


                /*
                TCanvas *cTime = new TCanvas("","",1100,850);
                cTime->Divide(4,4);
                for(int i=0; i<16; i++){
                    cTime->cd(i+1);
                    waveforms[i]->Draw("ALP");
                    waveforms[i]->GetYaxis()->SetRangeUser(-50, 50);
                }
                char savetitle[500];
                sprintf(savetitle, "./plots/run%d_ev%d_sim%d_waveforms.png", runNumber, event, isSimulation);
                cTime->SaveAs(savetitle);
                
                TCanvas *cFreq = new TCanvas("","",1100,850);
                cFreq->Divide(4,4);
                for(int i=0; i<16; i++){
                    cFreq->cd(i+1);
                    spectra[i]->Draw("ALP");
                    spectra[i]->GetYaxis()->SetRangeUser(1E-3, 2);
                    gPad->SetLogy();
                }
                sprintf(savetitle, "./plots/run%d_ev%d_sim%d_spectra.png", runNumber, event, isSimulation);
                cFreq->SaveAs(savetitle);
                */


            }
            
            if(!isSimulation){
                // only delete if it's not simulation
                delete realAtriEvPtr;
            }
        }
    }
    fpOut->Write();
    fpOut->Close();
    delete fpOut;

    fpIn->Close();
    delete fpIn;
}//close the main program


TGraph *makeFreqV_MilliVoltsNanoSeconds ( TGraph *grWave ) {
    double *oldY = grWave->GetY(); // mV
    double *oldX = grWave->GetX(); // ns
    int length=grWave->GetN();
    double deltaT = (oldX[1]-oldX[0]) * 1.e-9; // deltaT in s
    FFTWComplex *theFFT=FFTtools::doFFT(length,oldY); // FFT with mV unit
    int newLength=(length/2)+1;
    double *newY = new double [newLength];
    double *newX = new double [newLength];
    double deltaF=1./(deltaT*(double)length); //Hz
    double tempF=0;
    for(int i=0;i<newLength;i++) {
        
       
        // newY[i] = sqrt(2./double(grWave->GetN())) * FFTtools::getAbs(theFFT[i]); // from mV to V

        // normalize by N and deltaF for export to AraSim
        // this is necessary so that AraSim can scale the sigma values to different
        // length of waveform and frequency bin width step
        double temp = FFTtools::getAbs(theFFT[i]);
        temp *= 1E-3; // convert from mV to V
        temp /= double(length);
        temp /= sqrt(deltaF);

        newY[i] = temp;
        newX[i]=tempF;
        tempF+=deltaF;
    }
    TGraph *grSpectrum = new TGraph(newLength,newX,newY);

    // check Parseval

    // // time domain
    // double power_time = 0;
    // for(int i=0; i<grWave->GetN(); i++ ){
    //     power_time += TMath::Power(grWave->GetY()[i], 2.);
    // }

    // // frequency domain
    // double power_freq = 0;
    // for(int i=0; i<grSpectrum->GetN(); i++){
    //     power_freq += TMath::Power(grSpectrum->GetY()[i], 2.);
    // }

    // std::cout<<"Power time "<<power_time<<" and power frequency "<<power_freq<<std::endl;

    delete [] theFFT;
    delete [] newY;
    delete [] newX;
    return grSpectrum;
}

