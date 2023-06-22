# lightweight-monitor
Lightweight Python Monitor for Linux-Based Devices

This repository contains the code for conducting a monitor and error injection campaign on Linux Devices.
The code is compatible with Python 3.5.3 due to constraints we have in the usage of RaspBian 9 Stretch.

Help on the usage
```
usage: injection_main.py [-h] [-o OUTFILE] [-i INTERVAL] [-n NOBS] [-w WOBS]
                         [-id INJDUR] [-ir INJRATE] [-ic INJCOOLDOWN]
                         [-ij INJJSON] [-mf MERGEFILES] [-v VERBOSE]

optional arguments:
-h, --help            show this help message and exit
-o OUTFILE, --outfile OUTFILE
  location of the output file; default is 'test.csv' in the current folder
-i INTERVAL, --interval INTERVAL
  interval in ms between two observations; default is 1000 ms (1 sec)
-n NOBS, --nobs NOBS  number of observations before stopping; default is 15
-w WOBS, --wobs WOBS  number of observations to keep in RAM before saving to file; default is 10
  -id INJDUR, --injdur INJDUR
                        ms from beginning to end of an injection; default is 1000
  -ir INJRATE, --injrate INJRATE
                        error rate of injections into the system; default is 0.05
  -ic INJCOOLDOWN, --injcooldown INJCOOLDOWN
                        ms of cooldown after an injection (or minimum distance between injections; default is 5000
  -ij INJJSON, --injjson INJJSON
                        path to JSON file containing details of injectors; default is None
  -mf MERGEFILES, --mergefiles MERGEFILES
                        True if features and injections have to be merged at the end; default is True
  -v VERBOSE, --verbose VERBOSE
                        0 if all messages need to be suppressed, 2 if all have to be shown. 1 displays base info
```
