#!/bin/bash

MAX_JOBS=8

#for n in $(seq 1 4); do
for n in 4; do
	while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
	echo "  start $n →"
	( ./parsePy.py -rpq -n $n  1>/dev/null ) &
	while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
	( ./parsePy.py -rq -n $n 1>/dev/null ) &
	while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
	( ./parsePy.py -spq -n $n  1>/dev/null ) &
	while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
	( ./parsePy.py -sq -n $n  1>/dev/null ) &
done

if [[ 1 -eq 2 ]]; then
	NC=32
	for n in $(seq 1 4); do
		while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
		echo "  start $n →"
		( ./parsePy.py -rpq -n $n -c "$NC"  1>/dev/null ) &
		while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
		( ./parsePy.py -rq -n $n -c "$NC" 1>/dev/null ) &
		while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
		( ./parsePy.py -spq -n $n -c "$NC"  1>/dev/null ) &
		while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
		( ./parsePy.py -sq -n $n -c "$NC"  1>/dev/null ) &
	done
fi

while [[ $(jobs -lr | wc -l) -gt 0 ]]; do sleep 0.1; done
SELECT_STRING="S02bB_C+00dB"
cp -v "figures-measured/"*"${SELECT_STRING}"* ../tex/figures-measured/
SELECT_STRING="S03bB_C+00dB"
cp -v "figures-measured-32/"*"${SELECT_STRING}"* ../tex/figures-measured-32/

