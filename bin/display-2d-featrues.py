#!/usr/bin/python

import os
import sys
sys.path.append(os.path.abspath('..'))
import bcpy

signal = bcpy.BCPy(str(sys.argv[1]))
signal.label_channels("left")
signal.channels["Time"] = signal.channels["Feature 2 left"]
signal.plot_channel("Feature 1 left", discrete=True)

signal.read_ov_signal(str(sys.argv[2]))
signal.label_channels("right")
signal.channels["Time"] = signal.channels["Feature 2 right"]
signal.plot_channel("Feature 1 right", discrete=True)
#signal.read_ov_signal(str(sys.argv[3]))
#bps = signal.get_epoched_bandpowers()
#signal.plot_epoched_bandpowers(bps)
#signal.compute_bp()
#bp_channels = pt.funcs.get_channels_from_values(signal.bp_values, signal.header)
#signal.channels = bp_channels
#signal.plot_channels(discrete=False)

signal.plot_show()
