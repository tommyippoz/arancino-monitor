import time
import argparse

from tqdm import tqdm

from arancinomonitor.ProbeManager import ProbeManager
from arancinomonitor.utils import store_observations, current_ms

# Time between two system observations (in ms)
OBS_INTERVAL = 1000
# Time between two accesses in memory for storing obs data
STORE_INTERVAL = 10
# File where saving monitored data
FILENAME = "output_files/test.csv"
# Maximum number of observations (-1 if infinite)
N_OBS = 15
# verobsity level
VERBOSE = 1

if __name__ == '__main__':
    """
    Main to test ARANCINO Probes
    """

    # Parse Arguments
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-o", "--outfile", type=str,
                           help="location of the output file; default is 'test.csv' in the current folder")
    argParser.add_argument("-i", "--interval", type=int,
                           help="interval in ms between two observations; default is 1000 ms (1 sec)")
    argParser.add_argument("-n", "--nobs", type=int,
                           help="number of observations before stopping; default is 15")
    argParser.add_argument("-w", "--wobs", type=int,
                           help="number of observations to keep in RAM before saving to file; default is 10")
    argParser.add_argument("-v", "--verbose", type=int,
                           help="0 if all messages need to be suppressed, 2 if all have to be shown. "
                                "1 displays base info")
    args = argParser.parse_args()
    if hasattr(args, 'outfile') and args.outfile is not None:
        FILENAME = args.outfile
    if hasattr(args, 'interval') and args.interval is not None:
        OBS_INTERVAL = int(args.interval)
    if hasattr(args, 'nobs') and args.nobs is not None:
        N_OBS = int(args.nobs)
    if hasattr(args, 'wobs') and args.wobs is not None:
        STORE_INTERVAL = int(args.wobs)
    if hasattr(args, 'verbose') and args.verbose is not None:
        VERBOSE = int(args.verbose)

    if VERBOSE > 0:
        print('---------------------------------------------------------------')
        print('Monitor executes with verbosity=%d, reads every %d ms and for %d times.\n'
              'Data will be saved in the CSV file \'%s\' every %d observations'
              % (VERBOSE, OBS_INTERVAL, N_OBS, FILENAME, STORE_INTERVAL))
        print('---------------------------------------------------------------\n')

    # Init ProbeManager and check available Probes
    pm = ProbeManager()
    probes = pm.available_probes(verbose=False)
    if VERBOSE > 0:
        print("Available probes for this machine")
        for probe in probes:
            print('\t%s' % probe.describe())

    # Monitoring Process
    obs_data = []
    read_time = -1
    start_time = current_ms()
    n_obs = 0
    for obs_index in tqdm(range(N_OBS), desc='Monitor Progress Bar'):
        start_it = current_ms()
        if VERBOSE > 1:
            print("Read: time of %d ms" % read_time)
        obs_data.append(pm.read_probes_data())
        if len(obs_data) % STORE_INTERVAL == STORE_INTERVAL - 1:
            store_observations(FILENAME, obs_data)
            obs_data = []
        read_time = current_ms() - start_it
        if read_time < OBS_INTERVAL:
            time.sleep((OBS_INTERVAL - read_time)/1000)
        else:
            print("ERROR: monitor time was %d ms, desired interval is %d ms" % (read_time, OBS_INTERVAL))
            break

    # Print Observation Data which is left in the list
    if obs_data is not None and len(obs_data) > 0:
        store_observations(FILENAME, obs_data)
        obs_data = []





