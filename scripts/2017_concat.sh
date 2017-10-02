#!/bin/sh

datapath='/Volumes/WDC_internal/Users/bell/ecoraid/2017/Additional_FieldData/ArcticHeat/'

python ArcticHeatAirCraft2JSON.py -r -csv ${datapath}/AH20170916/20170916_190751_IWG.dat > 2017_IWG.all

python ArcticHeatAirCraft2JSON.py -r -csv ${datapath}/AH20170919/20170919L1/20170919L1_raw/AIMMS/20170919_IWG_combined.dat >> 2017_IWG.all

python ArcticHeatAirCraft2JSON.py -r -csv ${datapath}/AH20170920/20170920_combined_IWG.dat >> 2017_IWG.all

python ArcticHeatAirCraft2JSON.py -r -csv ${datapath}/AH20170921/AH20170921_raw/20170921_180651_IWG.dat >> 2017_IWG.all