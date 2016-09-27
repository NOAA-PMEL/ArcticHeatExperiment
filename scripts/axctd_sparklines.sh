#!/bin/sh

datapath='/Users/bell/in_and_outbox/2016/wood/ArcticHeat/sep/'


#AXCTD's

#9/10
python ArcticHeatCTDsparklines.py ${datapath}AH20160910_data/AH20160910_ax/16037895_2016_09_10_20_50_44.dta -axctd --maxdepth 985 --paramspan -5 10 --save_excel
python ArcticHeatCTDsparklines.py ${datapath}AH20160910_data/AH20160910_ax/16037899_2016_09_10_23_38_03.dta -axctd --maxdepth 88 --paramspan -5 10 --save_excel

#9/11
python ArcticHeatCTDsparklines.py ${datapath}AH20160911_data/AH20160911_ax/16037897_2016_09_11_19_36_03.dta -axctd --maxdepth 39 --paramspan -5 10 --save_excel

#9/15
python ArcticHeatCTDsparklines.py ${datapath}AH20160915_data/AH20160915_ax/16037896_2016_09_15_21_31_25.dta -axctd --maxdepth 43 --paramspan -5 10 --save_excel
python ArcticHeatCTDsparklines.py ${datapath}AH20160915_data/AH20160915_ax/16037898_2016_09_15_22_33_45.dta -axctd --maxdepth 42 --paramspan -5 10 --save_excel
