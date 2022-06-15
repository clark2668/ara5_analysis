setup_file = "/home/brianclark/ARA/DevAraRoot/throw_sim/noise_setup.txt"
output_dir = "/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning"

dag_file_name = 'dag_sim.dag'
instructions = ""
instructions += 'CONFIG config.dagman\n'
instructions += f'VARS ALL_NODES setupfile="{setup_file}" outputdir="{output_dir}"\n\n'
with open(dag_file_name, 'w') as f:
    f.write(instructions)


master_index = 200000
for run_number in range(0, 20, 1):
    instructions = ""
    instructions += f"JOB job_{run_number} run_sim.htc \n"
    instructions += f'VARS job_{run_number} runnumber="{master_index+run_number}" \n\n'
    
    with open(dag_file_name, 'a') as f:
        f.write(instructions)
