#!/bin/bash

infile=$1
channel=$2

source /home/brianclark/ARA/DevAraRoot/setup.sh

# loop over frequency bins
cd /home/brianclark/ARA/ara5_analysis/ara5_analysis/studies/2022.06_rayleigh_noise_update/fit_rayleighs
for bin in {0..512}
do
    ./fit_rayleigh ${infile} ${channel} ${bin}
done
