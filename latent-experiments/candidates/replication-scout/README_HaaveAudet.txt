# README for:
# Sampling is related to increased survival: A field experiment in black-capped chickadees
# Haave-Audet, E*., Martin, J. G. A., Wijmenga, J. J., & Mathot, K. J.
# *Corresponding author: haaveaud@ualberta.ca

# Summary:
# In this study, we evaluated the model predictions of adaptive sampling behaviour from Mathot and Dall [Am Nat, 
# 2013] in a free-living population of 132 individually marked black-capped chickadees. We tested whether there 
# was a relationship between ambient temperature (as a proxy for energy expenditure) and food availability (as a 
# proxy for starvation risk) on the probability of sampling previously experienced unrewarding feeders.

# Data collection was conducted by EHA, KJM, and JJW. Code for analyses was written by EHA, KJM, and JGAM.

# Files needed to replicate analyses:
# R script: sampling-survival-Haave-Audet-et-al-20230808.R
# Data file: data_HaaveAudet-et-al_20230529.txt

# Variable descriptions:   

# TransponderHexcode = Unique 10 digit alphanumeric individual ID
# Feeder = unique feeder that was visited during the observation
# Round = experimental replicate, 1 through 4
# treatment.sampling = treatment in place during the sampling period (full-empty, empty-full, empty-empty) 
# Sampled = 1 = yes 0 = no
# Adjacent = status of the adjacent feeder during the sampling period (full, empty)
# Start_DateTime = date-time at which the sampling treatment was initiated (MST)
# Stop_DateTime = date-time at which the sampling treatment was completed (MST)
# new.stop = adjusted sampling treatment stop date to calculate sampling during the first four days of treatment only (see Methods)
# AvgTemp = average daily temperature during the four day sampling period
# DNASex = sex assigned through molecular technique
# baseline_date = date on which baseline foraging data was collected (1 day before start of sampling period)
# baseline_temp = daily average temperature on day of baseline foraging 
# Survived = apparent annual survival 1 = yes 0 = no
# NSites = number of feeder sites visited by a chickadee during the sampling study
# ScTar = within-sex centered and scaled individual average tarsus length (mm)
# Non_Sampled = 1 = visited the adjecent feeder during the sampling period, 0 = did not visit the adjacent feeder during the sampling period

# Analyses were conducted using the following software:
# R version 4.1.3 (2022-03-10)
# Platform: x86_64-w64-mingw32/x64 (64-bit)
# Running under: Windows 10 x64 (build 22621)

# Packages and versions used in analyses
# (lme4) v. 1.1.27.1
# (MCMCglmm) v. 2.32
# (ggpubr) v. 0.4.0
# (broom.mixed) v. 0.2.7
# (tidyverse) v. 1.3.1
