#!/usr/bin/python

import os
import sys
sys.path.append(os.path.abspath('..'))
import bcpy


signal = SignalThing(str(sys.argv[1]), str(sys.argv[2]))
signal.values = funcs.get_epoch(signal.values, 10, 999999)
signal.filter_channel(8, 24, ["C3"])
print signal.compute_avg_baseline_bp("C3")
signal.plot_channel("C3")
for item in signal.compute_erd_percentage("C3",0.5,2,2)[770]:
    print item
signal.plot_stimulations([funcs.stimcodes["right"]])
signal.plot_epoched_bandpowers(signal.get_epoched_bandpowers("C3", 1))

features = SignalThing(str(sys.argv[3]))
for index, __ in enumerate(features.channels["Feature 1"]):
    features.channels["Feature 1"][index] *= 10
    
features.plot_channel("Feature 1", True)

#signal.revert_filtering()
#signal.filter_channel(8, 15, ["C3"])
#signal.plot_channel("C3")
#for item in signal.compute_erd_percentage("C3",0,1,1)[770]:
#    print item
#signal.plot_epoched_bandpowers(signal.get_epoched_bandpowers("C3", 1.0))


#bps = signal.get_epoched_bandpowers("C3")
#signal.plot_epoched_bandpowers(bps)
plt.show()


def ex2():
    #signal.values = funcs.get_epoch(signal.values, 10, 200)
    #signal.channels_from_values()

    #signal.filter_channel(8, 12, ["C3","C4","FC1","FC2","Cz"])
    signal.filter_channel(8, 30, ["C3"])

    print signal.compute_erd_percentage("C3")
    #stimul_times = signal.find_stimul_times([signal.stimcodes["left"]])
    #signal.compute_erd_percentage(stimul_times, "C4")

    #signal.channels_from_values()

    #signal.plot_channel("Cz")
    #signal.plot_channel("FC1")
    #signal.plot_channel("FC2")
    #signal.plot_channel("C3")
    #signal.plot_channel("C4")
    #signal.plot_stimulations()
    #powers = signal.get_epoched_bandpowers()
    #channel_powers = funcs.get_channels_from_values(powers, signal.header)
    #print channel_powers
    #signal.plot_channel("C3", channel_powers)
    #plt.show()

def ex1():
    toolbox = SignalThing(infile)

    #region1 = toolbox.get_epoch(40,60)
    #print toolbox.get_avg_values(region1)
    epoch = toolbox.get_epoch(10,60)
    toolbox.values = epoch
    toolbox.get_channel_values()
    #channels = toolbox.get_channel_values(epoch)
    #toolbox.filter_channel('C3', 5, 10, channels)
    #toolbox.plot_channel('C3', channels)
    #toolbox.filter_channel('C3', 1, 10)
    toolbox.plot_channel('Cz')
    #toolbox.plot_channel('C3', toolbox.unfiltered)
    plt.show()

    #for idx, num in enumerate(toolbox.channels['C3']):
    #    print str(num) + " " + str(toolbox.unfiltered['C3'][idx])
