infile="/home/brian/ARA/ara5_analysis/ara5_analysis/studies/2022.06_rayleigh_noise_update/save_ffts/fft_run3315.root"

dag_file_name = 'dag_fit.dag'
instructions = ""
instructions += 'CONFIG config.dagman\n'
instructions += f'VARS ALL_NODES file="{infile}" \n\n'
with open(dag_file_name, 'w') as f:
    f.write(instructions)


master_index = 0
for channel in range(1):
    for bin in range(512):
        instructions = ""
        instructions += f"JOB job_{master_index} fit_rayleigh.htc \n"
        instructions += f'VARS job_{master_index} channel="{channel}" bin="{bin}" \n\n'
        
        with open(dag_file_name, 'a') as f:
            f.write(instructions)

        master_index+=1
