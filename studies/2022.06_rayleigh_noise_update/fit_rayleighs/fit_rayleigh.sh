#!/bin/bash

infile=$1
channel=$2

#source /home/brianclark/ARA/DevAraRoot/setup.sh
source /home/brian/ARA/ara5_analysis/setup.sh 

# get to working directory
# cd /home/brianclark/ARA/ara5_analysis/ara5_analysis/studies/2022.06_rayleigh_noise_update/fit_rayleighs
cd /home/brian/ARA/ara5_analysis/ara5_analysis/studies/2022.06_rayleigh_noise_update/fit_rayleighs

# loop over frequency bins
for bin in {0..512}
do
    ./fit_rayleigh ${infile} ${channel} ${bin}
done
