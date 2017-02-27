#!/usr/bin/python

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import funcs
import inout
import bp
import stimul
import erd
import logging


class BCPy:
    def __init__(self, signal=None, stimulations=None, features=None,
                 header=None, sampling_frequency=None, csp_config=None):
        logging.basicConfig(format='%(asctime)s %(message)s',
                            level=logging.DEBUG)
        external_header = False
        if header is not None:
            logging.info("Reading header file %s", header)
            self.header = inout.get_external_header(header)
            external_header = self.header
        if signal is not None:
            self.read_ov_signal(signal, sampling_frequency, external_header)
        if stimulations is not None:
            self.read_ov_stimulations(stimulations)
        if features is not None:
            self.read_ov_features(features)
        if csp_config is not None:
            self.read_ov_csp_config(csp_config)

        self.freqs = dict()

    def read_ov_signal(self, infile, sampling_frequency=None,
                       external_header=False):
        """Read Openvibe signal file."""
        logging.info("Reading signal file %s", infile)
        if sampling_frequency is not None:
            logging.info("Setting sampling frequency to %d Hz",
                         sampling_frequency)

        self.header, self.values, self.sampling_freq = inout.read_ov_file(
            infile, sampling_frequency, external_header)
        self.channels_from_values()

    def read_ov_stimulations(self, infile):
        """Read Openvibe stimulations file."""
        logging.info("Reading stimulations file %s", infile)
        self.stimulation_header, self.stimulation_values, __\
            = inout.read_ov_file(infile)
        self.stimulations = inout.prepare_stimulation_dict(
            self.stimulation_values)
        # this provides us with dict mapping { timing: stimul_code }
        self.get_stimul_times()
        # this is reverse mapping { stimul_code: [list of timestamps] }

    def read_ov_features(self, infile):
        """Read Openvibe features file."""
        logging.info("Reading features file %s", infile)
        self.feature_header, self.feature_values, __ \
            = inout.read_ov_file(infile)
        self.feature_channels = inout.get_channels_from_values(
            self.feature_values, self.feature_header)

    def read_ov_csp_config(self, infile):
        """Read Openvibe Common Spatial Patterns filter configuration."""
        logging.info("Reading CSP configuration file %s", infile)
        self.csp_config = list()
        coefficients = inout.get_csp_config(infile)
        try:
            num_channels = len(self.header)-1
            if len(coefficients) % num_channels != 0:
                logging.error("Number of channels does not match number "
                              "of CSP coefficients. Cannot pair.")
                return
        except AttributeError:
            logging.error("Error: Channels are not defined.")
            return

        num_filters = len(coefficients) / num_channels
        for csp in range(num_filters):
            this_csp_config = dict()
            offset = (csp-1)*num_channels
            for i, channel in enumerate(self.header[1:]):
                this_csp_config[channel] = float(coefficients[i+offset])
            self.csp_config.append(this_csp_config)

    def write_csv(self, outfile):
        """Output CSV with signal values."""
        # TODO choice for signal/features at least should be provided?
        # or not? since it is not possible to fiddle with these structs?
        logging.info("Writing working data into file %s", outfile)
        self.values_from_channels()
        inout.write_csv(outfile, self.header, self.values)

    def channels_from_values(self):
        """Create class 'channel' dict with signal datapoints."""
        self.channels = inout.get_channels_from_values(
            self.values, self.header)
        if not hasattr(self, 'unfiltered'):
            self.unfiltered = dict()
            for channel in self.channels:
                self.unfiltered[channel] = self.channels[channel][:]

    def values_from_channels(self):
        """Create CSV-formatted list for signal datapoints before export."""
        self.values = inout.get_values_from_channels(
            self.channels, self.header)

    def squeeze_channels(self):
        """Replace channels an average channel from all available ones."""
        self.channels, self.header = funcs.squeeze_channels(self.channels,
                                                            self.header)

    def compute_bp(self):
        """Compute average bandpower per data point by squaring."""
        self.squared_channels = bp.compute_squared_bp(self.channels)

    def get_stimul_times(self, stimul_codes=None):
        """Get precise stimulation timings."""
        stimul_times = stimul.get_stimulation_timings(
            self.stimulations,
            self.channels,
            stimul_codes)
        self.stimul_times = stimul_times

    def filter_channel(self, low, high, channel):
        """Apply bandpass filter to selected channel."""
        signal = funcs.butter_bandpass_filter(
            self.channels[channel],
            low, high,
            self.sampling_freq
        )
        self.channels[channel] = signal[:]

    def filter_channels(self, low, high):
        """Invoke filter_channel for all entries in 'channels' dict."""
        channel_list = self.header[1:]
        for channel in channel_list:
            self.filter_channel(low, high, channel)

    def revert_filtering(self, channel_list=None):
        """Revert filtering of all channels or one selected."""
        if channel_list is None:
            channel_list = self.header[1:]
        for channel in channel_list:
            self.channels[channel] = self.unfiltered[channel][:]
        del self.squared_channels

    def get_epoched_bandpowers(self, width=1):
        """Compute bandpowers per epoch with 'width' of n seconds.

        Squared channel values are used as BPs here.
        """
        if not hasattr(self, 'squared_channels'):
            self.compute_bp()

        return bp.get_epoched_bandpowers(self.squared_channels, width=width)

    def get_epoched_bandpower(self, channel, width=1):
        """Call get_epoched_bandpowers with limited channel set."""
        if not hasattr(self, 'squared_channels'):
            self.compute_bp()

        limited_channels = dict(Time=self.channels["Time"])
        limited_channels[channel] = self.squared_channels[channel]
        return bp.get_epoched_bandpowers(limited_channels, width=width)

    def compute_avg_stimul_bp(self, channel, stim_codes=None,
                              duration=2, offset=0):
        """Call compute_avg_stimul_bps for limited channel set."""
        if not hasattr(self, 'squared_channels'):
            self.compute_bp()

        limited_channels = dict(Time=self.channels["Time"])
        limited_channels[channel] = self.squared_channels[channel]
        return stimul.compute_avg_stimul_bps(limited_channels, self.header,
                                             self.stimul_times,
                                             stim_codes, duration, offset)

    def compute_avg_stimul_bps(self, stim_codes=None,
                               duration=2, offset=0):
        """Compute avg bandpower around stimulation points using squaring."""
        if not hasattr(self, 'squared_channels'):
            self.compute_bp()

        if stim_codes is None:
            stim_codes = list(stimul.names)

        return stimul.compute_avg_stimul_bps(self.squared_channels,
                                             self.header,
                                             self.stimul_times,
                                             stim_codes, duration, offset)

    def compute_erds_using_squared(self, channel, stimul_code,
                                   offset=0.5, duration=4,
                                   baseline_duration=2):
        """Compute event-related (de)synchronization per stimulation point."""
        if not hasattr(self, 'squared_channels'):
            self.compute_bp()
        return erd.compute_erds_using_squared(self.channels,
                                              self.stimul_times,
                                              channel, stimul_code,
                                              offset, duration,
                                              baseline_duration,
                                              self.sampling_freq)

    def compute_erds_using_fft(self, channel, lowfreq, highfreq,
                               stimul_code,
                               offset=0.5, duration=4,
                               baseline_duration=2):
        """Compute event-related (de)synchronization per stimulation point."""
        return erd.compute_erds_using_fft(self.channels,
                                          self.sampling_freq,
                                          self.stimul_times,
                                          channel, stimul_code,
                                          lowfreq, highfreq,
                                          offset, duration, baseline_duration)

    def compute_mi_erds(self, lowfreq=8, highfreq=30):
        """Show ERD for left/right MI and C4/C3 channels."""
        self.compute_erd_using_fft("C3", lowfreq, highfreq, 770)
        self.compute_erd_using_fft("C4", lowfreq, highfreq, 769)

    def compute_fft(self, channel):
        """Compute Fourier transform per channel."""
        freq, y = bp.compute_fft(self.channels[channel], self.sampling_freq)
        self.freqs[channel] = [list(freq), list(y)]  # ->tuple?

    def compute_ffts(self):
        """Call compute_fft() for all channels."""
        for channel in self.channels:
            self.compute_fft(channel)

    def destroy_time(self):
        """Overwrite channels' "Time" with sequence of natural numbers.

        This function is useful for displaying e.g. features regardless
        on the time they've been generated."""
        self.unfiltered["Time"] = self.channels["Time"][:]
        for e, __ in enumerate(self.channels["Time"]):
            self.channels["Time"][e] = e

    def label_channels(self, caption):
        """Add label to channels.

        Good if you plot more channels or features or whatever in one plot.
        This change is not revertible at the moment. Just add stuff."""
        newheader = list()
        keys = self.header[:]
        for channel in keys:
            if channel == "Time":
                continue
            newlabel = channel + " " + caption
            newheader.append(newlabel)
            self.channels[newlabel] = self.channels.pop(channel)

        self.header = newheader[:]

    # Plotting

    def plot_channels(self, discrete=False):
        """Call plot_channel for all channels."""
        for channel in self.channels:
            if channel == "Time":
                continue
            else:
                self.plot_channel(channel, discrete=discrete)

    def plot_channel(self, channel, discrete=False):
        """Plot a channel."""
        # the 'discrete' param might be useless since we have plot_features nu
        if not discrete:
            plt.plot(self.channels['Time'], self.channels[channel],
                     label=channel)
        else:
            plt.plot(self.channels['Time'], self.channels[channel],
                     'o', label=channel)
        plt.subplot()
        plt.xlabel('Time')
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=1,
                   ncol=2, mode="expand", borderaxespad=0.)
        plt.xlim(15, 50)  # what do you think about these defaults?
        # plt.ylim(-450, 450)
        plt.autoscale(enable=False)

    def plot_features(self):
        """Plot a feature_channel."""
        # this deserves some TODO care
        plt.plot(self.feature_channels['Feature 1'],
                 self.feature_channels['Feature 2'],
                 'o', label="Features")
        plt.xlabel('Feature')
        plt.ylabel('Feature')
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=1,
                   ncol=2, mode="expand", borderaxespad=0.)

    def plot_stimulations(self, stimul_codes=None):
        """Create vertical bars from stimulation timings."""
        if stimul_codes is None:
            stimul_codes = [stimul.codes['left'], stimul.codes['right']]
            # I might want to change this in the future
        has_label = dict((code, False) for code in stimul_codes)

        for stimul_time in self.stimulations:
            if self.stimulations[stimul_time] in stimul_codes:
                line_color = stimul.pick_stimul_color(
                    self.stimulations[stimul_time])
                code = int(self.stimulations[stimul_time])
                if has_label[code]:
                    plt.axvline(stimul_time,
                                ymin=0.2, ymax=0.8, linewidth=2,
                                linestyle="dotted",
                                color=line_color)
                else:
                    plt.axvline(stimul_time,
                                ymin=0.2, ymax=0.8, linewidth=2,
                                linestyle="dotted",
                                color=line_color, label=stimul.names[code])
                    has_label[code] = True

    def plot_fft(self, channel, low=0.0, high=float("inf")):
        """Plot output from compute_fft held in freq class var."""
        if low == 0.0 and high == float("inf"):
            funcs.plot_data(self.freqs[channel][1], self.freqs[channel][0],
                            channel + " spectrum")
        else:
            a, b = bp.slice_freqs(self.freqs[channel][0], low, high)
            caption = channel + " spectrum [" + str(low)\
                + ", " + str(high) + "] Hz"
            funcs.plot_data(self.freqs[channel][1][a:b],
                            self.freqs[channel][0][a:b], label=caption)

    def plot(self, channels, discrete=False):
        """Plot non-internal structure. Useful for epoched_bandpowers."""
        for channel in channels:
            if channel == "Time":
                continue
            else:
                if not discrete:
                    plt.plot(channels['Time'], channels[channel],
                             label=channel)
                else:
                    plt.plot(channels['Time'], channels[channel],
                             'o', label=channel)
                plt.subplot()
                plt.xlabel('Time')
                plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=1,
                           ncol=2, mode="expand", borderaxespad=0.)
                # plt.xlim(20, 22)  # what do you think about these defaults?
                plt.ylim(-450, 450)
                plt.autoscale(enable=False)

    def plot_show(self):
        """Invoke plt.show()."""
        plt.show()

# Edit functions

    def cutout_epoch(self, low, high):
        """Remove chunk of signal data from class' channels variable."""
        self.channels = funcs.cutout_epoch(self.channels, low, high)
