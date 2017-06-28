#!/bin/sh

datapath='/Volumes/WDC_internal/Users/bell/ecoraid/2016/Additional_FieldData/ArcticHeat/AlamoFloats/netcdf/whoi/9058-netcdf-files/'

python alamo2csv.py -csv -is_whoi ${datapath}R9058_0061.nc > R9058_0061.csv
python alamo2csv.py -csv -is_whoi ${datapath}R9058_0062.nc > R9058_0062.csv
python alamo2csv.py -csv -is_whoi ${datapath}R9058_0063.nc > R9058_0063.csv
python alamo2csv.py -csv -is_whoi ${datapath}R9058_0064.nc > R9058_0064.csv
python alamo2csv.py -csv -is_whoi ${datapath}R9058_0065.nc > R9058_0065.csv
python alamo2csv.py -csv -is_whoi ${datapath}R9058_0066.nc > R9058_0066.csv
python alamo2csv.py -csv -is_whoi ${datapath}R9058_0068.nc > R9058_0068.csv
python alamo2csv.py -csv -is_whoi ${datapath}R9058_0069.nc > R9058_0069.csv
python alamo2csv.py -csv -is_whoi ${datapath}R9058_0070.nc > R9058_0070.csv
python alamo2csv.py -csv -is_whoi ${datapath}R9058_0071.nc > R9058_0071.csv
python alamo2csv.py -csv -is_whoi ${datapath}R9058_0072.nc > R9058_0072.csv
python alamo2csv.py -csv -is_whoi ${datapath}R9058_0073.nc > R9058_0073.csv
