from scipy import fft, arange
import bcpy.funcs as funcs


def compute_squared_bp(channels):
    """Compute band power estimates by squaring channel values."""
    squared_channels = dict()
    for channel in channels:
        if channel == "Time":
            squared_channels[channel] = channels[channel][:]
            continue
        squared_channel = [x**2 for x in channels[channel]]
        squared_channels[channel] = squared_channel

    return squared_channels


def compute_fft(data, sampling_freq):
    """Compute real part of FFT and return only the side > 0."""
    n = len(data)
    y = fft(data)/n
    k = arange(n)
    T = float(n/sampling_freq)
    freq = k/T  # two sides frequency range
    freq = freq[range(n/2)]  # one side frequency range
    return freq, abs(y)

    # Below is the numpy version
    # y = np.fft.fft(data)
    # freq = np.fft.fftfreq(len(data), 1.0/sampling_freq)
    # a = next(x[0] for x in enumerate(freq) if x[1] > 0)
    # b = next(x[0] for x in enumerate(freq) if x[1] < 0)
    # return freq[a:b].tolist(), np.abs(y)[a:b].tolist()


def get_epoch_bp(channels, sampling_freq, channel,
                 lowfreq, highfreq, starttime, stoptime):
    """Compute bandpower of selected epoch in selected freqs."""
    if starttime > stoptime:
        starttime, stoptime = stoptime, starttime
    epoch = funcs.get_epoch(channels, starttime, stoptime)
    freq, y = compute_fft(epoch[channel], sampling_freq)
    low, high = slice_freqs(freq, lowfreq, highfreq)
    freq = freq[low:high]
    y = y[low:high]

    return freq, y


def get_epoched_bandpowers(channels, width=1):
    """Compute average band power per epoch from squared channel values."""
    # this one is fast and a bit inaccurate
    avgs = dict((channel, []) for channel in channels)
    p = 0
    n = 500
    na = 499
    end = len(channels["Time"]) - n
    while True:
        for channel in channels:
            s = sum(channels[channel][p+0:p+(n-1)])/na
            avgs[channel].append(s)
        p += n
        if p > end:
            break
    return avgs


def get_epoched_bandpowers_orig(channels, width=1):
    import numpy as np
    # this one is correct
    if "Time" in channels:
        index = "Time"
    elif "Freq" in channels:
        index = "Freq"
    else:
        logging.warn("get_epoched_bandpowers_orig: no index, can't do it.")
        return

    result = dict((channel, []) for channel in channels)
    for second in np.arange(channels[index][0],
                            channels[index][-1],
                            width):
        epoch = funcs.get_epoch(channels, second, second+width)
        epoch_avg = funcs.get_channels_avgs(epoch)
        for channel in epoch_avg:
            result[channel].append(epoch_avg[channel])

    return result


def slice_freqs(data, low, high):
    """Find indices for desired range of freqs in FFT output."""
    if low > high:  # TODO error handling
        print("nope nope nope")

    it = (x[0] for x in enumerate(data) if (x[1] > low and x[1] < high))
    a = next(it)
    b = a
    for b in it:
        pass
    return a, b
