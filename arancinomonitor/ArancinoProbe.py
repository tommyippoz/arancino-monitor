import subprocess
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
        f_obj = getattr(psutil, "getloadavg", None)
        if callable(f_obj):
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
        try:
            tag = 'disk_io'
            pp_data = psutil.disk_io_counters()
            if pp_data is not None:
                pp_dict = pp_data._asdict()
                for pp_key in pp_dict.keys():
                    python_data[tag + '.' + pp_key] = pp_dict[pp_key]
        except:
            err = 1

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


class ScriptProbe(ArancinoProbe):

    def __init__(self, command, command_params, tag):
        """
        Constructor
        """
        self.shell_command = [command, command_params]
        self.tag = tag
        ArancinoProbe.__init__(self)

    def read_data(self) -> dict:
        """
        Reads probe data
        :return: a dictionary, or None if execution fails
        """
        cmd_output = subprocess.check_output([self.shell_command[0], self.shell_command[1]])
        dict_data = self.to_dict(cmd_output)
        if dict_data is not None:
            dict_data = {self.tag + '.' + str(key): val for key, val in dict_data.items()}
            return dict_data
        else:
            return None

    def to_dict(self, cmd_string) -> dict:
        """
        Abstract method to parse command string
        :param cmd_string:
        :return: the dict corresponding to the parsed string
        """
        if cmd_string is None or len(cmd_string) == 0:
            return None
        else:
            if isinstance(cmd_string, bytes):
                cmd_string = cmd_string.decode("utf-8")
            cmd_split = cmd_string.split('\n')
            cmd_dict = {}
            for cmd_item in cmd_split:
                if len(cmd_item) > 0:
                    if ':' in cmd_item:
                        c_name = cmd_item.split(':')[0].strip()
                        c_value = cmd_item.split(':')[1].strip()
                        if ' ' in c_value:
                            c_value = c_value.split(' ')[0].strip()
                        cmd_dict[c_name] = c_value
            return cmd_dict


class MemInfoProbe(ScriptProbe):

    def __init__(self):
        """
        Constructor
        """
        ScriptProbe.__init__(self, 'cat', '/proc/meminfo', 'meminfo')

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        return "MemInfo (" + str(self.n_indicators()) + ")"


class IOStatProbe(ScriptProbe):

    def __init__(self):
        """
        Constructor
        """
        ScriptProbe.__init__(self, 'iostat', '', 'iostat')

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        return "IOStat (" + str(self.n_indicators()) + ")"

    def to_dict(self, cmd_string) -> dict:
        """
        Abstract method to parse command string
        :param cmd_string:
        :return: the dict corresponding to the parsed string
        """
        if cmd_string is None or len(cmd_string) == 0:
            return None
        else:
            if isinstance(cmd_string, bytes):
                cmd_string = cmd_string.decode("utf-8")
            cmd_split = cmd_string.split('\n')
            s_head = None
            s_val = None
            for cmd_item in cmd_split:
                if cmd_item.startswith('avg-cpu'):
                    s_head = cmd_item.replace('%', '').split(' ')
                    s_head = [x.strip() for x in s_head[1:]]
                if s_head is not None:
                    s_val = [x.strip() for x in cmd_item.strip().split(' ')]
                    break
            if s_head is not None and s_val is not None:
                return {k: v for k, v in zip(s_head, s_val)}
            else:
                return {}


class VMInfoProbe(ScriptProbe):

    def __init__(self):
        """
        Constructor
        """
        ScriptProbe.__init__(self, 'cat', '/proc/vmstat', 'vmstat')

    def to_dict(self, cmd_string) -> dict:
        """
        Abstract method to parse command string
        :param cmd_string:
        :return: the dict corresponding to the parsed string
        """
        if cmd_string is None or len(cmd_string) == 0:
            return None
        else:
            if isinstance(cmd_string, bytes):
                cmd_string = cmd_string.decode("utf-8")
            cmd_split = cmd_string.split('\n')
            cmd_dict = {}
            for cmd_item in cmd_split:
                if len(cmd_item) > 0:
                    if ' ' in cmd_item:
                        c_name = cmd_item.split(' ')[0].strip()
                        c_value = cmd_item.split(' ')[1].strip()
                        if ' ' in c_value:
                            c_value = c_value.split(' ')[0].strip()
                        cmd_dict[c_name] = c_value
            return cmd_dict

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        return "VMStat (" + str(self.n_indicators()) + ")"
