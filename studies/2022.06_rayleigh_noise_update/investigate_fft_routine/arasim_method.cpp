// C/C++ Includes
#include <iostream>
#include <cstdlib>
#include <sstream>
#include <fstream>
#include <stdio.h>
#include <vector>
#include <cmath>
#include <algorithm>

// ROOT includes
#include "TRandom3.h"
#include "TGraph.h"
#include "TCanvas.h"

#include "FFTtools.h"

//AraSim Includes
#include "Tools.h"

using namespace std;

int main(int argc, char **argv)
{

    std::cout<<"Hi "<<std::endl;

    TRandom3 *random = new TRandom3(123450);

    double dT = 0.5E-9; // nanoseconds
    int length = 1024;
    double sigma = 10E-3; // RMS noise; 10 mv
    double dF = 1./(double(length) * dT); // Hz
    double times[length];
    double volts[length];
    int newLength = (length/2)+1;

    double times_forrealft[length];
    double volts_forrealft[length];
    double spectrum_realft[length];

    double *volts_doFFT = new double [length];
    double *spectrum_doFFT = new double [newLength];

    // fill the time domain traces
    for(int i=0; i<length; i++){
        
        double t = double(i) * dT;
        double v = random->Gaus(0, sigma);

        times[i] = t;
        volts[i] = v;

        times_forrealft[i] = t;
        volts_forrealft[i] = v;

        volts_doFFT[i] = v;
    }

    bool compare_doFFT_to_AraSim = true;
    if(compare_doFFT_to_AraSim){

        FFTWComplex *theFFT = FFTtools::doFFT(length, volts);
        for(int i=0; i<newLength; i++){
            spectrum_doFFT[i] = FFTtools::getAbs(theFFT[i]);
        }

        Tools::realft(volts_forrealft, 1, length); // forward transform
        for(int i=0; i<newLength; i++){
            spectrum_realft[i] = 
                sqrt(
                    pow(volts_forrealft[2*i], 2.)
                    +
                    pow(volts_forrealft[2*i+1], 2.)
                );
            
        }
        
        for(int i=0; i<newLength; i++){
            printf("Sample %d, Org %.2e, New %.2e, Ratio %.2e \n",
                i, spectrum_doFFT[i], spectrum_realft[i],
                spectrum_doFFT[i]/spectrum_realft[i]
            );
        }


    }

    bool findNormalization = false;
    if(findNormalization){
        TGraph *grOrg = new TGraph(length, times, volts);

        Tools::realft(volts_forrealft, 1, length); // forward transform
        Tools::realft(volts_forrealft, -1, length); // reverse transform

        TGraph *grNew = new TGraph(length, times_forrealft, volts_forrealft);

        for(int i=0; i<length; i++){
            printf("Samp %d, Org %.2e, New %.2e, Ratio New/Org %.2e \n",
                i, grOrg->GetY()[i], grNew->GetY()[i],
                grNew->GetY()[i]/grOrg->GetY()[i]
            );
        }

        // so, AraSim requires a normalizing factor of 2/N (on the voltage!!)
        // to get "round trip" behavior...
        
        TCanvas *c = new TCanvas("", "", 1100, 850);
        c->Divide(1, 2);
        c->cd(1);
        grOrg->Draw("ALP");
        grOrg->SetTitle("Original");
        c->cd(2);
        grNew->Draw("ALP");
        grNew->SetLineColor(kRed);
        grNew->SetTitle("After rount trip FFT");
        c->SaveAs("hi.png");
    }




}
