import os

def get_top_dir(station, year, sample):

    the_station = f'ARA0{station}' # expects format of ARA01
    top_dir = None

    if year == 2012:
        # need to sort out the 2012 burn sample at some point...
        # or, at least, where the full data is
        raise NotImplementedError(f"Year {year} is not supported")
    
    top_dir_list = {
        'burn': f'/mnt/scratch/baclark/ARA/burn_sample/{year}'
    }
    top_dir = os.path.join(
        top_dir_list[sample],
        f'{the_station}'
    )
    print(top_dir)

    # if year == 2013:

    #     top_dir_list = {
    #         'burn': '/data/wipac/ARA/2013/filtered/burnSample1in10/',
    #         'full': '/data/wipac/ARA/2013/filtered/full2013Data/'
    #     }

    #     top_dir = os.path.join(
    #         top_dir_list[sample],
    #         f'{the_station}',
    #         'root'
    #     )

    # if year > 2013:

    #     top_dir_list = {
    #         'burn': f'/data/wipac/ARA/{year}/unblinded/L1',
    #         'full': f'/data/wipac/ARA/{year}/blinded/L1/'
    #     }

    #     top_dir = os.path.join(
    #         top_dir_list[sample],
    #         f'{the_station}'
    #     )
    
    return top_dir

def list_all_files(station, year, sample):

    top_dir = get_top_dir(station, year, sample)
    
    full_file_list = []

    for root, dirs, files in os.walk(top_dir, topdown=False):
        for name in files:
            full_name = os.path.join(root, name)
            if 'root' not in full_name: # only check root files
                continue

            # files containing these words should be excluded
            # e.g. "runStart", "configFiles" files
            exclusions = ['Hk', 'old', 'start', 'Start', 'stop', 'Stop',
                'config', 'monitor', 'ukey', 'TIN'
            ]
            include = True
            for e in exclusions:
                if e in full_name:
                    include = False
        
            if include:
                full_file_list.append(full_name)

    return sorted(full_file_list) # return sorted

def harvest_run_num(file):
    basename = os.path.basename(file) # get the base name, e.g. "event2245.root"
    basename_noext = os.path.splitext(basename)[0] # this reduces to event2245

    if '_' in basename_noext:
        run_num = int(basename_noext.split("_", 1)[1]) # files like event_XXXX.root
    else:
        run_num = int(basename_noext.split("event", 1)[1]) # files like eventXXXX.root
    
    return run_num
