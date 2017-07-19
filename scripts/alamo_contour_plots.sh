#!/bin/sh

python ArcticHeat_ALAMOplotting_movie.py images/9058_002 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 2 -c --cd 1 1
python ArcticHeat_ALAMOplotting_movie.py images/9058_003 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 3 -c --cd 1 1
python ArcticHeat_ALAMOplotting_movie.py images/9058_004 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 4 -c --cd -2 1
python ArcticHeat_ALAMOplotting_movie.py images/9058_005 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 5 -c --cd -2 1


for i in {6..9}
do
	python ArcticHeat_ALAMOplotting_movie.py images/9058_00${i} --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 ${i} -c --cd -2 -4
done

for i in {10..73}
do
	python ArcticHeat_ALAMOplotting_movie.py images/9058_0${i} --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 ${i} -c --cd -2 -4
done

python ArcticHeat_ALAMOplotting_movie.py images/9058_074 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 74 -c --cd -1 -3
python ArcticHeat_ALAMOplotting_movie.py images/9058_075 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 75 -c --cd 0 -2
python ArcticHeat_ALAMOplotting_movie.py images/9058_076 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 76 -c --cd 0 -1
python ArcticHeat_ALAMOplotting_movie.py images/9058_077 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 77 -c --cd 0 0
