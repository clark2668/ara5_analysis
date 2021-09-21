import argparse
import path_tools as pt

years = [2013, 2014, 2015, 2016, 2017, 2018]
stations = [1, 2, 3, 4, 5]
sample = 'full'

for y in years:
    for s in stations:

        if y < 2018 and s > 3:
            continue

        print("Year {}, on station {}".format(y, s))

        file_list = pt.list_all_files(s, y, sample)
        if len(file_list) < 1:
            print("Skipping A{} {}".format(s, y))
            continue
        out_filename = f"filelist_a{s}_y{y}_{sample}.txt"

        with open(out_filename, 'w') as f:
            for file in file_list:
                f.write(f"{file}\n")

