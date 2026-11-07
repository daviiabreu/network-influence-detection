set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

uv := env_var_or_default("UV", "uv")
study := "studies/ic-2026-2027"

default:
    @just --list

sync:
    cd {{study}} && {{uv}} sync --locked --group dev

structure:
    cd {{study}} && {{uv}} run --locked python ../../scripts/check_repository.py

lint:
    bash -n scripts/build_and_smoke.sh
    shellcheck scripts/build_and_smoke.sh
    cd {{study}} && {{uv}} run --locked ruff format --check . ../../scripts && {{uv}} run --locked ruff check . ../../scripts

typecheck:
    cd {{study}} && MYPYPATH=src:experiments:publications/jcss-journal {{uv}} run --locked mypy --explicit-package-bases src tests ../../scripts experiments/exploratory/detection-boundary-v4/release_on_completion.py experiments/exploratory/detection-boundary-v4/report/release_handoff.py experiments/exploratory/detection-boundary-v4/report/rehearse_release_handoff.py publications/jcss-journal/toolchain.py publications/jcss-journal/build.py publications/jcss-journal/package.py

test *args:
    cd {{study}} && {{uv}} run --locked python ../../scripts/test_hermetic.py {{args}}

build:
    ./scripts/build_and_smoke.sh {{uv}}

check: structure lint typecheck

quality: check test build
