# Description:
These scripts do laugau fit to the track cluster charge distribution from DQM ROOT files. Two datra source can be used for this analysis

1. rundependency DQM plots: https://dqm.belle2.org/rundependency/pxd/display.php
    One can find the root files in
        https://dqm.belle2.org/rundependency/pxd/data/
    e.g. e0014/pxd_dqm_e0014r000054.root
    ## No updates after exp14?

2. DQM canvas plots
    One can find the root files in
        https://dqm.belle2.org/past_runs/
    e.g. expreco_exp16_canvas/dqm_e0016r000668_canvas.root
    ## Laugau fit results has been introduced in track cluster charge plots since exp16? One can extract fit results directly, no need to run these scriopts.

# Procedures to run the scripts:

1. Download the root files from either of the data sources, take DQM canvas plots in exp16  as example
>>> wget --user <DESY username> --password <password> --recursive --no-parent https://dqm.belle2.org/past_runs/expreco_exp16_canvas/

2. Fit multiple runs in one go, save fit reuslts to a npy file for each run.
Add some resonable information (data path, expnr, use rundependency DQM plots, thread_count...) in the first several lines of run_multi_trackcharge.py. This script use mult-thread to call trackcharge_langau*.py.
>>> python3 run_multi_trackcharge.py

One can also use trackcharge_langau.py or trackcharge_langau_DQMcanvas.py to run a single ROOT file.

3. Trk_cluster_charge.ipynb has some examples for plotting.

