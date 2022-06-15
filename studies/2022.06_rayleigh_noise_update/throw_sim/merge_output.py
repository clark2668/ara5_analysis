# trying this solution: https://root-forum.cern.ch/t/root-6-04-14-hadd-100gb-and-rootlogon/24581/3

import ROOT
import os, sys
import glob

merger = ROOT.TFileMerger(False)
# merger.SetFastMethod(True)

top_path = "/data/user/brianclark/ARA/ara5_analysis/simulations/noise_tuning/pre_tuning/test/"
file_list = sorted(glob.glob(f"{top_path}/AraOut0000[0-1].root"))
file_list = [f'{top_path}/AraOut.noise_setup.txt.run200000.root', f'{top_path}/AraOut.noise_setup.txt.run200001.root']
for f in file_list:
    print("Adding file {}".format(f))
    merger.AddFile(f)

merger.OutputFile(f"{top_path}/merged_run100000.root")
merger.Merge()