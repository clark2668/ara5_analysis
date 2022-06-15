import argparse
import os
import path_tools as pt

# years = [2013, 2014, 2015, 2016, 2017, 2018]
stations = [1, 2, 3, 4, 5]
years = [2018]
sample = 'full'
top_dir = '/data/user/brianclark/ARA/ara5_analysis/data/full'
ped_dir = '/data/user/brianclark/ARA/ara5_analysis/peds'

# set top dir to ped dir to make directory structure for peds
# top_dir = ped_dir

mode = 0o744


'''
Locate the original files on disk, and write them to a file
'''
find_original_files = True
if find_original_files:
    for y in years:
        for s in stations:

            if y < 2018 and s > 3:
                continue

            print("Year {}, on station {}".format(y, s))

            file_list = pt.list_all_files(s, y, sample)
            if len(file_list) < 1:
                print("Skipping A{} {}".format(s, y))
                continue
            out_filename = f"files/orig_filelist_a{s}_y{y}_{sample}.txt"

            with open(out_filename, 'w') as f:
                for file in file_list:
                    f.write(f"{file}\n")

'''
Make the output directories for the file symlinks
'''
make_output_directories = True
if make_output_directories:
    for y in years:
        year_dir = os.path.join(top_dir, f"{y}")
        if not os.path.isdir(year_dir):
            os.mkdir(year_dir, mode)

        for s in stations:
            in_filename = f"files/orig_filelist_a{s}_y{y}_{sample}.txt"
            if os.path.isfile(in_filename):
                station_dir = os.path.join(year_dir, f"A{s}")
                if not os.path.isdir(station_dir):
                    os.mkdir(station_dir, mode)
            else:
                print(f"File list ({in_filename}) doesn't exist")

'''
Actually make symlinks
'''
make_symlinks = True
if make_symlinks:
    for y in years:
        for s in stations:

            print("Working on symlinks for Y {}, Station {}".format(y, s))
            in_filename = f"./files/orig_filelist_a{s}_y{y}_{sample}.txt"
            
            if os.path.isfile(in_filename):
                file = open(in_filename, "r")
                for line in file:
                    src_file = line.split()[0] # grab the zero entry

                    run_num = pt.harvest_run_num(src_file)
                    
                    trg_dir = os.path.join( top_dir, f"{y}", f"A{s}")
                    if not os.path.isdir(trg_dir):
                        raise OSError(f"A target directory ({trg_dir}) is missing.")

                    run_num = str(run_num)
                    run_num = run_num.zfill(6) # make it six characters long
                    
                    trg_file = os.path.join(trg_dir, f"event_{run_num}.root")
                    if not os.path.isfile(trg_file):
                        os.symlink(src_file, trg_file)

                file.close()

'''
Harvest new file locations
'''
find_new_files = True
if find_new_files:
    for y in years:
        for s in stations:
            the_dir = os.path.join(top_dir, f"{y}", f"A{s}")

            if os.path.isdir(the_dir):
                file_list = sorted(os.listdir(the_dir))

                out_filename = f"./files/filelist_a{s}_y{y}_{sample}.txt"
                
                with open(out_filename, 'w') as f:
                    for file in file_list:
                        file_name = os.path.join(the_dir, file)
                        f.write(f"{file_name}\n")


'''
Make dag files for running repeder
'''
make_dag_files = True
if make_dag_files:
    for s in stations:
        for y in years:
            in_filename = f"files/filelist_a{s}_y{y}_{sample}.txt"
            if os.path.isfile(in_filename):

                out_dir = os.path.join(ped_dir, f"{y}", f"A{s}")
                if not os.path.isdir(out_dir):
                    print(f"Output directory ({out_dir}) is missing. Move on")

                dag_filename = f"run_repeder/dag_repeder_a_{s}_y_{y}.dag"
                instructions = ""
                instructions += 'CONFIG config.dagman\n'
                with open(dag_filename, "w") as f:
                    f.write(instructions)

                index = 0

                file = open(in_filename, "r")
                for line in file:
                    src_file = line.split()[0] # grab the zero entry
                    run_num = str(pt.harvest_run_num(src_file))
                    run_num = run_num.zfill(6) # make it six characters long
                    # out_file = f"reped_a_{s}_run_{run_num}.dat"
                    out_file = f"reped_run_{run_num}.dat"

                    instructions = ""
                    instructions += f"JOB job_{index} job.sub\n"
                    instructions += f'VARS job_{index} station="{s}" year="{y}" run="{run_num}" infile="{src_file}" outfile="{out_file}" outdir="{out_dir}"\n\n'
                    with open(dag_filename, "a") as f:
                        f.write(instructions)
                    
                    index+=1

                file.close()

                    

