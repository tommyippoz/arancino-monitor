import subprocess
import psutil
import redis


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

    def __init__(self, command: str, command_params: str, tag: str):
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
        try:
            cmd_output = subprocess.check_output([self.shell_command[0], self.shell_command[1]])
            dict_data = self.to_dict(cmd_output)
        except:
            dict_data = None
        if dict_data is not None:
            dict_data = {self.tag + '.' + str(key): val for key, val in dict_data.items()}
            return dict_data
        else:
            return None

    def to_dict(self, cmd_string: str) -> dict:
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
                if s_head is not None:
                    cmd_item = " ".join(cmd_item.split())
                    s_val = [x.strip() for x in cmd_item.strip().split(' ')]
                    break
                if cmd_item.startswith('avg-cpu'):
                    cmd_item = " ".join(cmd_item.split())
                    s_head = cmd_item.replace('%', '').split(' ')
                    s_head = [x.strip() for x in s_head[1:]]
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


class TempProbe(ScriptProbe):

    def __init__(self):
        """
        Constructor
        """
        ScriptProbe.__init__(self, 'cat', '/sys/class/thermal/thermal_zone0/temp', 'temperature')

    def to_dict(self, cmd_string) -> dict:
        """
        Abstract method to parse command string
        :param cmd_string:
        :return: the dict corresponding to the parsed string
        """
        if cmd_string is None or len(cmd_string) == 0:
            return None
        else:
            return {'temperature': int(cmd_string)}

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        return "Temperature (1)"


class NetProbe(ScriptProbe):

    def __init__(self):
        """
        Constructor
        """
        ScriptProbe.__init__(self, 'cat', '/proc/net/dev', 'netinfo')

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
            for i in range(2, len(cmd_split)):
                cmd_item = cmd_split[i]
                if len(cmd_item.strip()) > 0:
                    cmd_item = " ".join(cmd_item.split()).split(' ')
                    if len(cmd_item) > 0:
                        interface_name = cmd_item[0].replace(":", "").strip()
                        cmd_dict[interface_name + ".rec.bytes"] = cmd_item[1].strip()
                        cmd_dict[interface_name + ".rec.pkts"] = cmd_item[2].strip()
                        cmd_dict[interface_name + ".rec.errs"] = cmd_item[3].strip()
                        cmd_dict[interface_name + ".rec.drop"] = cmd_item[4].strip()
                        cmd_dict[interface_name + ".rec.fifo"] = cmd_item[5].strip()
                        cmd_dict[interface_name + ".rec.frame"] = cmd_item[6].strip()
                        cmd_dict[interface_name + ".rec.compressed"] = cmd_item[7].strip()
                        cmd_dict[interface_name + ".rec.multicast"] = cmd_item[8].strip()
                        cmd_dict[interface_name + ".sent.bytes"] = cmd_item[9].strip()
                        cmd_dict[interface_name + ".sent.pkts"] = cmd_item[10].strip()
                        cmd_dict[interface_name + ".sent.errs"] = cmd_item[11].strip()
                        cmd_dict[interface_name + ".sent.drop"] = cmd_item[12].strip()
                        cmd_dict[interface_name + ".sent.fifo"] = cmd_item[13].strip()
                        cmd_dict[interface_name + ".sent.frame"] = cmd_item[14].strip()
                        cmd_dict[interface_name + ".sent.compressed"] = cmd_item[15].strip()
                        cmd_dict[interface_name + ".sent.multicast"] = cmd_item[16].strip()
            return cmd_dict

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        return "NetProbe (" + str(self.n_indicators()) + ")"


class RedisDataProbe(ScriptProbe):

    def __init__(self):
        """
        Constructor
        """
        try:
            self.redis_obj = redis.Redis()
        except:
            self.redis_obj = None
        ArancinoProbe.__init__(self)

    def read_data(self) -> dict:
        """
        Reads probe data
        :return: a dictionary, or None if execution fails
        """
        if self.redis_obj is not None:
            redis_dict = {'redis.T': self.redis_obj.get('T'),
                          'redis.H': self.redis_obj.get('H'),
                          'redis.P': self.redis_obj.get('P')}
            return redis_dict
        else:
            return None

    def can_read(self) -> bool:
        """
        Returns a flag that tells if probe can read data from the system
        :return: True is probe can read (is available to be used)
        """
        return self.redis_obj is not None

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        return "RedisData (" + str(self.n_indicators()) + ")"


class RedisInfoProbe(ArancinoProbe):

    def __init__(self):
        """
        Constructor
        """
        try:
            self.redis_obj = redis.Redis()
        except:
            self.redis_obj = None
        ArancinoProbe.__init__(self)

    def describe(self) -> str:
        """
        Returns a string with details of this probe
        :return: string description of the probe
        """
        return "RedisInfo Probe (" + str(self.n_indicators()) + ")"

    def read_data(self) -> dict:
        """
        Reads probe data
        :return: a dictionary, or None if execution fails
        """
        if self.redis_obj is not None:
            redis_dict = self.redis_obj.info()
            if redis_dict is not None:
                for k in list(redis_dict.keys()):
                    if (not k.startswith('used_')) and (not k.startswith('active_')):
                        del redis_dict[k]
                redis_dict = {('redis_' + key): value for key, value in redis_dict.items()}
                redis_dict['redis_active_keys'] = str(len(self.redis_obj.keys('*')))
            return redis_dict
        else:
            return None

    def can_read(self) -> bool:
        """
        Returns a flag that tells if probe can read data from the system
        :return: True is probe can read (is available to be used)
        """
        return self.redis_obj is not None
