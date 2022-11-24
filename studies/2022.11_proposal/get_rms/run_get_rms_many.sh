#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=01:30:00
#SBATCH --export=ALL
#SBATCH --output=logs/run_batch_%A_%a.out
#SBATCH --error=logs/run_batch_%A_%a.err
#######SBATCH --partition=deyoungbuyin
######SBATCH -A general
#######SBATCH -A deyoungbuyin
#SBATCH --qos=deyoungbuyin_large
######SBATCH --qos=scavenger



# pre 2018, 2400 is enough
# for 2018+, need 3068 (A3)
# for 2019+, need 3400 (A3 again)
# for 2020+, need 3000 (about all of them)
# for 2021, need 3000 (about all of them)
# for 2022, need 3000 (more like 2800, but yolo)

# each run can take up to 4 minutes
# for 20 runs, therefore need 90 minutes to be safe


#SBATCH --job-name=RMS_A1_Y2022
#SBATCH --array=0-3000:20

STATION=1
YEAR=2022

in_files_dir='/mnt/scratch/baclark/ARA/burn/'${YEAR}'/A'${STATION}
out_files_dir='/mnt/scratch/baclark/ARA/rms/'${YEAR}'/A'${STATION}
echo $in_files_dir
echo $out_files_dir

readarray -t FILES < ../get_run_list/files/filelist_a${STATION}_y${YEAR}_burn.txt

start_index=$SLURM_ARRAY_TASK_ID
stop_index=$(($start_index+19))

echo "Starter is " $start_index
for i in $(seq $start_index 1 $stop_index)
do
    input_file=${FILES[i]}
    echo "Input file" $input_file

    output_file=`basename $input_file .root`

    # fancy awk to get the 00XXXX run number
    output_file=$(echo "$output_file" | awk -F '_' '{print $2}' )
    output_file="rms_run_"${output_file}".root"

    echo "Output file" $output_file

    source /mnt/home/baclark/ara/ara5_analysis/studies/2022.11_proposal/env.sh
    cd /mnt/home/baclark/ara/ara5_analysis/studies/2022.11_proposal/get_rms/
    ./get_rms $STATION $YEAR $TMPDIR/. $output_file $input_file

    if test -f "$TMPDIR/$output_file"; then

        echo "RMS file was generated moving..."

        cp ${TMPDIR}/${output_file} $out_files_dir/.

        echo "File move complete"

    else
        echo "$output_file does NOT exist -- rms failed. Fail!"
        echo "Stats: $input_file $output_file $out_files_dir"
        echo $input_file >> /mnt/home/baclark/ara/ara5_analysis/studies/2022.11_proposal/get_run_list/files/redo_rms_${STATION}_${YEAR}.txt
        # exit 1
        continue
    fi


done

