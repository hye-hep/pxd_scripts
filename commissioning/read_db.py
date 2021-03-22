from VXD import ConfigDB
import epics_utils

# Load commit from DB

#dcd_pvs=['dacifbpbias:VALUE:set', 'dacipsource:VALUE:set', 'dacipsource2:VALUE:set', 'dacipsource_middle:VALUE:set']
#dhp_pvs = ['idac_cml_tx_bias:VALUE:set', 'idac_cml_tx_biasd:VALUE:set', 'iref_trimming:VALUE:set']
ps_pvs=['clear-on-stage2:VOLT:cur','clear-off:VOLT:cur']

modules = ['1011','1021','1031','1041','1051','1061','1071','1081', '2041','2051', '1012','1022','1032','1042','1052','1062','1072','1082', '2042','2052']
#modules = ['1011']

db = ConfigDB.ConfigDB()
commitid = epics_utils.get_pv("PXD:B:config-commitid").get()
try:
    db.loadCommitData(commitid)
    print('load commit#',commitid)
except:
    print('can not load commit data.')
    raise IOError


#read the pv value from configDB, e.g.
pv_list = []
for module in modules:
    if 'ps_pvs' in globals():
        for pv in ps_pvs:
            print('P%s:%s'%(module,pv), db.getPV('P%s:%s'%(module,pv)))

    if 'dcd_pvs' in globals():
        for asic in range(1,5):
            for pv in dcd_pvs:
                print('H%s:R%s:%s'%(module,asic, pv), db.getPV('H%s:R%s:%s'%(module,asic, pv)))
    if 'dhp_pvs' in globals():
        for asic in range(1,5):
            for pv in dhp_pvs:
                print('H%s:D%s:%s'%(module,asic, pv),epics_utils.get_pv('H%s:D%s:%s'%(module,asic, pv)).get(),db.getPV('H%s:D%s:%s'%(module,asic, pv)))
#                pv_list.append([epics_utils.pvname('H%s:D%s:%s'%(module,asic, pv)), db.getPV('H%s:D%s:%s'%(module,asic, pv))])

#epics_utils.pvlist_put(pvlist)
#modulesPXD = ["PXD:H"+str(module) for module in modules]
#epics_utils.write_to_JTAG_parallel(modulesPXD, 0, "dhpglobal")
