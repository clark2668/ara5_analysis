#!/bin/bash

INFILE=$1
OUTFILE=$2
OUTDIR=$3

echo "Working on file "$INFILE
echo "Output file name "$OUTFILE

source /cvmfs/ara.opensciencegrid.org/trunk/centos7/setup.sh
${ARA_UTIL_INSTALL_DIR}/bin/repeder $INFILE $OUTFILE -d -x hist_channel_mask=0x0f0f0f0f

echo "Repder done, preparing to zip..."

gzip $OUTFILE

echo "Zipping done, preparing to move..."

cp ${OUTFILE}.gz $OUTDIR/.

echo "File move complete"

rm ${OUTFILE}.gz

echo "Cleanup done"