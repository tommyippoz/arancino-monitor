import time

from arancinomonitor.ProbeManager import ProbeManager
from arancinomonitor.utils import current_ms, store_observations

# Time between two system observations (in ms)
OBS_INTERVAL = 1000
# Time between two accesses in memory for storing obs data
STORE_INTERVAL = 10
# File where saving monitored data
FILENAME = "test.csv"
# Maximum number of observations (-1 if infinite)
N_OBS = 15

if __name__ == '__main__':
    """
    Main to test ARANCINO Probes
    """

    # Init ProbeManager and check available Probes
    pm = ProbeManager()
    probes = pm.available_probes(verbose=False)
    for probe in probes:
        print(probe.describe())

    # Monitoring Process
    obs_data = []
    read_time = -1
    start_time = current_ms()
    while True:
        start_it = current_ms()
        print("Read: time of %d ms" % read_time)
        if (N_OBS > 0) and (start_it > start_time + N_OBS*OBS_INTERVAL):
            break
        obs_data.append(pm.read_probes_data())
        if len(obs_data) % STORE_INTERVAL == STORE_INTERVAL - 1:
            store_observations(FILENAME, obs_data)
        read_time = current_ms() - start_it
        if read_time < OBS_INTERVAL:
            time.sleep((OBS_INTERVAL - read_time)/1000)
        else:
            print("ERROR: monitor time was %d ms, desired interval is %d ms" % (read_time, OBS_INTERVAL))

    # Print Observation Data which is left in the list
    if obs_data is not None and len(obs_data) > 0:
        store_observations(FILENAME, obs_data)





