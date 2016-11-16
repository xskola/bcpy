import csv
import sys
import logging
import re


def get_csv_content(infile):
    """Open a CSV and get it contents into a list."""
    # use Dialect to guess
    with open(infile, 'rb') as f:
        for size in [1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072]:
            try:
                dialect = csv.Sniffer().sniff(f.read(size), ",;")
                f.seek(0)
            except csv.Error:
                continue
            except MemoryError:
                print "Error: Could not determine CSV delimiter."
                sys.exit(1)
            else:
                break
        try:
            reader = csv.reader(f, dialect)
        except UnboundLocalError:
            print "Error reading CSV file."
            sys.exit(1)
        textvalues = list(reader)
    return textvalues


def get_csp_config(infile):
    """Get CSP coefficient from Openvibe CSP config file."""
    pattern = '<SettingValue>(.+?)</SettingValue>'
    with open(infile, 'r') as f:
        content = f.read()
    coefficients = re.search(pattern, content).group(1).split(" ")
    coefficients = [x for x in coefficients if len(x) > 1]
    return coefficients


def extract_ov_header(textvalues, create_faketime=False):
    """Extract channel info from Openvibe CSV, also get sampling frequency."""
    header = list()
    initheader = textvalues[0][:]
    freq_present = False
    time_present = False

    # If there is a number on the first line of given CSV,
    # it is not the header format we know. We create stuff then.
    try:
        val = float(textvalues[0][0])
    except ValueError:
        pass
    else:
        logging.info("The header appears to be missing")
        header = ["ch" + str(x) for x in iter(
            range(1, 1+len(textvalues[0][:])))]
        logging.info("Created dummy channel names '%s'", header)
        # If header is missing, we create faketime. Function compute_numvalues
        # is responsible for this step and for renaming Faketime back to Time.
        #
        # However, we assume that no header means no time field in CSV.
        # This behaviour may be found inappropriate and reverted in da future.
        header.insert(0, "Faketime")
        return header, None

    for field in initheader:
        if field == "Time (s)":
            correct = "Time"
            time_present = True
        elif field == "Sampling Rate":
            freq_present = True
            continue
        elif field == "Identifier":
            correct = "Stimulation"
        else:
            correct = field

        header.append(correct)

    if time_present is False:
        header.insert(0, "Faketime")

    if freq_present is False:
        return header, None

    # sampling freq is the last value on second row
    textfreq = textvalues[1][-1]

    try:
        freq = int(textfreq)
        del textvalues[1][-1]
    except ValueError:
        freq = None

    return header, freq


def compute_numvalues(textvalues, header, sampling_frequency=None):
    """Convert CSV values to numerical bits in lists."""
    numvalues = list()
    faketime = 0
    create_faketime = False

    if header is not False and header[0] == "Faketime":
        create_faketime = True
        if sampling_frequency is None:
            faketime_step = 1
            logging.warning("Could not determine sampling frequency, "
                            "fake time values will equal recorded frames.")
            logging.info("You should provide sampling frequency using a "
                         "sampling_frequency attribute in BCPy constructor."
                         "Some functions won't work properly otherwise.")
        else:
            faketime_step = 1.0/sampling_frequency
            logging.info("Fake time values created out of sampling frequency")

    for row in textvalues:
        numrow = list()
        if create_faketime:
            numrow.append(faketime)
            faketime += faketime_step
        for field in row:
            try:
                numfield = float(field)
                numrow.append(numfield)
            except ValueError as ex:
                continue

        if not numrow == []:
            numvalues.append(numrow)
    if header is not False and create_faketime:
        header[0] = "Time"
    return header, numvalues


def read_ov_file(infile, sampling_frequency=None, external_header=False):
    """Set of actions to handle an Openvibe-generated CSV."""
    textvalues = get_csv_content(infile)
    if external_header is False:
        header, freq = extract_ov_header(textvalues)
        header, numvalues = compute_numvalues(textvalues, header,
                                              sampling_frequency)
    else:
        header, numvalues = compute_numvalues(textvalues, external_header,
                                              sampling_frequency)
    if sampling_frequency is not None:
        freq = sampling_frequency
        # override read value if any other is given
    return header, numvalues, freq


def get_external_header(infile):
    """Read header with channel info from another file."""
    textvalues = get_csv_content(infile)
    header, __ = extract_ov_header(textvalues)
    return header


def get_channels_from_values(values, header):
    """Create a dict ('channels') with channel-sorted values.

       channels = dict(channel1_name: [channel1_val1, channel1_val2, ...],
                       channel2_name: [channel2_val1, channel2_val2, ...],
                       ...)
       (channels["Time"] is a special entry with timestamps)
    """

    channels = dict()

    for index, channel in enumerate(header):
        data = [item[index] for item in values]
        channels[channel] = data

    return channels


def get_values_from_channels(channels, header):
    """Convert from channel-sorted dict to CSV-like list of values."""
    values = list()

    for index, __ in enumerate(channels["Time"]):
        row = list()
        for channel in header:
            row.append(channels[channel][index])
        values.append(row)

    return values


def prepare_stimulation_dict(stimulation_values):
    """Prepare a dict with structure {timing of stimulus:type of stimulus}."""
    stimulations = dict()
    for row in stimulation_values:
        stimulations[row[0]] = row[1]

    return stimulations


def write_csv(outfile, header, values):
    """Output CSV from 'values'."""
    with open(outfile, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(values)
