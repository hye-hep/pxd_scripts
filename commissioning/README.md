Some scripts used in PXD commissioning or analyses of observations during PXD operation

>>> compare_commits.py

compare the difference between two commits in configDB.

>>> dhh_fw_version_from_arch.py

Read the DHH firmware information from archiver and interpret it.

>>> ps-test.py

Enable the PS and apply some predefined voltages (masking all OVP channels may be necessary). It's used in PS standalone or cable qualification.

>>> read_db.py

To read the PV values in configDB.


>>> flip_clear_gate/

These scripts are used when studying the flip clear/gate since exp10, major part of the anayses is to plot pedestals or occupancy. 


>>> hitmap/

run_hitmap.py # Creat hitmaps from local run data, usually the first .dat file is used. 

dead_gates_stats.ipynb # A script to count dead gates, this detection method is included in the run_ana scirpt.


>>> hv_curr/

Some .plt to show hv current development. 

HV_IV_curve_plot.ipynb # is used to compare the HV I-V curves.

HV_curr_lmfit.ipynb # an example of exponential fit of the discharging-like effect of HV current during beam off period.


>>> noisy_drains_gates/

Some scripts concerning the hot drains or gates, mainly the noisy gate on 1022 and drain lines of 2052.


>>> pedestals/  # some scripts for pedestals plotting.

Noise_pede_IBBelle_cold.ipynb # compare noise at differet temperature.

ped_diff.ipynb # Compare two sets of pedestals

plot_module_mask.ipynb # Plot the module mask

plot_pede_noise_ana.ipynb # read the pedestal calibration results and do plotting

raw_pedestals.ipynb # plot the raw pedestals and compare. It reads the raw data file of loaldaq.  


>>> sr/ 

SR_clusterCharge_exp0012run2153.ipynb # a script used to analyze exp12 run 2153. The hitmaps within the different cluster charge regions are plotted, it was observed that the pattern in +x bwd has larger cluser charge and independent with injection

occ_photonRate_vs_beamPara_arch.ipynb # a script to plot PXD occupancy or photon rate v.s. beam parameters. Data is read from archiver.

photoRate_vs_beamCurr_exp12.ipynb # plot photon rate v.s. beam currents.
