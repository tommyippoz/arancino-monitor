import json
import subprocess
import jc
import psutil


class ArancinoProbe:
    """
    Abstract class for ARANCINO probes
    """

    def __init__(self):
        """
        Constructor
        """
        self.indicators = self.list_indicators()
        pass

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        pass

    def read_data(self) -> dict:
        """
        Reads probe data
        :return: a dictionary, or None if execution fails
        """
        pass

    def list_indicators(self) -> list:
        """
        Lists indicators for this probe
        :return: list of strings, or None if probe cannot read
        """
        if hasattr(self, 'indicators') and (self.indicators is not None):
            return self.indicators
        if self.can_read():
            r_data = self.read_data()
            if r_data is not None and isinstance(r_data, dict):
                return list(r_data.keys())
        else:
            return None

    def can_read(self) -> bool:
        """
        Returns a flag that tells if probe can read data from the system
        :return: True is probe can read (is available to be used)
        """
        return self.read_data() is not None

    def n_indicators(self) -> int:
        """
        return the number of indicators in this probe
        :return: an int (number of indicators)
        """
        ind_list = self.list_indicators()
        if ind_list is not None:
            return len(ind_list)
        else:
            return 0


class PythonProbe(ArancinoProbe):

    def __init__(self):
        """
        Constructor
        """
        ArancinoProbe.__init__(self)
        pass

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        return "Python Probe (" + str(self.n_indicators()) + ")"

    def read_data(self) -> dict:
        """
        Reads probe data
        :return: a dictionary, or None if execution fails
        """
        python_data = {}
        n_proc = psutil.cpu_count()

        # CPU Times
        tag = 'cpu_times'
        pp_data = psutil.cpu_times()
        if pp_data is not None:
            pp_dict = pp_data._asdict()
            for pp_key in pp_dict.keys():
                python_data[tag + '.' + pp_key] = pp_dict[pp_key]

        # CPU Stats
        tag = 'cpu_stats'
        pp_data = psutil.cpu_stats()
        if pp_data is not None:
            pp_dict = pp_data._asdict()
            for pp_key in pp_dict.keys():
                python_data[tag + '.' + pp_key] = pp_dict[pp_key]

        # CPU Load
        tag = 'cpu_load'
        pp_data = psutil.getloadavg()
        if pp_data is not None and isinstance(pp_data, tuple) and len(pp_data) == 3:
            python_data[tag + ".load_1m"] = pp_data[0]
            python_data[tag + ".load_5m"] = pp_data[1]
            python_data[tag + ".load_15m"] = pp_data[2]

        # Swap Memory
        tag = 'swap'
        pp_data = psutil.swap_memory()
        if pp_data is not None:
            pp_dict = pp_data._asdict()
            for pp_key in pp_dict.keys():
                python_data[tag + '.' + pp_key] = pp_dict[pp_key]

        # Virtual Memory
        tag = 'virtual'
        pp_data = psutil.virtual_memory()
        if pp_data is not None:
            pp_dict = pp_data._asdict()
            for pp_key in pp_dict.keys():
                python_data[tag + '.' + pp_key] = pp_dict[pp_key]

        # Disk
        tag = 'disk'
        pp_data = psutil.disk_usage('/')
        if pp_data is not None:
            pp_dict = pp_data._asdict()
            for pp_key in pp_dict.keys():
                python_data[tag + '.' + pp_key] = pp_dict[pp_key]

        # Disk IO
        tag = 'disk_io'
        pp_data = psutil.disk_io_counters()
        if pp_data is not None:
            pp_dict = pp_data._asdict()
            for pp_key in pp_dict.keys():
                python_data[tag + '.' + pp_key] = pp_dict[pp_key]

        # Net IO
        tag = 'net_io'
        pp_data = psutil.net_io_counters()
        if pp_data is not None:
            pp_dict = pp_data._asdict()
            for pp_key in pp_dict.keys():
                python_data[tag + '.' + pp_key] = pp_dict[pp_key]

        return python_data

    def can_read(self) -> bool:
        """
        Returns a flag that tells if probe can read data from the system
        :return: True is probe can read (is available to be used)
        """
        return True


class JSONProbe(ArancinoProbe):

    def __init__(self, command, command_params, jc_flag, tag):
        """
        Constructor
        """
        self.shell_command = [command, command_params]
        self.jc_flag = jc_flag
        self.tag = tag
        ArancinoProbe.__init__(self)

    def read_data(self) -> dict:
        """
        Reads probe data
        :return: a dictionary, or None if execution fails
        """
        cmd_output = subprocess.check_output([self.shell_command[0], self.shell_command[1]], text=True)
        json_data = jc.parse(self.jc_flag, cmd_output)
        if isinstance(json_data, list):
            if len(json_data) == 1:
                json_data = {self.tag + '.' + str(key): val for key, val in json_data[0].items()}
            elif len(json_data) == 0:
                cmd_output = '{"' + cmd_output[0:-1].replace(' ', '": ').replace('\n', ', "') + "}"
                json_data = {self.tag + '.' + str(key): val for key, val in json.loads(cmd_output).items()}
            else:
                print("BOOH")
        elif isinstance(json_data, dict):
            json_data = {self.tag + '.' + str(key): val for key, val in json_data.items()}
        return json_data


class MemInfoProbe(JSONProbe):

    def __init__(self):
        """
        Constructor
        """
        JSONProbe.__init__(self, 'cat', '/proc/meminfo', 'proc', 'meminfo')

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        return "MemInfo (" + str(self.n_indicators()) + ")"


class IOStatProbe(JSONProbe):

    def __init__(self):
        """
        Constructor
        """
        JSONProbe.__init__(self, 'iostat', '', 'iostat', 'iostat')

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        return "IOStat (" + str(self.n_indicators()) + ")"


class VMInfoProbe(JSONProbe):

    def __init__(self):
        """
        Constructor
        """
        JSONProbe.__init__(self, 'cat', '/proc/vmstat', 'vmstat', 'vmstat')

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        return "VMStat (" + str(self.n_indicators()) + ")"
