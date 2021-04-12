#!/usr/bin/env python

import epics as e
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--up", action="store_true")
parser.add_argument("-d", "--down", action="store_true")
parser.add_argument("-i", "--id", type=int, default=None)
args = parser.parse_args()

unit_id = args.id
if not unit_id is None:

    pvset = {"sw-sub":{"CURR":15,"VOLT":-6500},
             "sw-dvdd":{"CURR":15,"VOLT":1750},
             "sw-refin":{"CURR":15,"VOLT":-5200},
             "dcd-amplow":{"CURR":300,"VOLT":380},
             "dcd-avdd":{"CURR":3000,"VOLT":1900},
             "dcd-dvdd":{"CURR":1000,"VOLT":1850},
             "dcd-refin":{"CURR":1000,"VOLT":500},
             "dhp-core":{"CURR":800,"VOLT":1200},
             "dhp-io":{"CURR":550,"VOLT":1800},
             "bulk":{"CURR":10,"VOLT":10000},
             "clear-on":{"CURR":70,"VOLT":19000},
             "clear-off":{"CURR":40,"VOLT":4500},
             "gate-on1":{"CURR":30,"VOLT":-1500},
             "gate-on2":{"CURR":30,"VOLT":-1600},
             "gate-on3":{"CURR":30,"VOLT":-1700},
             "gate-off":{"CURR":30,"VOLT":3000},
             "source":{"CURR":150,"VOLT":6000},
             "ccg1":{"CURR":10,"VOLT":-100},
             "ccg2":{"CURR":10,"VOLT":-200},
             "ccg3":{"CURR":10,"VOLT":-300},
             "hv":{"CURR":1000,"VOLT":-70000},
             "drift":{"CURR":10,"VOLT":-5000},
             "guard":{"CURR":10,"VOLT":-4000}
    }

    pvs = {}
    for pvname, settings in pvset.items():
        pvs[pvname] = {}
        for setname in settings.keys():
            name = "PXD:P{}:{}:{}:req".format(unit_id, pvname, setname)
            print "pvname", name
            pvs[pvname][setname] = e.PV(name)

    act = None
    if args.up == True:
        act = ["CURR", "VOLT"]
    elif args.down == True:
        act = ["VOLT", "CURR"]
        n = {}
        keys = pvset.keys()
        keys.reverse()
        print(keys)
        for key in keys:
            n[key] = pvset[key]
        pvset = n

    if not act is None:
        for a in act:
            for pvname, settings in pvs.items():
                value = 0
                if args.up == True: value = pvset[pvname][a]
                print("Setting PXD:P{}:{}:{}:req to {}".format(unit_id, pvname, a, value))
#                settings[a].put(value)
