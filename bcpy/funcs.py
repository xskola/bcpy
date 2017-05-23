from . import inout
from scipy.signal import butter, filtfilt, iirdesign
import matplotlib.pyplot as plt
import logging


def get_epoch(struct, low, high):
    """Limit channel structure according to given 'Time' constraints.

    Input is either dictionary of 'channels' that must contain 'Time' key.
    Or a list/tuple with lists of values, than first "column" is used as
    a filtering criterion.
    """
    if low > high:
        low, high = high, low
    if type(struct) is dict:
        if "Time" in struct:
            key = "Time"
        elif "Freq" in struct:
            key = "Freq"
        else:
            logging.warn("get_epoch: no index, can't do it.")
            return
        data = struct[key]
    elif type(struct) is list or type(struct) is tuple:
        data = struct[0]
    else:
        return None

    it = (x[0] for x in enumerate(data) if (x[1] > low and x[1] < high))
    a = next(it)
    b = a
    for b in it:
        pass

    if type(struct) is dict:
        epoch = dict()
        for channel in struct:
            epoch[channel] = struct[channel][a:b]
        return epoch

    if type(struct) is list or type(struct) is tuple:
        epoch = list()
        for elem in struct:
            epoch.append(elem[a:b])
        return epoch


def cutout_epoch(struct, low, high):
    """Remove a chunk of channel data defined by its Time boundaries."""
    if type(struct) is list:
        raise TypeError('Cutting out is supported only for dicts.')
        # We might want to do this even for lists in the Future.
        return

    if low == 0:
        piece1 = dict.fromkeys(struct, [])
    else:
        piece1 = get_epoch(struct, 0, low)
    if high == float("inf"):
        piece2 = dict.fromkeys(struct, [])
    else:
        piece2 = get_epoch(struct, high, float("inf"))

    result = dict()
    for key in struct:
        result[key] = piece1[key] + piece2[key]

    return result


def get_channels_avgs(channels):
    """Compute average values for all keys in given dict of channels."""
    output = dict()
    for channel in channels.keys():
        try:
            output[channel] = sum(channels[channel])/len(channels[channel])
        except ZeroDivisionError:
            logging.error("get_channels_avg: this epoch has empty channel " + channel + ".")
            output[channel] = 0
    return output


def get_avg_values_lists(data):
    """Compute average values for data in lists."""
    output = list()
    for l in data:
        output.append(sum(l)/len(l))
    return output


def squeeze_channels(channels, header):
    """Create an average channel from all available ones."""
    values = inout.get_values_from_channels(channels, header)
    result = list()
    for line in values:
        row = [line[0]]
        average = sum(line[1:])/len(line[1:])
        row.append(average)
        result.append(row)

    new_header = ["Time", "Avg"]
    avg_channels = inout.get_channels_from_values(result, new_header)
    return avg_channels, new_header


def butter_bandpass_filter(data, lowcut, highcut, fs, setorder=False, order=4):
    """Perform band pass filtering using butterworth filter."""
    def butter_bandpass(lowcut, highcut, fs, order):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        hz = 1 / nyq
        ws = [low-hz, high+hz]
        if setorder is True:
            b, a = butter(order, [low, high], btype='band')
        else:
            b, a = iirdesign(wp=[low, high], ws=ws,
                             gstop=10, gpass=0.2, ftype='ellip', output='ba')
        return b, a

    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y.tolist()


def plot_data(data, time=None, label=None, log=False):
    """An overly simple wrapper for matplotlib."""
    if time is None:
        plt.plot(data, label=label)
        # plt.xlim(10000,12000) # this may result in initial confusion
        # plt.ylim(-20, 20) # the initial scale may be completely derailed
    else:
        plt.plot(time, data, label=label)
        # plt.xlim(20,22) # also bad
        # plt.ylim(-450, 450)
    # TODO
    plt.subplot()
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=1,
               ncol=6, mode="expand", borderaxespad=0.)
    if log is True:
        plt.yscale('log')
    # Next step here is to get sensible zoom from the datapoint count

    plt.autoscale(enable=False)
