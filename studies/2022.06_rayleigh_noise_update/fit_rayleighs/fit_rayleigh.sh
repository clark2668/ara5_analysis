#!/bin/bash

infile=$1
channel=$2
frequency=$3

source /home/brianclark/ARA/DevAraRoot/setup.sh

cd /home/brianclark/ARA/DevAraRoot/rayleigh/fit_rayleighs
./fit_rayleigh ${infile} ${channel} ${frequency}
