#!/bin/bash
set -uo pipefail
umask 077
coord=${V4_COORD:-$HOME/.local/state/research-workbench/coord-20260925}
out=$coord/v4-release
script=${1:?report checkout}/studies/ic-2026-2027/experiments/exploratory/detection-boundary-v4/release_on_completion.py
test -f "$script" || exit 1
mkdir -p "$out" && chmod 700 "$out"
cd "${V4_FROZEN:-$HOME/.local/state/research-workbench/ic-boundary-v4}/studies/ic-2026-2027" || exit 1
export UV_CACHE_DIR=/private/tmp/uv-cache-v44
export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
run() {
  "${V4_UV:-$HOME/.local/bin/uv}" run --frozen python "$script" \
    --freeze experiments/exploratory/detection-boundary-v4/freeze-v4.json \
    --allocation "$coord/v4-allocation.json" "$@"
}
release() {
  run --record "$out/release-record.json" >>"$out/release.stdout" 2>>"$out/release.stderr"
  status=$?
  echo "exit=$status $(date -u +%FT%TZ)" >>"$out/release.exit"
  if [ "$status" -ne 0 ]; then
    { echo "release refused: exit=$status $(date -u +%FT%TZ)"; tail -n 1 "$out/release.stderr"; } >"$out/release-ALERT.tmp"
    mv "$out/release-ALERT.tmp" "$out/release-ALERT"
  fi
  return "$status"
}
if test -e "$out/release-record.json"; then release; exit "$?"; fi
closed() { [ "$(date -u +%Y%m%d%H%M)" -ge 202610190300 ]; }
while :; do
  if closed; then
    while pgrep -f run_curve.py >/dev/null; do sleep 30; done
    release && exit 0
    sleep 1800
  elif run --check-only | grep -q '"complete": true'; then
    release && exit 0
    sleep 1800
  else
    sleep 300
  fi
done
