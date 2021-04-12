#!/usr/bin/env python

"""
This script is used for service qualification of Camera Link Cables. 
One DHE (+ DHI channel) is used for testing CLC cables, it need to be specified in script and in sequencer set to follow global 
Following aspects are included in testing:
    - turning on to standby (DHP link checks, sw_seq_GM are not skiped)
    - JTAG, ASIC IDCode, PV dumps 
    - Trigger
"""

from epics_utils import get_pv
import time
from waiting import wait, TimeoutExpired
import log_utils
import numpy as np
from os.path import isfile
import config_utils

logger = log_utils.get_pxd_main_logger(application_name="ServiceTest", loglevel=log_utils.FINEST, no_remote=True)

if __name__ == "__main__":

    ## turn on module to STANDBY and check the time cost. 
    dhe = 'H2041'
    dhc = 'H20'
    dhi = 'H28m'

    # off: 1, standby: 2, peak: 3
    target = 2
    seq_req = get_pv('PXD:B:PSC-State:req:S')
    seq_cur = get_pv('PXD:B:PSC-State:cur:S')

    sucess = True
    assert seq_cur.get() == 1

    logger.info('Set PS state from %s to %s'%(seq_cur.get(), target))

    # skip acmc, offset upload and pedestals upload. Time cost in ploading pedestals can vary for each time so it's hard to compare.
    get_pv('PXD:%s:skip_acmc:S'%dhe).put(1)
    get_pv('PXD:%s:skip_offsets:S'%dhe).put(1)
    get_pv('PXD:%s:skip_pedestals:S'%dhe).put(1)
    # enable DHP links check
    get_pv('PXD:%s:skip_dhp_link_check:S'%dhe).put(0)

    # check the time cost
    t0 = time.time()
    seq_req.put(target)

    def is_ready(target):
        if seq_cur.get() == target:
            return True
        return False

    try:
        wait(lambda: is_ready(target), timeout_seconds = 600)
    except TimeoutExpired:
        logger.warning('Turning on takes too long! (>600s)')
        sucess = False
        assert sucess
    else:
        t1 = time.time()
        if target == 2:
            if 53<t1-t0<55: 
                logger.info("STANDBY reached, time consuming %f s, should be ~54s."%(t1-t0))
            else:
                logger.warning("STANDBY reached, time consuming %f s, should be ~54s."%(t1-t0))
        else:
            logger.info("PS state %s reached, time consuming %f s"%(target, t1-t0))

    time.sleep(2)

    ## check DHP link status
    # dhi long rst
    get_pv('PXD:%s:dhp_rst_long:S:set'%dhi).put(1)
    time.sleep(2)

    ## check dhp links
    if [get_pv('PXD:%s:dhp_alive%s:S:cur'%(dhe,i)).get() for i in [1,2,3,4]] != [1]*4:
        logger.warning('DHP links are not all alive!')
        sucess = False
    else:
        logger.info('DHP links are all alive.')
    if [get_pv('PXD:%s:dhp%s_channel_up:S:cur'%(dhe,i)).get() for i in [1,2,3,4]] != [1]*4:
        logger.warning('DHP links are not all up!')
        sucess = False
    else:
        logger.info('DHP links are all up.')

    time.sleep(1)

    ## check DCD IDCode
    for i in [1,2,3,4]:
        get_pv('PXD:%s:R%s:idcode_dispatch:ID:trg'%(dhe,i)).put(1)
        time.sleep(0.5)
    if [get_pv('PXD:%s:R%s:idcode:ID:cur'%(dhe,i)).get() for i in [1,2,3,4]] != [-2023406815]*4:
        logger.warning('DCD IDCodes are not all correct!')
        sucess = False
    else:
        logger.info('DCD IDCodes are all correct.')

    ## check Switcher IDCode
    for i in [1,2,3,4,5,6]:
        get_pv('PXD:%s:S%s:idcode:trg'%(dhe,i)).put(1)
        time.sleep(0.5)
    if [get_pv('PXD:%s:S%s:idcode:ID:cur'%(dhe,i)).get() for i in [1,2,3,4,5,6]] != [591751049]*6:
        logger.warning('SW IDCodes are not all correct!')
        sucess = False
    else:
        logger.info('SW IDCodes are all correct.')

    time.sleep(1)

    ## check trigger
    # issue dhc reset
    get_pv('PXD:%s:dhc_rst:S:set'%dhc).put(1)
    time.sleep(2)

    # send 20 triggers
    total_trg = 250
    get_pv('PXD:%s:dhc_trigger_rate:VALUE:set'%dhc).put(100)
    get_pv('PXD:%s:dhc_number_triggers:VALUE:set'%dhc).put(total_trg)
    time.sleep(0.5)
    get_pv('PXD:%s:dhc_ipbtrigger_en:S:set'%dhc).put(1)
    time.sleep(np.ceil(total_trg/100) + 1)
    get_pv('PXD:%s:dhc_ipbtrigger_en:S:set'%dhc).put(0)
    time.sleep(1)

    trg_count = [
        get_pv('PXD:%s:dhc_trg_cnt:VALUE:cur'%dhc).get(), # dhc_trg_count 
        get_pv('PXD:%s:dhc_rec_trg_cnt:CNT:cur'%dhc).get(), # rec_trg
        get_pv('PXD:%s:dhc_ACC_TRG_CNT:CNT:cur'%dhc).get(), # acc_trg
        get_pv('PXD:%s:trg:CNT:cur'%dhi).get(), # dhi_trg_count
        get_pv('PXD:%s:trg:CNT:cur'%dhe).get() # dhe_trg_count
    ]

    if all(x==trg_count[0] for x in trg_count):
        logger.info('DHI, DHE receive correct number of triggers.')
    else:
        logger.warning('DHI, DHE do not receive correct number of triggers!')
        sucess = False

    time.sleep(1)

    def create_pvdump(filename):
        try:
            system_cfg = config_utils.Configuration(commitid="current", useprogresspv=False,
                                                    dhe=[dhe], dhc=[dhc], dhi=[dhi])
            system_cfg.read()
            system_cfg.save(filename)
        except KeyError:
            logger.warning('Some keys not found, are you sure the DHEs match the ones in the current commit?'
                               'PVDump will not be created!')

    if not sucess:
        logger.warning( 'Stop checking because not some checks failed!')
    else:
        logger.info('All checks are successful, next will be PVdump and then module will be switched off.')
        ## check PV dump
        ref_name = dhe+'PVdump_ref.npy'
        if not isfile(ref_name):
            logger.warning('No reference of PV dump found! Create one instead.')
            create_pvdump(ref_name)
        else:
            file_name = dhe+"PVdump_"+time.ctime().replace(" ","_").replace("__","_").replace(":","-")+".npy"
            create_pvdump(file_name)

            # compare pv dumps
            pvs1 = np.load(ref_name, allow_pickle=True).item()
            pvs2 = np.load(file_name, allow_pickle=True).item()
            pvs_diff = [k for k in pvs2 if k in pvs1 and pvs1[k]!=pvs2[k]]
            logger.info('%s items are different in PV dump.'%(len(pvs_diff)))
            for k in pvs_diff:
                print(k,'ref: ',pvs1[k],' current value: ',pvs2[k])

        ## switch off module 
        target = 1

        t0 = time.time()
        seq_req.put(target)

        try:
            wait(lambda: is_ready(target), timeout_seconds = 600)
        except TimeoutExpired:
            logger.warning('Turning off takes too long! (>600s)')
        else:
            t1 = time.time()
            logger.info("PS state %s reached, time consuming %f s"%(target, t1-t0))

