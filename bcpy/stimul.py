import funcs
import bp

codes = dict(
    left=769,
    right=770,
    eot=800,  # end of trial
    eos=1010,  # end of session
)


names = dict([(codes[x], x) for x in codes])
# this reverse mapping was proudly generated using an assumption of bijectivity


def get_stimulation_timings(stimulations, channels, stimul_codes=None):
    """Search 'stimulations' structure and get its precise timings."""
    if stimul_codes is None:
        stimul_codes = list(codes.values())

    stimpoints = dict()
    for stimul_code in stimul_codes:
        stimpoints[stimul_code] = list()

    for stimul_start in stimulations:
        for stimul_code in stimul_codes:
            if stimulations[stimul_start] == stimul_code:
                timeval = channels["Time"][next(
                    x[0] for x in enumerate(channels["Time"])
                    if x[1] > stimul_start)]
                # find first Time value greater than
                # stimulation code provided timestamp

                # timeval = stimul_start
                # ^^^ explore this mighty simplification
                stimpoints[stimul_code].append(timeval)

    return stimpoints


def compute_avg_stimul_bps(channels, header, stimul_times,
                           stim_codes, duration, offset=0):
    """Compute average band powers around all stimuli.

    Negative duration computes pre-stimul BPs.
    This is an average of all averages before stimulation points."""
    epochs = dict((x, []) for x in channels.keys())

    for stimul_code in stimul_times:
        if stimul_code not in stim_codes:
            if stimul_code in epochs:
                del epochs[stimul_code]
            continue

        for timestamp in stimul_times[stimul_code]:
            epoch = funcs.get_epoch(channels,
                                    timestamp+offset+duration,
                                    timestamp)
            avg = funcs.get_channels_avgs(epoch)
            for channel in avg:
                epochs[channel].append(avg[channel])

    return funcs.get_channels_avgs(epochs)


def compute_avg_prestimul_bps_fft(channels, header, stimul_times,
                                  stim_codes, baseline_duration):
    """Compute average band powers before all stimuli."""
    # a sketch for TODO using FFT BP
    # ...
    epochs = dict((x, []) for x in channels.keys())
    bps = list()

    for stimul_code in stimul_times:
        if stimul_code not in stim_codes:
            if stimul_code in epochs:
                del epochs[stimul_code]
            continue

        for timestamp in stimul_times[stimul_code]:
            x, power = bp.get_epoch_bp(channels, 500, "C4", 8, 12,
                                       timestamp-baseline_duration, timestamp)
            funcs.plot_data(x, power)
            bps.append(sum(power)/len(power))

    return sum(bps)/len(bps)


def pick_stimul_color(code):
    """Generate recyclable colors for vertical lines for stimuli codes."""
    if code == codes["left"]:
        return "green"
    if code == codes["right"]:
        return "red"
    else:
        return (code*7 % 10*0.1, code*3 % 10*0.1, code*4 % 10*0.1)
