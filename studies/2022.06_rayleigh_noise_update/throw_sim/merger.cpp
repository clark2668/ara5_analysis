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
    fm->OutputFile("merged.root");
    fm->AddFile("AraOut.noise_setup_1024.txt.run40003.root");
    fm->AddFile("AraOut.noise_setup_1024.txt.run40004.root");
    fm->Merge();

}//close the main program