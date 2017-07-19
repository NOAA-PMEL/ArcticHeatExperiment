#!/bin/sh

: '
for i in {2..5}
do
	python ArcticHeat_ALAMOplotting_movie.py images/9058_00${i} --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 ${i} -c --cd 1 1 1 1 1 1 1 1 1
done


python ArcticHeat_ALAMOplotting_movie.py images/9058_006 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 6 -c --cd -4 1 1 1 1 1 1 1 1
python ArcticHeat_ALAMOplotting_movie.py images/9058_007 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 7 -c --cd -4 1 1 1 1 1 1 1 -5
python ArcticHeat_ALAMOplotting_movie.py images/9058_008 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 8 -c --cd -4 1 1 1 1 1 1 -6 -5
python ArcticHeat_ALAMOplotting_movie.py images/9058_009 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 9 -c --cd -4 1 1 1 1 1 -7 -6 -5
python ArcticHeat_ALAMOplotting_movie.py images/9058_010 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 10 -c --cd -4 1 1 1 1 -8 -7 -6 -5
python ArcticHeat_ALAMOplotting_movie.py images/9058_011 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 11 -c --cd -4 1 1 1 -9 -8 -7 -6 -5
python ArcticHeat_ALAMOplotting_movie.py images/9058_012 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 12 -c --cd -4 1 1 -10 -9 -8 -7 -6 -5
python ArcticHeat_ALAMOplotting_movie.py images/9058_013 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 13 -c --cd -4 1 -11 -10 -9 -8 -7 -6 -5


for i in {14..73}
do
	python ArcticHeat_ALAMOplotting_movie.py images/9058_0${i} --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 ${i} -c --cd -4 -12 -11 -10 -9 -8 -7 -6 -5
done
'
for i in {74..77}
do
	python ArcticHeat_ALAMOplotting_movie.py images/9058_0${i} --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 ${i} -c --cd $((i-74-4)) $((i-74-12)) $((i-74-11)) $((i-74-10)) $((i-74-9)) $((i-74-8)) $((i-74-7)) $((i-74-6)) $((i-74-5))
done


python ArcticHeat_ALAMOplotting_movie.py images/9058_083 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 83 -c --cd 0 -8 -7 -6 -5 -4 -3 -2 -1
python ArcticHeat_ALAMOplotting_movie.py images/9058_084 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 84 -c --cd 0 -7 -6 -5 -4 -3 -2 -1 0
python ArcticHeat_ALAMOplotting_movie.py images/9058_085 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 85 -c --cd 0 -6 -5 -4 -3 -2 -1 0 0
python ArcticHeat_ALAMOplotting_movie.py images/9058_086 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 86 -c --cd 0 -5 -4 -3 -2 -1 0 0 0
python ArcticHeat_ALAMOplotting_movie.py images/9058_087 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 87 -c --cd 0 -4 -3 -2 -1 0 0 0 0
python ArcticHeat_ALAMOplotting_movie.py images/9058_088 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 88 -c --cd 0 -3 -2 -1 0 0 0 0 0
python ArcticHeat_ALAMOplotting_movie.py images/9058_089 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 89 -c --cd 0 -2 -1 0 0 0 0 0 0
python ArcticHeat_ALAMOplotting_movie.py images/9058_090 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 90 -c --cd 0 -1 0 0 0 0 0 0 0
python ArcticHeat_ALAMOplotting_movie.py images/9058_091 --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 91 -c --cd 0 0 0 0 0 0 0 0 0

: '
for i in {100..147}
do
	python ArcticHeat_ALAMOplotting_movie.py images/9058_${i} --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 ${i} -c --cd $((i-73)) 1
done

for i in {148..220}
do
	python ArcticHeat_ALAMOplotting_movie.py images/9058_${i} --maxdepth 55 -alamo 9058 --paramspan -2 7 -alamocycle 1 ${i} -c --cd 0 $((i-146))
done
'