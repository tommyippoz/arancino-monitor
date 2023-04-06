class ArancinoProbe:
    """
    Abstract class for ARANCINO probes
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def describe(self):
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        pass

    def read_data(self):
        """
        Reads probe data
        :return: a dictionary, or None if execution fails
        """
        pass

    def can_read(self):
        """
        Returns a flag that tells if probe can read data from the system
        :return: True is probe can read (is available to be used)
        """
        pass


class PythonProbe(ArancinoProbe):

    def __init__(self):
        """
        Constructor
        """
        ArancinoProbe.__init__(self)
        pass

    def describe(self):
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        pass

    def read_data(self):
        """
        Reads probe data
        :return: a dictionary, or None if execution fails
        """
        pass

    def can_read(self):
        """
        Returns a flag that tells if probe can read data from the system
        :return: True is probe can read (is available to be used)
        """
        return True
