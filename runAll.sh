#!/bin/bash

MAX_JOBS=4

echo "Starting:"
for n in 1 2 3 4 5 6; do
	while [[ $MAX_JOBS -le $(jobs -l | wc -l) ]]; do sleep 0.1; done
	(
		echo "  start $n →"
		./tankPlot.py -n $n -sq &>/dev/null
		./tankPlot.py -n $n -rq &>/dev/null
		echo "    止 end $n"
	) &
done
while [[ $(jobs -l | wc -l) -gt 1 ]]; do sleep 0.1; done
echo "DONE!"
