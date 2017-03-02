BCPy is a tool for analysis of EEG data with focus on motor imagery brain-computer interface (MI-BCI) data analysis, such is ERD computation and plotting data with regard to stimuli in MI-BCI training. It is currently being developed and there is no stable release. It might work, though.

## Examples

First of all, let me tell you there is a couple of examples in the bin/ folder in BCPy tree. You might get a very clear idea on how to operate this pile of code out of reading the examples. For very poor wannabe manual, read on please.

## Reading files

BCPy supports Openvibe-exported CSVs using these functions:

 * Signal files `read_ov_signal()`
 * Stimulation timings `read_ov_stimulations()`
 * Exported features `read_ov_features()`

However, even generic CSVs are supported, assuming that you provide an external header in a separate file. The constructor of BCPy class allows you to specify path to OV signal/stimulations/features files, header, and sampling frequency (provided it is not in the signal file).

`__init__(self, signal=None, stimulations=None, features=None, header=None, sampling_frequency=None)`

## File format

The CSV is expected to have following format:

```
Time (s), (channel name1), (channel name2), (...), Sampling Rate
(time value1), (channel1 value1), (channel2 value1), (...), (sampling frequency)
(time value2), (channel1 value2), (channel2 value2), (...)
(...), (...), (...), (...)
```

In case you don't use Openvibe exported CSVs, your file might look something like:

```
(channel1 value1), (channel2 value1), (...)
(channel1 value2), (channel2 value2), (...)
(...), (...), (...)
```

Which needs to be accompanied by header file in format

```
(channel name1), (channel name2), (...)
```

and sampling_frequency parameter set in the constructor, otherwise half of the functionality will be broken. There is currently not much of an error checking, so the program crashes on missing values when there are some.

# Incomplete overview of BCPy functionality

Please look at bcpy/bcpy.py for complete list of BCPy class functionality. BCPy class methods call underlying methods from bp.py, erd.py, funcs.py, inout.py, and stimul.py modules. Underlying methods have more general usability and you might prefer to directly use them in some cases. Also more detailed docstring documentation is provided in lower level files.

## Filtering

```
def filter_channel(self, low, high, channel): Apply bandpass filter to selected channel.
def filter_channels(self, low, high): Invoke filter_channel for all entries in 'channels' dict.
def revert_filtering(self, channel_list=None): Revert filtering of all channels or one selected.
```

## Band-power
Approximation of band-power is stored in `BCPy.squared_channels` variable, computed upon signal reading.

This function gives an approximation of band-power in epochs that could be easily plotted.
```
def get_epoched_bandpowers(self, width=1): Compute bandpowers per epoch with 'width' of n seconds.
```

FFT:
```
def compute_fft(self, channel): Compute Fourier transform per channel.
def compute_ffts(self): Call compute_fft() for all channels.
```

## ERD

```
compute_erds_using_squared(self, channel, stimul_code, offset=0.5, duration=4, baseline_duration=2):
```
Compute event-related (de)synchronization per stimulation point.
```
compute_avg_stimul_ffts(self, channel, stim_codes, duration, lowfreq, highfreq, offset=0):
```
Compute average frequency spectra (FFT) for `duration` seconds before and after all listed `stim_codes`. Difference between these spectra shows strong/weak frequency components of ERD. Example shown in `bin/bcpy-stimuli-fft-diff`.

## CSP
```
read_ov_csp_config(self, infile): Read Openvibe Common Spatial Patterns filter configuration.
```
CSP configurations are paired with channels in `BCPy.header` to dictionaries. The dictionaries are saved to list of spatial filters `BCPy.csp_config`. An example that prints CSP configuration can be found in `bin/bcpy-csp`.

## Plotting

```
def plot_channel(self, channel, discrete=False): Plot a channel.
def plot_channels(self, discrete=False): Call plot_channel for all channels.
def plot_features(self): Plot a feature_channel.
def plot_stimulations(self, stimul_codes=None): Create vertical bars from stimulation timings.
def plot_fft(self, channel, low=0.0, high=float("inf")): Plot output from compute_fft held in freq class var.
def plot(self, channels, discrete=False): Plot non-internal structure. Useful for epoched_bandpowers.
def plot_show(self): Invoke plt.show().
```

Either matplotlib show function or `BCPy.plot_show()` must be called in order to show the plot.

## Editing

```
def cutout_epoch(self, low, high): Remove chunk of signal data from class' channels variable.
def squeeze_channels(self): Replace the channel set with one average channel from all available ones.
```

## Writing files

Signal values can be exported to separate CSV using `write_csv()` function.

```
def write_csv(self, outfile): Output CSV with signal values.
```

## Class variables

Upon reading a CSV signal file into `BCPy.values`, the samples are re-organized channel-wise into dictionary `BCPy.channels`, that has a form:

```
{ "Time": list(timevalue1, timevalue2, ...),
  channel1_name: list(value1, value2, ...),
  channel2_name: list(value1, value2, ...),
  ...
}
```

All signal operations are executed on `channels` structure. Channel names are held in `BCPy.header`, including the "Time" fake channel. Sampling frequency lies in `BCPy.sampling_freq`. When filtering is invoked, originals of the `channels` are copied into `BCPy.unfiltered` and drawn back in case of invocation of `revert_filtering()`.

Features and stimulation structures are prefixed with `feature` and `stimulations`, such as `BCPy.feature_header`, `BCPy.stimulations_header`, `BCPy.feature_channels`. Dictionaries for stimulations are two:

 * `BCPy.stimulations`: provides us with dict mapping `{ timing: stimul_code }`
 * `BCPy.stimul_times`: this is reverse mapping `{ stimul_code: [list of timestamps] }`


# If you really want to use this,

it will make me very happy; however, I am aware of the heavily developmental status of this set of sources. You probably have more problems after the decision to try this application has been made. Don't hesitate to contact me in case of everything-is-on-fire or other classes of problems, I might help you.
