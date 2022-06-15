// C/C++ Includes
#include <iostream>
#include <cstdlib>
#include <sstream>
#include <fstream>
#include <stdio.h>
#include <vector>
#include <cmath>
#include <algorithm>

#include "TFileMerger.h"


using namespace std;

int main(int argc, char **argv)
{
    TFileMerger *fm;
    fm = new TFileMerger(kFALSE);
    fm->OutputFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/merged.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200000.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200001.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200002.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200003.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200004.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200005.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200006.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200007.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200008.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200009.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200010.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200011.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200012.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200013.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200014.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200015.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200016.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200017.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200018.root");
    fm->AddFile("/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/AraOut.noise_setup.txt.run200019.root");
    fm->Merge();

}//close the main program