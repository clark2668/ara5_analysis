import argparse

parser = argparse.ArgumentParser(description="Make File List")
parser.add_argument('--station', dest='station',
    required=True, help='ARA station')
parser.add_argument('--year', dest='year',
    required=True, help='Year')
parser.add_argument('--sample', dest='sample',
    required=True, help='burn or full'
)
args = parser.parse_args()

station = int(args.station)
year = int(args.year)
sample = args.sample


import path_tools as pt
file_list = pt.list_all_files(station, year, sample)
out_filename = f"filelist_A{station}_Y{year}_{sample}.txt"

with open(out_filename, 'w') as f:
    for file in file_list:
        f.write(f"{file}\n")
