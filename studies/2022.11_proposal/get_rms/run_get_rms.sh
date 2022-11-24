#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=00:20:00
#SBATCH --export=ALL
#SBATCH --output=logs/run_batch_%A_%a.out
#SBATCH --error=logs/run_batch_%A_%a.err
#######SBATCH --partition=deyoungbuyin
#SBATCH -A general
#######SBATCH -A deyoungbuyin
########SBATCH --qos=deyoungbuyin_large
######SBATCH --qos=scavenger

#SBATCH --job-name=RMS_A2_Y2014
#SBATCH --array=0-999

STATION=2
YEAR=2014

in_files_dir='/mnt/scratch/baclark/ARA/burn/'${YEAR}'/A'${STATION}
out_files_dir='/mnt/scratch/baclark/ARA/rms/'${YEAR}'/A'${STATION}
echo $in_files_dir
echo $out_files_dir

readarray -t FILES < ../get_run_list/files/filelist_a${STATION}_y${YEAR}_burn.txt

input_file=${FILES[SLURM_ARRAY_TASK_ID]}
echo $input_file

output_file=`basename $input_file .root`

# fancy awk to get the 00XXXX run number
output_file=$(echo "$output_file" | awk -F '_' '{print $2}' )
output_file="rms_run_"${output_file}".root"

echo $output_file

source /mnt/home/baclark/ara/ara5_analysis/studies/2022.11_proposal/env.sh
cd /mnt/home/baclark/ara/ara5_analysis/studies/2022.11_proposal/get_rms/
./get_rms $STATION $YEAR $TMPDIR/. $output_file $input_file

if test -f "$TMPDIR/$output_file"; then

    echo "RMS file was generated moving..."

    cp ${TMPDIR}/${output_file} $out_files_dir/.

    echo "File move complete"

else
    echo "$output_file does NOT exist -- repeder failed. Fail!"
    echo "Stats: $input_file $output_file $out_files_dir"
    echo $input_file >> /mnt/home/baclark/ara/ara5_analysis/studies/2022.11_proposal/get_run_list/files/redo_rms_${STATION}_${YEAR}.txt
    exit 1
fi