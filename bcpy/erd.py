import funcs
import stimul
import bp


def erd(active, rest):
    """The event-related de/sync formula. Output is in percents.

    If result is < 0, than what we have is ERD. Positive numbers denote ERS.
    """
    return ((active-rest)/rest)*100


def compute_erds_using_squared(channels, stimul_times, channel,
                               wanted_stimul_code,
                               offset, duration, baseline_duration):
    """Compute relative ERD/ERS for all stimulation points.

    ERD is computed from active state of "duration" seconds, "offset" seconds
    after stimuli in "stimul_times" and rest state of "baseline_duration"
    before the stimuli, this all for one "channel"."""

    erds = list()
    for timestamp in stimul_times[wanted_stimul_code]:
        active_epoch = funcs.get_epoch(channels, timestamp+offset,
                                       timestamp+offset+duration)
        baseline_epoch = funcs.get_epoch(channels,
                                         timestamp-baseline_duration,
                                         timestamp)

        active = funcs.get_channels_avgs(active_epoch)[channel]
        baseline = funcs.get_channels_avgs(baseline_epoch)[channel]

        this_erd = erd(active, baseline)
        erds.append(this_erd)

    return print_erd_stats(channel, wanted_stimul_code, erds)


def compute_erds_using_fft(channels, sampling_freq, stimul_times,
                           channel, wanted_stimul_code,
                           lowfreq, highfreq,
                           offset, duration, baseline_duration):
    """Not Really Working: Compute relative ERD/ERS for stimulation points"""
    # The issue here is that different lengths of signal produce different
    # results in frequency spectrum values. So I guess we need to normalize.
    # (somehow)
    erds = list()
    for timestamp in stimul_times[wanted_stimul_code]:
        # use epoching function to get slice of channels dict
        __, active = bp.get_epoch_bp(channels, sampling_freq, channel,
                                     lowfreq, highfreq,
                                     timestamp+offset,
                                     timestamp+offset+duration)
        __, baseline = bp.get_epoch_bp(channels, sampling_freq, channel,
                                       lowfreq, highfreq,
                                       timestamp-baseline_duration, timestamp)
        # compute average for the whole frequency range
        active_avg = (sum(active)/len(active))  # /duration
        baseline_avg = (sum(baseline)/len(baseline))  # /baseline_duration
        avgerd = erd(active_avg, baseline_avg)
        erds.append(avgerd)

    print_erd_stats(channel, wanted_stimul_code, erds, lowfreq, highfreq)


def print_erd_stats(channel, wanted_stimul_code, erds,
                    lowfreq=None, highfreq=None):
    """Guess this will be decomissioned soon. Print table with ERD/S stats."""
    return str(sum(erds)/len(erds))
    # Don't print the fancy table. I guess it is pointless.
    title = "ERD/ERS stats for channel " + channel + " and event '"\
            + stimul.names[wanted_stimul_code] + "'"
    print title
    print "-" * len(title)
    if lowfreq is not None:
        print "Frequency range from " + str(lowfreq) + " Hz to "\
              + str(highfreq) + " Hz"
    print "Avg: " + str(sum(erds)/len(erds))
    print "Max: " + str(max(erds))
    print "Min: " + str(min(erds))
