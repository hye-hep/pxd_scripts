#! /usr/bin/python3

import os
import numpy as np
from matplotlib import pyplot as plt
import plots
from epics_utils import get_pv
from pyDepfetReader import FileReader
from argparse import ArgumentParser
from glob import glob
import time

max_row = 768
max_col = 256

dhes = ['H1011','H1021','H1031','H1041','H1051','H1061','H1071','H1081', 'H1012','H1022', #'H1032',
    'H1042','H1052','H1062','H1072','H1082', 'H2041','H2051','H2042','H2052']

if __name__ == '__main__':

    parser = ArgumentParser(description='Analyse run data')
    parser.add_argument('--exp', dest='expnr',type=int,default=12)
    parser.add_argument('--run', dest='run',type=int,default=0)
    parser.add_argument('-f', '--file',dest='filename',default=None)
    parser.add_argument('--nframes', dest='nframes',type=int,default=0)
    args = parser.parse_args()

    if not args.filename:
        plthead="Exp%s_Run%s"%(args.expnr,args.run)
        file_path="/data/commissioning/runs/all/EXP"+format(args.expnr,"04")
        file_names=glob(os.path.join(file_path,"Run"+format(args.run,"04")+"-0.dat"))
        #file_names=glob(os.path.join(file_path,"Run"+format(args.run,"04")+"*.dat"))
    else:
        plthead='data'
        file_names=[args.filename]
        file_path=os.path.realpath(args.filename)

    print(file_names)

    if len(file_names) == 0:
        print("No data file found.")
        import sys
        sys.exit()

    devices={}
    modules={}
    module_type={}
    for dhe in dhes:
        devices[dhe] = get_pv("PXD:B:config-"+dhe,"device_config:VALUE:set").get()
        modules[dhe] = get_pv("PXD:B:config-"+dhe,"device_module:VALUE:set").get()
        module_type[dhe] = get_pv("PXD:B:config-"+dhe,"module_type:VALUE:set").get()

    totalNumberOfFrames=args.nframes

    reader = FileReader(-1,0)
    reader.set_debug_output(False)
    #reader.set_fill_info = True
    #reader.return_trigger = True
    reader.return_time = True
    #reader.return_dhc_time = True

    if totalNumberOfFrames ==0:
        for f in file_names:
            reader.open(f)
            print(f, reader.getNumberOfFrames())
            totalNumberOfFrames = totalNumberOfFrames + reader.getNumberOfFrames()

    hitmaps={}

    t0 = time.time()
    for dhe in dhes:
        hitmaps[dhe]=np.zeros((max_row, max_col), dtype=np.int64)
    for f in file_names:
        reader.open(f)

        for idx,event in enumerate(reader):
            for dhe, data,raw,dac in event:
                if dhe in dhes:
                    hitmaps[dhe][data[:, 1], data[:, 0]] += 1

    print('total frames ', totalNumberOfFrames)
    print('cost time',time.time()-t0)

    np.save("hitmaps_%s"%plthead, hitmaps)

