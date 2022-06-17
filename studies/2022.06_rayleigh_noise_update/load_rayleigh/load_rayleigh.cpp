// C/C++ Includes
#include <iostream>
#include <cstdlib>
#include <sstream>
#include <fstream>
#include <stdio.h>
#include <vector>
#include <cmath>
#include <algorithm>
#include <sys/stat.h>
#include <stdexcept>

//ROOT Includes
#include "TTree.h"
#include "TFile.h"
#include "TGraph.h"
#include "TCanvas.h"
#include "TAxis.h"

#include "Tools.h"

using namespace std;

void loadFile(string filename){

    int DATA_BIN_SIZE = 16384; //FIXME: this needs to change back to the settings1 value
    double TIMESTEP = 3.125e-10; //FIXME: this needs to change back to the settings1 value
    int numChans = 16; // FIXME: don't assume the number of channels

    // first, check if the file exists
    char errorMessage[400];
    struct stat buffer;

    bool rayleighFileExists = (stat(filename.c_str(), &buffer)==0);
    if (!rayleighFileExists){
        sprintf(errorMessage, "Rayleigh noise fits file is not found (rayleigh file exists %d) ", rayleighFileExists);
        throw std::runtime_error(errorMessage);
    }

    ifstream rayleighFile(filename.c_str()); // open the file
    string line; // a dummy variable we can stream over

    // first, make sure our user has formatted the file correctly
    // in particular, it means we really need to see the word "Frequency" as the first word in the header file
    string expected_first_column_header = "Frequency";
    if(rayleighFile.is_open()){
        while(rayleighFile.good()){
            getline(rayleighFile, line, ',');
            string first_header_entry = line.c_str();
            if (! (first_header_entry == expected_first_column_header)){
                sprintf(errorMessage, 
                    "The first word of the header line is '%s'. It was expected to be '%s'. Please double check file format!!", 
                    first_header_entry.c_str(),
                    expected_first_column_header.c_str());
                throw std::runtime_error(errorMessage);
            }
            else{
                // otherwise, the first header of the file is correct, and we can proceed
                break;
            }
        }
    }
    else{
        sprintf(errorMessage, "Rayleigh noise file did not open correctly.");
        throw std::runtime_error(errorMessage);

    }
    // go back to the beginning of the file
    // we have already verified that the file exists, so no need to check again...
    rayleighFile.clear();
    rayleighFile.seekg(0, ios::beg);

   
    // second, figure out how many frequency bins are available
    int lineCount = 0;
    if(rayleighFile.is_open()){
        while(rayleighFile.peek()!=EOF){
            getline(rayleighFile, line);
            lineCount++;
        }
    }
    rayleighFile.clear(); // back to the beginning of the file again
    rayleighFile.seekg(0, ios::beg);
    int numFreqBins = lineCount - 1; // one row is dedicated to headers; number of freq bins is therefore # rows - 1

    // Set up containers to stream the csv file into.
    // vector of the frequencies
    std::vector<double> frequencies;
    frequencies.resize(numFreqBins); // resize to account for the number of frequency bins
    
    /*
    Then a vector of vectors to hold the fit values.
    The first dimension is for the number of channels (so this is "number of channels" long).
    The second dimension is for the number of frequency bins (so this is "number of frequency bins" long).
    (which goes first and which goes second is arbitrary; 
    the TestBed version does it in this order, so replicate here)
    */
    std::vector< std::vector <double> > fits; 
    fits.resize(numChans); // resize to account for number of channels
    for(int iCh=0; iCh<numChans; iCh++) fits[iCh].resize(numFreqBins); // resize to account for number of freq bins


    /*
    Now, we loop over the rows of the file again,
    and get the frequency values out, as well as the fit values
    */
    int theLineNo = 0; // an indicator so we know if we are on the first line of the file
    if (rayleighFile.is_open()){
        while(rayleighFile.good()){

            if(theLineNo == 0 ){
                // skip the first line (the header file)
                getline (rayleighFile, line);
                theLineNo++;
            }
            else{
                /*
                from the second line forward, read in the values
                the first column is the frequency
                the second, third, etc. column should be the fit values for all channels.
                so we need to loop over all the comma separated entries in the single line
                */

                // first, peel off the frequency
                int theFreqBin = theLineNo -1 ;
                getline(rayleighFile, line, ',');
                double temp_freq_val = atof(line.c_str()); // the frequency in MHz
                if(std::isnan(temp_freq_val) || temp_freq_val < 0 || temp_freq_val > 1200){
                    sprintf(errorMessage, 
                            "A rayleigh frequency value (freq bin %d) is a nan or negative or very large (%e). Stop!", 
                            temp_freq_val);
                    throw std::runtime_error(errorMessage);
                }
                // printf("Frequency bin %d value is %f \n", theFreqBin, temp_freq_val);
                frequencies[theFreqBin] = temp_freq_val;

                /*
                then loop over the channels, splitting most on the comma ","
                Because the "separating" character for the very last channel is a newline (\n),
                we have to loop over n_channels - 1 here,
                and then change to the newline characeter for the final channel
                (see below).
                */
                int numCols = 0;
                while(numCols < numChans-1){
                    getline(rayleighFile, line, ',');
                    double temp_fit_val = atof(line.c_str());
                    if(std::isnan(temp_fit_val) || temp_fit_val < 0 || temp_fit_val > 20){
                        sprintf(errorMessage, 
                            "A rayleigh fit value (freq bin %d, ch %d) is a nan or negative or very large. Stop!", 
                            theFreqBin, numCols, temp_fit_val);
                        throw std::runtime_error(errorMessage);
                    }
                    // printf("  The Fit Val for Freq Bin %d, Col %d, is %.4f \n", theFreqBin, numCols, temp_fit_val);
                    fits[numCols][theFreqBin] = temp_fit_val;
                    numCols++; // advance number of columns
                }

                // once more to get the final channel, this time we need to detect the newline character
                // NB: at this point, numCols == final channel number, so we can just use it
                // (no need to incremete numCols again)
                getline(rayleighFile, line, '\n');
                double temp_fit_val = atof(line.c_str());
                // printf("  The Fit Val for Freq Bin %d, Col %d, is %.4f \n", theFreqBin, numCols, temp_fit_val);
                fits[numCols][theFreqBin] = temp_fit_val;

                // now we're done!
                theLineNo++; //advance the line number

            }
        }
    }
    rayleighFile.close(); 
    
    // can be useful for debugging (leave commented out for now)
    // for(int iCh=0; iCh<fits.size(); iCh++){
    //     printf("Channel %d \n", iCh);
    //     for(int iFbin=0; iFbin < fits[iCh].size(); iFbin++){
    //         printf("  Freq Bin %d, Fit Val us %.4f \n", iFbin, fits[iCh][iFbin]);
    //     }
    // }

    /*
    Now, we have loaded the frequencies with the sampling a user inputs.
    We need to interpolate them onto the frequency space needed by AraSim.
    */

    double df_fft = 1./ ( (double)(DATA_BIN_SIZE) * TIMESTEP ); // the frequency step
    
    double interp_frequencies_databin[DATA_BIN_SIZE/2];   // array for interpolated FFT frequencies
    for(int i=0; i<DATA_BIN_SIZE/2.; i++){
        // set the frequencies
        interp_frequencies_databin[i] = (double)i * df_fft / (1.E6); // from Hz to MHz
    }
    std::vector< std::vector< double > > fits_databin_ch; // same structure as fits, but this time interpolated
    fits_databin_ch.resize(fits.size()); // resize to number of channels

    // loop over channel, and do the interpolation
    for(int iCh=0; iCh<fits.size(); iCh++){

        // the content of the vectors needs to be stuffed into arrays for the interpolator
        // dumb, but oh well...
        double original_frequencies_asarray[numFreqBins];
        std::copy(frequencies.begin(), frequencies.end(), original_frequencies_asarray);

        double original_fits_asarray[numFreqBins];
        std::copy(fits[iCh].begin(), fits[iCh].end(), original_fits_asarray);

        // output value
        double interp_fits_databin[DATA_BIN_SIZE/2];   // array for interpolated rayleigh fit values

        // now, do interpolation
        Tools::SimpleLinearInterpolation(
            numFreqBins, original_frequencies_asarray, original_fits_asarray, // from the original binning
            DATA_BIN_SIZE/2, interp_frequencies_databin, interp_fits_databin // to the new binning
            );
        
        // copy the interpolated values out
        for(int iFreqBin=0; iFreqBin<DATA_BIN_SIZE/2; iFreqBin++){
            fits_databin_ch[iCh].push_back( interp_fits_databin[iFreqBin] );
        }

    }

    // and now we're good and truly done
    
    // let's see our handy work by making a simple plot
    TCanvas *c = new TCanvas("","", 1100, 850);
    TGraph *grOld = new TGraph(frequencies.size(), &frequencies[0], &fits[3][0]);
    TGraph *grNew = new TGraph(DATA_BIN_SIZE/2, interp_frequencies_databin, &fits_databin_ch[3][0]);
    grNew->Draw("ALP");
    grOld->Draw("LPsame");
    // grOld->GetXaxis()->SetRangeUser(0., 2000.);
    grNew->SetLineColor(kRed);
    c->SaveAs("interp_test.png");

}


int main(int argc, char **argv)
{
    
    loadFile("merged.txt");

}//close the main program