import os.path
import time


def current_ms():
    """
    Reports the current time in milliseconds
    :return: long int
    """
    return round(time.time() * 1000)


def store_observations(filename, obs_data):
    """
    stores observation data into a file
    :param filename: the target file
    :param obs_data: observations to store
    """
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write("%s\n" % ','.join([str(ov) for ov in obs_data[0].keys()]))
    with open(filename, 'a') as f:
        for obs in obs_data:
            f.write("%s\n" % ','.join([str(ov) for ov in obs.values()]))
    pass
