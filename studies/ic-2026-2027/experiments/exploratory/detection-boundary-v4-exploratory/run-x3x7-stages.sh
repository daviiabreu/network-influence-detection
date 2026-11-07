#!/usr/bin/env bash
set -euo pipefail
out=$1
processes=$2
base=$3
total=$4
only=$5
shift 5
python=.venv/bin/python
selection=${STAGES:-x5,x7,x3,x4a,x4b,x6a,x6b}
for stage in ${selection//,/ }; do
	case "$stage" in
	x5 | x7 | x3 | x4a | x4b | x6a | x6b) ;;
	*) exit 2 ;;
	esac
done
pids=()
for k in $(seq 0 $((processes - 1))); do
	(
		split=()
		if [ -n "$total" ]; then
			split=(--shard $((base + k)) --shards "$total")
		fi
		filter=()
		if [ -n "$only" ]; then
			filter=(--only "$only")
		fi
		for stage in x5 x7 x3 x4a x4b x6a x6b; do
			case ",$selection," in
			*",$stage,"*) ;;
			*) continue ;;
			esac
			name=$stage
			case "$stage" in
			x4*) name=x4 ;;
			x6*) name=x6 ;;
			esac
			case " $* " in
			*" $name "*) ;;
			*) continue ;;
			esac
			code=0
			$python -m "ic_study.simulation.v4_exploratory_$name" run --out "$out" --kind "$stage" \
				${split[@]+"${split[@]}"} ${filter[@]+"${filter[@]}"} || code=$?
			echo "$name $stage ${split[*]-} exit=$code" >>"$out/logs/worker-$k.status"
			[ "$code" -eq 0 ] || exit "$code"
		done
	) >>"$out/logs/worker-$k.log" 2>&1 &
	pids+=("$!")
done
failure=0
for pid in "${pids[@]}"; do
	code=0
	wait "$pid" || code=$?
	if [ "$failure" -eq 0 ] && [ "$code" -ne 0 ]; then
		failure=$code
	fi
done
exit "$failure"
