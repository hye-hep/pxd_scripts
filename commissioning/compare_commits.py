#!/usr/bin/env python
"""
compare two commits in configDB
"""

from VXD import ConfigDB
from VXD.ConfigDB import dict_compare
from epics_utils import get_pv

#commit1 = get_pv("PXD:B:config-commitid").get()
commit1 = 574
commit2 = 575

db = ConfigDB.ConfigDB()

# load the first commit and get all PVs
db.loadCommitData(commit1)
# convert the first dict to a readable object
pvs1 = {}
for key, node in db.getallPVs().items():
    pvs1[key] = node.value
print('load',len(pvs1.keys()),'PVs from commit', commit1)

# load the commit of the second commit and get all PVs
db.loadCommitData(commit2)
# compare the second dict to a readable object
pvs2 = {}
for key, node in db.getallPVs().items():
    pvs2[key] = node.value
print('load',len(pvs2.keys()),'PVs from commit', commit2)


# use the helper function to get the modified dict values
added, removed, modified, same = dict_compare(pvs1, pvs2)


print(len(added),'Added:')
for key in added:
    print(key)


print(len(removed),'Removed:')
for key in removed:
    print(key)

print(len(modified),'Modified: PV (val_commit%s,val_commit%s)'%(commit1,commit2))
for key in sorted(modified.keys()):
    if 'offset_data' in key:
    #    print key
        continue
    print(key,modified[key])
