// C/C++ Includes
#include <iostream>
#include <fstream>
#include <cstring>
#include <zlib.h>
#include <sstream>
#include <cstdlib>

#include "AraEventCalibrator.h"
#include "UsefulAtriStationEvent.h"

using namespace std;

int numberOfPedestalValsInBuffer(std::stringstream &buffer){
    int numPedVals=0;
    std::string dummy;
    while(buffer >> dummy >> dummy >> dummy){
        for(int samp=0; samp < SAMPLES_PER_BLOCK; samp++){
            buffer >> dummy;
            numPedVals++;
        }
    }
    return numPedVals;
}

int main(int argc, char **argv)
{

    // std::string file = "reped_run_1448.dat.gz";
    // std::string file = "reped_run_1448_raw.dat";
    char bleh[400];
    gzFile inPed = gzopen(file.c_str(), "r");
    if(inPed){

        int numExpected = DDA_PER_ATRI*BLOCKS_PER_DDA*RFCHAN_PER_DDA*SAMPLES_PER_BLOCK;
        std::cout<<"Num expected "<<numExpected<<std::endl;
        char buffer[6000000];
        int nRead = gzread(inPed, &buffer, sizeof(buffer)/sizeof(buffer[0])-1);

        std::string string_buffer(buffer); // shove this back into a string
        std::stringstream ss_test(string_buffer); // and then convert to stringstream

        int numPedVals = numberOfPedestalValsInBuffer(ss_test);
        
        std::stringstream ss(string_buffer); // and then convert to stringstream

        std::string dda_buf;
        std::string block_buf;
        std::string chan_buf;
        std::string ped_buf;

        while ( ss >> dda_buf >> block_buf >> chan_buf){
            int dda = std::stoi(dda_buf);
            int block = std::stoi(block_buf);
            int chan = std::stoi(chan_buf);

            for(int samp=0; samp < SAMPLES_PER_BLOCK; samp++){
                ss >> ped_buf;
                short pedVal = short(std::stoi(ped_buf));
            }
        }
    }
}
