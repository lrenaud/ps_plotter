#!/bin/bash

MAX_JOBS=4

for n in $(seq 1 4); do
	while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
	echo "  start $n →"
	( ./parsePy.py -rq -n $n 1>/dev/null ) &
	while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
	( ./parsePy.py -rpq -n $n  1>/dev/null ) &
	while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
	( ./parsePy.py -sq -n $n  1>/dev/null ) &
	while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
	( ./parsePy.py -spq -n $n  1>/dev/null ) &
done

while [[ $(jobs -lr | wc -l) -gt 0 ]]; do sleep 0.1; done
SELECT_STRING="S02bB_C+00dB"
rsync -aPv "figures-measured/"*"${SELECT_STRING}"* ../tex/figures-measured/

