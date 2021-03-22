#!/usr/bin/env python

import subprocess
import shlex
import time
from multiprocessing.pool import ThreadPool

from os.path import isfile, join
from os import listdir
import re
from glob import glob

if __name__ == '__main__':

    expnr = 16
    path = 'dqm.belle2.org/past_runs/expreco_exp%i_canvas'%expnr

    rundependency = False

    thread_count=5
    #thread_count = multiprocessing.cpu_count()

    if rundependency:
        files = glob(join(path,'pxd_dqm_e%04i*.root'))
    else:
        files = glob(join(path,'dqm_*canvas.root'))

    runs = [int(filter(str.isdigit, re.findall('r\d{6}', fname)[0])) for fname in files]

    length =len(runs)
    print('from run%i to %i, in total %s'%(runs[0],runs[-1],length))

    def call_proc(cmd):
        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return (out, err)

    pool = ThreadPool(thread_count)

    t0 = time.time()
    results = []

    for run in runs:
        arguments = '--path %s --exp %s --run %s'%(path, expnr, run)
        if rundependency:
            results.append(pool.apply_async(call_proc, ("python trackcharge_langau.py " + arguments,)))
        else:
            results.append(pool.apply_async(call_proc, ("python trackcharge_langau_DQMcanvas.py " + arguments,)))

    pool.close()
    pool.join()

    for result in results:
        out, err = result.get()
        print("out: {} err: {}".format(out, err))

    t1 = time.time()
    print('length %s, count %s'%(length,thread_count))
    print('time cost',t1-t0)


