import threading
import time

from arancinomonitor.utils import current_ms


class LoadInjector:
    """
    Abstract class for Injecting Errors in the System probes
    """

    def __init__(self, duration_ms: float = 1000):
        """
        Constructor
        """
        self.duration_ms = duration_ms
        self.inj_thread = None
        self.completed_flag = True
        self.injected_interval = []

    def inject_body(self):
        """
        Abstract method to be overridden
        """
        pass

    def inject(self):
        """
        Caller of the body of the injection mechanism, which will be executed in a separate thread
        """
        self.inj_thread = threading.Thread(target=self.inject_body, args=())
        self.inj_thread.start()

    def is_injector_running(self):
        """
        True if the injector has finished working (end of the 'injection_body' function)
        """
        return not self.completed_flag

    def get_injections(self) -> list:
        """
        Returns start-end times of injections exercised with this method
        """
        return self.injected_interval

    def get_name(self) -> str:
        """
        Abstract method to be overridden
        """
        return "Injector" + "(d" + str(self.duration_ms) + ")"


class SpinInjection(LoadInjector):
    """
    SpinLoop Error
    """
    def __init__(self, duration_ms: float = 1000):
        """
        Constructor
        """
        LoadInjector.__init__(self, duration_ms)

    def inject_body(self):
        """
        Abstract method to be overridden
        """
        self.completed_flag = False
        start_time = current_ms()
        while True:
            if current_ms() - start_time > self.duration_ms:
                break

        self.injected_interval.append({'start': start_time, 'end': current_ms()})
        self.completed_flag = True

    def get_name(self) -> str:
        """
        Abstract method to be overridden
        """
        return "SpinInjection" + "(d" + str(self.duration_ms) + ")"


class MemoryAllocationInjection(LoadInjector):
    """
    Attempts to allocate the given amount of RAM to the running Python process.
    param ram_to_allocate_mb: the amount of RAM in megabytes to allocate
    """

    def __init__(self, duration_ms: float = 1000, ram_to_allocate_mb: int = 1000):
        """
        Constructor
        """
        LoadInjector.__init__(self, duration_ms)
        self.ram_to_allocate_mb = ram_to_allocate_mb

    def inject_body(self):
        """
        Abstract method to be overridden
        """
        self.completed_flag = False
        start_time = current_ms()
        self.stress_ram(1.0, start_time)
        self.injected_interval.append({'start': start_time, 'end': current_ms()})
        self.completed_flag = True

    def stress_ram(self, mem_factor, start_time):
        """
        Attempts to allocate the given amount of RAM to the running Python process.
        param ram_to_allocate_mb: the amount of RAM in megabytes to allocate
        """
        try:
            # Each element takes approx 8 bytes
            # Multiply n by 1024**2 to convert from MB to Bytes
            _ = [0] * int((((self.ram_to_allocate_mb * mem_factor) / 8) * (1024 ** 2)))
            # This is just to keep the process running until halted
            sleep_s = (start_time + self.inject_interval - current_ms()) / 1000.0
            if sleep_s > 0:
                time.sleep(self.inject_interval)

        except MemoryError:
            # We didn't have enough RAM for our attempt, so we will recursively try
            # smaller amounts 10% smaller at a time
            self.stress_ram(int((self.ram_to_allocate_mb * mem_factor) * 0.9), start_time)


class MemoryUsageInjection(LoadInjector):
    """
    Loops and adds data to an array
    """

    def __init__(self, duration_ms: float = 1000, items_for_loop: int = 1000):
        """
        Constructor
        """
        LoadInjector.__init__(self, duration_ms)
        self.items_for_loop = items_for_loop

    def inject_body(self):
        """
        Abstract method to be overridden
        """
        self.completed_flag = False
        start_time = current_ms()
        my_list = []
        while True:
            my_list.append([999 for i in range(0, self.items_for_loop)])
            if current_ms() - start_time > self.duration_ms:
                break
            else:
                time.sleep(0.001)

        self.injected_interval.append({'start': start_time, 'end': current_ms()})
        self.completed_flag = True

    def get_name(self) -> str:
        """
        Abstract method to be overridden
        """
        return "MemoryUsageInjection-" + str(self.items_for_loop) + "i-(d" + str(self.duration_ms) + ")"

