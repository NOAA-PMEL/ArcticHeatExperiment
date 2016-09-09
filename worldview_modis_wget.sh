#!/bin/bash

progdir="/Volumes/WDC_internal/Users/bell/Programs/Python/FOCI_Analysis/ArcticHeatExperiment/"

for i in `seq 174 200`;
do
        python ${progdir}worldview_modis_wget.py ${i} Aqua jpeg large
done  

img_dir="/Volumes/WDC_internal/Users/bell/Programs/Python/FOCI_Analysis/ArcticHeatExperiment/*.jpeg"
for files in $img_dir
do
	convert ${files} -fill white -undercolor '#00000080' -pointsize 50 -gravity NorthEast -annotate +10+10 %t ${files}.jpg
done
