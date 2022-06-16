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

using namespace std;

void loadFile(string filename){

    // first, check if the file exists
    char errorMessage[400];
    struct stat buffer;

    bool rayleighFileExists = (stat(filename.c_str(), &buffer)==0);
    if (!rayleighFileExists){
        sprintf(errorMessage, "Rayleigh noise fits file is not found (rayleigh file exists %d) ", rayleighFileExists);
        throw std::runtime_error(errorMessage);
    }

    ifstream rayleighFile(filename.c_str());

    int numChans = 16; // FIXME: don't assume the number of channels 

    int init = 1; // an indicator so we know if we are on the first line of the file
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

    // first, figure out how many frequency bins we have
    int lineCount = 0;
    if(rayleighFile.is_open()){
        while(rayleighFile.peek()!=EOF){
            getline(rayleighFile, line);
            lineCount++;
        }
    }
    else{
        sprintf(errorMessage, "Rayleigh noise file did not open correctly.");
        throw std::runtime_error(errorMessage);

    }
    int numFreqBins = lineCount - 1; // one row is dedicated to headers; number of freq bins is therefore # rows - 1
    std::cout<<"Number of freq bins "<<numFreqBins<<endl;

    // // go back to the beginning
    // // we have already verified that the file exists, so no need to check again...
    // rayleighFile.clear();
    // rayleighFile.seekg(0, ios::beg);
    // if (rayleighFile.is_open()){

    //     while(rayleighFile.good()){

    //         if(init==1){

    //         }

    //         if(init ==1){
    //             // skip the first line
    //             getline (rayleighFile, line);
    //             init++;
    //         }
    //         else{
    //             /*
    //             from the second line forward, read!
    //             the first column is the frequency
    //             the second, third, etc. column should be the fit values for all channels.
    //             so we need to loop
    //             */

    //             // first, peel off the frequency
    //             getline(rayleighFile, line, ',');
    //             double temp_freq_val = atof(line.c_str()); // the frequency in MHz
    //             printf("Frequency value is %f \n", temp_freq_val);

    //             /*
    //             then loop over the channels
    //             because the "separating" character for the very last channel is a newline (\n)
    //             we have to loop over n_channels - 1 here
    //             and then change the newline characeter for the final channel to \n
    //             (see below)
    //             */
    //             int num_cols = 0;
    //             while(num_cols < numChans-1){

    //                 getline(rayleighFile, line, ',');
    //                 double temp_fit_val = atof(line.c_str());
    //                 printf("  The Fit Val for Col %d is %.4f \n", num_cols, temp_fit_val);
    //                 num_cols++; // advance number of columns

    //             }

    //             // once more to get the final channel, this time we need to detect the newline character
    //             num_cols++;
    //             getline(rayleighFile, line, '\n');
    //             double temp_fit_val = atof(line.c_str());
    //             printf("  The Fit Val for Col %d is %.4f \n", num_cols, temp_fit_val);


    //             // now we're done!

    //         }
    //     }        
    // }


}


int main(int argc, char **argv)
{
    
    loadFile("merged.txt");

}//close the main program