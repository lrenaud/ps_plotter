#!/bin/bash

MAX_JOBS=4

for n in 2 12; do
	while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
	(
		echo "  start $n →"
		./tankPlot.py -n $n --subplot -sq 1>/dev/null
		./tankPlot.py -n $n --subplot -rq 1>/dev/null
		echo "    止 end $n"
	) &
	while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
	(
		echo "  start $n →"
		./tankPlot.py -n $n -sq 1>/dev/null
		./tankPlot.py -n $n -rq 1>/dev/null
		echo "    止 end $n"
	) &
done

#bash ./runParse.sh &

while [[ $(jobs -lr | wc -l) -gt 0 ]]; do sleep 0.1; done
#mkdir -p figures-png
#rm figures-png/*.png &>/dev/null
mv figures/*.png figures-png/
echo "DONE!"
