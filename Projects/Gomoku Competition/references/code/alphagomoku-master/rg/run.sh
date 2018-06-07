#! /bin/bash

for i in {1..4}; do
	cd "training$i" || exit
	echo "Spawning $i in $(pwd)"
	ocaml ../gomoku.ml &
	cd .. || exit
done

wait

