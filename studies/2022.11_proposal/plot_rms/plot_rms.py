import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import argparse
import ROOT, array, ctypes, datetime
from matplotlib import style
style.use('plt.mplstyle')

def get_unixtime_rms_arrays(bad_run_list, file_list):
    
    unixtimes = []
    rms = {}
    for c in range(16):
        rms[c] = []
    runnums = []
    
    for f in file_list:
        print(f'Working on {f}')

        rf_rms = array.array("d", [0]*16)
        unix_time = ctypes.c_int()
        run_num = ctypes.c_int()

        file = ROOT.TFile.Open(f)
        inTree = file.Get("rms_tree")
        inTree.SetBranchAddress("runNumber", run_num)
        inTree.SetBranchAddress("RMS_RFTrigger", rf_rms)
        inTree.SetBranchAddress("unixTime", unix_time)
        inTree.GetEntry(0) # there's only one entry

        if run_num.value not in bad_run_list:
            unixtimes.append(datetime.datetime.fromtimestamp(unix_time.value))
            runnums.append(run_num.value)
            for c in range(16):
                rms[c].append(rf_rms[c])
        
        file.Close()

    unixtimes = np.asarray(unixtimes)
    rms = np.array(list(rms.values())) # cast this into a 2D array
    runnums = np.asarray(runnums)
    return unixtimes, rms, runnums

def load_bad_run_list(station):
    info = np.genfromtxt(f'runlogs/logs/a{station}_log.txt', 
            skip_header=0, delimiter='\t',
            names=['run', 'user', 'reason', 'log']
            )
    return info['run']

get_arrays = False
if get_arrays:

    stations = [1, 2, 3, 4, 5]
    stations = [1]
    for s in stations:

        bad_runs = load_bad_run_list(s)

        import glob
        top_dir = '/mnt/scratch/baclark/ARA/rms/'
        files = sorted(glob.glob(f'{top_dir}/*/A{s}/*.root'))

        unixtimes, rms, runnums = get_unixtime_rms_arrays(bad_runs, files)

        np.savez(f'a{s}_rms_vs_unixtime.npz',
            unixtimes=unixtimes, rms=rms, runnums=runnums
        )

plot_arrays = True
if plot_arrays:

    which_chans = {
        1: 5, # maybe 5? 
        2: 2, 
        3: 13,  # 5 isn't bad, or 9, or 13, or 14
        4: 1, # 5 isn't *horrible*, 10 not bad, 13 not bad, 14 not bad (use for now)
        5: 1
    }

    def harvest(npz_file, chan):
        file = np.load(npz_file, allow_pickle=True)
        return file['unixtimes'], file['rms'][chan], file['runnums']

    stations = [1, 2, 3, 4, 5]
    unixtimes = {}
    rms = {}
    runnums = {}
    masks = {}
    guard_time = 1325394000 # something early
    guard_time = 1513317600
    guard_time_2 = 1610690400
    guard_time_2 = 1642226400 # to show 2021
    # guard_time_2 = 1800000000

    for s in stations:
        tmp_unixtimes, tmp_rms, tmp_runnums = harvest(
            f'a{s}_rms_vs_unixtime.npz',
            which_chans[s]
            )
        unixtimes[s] = tmp_unixtimes
        rms[s] = tmp_rms
        runnums[s] = tmp_runnums
        unixtimes_utimes = np.asarray([datetime.datetime.timestamp(b) for b in tmp_unixtimes])
        time_mask = unixtimes_utimes > guard_time
        time_mask = np.logical_and(time_mask, unixtimes_utimes < guard_time_2)

        masks[s] = time_mask

    pa_data = np.genfromtxt('avgRMS_PA_SWTrigs.txt',
        delimiter=' ',
        names=['run', 'unixtime', 
        '0', '1', '2', '3', '4', '5', '6', '7', 
        '8', '9', '10', '11', '12', '13', '14', '15']
    )
    pa_unixtimes = []
    for i in pa_data['unixtime']:
        pa_unixtimes.append(datetime.datetime.fromtimestamp(int(i)))
    pa_unixtimes = np.asarray(pa_unixtimes)
    unixtimes['pa'] = pa_unixtimes
    rms['pa'] = pa_data['1']
    pa_unixtimes_utimes = np.asarray([datetime.datetime.timestamp(b) for b in pa_unixtimes])
    time_mask = pa_unixtimes_utimes > guard_time
    time_mask = np.logical_and(time_mask, pa_unixtimes_utimes < guard_time_2)
    print(time_mask)
    masks['pa'] = time_mask
    runnums['pa'] = pa_data['run']
    

    import itertools
    markers = itertools.cycle(('o', 's', '^', 'v', '>', '<'))
    fig = plt.figure(figsize=(10,8))
    ax = fig.add_subplot(111)
    stations = [1, 2, 3, 4]
    for s in stations:
        
        the_mark = next(markers)
        ax.plot(unixtimes[s][masks[s]], rms[s][masks[s]], the_mark, label=f'Station {s}', alpha=0.2)

    the_mark = next(markers)
    ax.plot(unixtimes['pa'][masks['pa']], rms['pa'][masks['pa']],
        the_mark, label='PA & Station 5', alpha=0.2
    )
    leg = ax.legend(loc='upper right', ncol=2, markerscale=2.)
    for l in leg.legendHandles:
        # l._sizes = [30]
        l.set_alpha(1)

    ax.set_xlabel("Time")
    ax.set_ylabel("RMS of Noise Waveforms [mV]")
    ax.set_ylim([0,100])
    ax=plt.gca()

    # start_time = int(1513317600)
    # stop_time =  int(1547532000)
    # ax.set_xlim([start_time, stop_time])

    ax.set_xticklabels(ax.get_xticks(), rotation = 45)
    import matplotlib.dates as md
    xfmt = md.DateFormatter('%Y-%m')
    # xfmt = md.DateFormatter('%Y')
    ax.xaxis.set_major_formatter(xfmt)
    plt.subplots_adjust(bottom=0.2)
    fig.tight_layout()
    fig.savefig("rms_vs_time.png")


# fig = plt.figure(figsize=(10, 8))
# ax = fig.add_subplot(111)
# ax.plot(runnums['pa'],  unixtimes['pa'], 'o')
# ax.plot(runnums['pa'][masks['pa']],  unixtimes['pa'][masks['pa']], 'o')
# import matplotlib.dates as md
# # xfmt = md.DateFormatter('%Y-%m-%d')
# xfmt = md.DateFormatter('%Y-%m')
# ax.yaxis.set_major_formatter(xfmt)
# plt.subplots_adjust(left=0.2)
# fig.tight_layout()
# fig.savefig("time_vs_runno_pa.png")
# del fig, ax
