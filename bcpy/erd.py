from . import funcs
from . import stimul
from . import bp


def erd(active, rest):
    """The event-related de/sync formula. Output is in percents.

    If result is < 0, than what we have is ERD. Positive numbers denote ERS.
    """
    return ((active-rest)/rest)*100


def compute_erds_using_squared(channels, stimul_times, channel,
                               wanted_stimul_code,
                               offset, duration, baseline_duration,
                               sampling_frequency):
    """Compute relative ERD/ERS for all stimulation points.

    ERD is computed from active state of "duration" seconds, "offset" seconds
    after stimuli and rest state of "baseline_duration" before the stimuli,
    this all for one "channel" in "stimul_times" dict.

    Non-squared channels are used as normalization takes places before ERD
    computation (B. Graimann et al: Visualization of significant ERD/ERS
    patterns in multichannel EEG and ECoG data).
    """

    all_trials = list()

    def avg(x):
        return sum(x)/len(x)

    for timestamp in stimul_times[wanted_stimul_code]:
        epoch = funcs.get_epoch(channels, timestamp-baseline_duration,
                                timestamp+offset+duration)[channel]
        all_trials.append(epoch)

    average_epoch = [avg(x) for x in [list(col) for col in zip(*all_trials)]]

    weighted_trial = list()
    weighted_all_trials = list()
    for trial in all_trials:
        weighted_trial = list()
        for j, sample in enumerate(trial):
            try:
                w_sample = (sample-average_epoch[j])**2
            except IndexError:
                pass
                # silently skip ends of epochs where frames might be missing
            weighted_trial.append(w_sample)
            # (sample - mean of j-th sample averaged over all trials)^2
        weighted_all_trials.append(weighted_trial)

    average_w_trial = [avg(x) for x in [list(col)
                                        for col in zip(*weighted_all_trials)]]
    # contains samples in average of all weighted trials

    baseline_avg_trial = list()
    last_baseline_sample = int(baseline_duration*sampling_frequency)
    for sample in average_w_trial[:last_baseline_sample]:
        baseline_avg_trial.append(sample)
    baseline_average = avg(baseline_avg_trial)
    # contains only one number

    first_active_sample = int(baseline_duration*sampling_frequency
                              + offset*sampling_frequency)
    average_erd = [erd(x, baseline_average) for x in
                   average_w_trial[first_active_sample:]]
    result_erd = avg(average_erd)
    # computed for each sample of active period with reference
    # to average from all baselines, then squeezed to one value

    # the ERD course plot is best seen from weigthed BP of a trial
    # but better to undersample it
    sample_batch_size = int(sampling_frequency/4)
    smoothed = list()
    for p in range(0, len(average_w_trial), sample_batch_size):
        epoch = average_w_trial[p:p+sample_batch_size]
        smoothed.append(avg(epoch))

    return result_erd, smoothed


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
