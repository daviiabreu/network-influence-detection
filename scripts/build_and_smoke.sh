#!/usr/bin/env bash
set -euo pipefail

if [[ $# -gt 1 ]]; then
  echo "usage: build_and_smoke.sh [uv]" >&2
  exit 2
fi

uv_bin=${1:-uv}
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
build_tmp=$(mktemp -d "${TMPDIR:-/tmp}/ic-study-build.XXXXXX")
trap 'rm -rf -- "$build_tmp"' EXIT

cd "$repo_root/studies/ic-2026-2027"
"$uv_bin" build --no-sources --no-build-isolation --out-dir "$build_tmp/dist"
wheel_file=$(find "$build_tmp/dist" -maxdepth 1 -name '*.whl' -print -quit)
if [[ -z "$wheel_file" ]]; then
  echo "wheel not produced" >&2
  exit 1
fi
"$uv_bin" venv --python 3.12 "$build_tmp/venv"
"$uv_bin" export --quiet --locked --no-dev --no-emit-project \
  --output-file "$build_tmp/runtime-requirements.txt"
"$uv_bin" pip install --python "$build_tmp/venv/bin/python" \
  --requirement "$build_tmp/runtime-requirements.txt"
"$uv_bin" pip install --python "$build_tmp/venv/bin/python" --no-deps "$wheel_file"
cd "$build_tmp"
"$build_tmp/venv/bin/python" -I -c \
  'from importlib import import_module; from importlib.metadata import version; modules = ("ic_study", "ic_study.models", "ic_study.simulation", "ic_study.metrics", "ic_study.analysis", "ic_study.validation"); assert all(import_module(name).__doc__ for name in modules); assert version("ic-study") == "0.0.0"'
echo "wheel smoke: ic-study passed outside checkout"
