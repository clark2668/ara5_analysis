infile="/home/brianclark/ARA/DevAraRoot/rayleigh/fft_run3315.root"
channel = 0

dag_file_name = 'dag_fit.dag'
instructions = ""
instructions += 'CONFIG config.dagman\n'
instructions += f'VARS ALL_NODES file="{infile}" \n\n'
with open(dag_file_name, 'w') as f:
    f.write(instructions)


master_index = 0
for freq_bin in range(12):
    instructions = ""
    instructions += f"JOB job_{master_index} fit_rayleigh.htc \n"
    instructions += f'VARS job_{master_index} channel="{channel}" freqbin="{freq_bin}" \n\n'
    
    with open(dag_file_name, 'a') as f:
        f.write(instructions)

    master_index+=1
