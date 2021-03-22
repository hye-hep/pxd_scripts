#!/usr/bin/env python

import epics_archiver
import datetime
import time
import log_utils
from argparse import ArgumentParser

'''
Author: Hua Ye

Read the DHH firmware PV from archiver and convert to an understandable format

Usage:

>>> dhh_fw_archiver.py --dhh H1021 --date "2019,03,27,11,0,0"
2019-03-27 11:00:00 - 2019-03-27 11:00:05
H1021 fw : 20190321_0653

>>> dhh_fw_archiver.py --dhh H1021 H38m H60 --date "2019,04,10,11,0,0" --to_date "2019,04,10,12,0,0"
2019-04-10 11:00:00 - 2019-04-10 12:00:00
H1021 fw : 20190321_0653
H38m fw : 20190129_1334
H38m fw : 20190129_1334
H38m fw : 20190129_1334
H60 fw : 20190408_1743
H60 fw : 20190408_1743
H60 fw : 20190315_1511

>>> dhh_fw_archiver.py
2019-05-09 10:48:34.034880 - 2019-05-09 10:48:39.034880
H30 fw : 20190315_1511
H40 fw : 20190315_1511
H50 fw : 20190315_1511
H60 fw : 20190315_1511
H38m fw : 20190405_1345
H48m fw : 20190405_1345
H58m fw : 20190405_1345
H68m fw : 20190405_1345
H1012 fw : 20190321_0653
H1082 fw : 20190321_0653
H1022 fw : 20190321_0653
H2042 fw : 20190321_0653
H1032 fw : 20190321_0653
H1062 fw : 20190321_0653
H1072 fw : 20190321_0653
H2052 fw : 20190321_0653
H1042 fw : 20190321_0653
H1052 fw : 20190321_0653
H1071 fw : 20190321_0653
H1061 fw : 20190321_0653
H2051 fw : 20190321_0653
H1041 fw : 20190321_0653
H1051 fw : 20190321_0653
H1011 fw : 20190321_0653
H1081 fw : 20190321_0653
H1031 fw : 20190321_0653
H2041 fw : 20190321_0653
H1021 fw : 20190321_0653

'''

if __name__ == "__main__":
    parser = ArgumentParser(description='read_dhh_fw_info_from_archiver')
    parser.add_argument('--dhh', dest='dhh', nargs='+', default=None, help='e.g. H1011 H38m H50, default: all')
    parser.add_argument('--date', dest='from_date', default=None, help='e.g. "2019,03,27,11,0,0", default: 10s ago')
    parser.add_argument('--to_date', dest='to_date', default=None, help='e.g. "2019,03,27,11,0,0", optional')
    args = parser.parse_args()

    if args.dhh is None:
        dhh_list = ['H30','H40','H50','H60',
                'H38m','H48m','H58m','H68m',
                'H1012','H1082','H1022','H2042','H1032',
                'H1062','H1072','H2052','H1042','H1052',
                'H1071','H1061','H2051','H1041','H1051',
                'H1011','H1081','H1031','H2041','H1021']
    else:
        dhh_list=args.dhh

    if args.from_date is None:
        start_datetime = datetime.datetime.now() - datetime.timedelta(seconds = 10)
    else:
        start_datetime = datetime.datetime.strptime(args.from_date, "%Y,%m,%d,%H,%M,%S")

    if args.to_date is None:
        stop_datetime = start_datetime+datetime.timedelta(seconds = 5)
    else:
        stop_datetime = datetime.datetime.strptime(args.to_date, "%Y,%m,%d,%H,%M,%S")

    logger = log_utils.get_pxd_main_logger(application_name="read_dhh_fw_info_from_archiver", no_remote=True)

    belle2_archiver = epics_archiver.epics_archiver("172.22.16.120:17668")
    archiver_start = belle2_archiver.date_parser(start_datetime)
    archiver_stop = belle2_archiver.date_parser(stop_datetime)
    archiver = epics_archiver.epics_archiver("172.22.18.80:80")
    time.sleep(3)

    data_dict = {}

    print "%s - %s" % (start_datetime, stop_datetime)
    for dhh in dhh_list:
        try:
            data_dict[dhh] = archiver.getData('PXD:%s:revision:VALUE:cur' % dhh, archiver_start, archiver_stop)
            for a in data_dict[dhh].get("vals"):
                print "%s fw : 20%s%02i%02i_%02i%02i" % (dhh, (a>>20) & 0x1F, (a>>16) & 0x0F, (a>>11) & 0x1F, (a>>6) & 0x1F, a & 0x3F)
        except Exception as e:
            logger.warning(repr(e))
