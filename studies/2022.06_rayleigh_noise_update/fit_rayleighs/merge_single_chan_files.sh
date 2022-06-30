#!/bin/bash

for i in {0..15}
do
    echo "Frequency,Channel,Fit,ChiSquare" > sigmavsfreq_ch$i.txt
    cat fits/sigmavsfreq_ch${i}_*.txt > sigmavsfreq_ch$i.txt
done