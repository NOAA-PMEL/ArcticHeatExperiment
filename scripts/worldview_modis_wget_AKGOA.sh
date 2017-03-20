#!/bin/bash

progdir="/Volumes/WDC_internal/Users/bell/Programs/Python/FOCI_Analysis/ArcticHeatExperiment/"

for i in `seq 1 90`;
do
        python ${progdir}worldview_modis_wget.py ${i} Aqua jpeg large --bbox -180 39.5 -121.25 72.5
done  

img_dir="/Volumes/WDC_internal/Users/bell/Programs/Python/FOCI_Analysis/ArcticHeatExperiment/*.jpeg"
for files in $img_dir
do
	convert ${files} -fill white -undercolor '#00000080' -pointsize 50 -gravity NorthEast -annotate +10+10 %t ${files}.jpg
done
