#!/usr/bin/env bash
# Launcher of the v4 exploratory successors X3 to X7 on a Linux exploration host.
#
# Usage: launch-x3x7.sh <commit> <out> <processes> <mode> <analysis>[,<analysis>...]
#
#   <commit>     exact pushed commit to check out
#   <out>        run directory; must lie under
#                ~/.local/state/research-workbench/sealed-v4-exploratory-x3-x7
#   <processes>  concurrent processes, one per logical thread
#   <mode>       probe         timing probe only
#                precondition  probe, then the declared bitwise preconditions
#                run           probe, the preconditions that <out> lacks, then
#                              <processes> resumable workers and the closing
#                              status and, for open analyses, aggregate
#   <analysis>   selected modules; every worker runs its stages in the
#                registered order, with no barrier on the host or across
#                hosts: with fixed shards a barrier only idles threads, and
#                the registered priority applies if capacity runs short.
#                Without shards, the shared queue claims earlier units
#                first. IMPLEMENTATION-FIXES.md gives the reasoning.
#
# Environment:
#   REPO         clone of the canonical remote (default
#                ~/Documents/github/research-workbench-v4x); cloned from REMOTE
#                when missing and REMOTE is a bundle file
#   REMOTE       remote name, URL or git bundle file (default origin)
#   CHECKOUT     worktree of the commit (default "$REPO-<8 hex digits>")
#   SHARD_TOTAL  global shard count of a split across hosts; worker k of this
#   SHARD_BASE   host runs global shard SHARD_BASE + k (SHARD_BASE default 0),
#                and every listed analysis splits by unit index modulo
#                SHARD_TOTAL; unset, the workers share one queue
#   ONLY         unit indices for every listed analysis, such as 0-35
#   STAGES       optional subset of x5,x7,x3,x4a,x4b,x6a,x6b; order stays fixed
#   PROBE_COUNT  panels per probed kind (default 8)
#
# A host without access to GitHub uses a bundle made on a connected clone by
#   git bundle create research-workbench-launch.bundle research/v4-x3x7-launch
# and copied to the host, then REMOTE=/path/research-workbench-launch.bundle.
#
# The launcher fetches REMOTE into REPO and checks the commit out in a worktree
# of its own, so launches at different commits never share a checkout or an
# environment. It syncs the locked environment there, checks that the tracked
# tree is clean, limits BLAS to one thread and starts one detached supervisor
# that holds a lock on <out>. Each precondition job runs in its own process.
# An analysis whose precondition fails does not run here. Nothing written to
# the logs is a statistic: probe timings, unit ids, status codes, counts and
# fit statuses only.
set -euo pipefail
umask 077
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
for tool in git uv flock xargs; do
	command -v "$tool" >/dev/null || {
		echo "launch-x3x7.sh needs $tool on PATH" >&2
		exit 1
	}
done
if [ $# -ne 5 ]; then
	sed -n '2,47p' "$0" >&2
	exit 2
fi
commit=$1
mkdir -p "$2/logs"
out=$(cd "$2" && pwd -P)
processes=$3
mode=$4
analyses=$5
case "$mode" in
probe | precondition | run) ;;
*)
	echo "unknown mode $mode" >&2
	exit 2
	;;
esac
test "$processes" -ge 1
base=${SHARD_BASE:-0}
total=${SHARD_TOTAL:-}
if [ -n "$total" ]; then
	test "$base" -ge 0 && test "$total" -ge $((base + processes)) || {
		echo "shards $base..$((base + processes - 1)) do not fit in SHARD_TOTAL=$total" >&2
		exit 2
	}
elif [ -n "${SHARD_BASE:-}" ]; then
	echo "SHARD_BASE needs SHARD_TOTAL" >&2
	exit 2
fi
repo=${REPO:-$HOME/Documents/github/research-workbench-v4x}
remote=${REMOTE:-origin}
if ! flock -n "$out/logs/supervisor.lock" true; then
	echo "a supervisor still holds $out/logs/supervisor.lock" >&2
	exit 1
fi
if [ -f "$remote" ]; then
	remote=$(cd "$(dirname "$remote")" && pwd -P)/$(basename "$remote")
	if [ ! -e "$repo/.git" ]; then
		git clone --quiet --no-checkout "$remote" "$repo"
	fi
	git -C "$repo" bundle verify --quiet "$remote" >/dev/null
	git -C "$repo" fetch --quiet "$remote" "+refs/heads/*:refs/remotes/bundle/*"
else
	git -C "$repo" fetch --quiet "$remote"
fi
full=$(git -C "$repo" rev-parse --verify --quiet "$commit^{commit}")
checkout=${CHECKOUT:-$repo-${full:0:8}}
if [ ! -e "$checkout/.git" ]; then
	git -C "$repo" worktree add --quiet --detach "$checkout" "$full"
fi
cd "$checkout"
test "$(git rev-parse HEAD)" = "$full"
test -z "$(git status --porcelain --untracked-files=no)"
cd studies/ic-2026-2027
uv sync --locked --quiet
export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
supervisor="$out/logs/$mode-supervisor.sh"
cat >"$supervisor" <<'EOF'
set -u
umask 077
cd "$1" || exit 1
out=$2
processes=$3
mode=$4
analyses=$5
only=$6
count=$7
base=$8
total=$9
python=.venv/bin/python
logs="$out/logs"
module() { echo "ic_study.simulation.v4_exploratory_$1"; }
precondition_job() {
	$python -m "$(module "$1")" precondition --out "$out" --name "$2" --cell "$3" \
		--side "$4" >"$logs/precondition-$2-$4-$3.log" 2>&1
	echo "exit=$?" >"$logs/precondition-$2-$4-$3.status"
}
export -f module precondition_job
export out logs python
IFS=, read -r -a names <<<"$analyses"
echo "started $(date -u +%FT%TZ) mode=$mode analyses=$analyses processes=$processes${total:+ shards=$base..$((base + processes - 1))/$total}"
for name in "${names[@]}"; do
	for k in $(seq 0 $((processes - 1))); do
		$python -m "$(module "$name")" probe --count "$count" \
			>"$logs/probe-$name-$k.json" 2>"$logs/probe-$name-$k.err" &
	done
	wait
done
echo "probed $(date -u +%FT%TZ)"
if [ "$mode" = probe ]; then
	exit 0
fi
jobs="$logs/precondition-jobs.txt"
: >"$jobs"
for name in "${names[@]}"; do
	if $python -m "$(module "$name")" check --out "$out" >"$logs/check-$name.json" 2>&1; then
		echo "$name already has a passing precondition on this host class"
		continue
	fi
	$python -m "$(module "$name")" plan | sed "s/^/$name /" >>"$jobs"
done
xargs -r -P "$processes" -L 1 bash -c 'precondition_job "$@"' _ <"$jobs"
cut -d' ' -f1,2 "$jobs" | sort -u | while read -r name spec; do
	$python -m "$(module "$name")" verify --out "$out" --name "$spec" \
		>"$logs/verify-$spec.log" 2>&1
	echo "exit=$?" >"$logs/verify-$spec.status"
done
echo "preconditions $(date -u +%FT%TZ)"
passing=()
for name in "${names[@]}"; do
	if $python -m "$(module "$name")" check --out "$out" >"$logs/check-$name.json" 2>&1; then
		passing+=("$name")
	else
		echo "precondition of $name did not pass on this host; $name does not run here"
	fi
done
if [ "$mode" = precondition ] || [ ${#passing[@]} -eq 0 ]; then
	exit 0
fi
bash experiments/exploratory/detection-boundary-v4-exploratory/run-x3x7-stages.sh \
    "$out" "$processes" "$base" "$total" "$only" "${passing[@]}" || exit $?
echo "workers $(date -u +%FT%TZ)"
for name in "${passing[@]}"; do
	read -r _ access kinds <<<"$($python -m "$(module "$name")" describe)"
	for kind in ${kinds//,/ }; do
		$python -m "$(module "$name")" status --out "$out" --kind "$kind" \
			>"$logs/status-$kind.json" 2>&1
	done
	if [ "$access" = open ]; then
		$python -m "$(module "$name")" aggregate --out "$out" --output "$out/$name.json" \
			>"$logs/aggregate-$name.log" 2>&1
		echo "exit=$?" >"$logs/aggregate-$name.status"
	fi
done
echo "finished $(date -u +%FT%TZ)"
EOF
nohup flock -n "$out/logs/supervisor.lock" bash "$supervisor" "$PWD" "$out" \
	"$processes" "$mode" "$analyses" "${ONLY:-}" "${PROBE_COUNT:-8}" "$base" "$total" \
	>>"$out/logs/$mode.log" 2>&1 </dev/null &
echo "launched $mode of $analyses at $(git rev-parse HEAD) into $out"
