import csv
import datetime
import os.path
import time
import argparse

from tqdm import tqdm

from arancinomonitor.InjectionManager import InjectionManager
from arancinomonitor.ProbeManager import ProbeManager
from arancinomonitor.utils import store_observations, current_ms

INJECTORS = []
# Time between two system observations (in ms)
OBS_INTERVAL = 1000
# Time between two accesses in memory for storing obs data
STORE_INTERVAL = 10
# File where saving monitored data
FILENAME = "output_files/test.csv"
# Maximum number of observations (-1 if infinite)
N_OBS = 15
# duration (ms) of an injection
INJ_DURATION = 1000
# injection rate (or supposed error rate)
INJ_RATE = 0.5
# injection rate (or supposed error rate)
INJ_COOLDOWN = 5000
# path to JSON file specifying injectors
INJ_JSON = 'input_files/injectors_json.json'
# verbosity level
VERBOSE = 1

if __name__ == '__main__':
    """
    Main to test ARANCINO Monitor + Injector
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
    argParser.add_argument("-id", "--injdur", type=int,
                           help="ms from beginning to end of an injection; default is 1000")
    argParser.add_argument("-ir", "--injrate", type=float,
                           help="error rate of injections into the system; default is 0.05")
    argParser.add_argument("-ic", "--injcooldown", type=int,
                           help="ms of cooldown after an injection (or minimum distance between injections; default is 5000")
    argParser.add_argument("-ij", "--injjson", type=str,
                           help="path to JSON file containing details of injectors; default is None")
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
    if hasattr(args, 'injdur') and args.injdur is not None:
        INJ_DURATION = int(args.injdur)
    if hasattr(args, 'injrate') and args.injrate is not None:
        INJ_RATE = float(args.injrate)
    if hasattr(args, 'injcooldown') and args.injcooldown is not None:
        INJ_COOLDOWN = int(args.injcooldown)
    if hasattr(args, 'injjson') and args.injjson is not None and os.path.exists(args.injjson):
        INJ_JSON = args.injjson
    if hasattr(args, 'verbose') and args.verbose is not None:
        VERBOSE = int(args.verbose)

    if VERBOSE > 0:
        print('---------------------------------------------------------------')
        print('Monitor executes with verbosity=%d, reads every %d ms and for %d times.\n'
              'Data will be saved in the CSV file \'%s\' every %d observations'
              % (VERBOSE, OBS_INTERVAL, N_OBS, FILENAME, STORE_INTERVAL))
        print('Injector Detail: duration=%dms, rate of %.3f, cooldown=%dms' %
              (INJ_DURATION, INJ_RATE, INJ_COOLDOWN))
        print('---------------------------------------------------------------\n')

    # Update Filename
    time_str = str(datetime.datetime.fromtimestamp(current_ms() / 1000.0))
    time_str = time_str.split('.')[0].replace(' ', '_')
    INJ_FILENAME = FILENAME.replace('.csv', '') + '_inj_' + time_str + '.csv'
    FILENAME = FILENAME.replace('.csv', '') + '_' + time_str + '.csv'

    # Init ProbeManager and check available Probes
    pm = ProbeManager()
    probes = pm.available_probes(verbose=False)
    if VERBOSE > 0:
        print("Available probes for this machine")
        for probe in probes:
            print('\t%s' % probe.describe())

    # Setup of the Injector
    im = InjectionManager(duration_ms=INJ_DURATION, error_rate=INJ_RATE, cooldown=INJ_COOLDOWN)
    if INJ_JSON is None or not os.path.exists(INJ_JSON):
        im.available_injectors()
    else:
        im.fromJSON(INJ_JSON, verbose=True)
    im.start_campaign(cycle_ms=OBS_INTERVAL, cycles=N_OBS, verbose=False)

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

    # Retrieve Injections info
    inj_log = im.collect_injections(VERBOSE)
    with open(INJ_FILENAME, 'w', newline='') as myFile:
        writer = csv.writer(myFile)
        keys = ['start', 'end', 'inj_name']
        writer.writerow(keys)
        for dictionary in inj_log:
            writer.writerow([str(dictionary[d_key]) for d_key in keys])
