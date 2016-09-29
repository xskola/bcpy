from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt


def get_epoch(struct, low, high):
    """Limit channel structure according to given 'Time' constraints.

    Input is either dictionary of 'channels' that must contain 'Time' key.
    Or a list/tuple with lists of values, than first "column" is used as
    a filtering criterion.
    """
    if low > high:
        low, high = high, low
    if type(struct) is dict:
        data = struct["Time"]
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


def get_channels_avgs(channels):
    """Compute average values for all keys in given dict of channels."""
    output = dict()
    for channel in channels.keys():
        output[channel] = sum(channels[channel])/len(channels[channel])
    return output


def get_avg_values_lists(data):
    """Compute average values for data in lists."""
    output = list()
    for l in data:
        output.append(sum(l)/len(l))
    return output


def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    """Perform band pass filtering using butterworth filter."""
    def butter_bandpass(lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y.tolist()


def plot_data(data, time=None, label=None):
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
               ncol=2, mode="expand", borderaxespad=0.)
    # plt.yscale('log')
    # Next step here is to get sensible zoom from the datapoint count

    plt.autoscale(enable=False)
