import csv
import json
import multiprocessing
import os.path
import random
import threading
import time

from arancinomonitor.LoadInjector import SpinInjection, DiskStressInjection, CPUStressInjection, \
    LoadInjector, MemoryStressInjection, RedisStressInjection
from arancinomonitor.utils import current_ms


def get_all_injectors(inj_duration):
    """
    Returns a list of all injectors (without checking for availability)
    :return: a list of injectors
    """
    inj_list = [MemoryStressInjection(duration_ms=inj_duration),
                CPUStressInjection(duration_ms=inj_duration),
                DiskStressInjection(duration_ms=inj_duration),
                SpinInjection(duration_ms=inj_duration),
                RedisStressInjection(duration_ms=inj_duration)]
    return inj_list


class InjectionManager:
    """
    Class that manages the injection of errors
    """

    def __init__(self, duration_ms: int = 1000, error_rate: float = 0.02, cooldown: float = 1):
        """
        Constructor
        """
        self.inj_duration = duration_ms
        self.error_rate = error_rate
        self.inj_cooldown = cooldown
        self.campaign_running = False
        self.injectors = None
        self.injections = None
        self.camp_thread = None
        self.available_inj = None

    def available_injectors(self, set_inj=True, verbose=True):
        """
        Returns a list of available injectors for this system
        :param set_inj: True is available injectors should become default injectors for this object
        :param verbose: True is debug information has to be shown
        :return: a list of available probes
        """
        av_inj = get_all_injectors(self.inj_duration)
        if verbose:
            print("\t%d injectors are defined in the library" % len(av_inj))
        for inj in av_inj:
            if verbose:
                print(inj.get_name())
        if set_inj:
            self.injectors = av_inj
        return av_inj

    def start_campaign(self, inj_filename, cycle_ms: int = 1000, cycles: int = 100, verbose: bool = True):
        """
        Caller of the body of the injection mechanism, which will be executed in a separate Process
        """
        self.camp_thread = multiprocessing.Process(target=self.campaign_body,
                                                   args=(inj_filename, cycle_ms, cycles, verbose))
        self.camp_thread.start()

    def campaign_body(self, inj_filename: str, cycle_ms: int = 1000, cycles: int = 100, verbose: bool = True):
        """
        Handles the error injection campaign
        """
        self.campaign_running = True
        self.available_inj = None
        inj_timer = 0

        if self.injectors is not None and len(self.injectors) > 0:

            for cycle_id in range(0, cycles):
                start_ms = current_ms()
                # If there are no active injections and no cooldown
                # If there is enough time before end of campaign
                # If probability activates
                if self.available_inj is None and inj_timer == 0 \
                        and ((cycles - cycle_id - 1) * cycle_ms > self.inj_duration) \
                        and (random.randint(0, 999) / 999.0) <= self.error_rate:
                    # Randomly chooses an injector and performs injection
                    while self.available_inj is None:
                        inj_index = random.randint(0, len(self.injectors) - 1)
                        if not self.injectors[inj_index].is_injector_running():
                            self.available_inj = self.injectors[inj_index]
                    if verbose:
                        print("Injecting with injector '%s'" % self.available_inj.get_name())
                    inj_thread = threading.Thread(target=self.available_inj.inject)
                    inj_thread.start()
                    inj_timer = self.inj_duration + self.inj_cooldown
                sleep_s = (cycle_ms - (current_ms() - start_ms)) / 1000.0
                if sleep_s > 0:
                    time.sleep(sleep_s)
                # Managing cooldown
                inj_timer = inj_timer - cycle_ms if inj_timer > 0 else 0
                if inj_timer < self.inj_cooldown:
                    self.available_inj = None

        else:
            print("No injectors were set for this experimental campaign")

        self.campaign_running = False
        self.collect_injections()
        with open(inj_filename, 'w', newline='') as myFile:
            writer = csv.writer(myFile)
            keys = ['start', 'end', 'inj_name']
            writer.writerow(keys)
            for dictionary in self.injections:
                writer.writerow([str(dictionary[d_key]) for d_key in keys])

    def is_campaign_running(self):
        """
        Returns a flag that tells if the injection campaign is ongoing
        """
        return self.campaign_running

    def collect_injections(self, verbose=True) -> list:
        """
        :param verbose: True if debug information need to be shown
        Collects and outputs injections for this run
        """
        while self.is_campaign_running():
            # This should not happen unless strange overhead happen
            print("Warning! Injection campaign is still running, trying to force-close")
            self.force_close_injections()
            time.sleep(1)
        if self.injections is None:
            self.injections = []
            for inj in self.injectors:
                inj_log = inj.get_injections()
                if inj_log is not None and len(inj_log) > 0:
                    new_inj = [dict(item, inj_name=inj.get_name()) for item in inj_log]
                    self.injections.extend(new_inj)
                    if verbose:
                        print("Injections with injector '" + str(inj.get_name()) + "': " + str(len(new_inj)))
        return self.injections

    def get_injectors(self):
        return self.injectors

    def has_injectors(self):
        return self.injectors is not None and len(self.injectors) > 0

    def fromJSON(self, json_object, set_inj=True, verbose=True):
        """
        Method to read a JSON object and extract injectors that are specified there
        :param json_object: the json object or file containing a json object
        :param set_inj: True is available injectors should become default injectors for this object
        :param verbose: True is debug information has to be shown
        :return: a list of available probes
        """
        try:
            json_object = json.loads(json_object)
        except ValueError:
            if os.path.exists(json_object):
                with open(json_object) as f:
                    json_object = json.load(f)
            else:
                print("Could not parse input %s" % json_object)
                json_object = None
        if json_object is not None:
            # Means it is a JSON object
            json_injectors = []
            for job in json_object:
                job["duration_ms"] = self.inj_duration
                new_inj = LoadInjector.fromJSON(job)
                if new_inj is not None and new_inj.is_valid():
                    # Means it was a valid JSON specification of an Injector
                    json_injectors.append(new_inj)
                    if verbose:
                        print('New injector loaded from JSON: %s' % new_inj.get_name())
            if set_inj:
                self.injectors = json_injectors

    def force_close_injections(self):
        if self.available_inj is not None:
            self.available_inj.force_close()
