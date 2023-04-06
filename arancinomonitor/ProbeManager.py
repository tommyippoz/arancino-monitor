from arancinomonitor.ArancinoProbe import PythonProbe


def get_all_probes():
    """
    Returns a list of all ARANCINO probes (without checking for availability)
    :return: a list of probes
    """
    probes_list = [PythonProbe(), ]
    return probes_list


class ProbeManager:
    """
    Class that manages ARANCINO probes
    """

    def __init__(self):
        """
        Constructor
        """
        self.probes = None
        pass

    def available_probes(self, set_probes=True, verbose=True):
        """
        Returns a list of available probes for this system
        :param set_probes: True is available probes should become default probes for this object
        :param verbose: True is debug information has to be shown
        :return: a list of available probes
        """
        all_probes = get_all_probes()
        if verbose:
            print("%d probes are defined in the library" % len(all_probes))
        av_probes = []
        for probe in all_probes:
            if probe.can_read():
                av_probes.append(probe)
        if verbose:
            print("%d probes are ready to be used in this system" % len(av_probes))
        if set_probes:
            self.probes = av_probes
        return av_probes
