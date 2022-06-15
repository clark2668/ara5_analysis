#!/bin/bash

setupfile=$1
outputdir=$2
runnumber=$3

source /home/brianclark/ARA/DevAraRoot/setup.sh

# get to the right folder and run AraSim
cd /home/brianclark/ARA/DevAraRoot/AraSim
./AraSim ${setupfile} ${runnumber} $TMPDIR

# at the end, move the results back
mv $TMPDIR/*.root $outputdir
