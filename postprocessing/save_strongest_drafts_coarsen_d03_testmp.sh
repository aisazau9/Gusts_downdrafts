#!/bin/bash

#PBS -N save_strong
#PBS -P up6
#PBS -q hugemem
#PBS -l walltime=04:00:00
#PBS -l ncpus=12
#PBS -l mem=500gb
#PBS -l jobfs=2gb
#PBS -l wd
#PBS -l storage=gdata/sx70+gdata/up6+gdata/hh5+gdata/rt52+gdata/zz93+gdata/hh5+scratch/up6+gdata/w28+gdata/xp65
#PBS -M a.isaza@unsw.edu.au
#PBS -m e

module use /g/data3/xp65/public/modules
module load conda/analysis3

cd /g/data/up6/ai2733/Gusts_downdrafts/postprocessing

python save_strongest_drafts_coarsen_testmp.py "d03"
