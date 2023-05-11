import argparse
import os.path
import sys
from _csv import reader, writer

# Name of the file containing monitored data
MONITOR_FILE = None
# Name of the file containing injections
INJECTIONS_FILE = None
# Name of the output file
OUTPUT_FILE = 'monitor_labeled.csv'
# Tag of the timestamp
TIMESTAMP_TAG = 'timestamp'
# verbosity level
VERBOSE = 1

if __name__ == '__main__':
    """
    Main to merge monitored data and injections data
    """

    # Parse Arguments
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-o", "--outfile", type=str,
                           help="location of the output file; default is 'monitor_labeled.csv' in the current folder")
    argParser.add_argument("-m", "--monfile", type=str,
                           help="location of the monitor file; mandatory input")
    argParser.add_argument("-i", "--injfile", type=str,
                           help="location of the injection file; mandatory input")
    argParser.add_argument("-t", "--timetag", type=str,
                           help="tag of the timestamp in the monitor file; default is 'timestamp'")
    argParser.add_argument("-v", "--verbose", type=int,
                           help="0 if all messages need to be suppressed, 2 if all have to be shown. "
                                "1 displays base info")
    args = argParser.parse_args()
    if hasattr(args, 'outfile') and args.outfile is not None and os.path.exists(os.path.dirname(args.outfile)):
        OUTPUT_FILE = args.outfile
    if hasattr(args, 'monfile') and args.monfile is not None and os.path.exists(args.monfile):
        MONITOR_FILE = args.monfile
    if hasattr(args, 'injfile') and args.injfile is not None and os.path.exists(args.injfile):
        INJECTIONS_FILE = args.injfile
    if hasattr(args, 'timetag') and args.timetag is not None:
        TIMESTAMP_TAG = args.timetag
    if hasattr(args, 'verbose') and args.verbose is not None:
        VERBOSE = int(args.verbose)

    if VERBOSE > 0:
        print('-----------------------------------------------------------------------')
        print('Merging monitored data with injections to obtain a unique labeled file')
        print('-----------------------------------------------------------------------\n')

    if MONITOR_FILE is None:
        print('File containing monitored data is not set or not valid')
    elif INJECTIONS_FILE is None:
        print('File containing injection data is not set or not valid')
    else:
        # Create dict of injections: start_time, end_time, tag
        injections = []
        with open(INJECTIONS_FILE, 'r') as read_obj:
            csv_reader = reader(read_obj)
            header = next(csv_reader)
            # Iterate over each row after the header in the csv
            for row in csv_reader:
                if row is not None and len(row) == 3:
                    injections.append({'start_time': int(row[0].strip()),
                                       'end_time': int(row[1].strip()),
                                       'tag': row[2].strip()})
        injections = sorted(injections, key=lambda d: d['start_time'])

        if VERBOSE > 0:
            print(str(len(injections)) + " injections were retrieved")

        # Opens output file
        with open(OUTPUT_FILE, 'w') as wrt_obj:
            csv_writer = writer(wrt_obj)

            # Iterates over monitor file
            with open(MONITOR_FILE, 'r') as read_obj:
                csv_reader = reader(read_obj)
                header = next(csv_reader)
                # Check file as empty
                if header is not None:
                    header.append('label')
                    csv_writer.writerow(header)
                    # Gets index of the timestamp
                    try:
                        timestamp_index = header.index(TIMESTAMP_TAG)
                    except ValueError:
                        try:
                            timestamp_index = header.index('_timestamp')
                        except ValueError:
                            try:
                                timestamp_index = header.index('timestamp')
                            except ValueError:
                                try:
                                    timestamp_index = header.index('time')
                                except ValueError:
                                    print('No timestamp in the file')
                                    sys.exit(1)
                    # Iterate over each row after the header in the csv
                    inj_index = 0
                    for row in csv_reader:
                        if row is not None and len(row) > timestamp_index:
                            r_time = row[timestamp_index]
                            if r_time.isnumeric():
                                r_time = int(r_time)
                                anomaly_tag = 'normal'
                                if injections is not None and inj_index < len(injections):
                                    while inj_index < len(injections) - 1 and \
                                            r_time > injections[inj_index]['end_time']:
                                        inj_index = inj_index + 1
                                    if injections[inj_index]['start_time'] <= r_time <= injections[inj_index]['end_time']:
                                        anomaly_tag = injections[inj_index]['tag']
                                row.append(anomaly_tag)
                                csv_writer.writerow(row)

