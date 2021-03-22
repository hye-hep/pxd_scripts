#!/usr/bin/env python3

"""
Simple example how to talk to the RunDB in python

This works in any python installation with python version >=3.5 and the requests
package installed.

Run with: `python rundb_list_expertflags.py`

Returns a list of the experiment number, run number and recorded luminosity for all runs with given expert quality flag.
"""

# Specifications (must be given)
# ------------------------------------------------------
# for which subdetector
subdetector = 'pxd'
# for which run type
run_type = 'physics'
# for which quality flag
quality_flag = 'GOOD'
#quality_flag = 'RECOVERABLE'
# Experiment range
min_exp = 16
max_exp = 16
# Run range (for all runs: 0, 1e4)
min_run = 0
max_run = 1e4
# ------------------------------------------------------

import requests
import getpass

class RunDB:
    """
    Simple api class to just get run information from the RunDB
    """

    URL = "https://rundb.belle2.org"

    def __init__(self, apikey=None, username=None):
        """Create an object and setup authentication"""
        self._session = requests.Session()
        if apikey is None:
            ## If no specific username use the local system username
            #if username is None:
            #    username = getpass.getuser()
            username = getpass.getpass("DESY username:")
            # If we don't have an api key use desy username/password
            self._session.auth = (username, getpass.getpass("DESY password (%s): "%username))
        else:
            # Otherwise use the api key
            self._session.headers.update({'Authorization': f'Bearer {apikey}'})
        # And request json output ...
        self._session.headers.update({'Content-Type': 'application/json'})

    def _pagination(self, request):
        """Deal with api pagination of an initial request to the api.

        It will return all the objects from all pages lazily requesting new pages
        as objects are consumed. Will work for all list requests to the server

        Parameters:
            request (requests.Request): A get request to paginate through the results
        """
        while True:
            # check the return value and raise exception on error
            request.raise_for_status()
            # and otherwise get the json
            result = request.json()
            # and return the objects one by one by yielding objects from the list
            # of results
            yield from result['results']
            # check if there's a next page, if not done
            if result['next'] is None:
                break
            # otherwise continue with the next page
            # yees, global variable ...
            request = self._session.get(result['next'])

    def get_run_info(self, **search_params):
        """Return the run information from the run registry.

        All arguments are forwarded to the run registry `/run/` method
        documented at https://rundb.belle2.org/rest/v1/swagger/. Please check
        there for up to date documentation, at the time of this writing the
        supported arguments are

          * min_experiment (int)
          * max_experiment (int)
          * min_run (int)
          * max_run (int)
          * min_date (iso8601 date string, e.g. 2020-05-06)
          * max_date (iso8601 date string, e.g. 2020-05-06)
          * run_type (str, e.g. physics, cosmic)
          * all_detectors_running (bool)
          * limit (int, number of results to return per page (?))
          * offset (int, initial index from which to return the results (?))
          * expand (bool): If true return full run objects, not just a summary
            links to the run objects

        If expand=False you can request the full objects for each run by calling
        `get_details` with the returned run summary object as argument.
        `expand=False` is much faster if no further details are needed but
        getting the details in a separate step for many many runs will be slow
        so depending on how many runs are selected one or the other may be
        faster.
        """
        req = self._session.get(f'{self.URL}/rest/v1/runs/', params=search_params)
        return self._pagination(req)

    def get_details(self, run_summary):
        """
        Return details for a run summary object returned from `get_run_info`
        if `expand` was not set to True
        """
        # Get the url object
        req = self._session.get(run_summary['url'])
        # Raise an exception in case of any error
        req.raise_for_status()
        # And return the json object
        return req.json()


if __name__ == "__main__":
    rundb = RunDB()
    # get the list of runs, all parameters are forwarded as get request
    # parameters. expand=True makes the server return full run info with all
    # sub objects, not just the short one and is not optional. For possible arguments and properties
    # https://rundb.belle2.org/rest/v1/swagger/

    print('Subdetector: {}'.format(subdetector))

    run_dict = {}
    for run in rundb.get_run_info(min_experiment=min_exp, max_experiment=max_exp, min_run=min_run,
                                  max_run=max_run, run_type=run_type, expand=True):

        if not all(run['detectors'][f'status_{det}'] == 'RUNNING' for det in ['pxd', 'svd', 'cdc', 'ecl']):
            continue
        if run['detectors']['magnet_solenoid_field'] < 1e3:
            continue
        if not run['quality_expert'][subdetector] == quality_flag:
            continue
        # some entries for luminosity are missing (NoneType)
        if run['statistics']['lumi_recorded']: lumi_rec = '{0:8.1f}'.format(run['statistics']['lumi_recorded'])
        else: lumi_rec = '--None--'

        #print(run['experiment'], run['run'], lumi_rec, run['quality_expert'][subdetector])
        #print(run['experiment'], run['run'], run['time_start'], run['time_stop'], lumi_rec, run['quality_expert'][subdetector])
        print(run['experiment'], run['run'], run['time_start'], run['time_stop'])

        run_dict[run['run']] = [run['time_start'], run['time_stop']]


    import numpy as np
    if max_exp != min_exp:
        np.save('exp%s-%s_run_time_info'%(min_exp,max_exp),run_dict)
    else:
        np.save('exp%s_run_time_info'%min_exp,run_dict)
