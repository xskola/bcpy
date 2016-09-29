import csv
import sys


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


def extract_ov_header(textvalues):
    """Extract channel info from Openvibe CSV, also get sampling frequency."""
    header = list()
    initheader = textvalues[0][:]
    freq_present = False

    for field in initheader:
        if field == "Time (s)":
            correct = "Time"
        elif field == "Sampling Rate":
            freq_present = True
            continue
        elif field == "Identifier":
            correct = "Stimulation"
        else:
            correct = field

        header.append(correct)

    if not freq_present:
        return header, None

    # sampling freq is the last value on second row
    textfreq = textvalues[1][-1]

    try:
        freq = int(textfreq)
        del textvalues[1][-1]
    except ValueError:
        freq = None

    return header, freq


def compute_numvalues(textvalues):
    """Convert CSV values to numerical bits in lists."""
    numvalues = list()
    for row in textvalues:
        numrow = list()
        for field in row:
            try:
                numfield = float(field)
                numrow.append(numfield)
            except ValueError as ex:
                continue

        if not numrow == []:
            numvalues.append(numrow)
    return numvalues


def read_ov_file(infile):
    """Set of actions to handle an Openvibe-generated CSV."""
    textvalues = get_csv_content(infile)
    header, freq = extract_ov_header(textvalues)
    numvalues = compute_numvalues(textvalues)
    return header, numvalues, freq


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
