#!/bin/bash
#SBATCH --job-name=runRepeder_A2_Y2013
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=8G
#SBATCH --time=00:20:00
#SBATCH --export=ALL
#SBATCH --array=0-2
#SBATCH --output=logs/run_batch_%A_%a.out
#SBATCH --error=logs/run_batch_%A_%a.err
#SBATCH --qos=deyoungbuyin_large

STATION=2
YEAR=2013

in_files_dir='/mnt/scratch/baclark/ARA/burn/'${YEAR}'/A'${STATION}
out_files_dir='/mnt/scratch/baclark/ARA/peds/A'${STATION}
echo $in_files_dir
echo $out_files_dir

# FILES=($in_files_dir/*.root)
readarray -t FILES < files/filelist_a${STATION}_y${YEAR}_burn.txt

# input_file=${FILES[1]}
input_file=${FILES[SLURM_ARRAY_TASK_ID]}
echo $input_file

output_file=`basename $input_file .root`

# fancy awk to get the 00XXXX run number
output_file=$(echo "$output_file" | awk -F '_' '{print $2}' )
output_file="reped_run_"${output_file}".dat"

source /mnt/home/baclark/ara/ara5_analysis/studies/2022.11_proposal/env.sh
${ARA_UTIL_INSTALL_DIR}/bin/repeder -d -m 0 -M 4096 $input_file $output_file

if test -f "$output_file"; then

    echo "Repder done, preparing to zip..."
    gzip $output_file

    echo "Zipping done, preparing to move..."

    cp ${output_file}.gz $out_files_dir/.

    echo "File move complete"

    rm ${output_file}.gz

    echo "Cleanup done"
else
    echo "$output_file does NOT exist -- repeder failed. Fail!"
    echo "Stats: $input_file $output_file $out_files_dir"
    echo $input_file >> /mnt/home/baclark/ara/ara5_analysis/studies/2022.11_proposal/get_run_list/files/redo_reped_${STATION}_${YEAR}.txt
    exit 1
fi