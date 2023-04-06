from arancinomonitor.ArancinoProbe import PythonProbe, MemInfoProbe, IOStatProbe, VMInfoProbe
from arancinomonitor.utils import current_ms


def get_all_probes():
    """
    Returns a list of all ARANCINO probes (without checking for availability)
    :return: a list of probes
    """
    probes_list = [VMInfoProbe(), IOStatProbe(), PythonProbe(), MemInfoProbe()]
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

    def read_probes_data(self) -> dict:
        if self.probes is None or len(self.probes) == 0:
            return None
        else:
            dict_data = {'timestamp': current_ms()}
            for probe in self.probes:
                p_data = probe.read_data()
                if p_data is not None:
                    dict_data.update(p_data)
            return dict_data
