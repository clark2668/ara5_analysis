import os

def get_top_dir(station, year, sample):

    the_station = f'ARA0{station}' # expects format of ARA01
    top_dir = None

    if year == 2012:
        # need to sort out the 2012 burn sample at some point...
        # or, at least, where the full data is
        raise NotImplementedError(f"Year {year} is not supported")

    if year == 2013:

        top_dir_list = {
            'burn': '/data/wipac/ARA/2013/filtered/burnSample1in10/',
            'full': '/data/wipac/ARA/2013/filtered/full2013Data/'
        }

        top_dir = os.path.join(
            top_dir_list[sample],
            f'{the_station}',
            'root'
        )

    if year > 2013:

        top_dir_list = {
            'burn': '/data/wipac/ARA/2014/unblinded/L1',
            'full': '/data/wipac/ARA/2014/blinded/L1/'
        }

        top_dir = os.path.join(
            top_dir_list[sample],
            f'{the_station}'
        )
    
    return top_dir

def list_all_files(station, year, sample):

    top_dir = get_top_dir(station, year, sample)
    
    full_file_list = []

    for root, dirs, files in os.walk(top_dir, topdown=False):
        for name in files:
            full_name = os.path.join(root, name)
            if 'root' not in full_name: # only check root files
                continue
            if 'Hk' in full_name: # skip Hk files
                continue
            if 'old' in full_name:
                continue
            if 'start' in full_name: # skip runstart files
                continue
            if 'Start' in full_name: # skip runStart files
                continue
            if 'stop' in full_name: # skip runstop files
                continue
            if 'Stop' in full_name: # skip runStop files
                continue
            if 'config' in full_name: # skip configFile files
                continue
            if 'monitor' in full_name: # skip monitor files
                continue
        
            full_file_list.append(full_name)

    return sorted(full_file_list) # return sorted
