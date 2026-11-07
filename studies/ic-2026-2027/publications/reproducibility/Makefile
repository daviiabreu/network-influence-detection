STUDY := $(abspath ../..)
UV ?= uv
PYTHON ?= python3.12
SHARD ?= 0
SHARDS ?= 8
CONFIRMATORY_REVISION := 375138418f7f9e4528f0c2466f4600a76fee1bad
V4_RUNNER := experiments/exploratory/detection-boundary-v4/run_gate.py
V4_CURVE := experiments/exploratory/detection-boundary-v4/run_curve.py
V4_WRAPPER := experiments/exploratory/detection-boundary-v4/release_on_completion.py
BUILDER := $(STUDY)/publications/reproducibility/build_ic_release.py

.PHONY: example test package verify v4-ready v4-allocation g0 g1b g1c g2 g2c tier release-on-completion release-at-close report export project short-path

example:
	@test -n "$(ARTIFACT_ROOT)" && test -n "$(OUTPUT_DIR)" || (echo "Set ARTIFACT_ROOT and a new OUTPUT_DIR" >&2; exit 2)
	cd "$(STUDY)" && $(UV) run --locked python publications/reproducibility/regenerate_fragmentation.py \
		--study-root . --artifact-root "$(ARTIFACT_ROOT)" --output-dir "$(OUTPUT_DIR)"

test:
	cd "$(STUDY)" && $(UV) run --locked pytest -q tests/unit/test_ic_release_package.py

package:
	@test -n "$(REPOSITORY)" && test -n "$(PLAN)" && test -n "$(OUTPUT_DIR)" || (echo "Set REPOSITORY, PLAN and a new OUTPUT_DIR" >&2; exit 2)
	$(PYTHON) "$(BUILDER)" build --repository "$(REPOSITORY)" --plan "$(PLAN)" \
		--output "$(OUTPUT_DIR)" $(if $(RELEASE_ROOT),--release-root "$(RELEASE_ROOT)",) \
		$(if $(REDACTION_RULES),--redaction-rules "$(REDACTION_RULES)",)

verify:
	@test -n "$(BUNDLE)" || (echo "Set BUNDLE" >&2; exit 2)
	$(PYTHON) "$(BUILDER)" verify --bundle "$(BUNDLE)" $(if $(MANIFEST_SHA256),--manifest-sha256 "$(MANIFEST_SHA256)",)

v4-ready:
	@test -n "$(FROZEN_STUDY)" && test -n "$(FREEZE)" && test -f "$(FREEZE)" || (echo "Set FROZEN_STUDY and the original FREEZE; current reporting code cannot run frozen gates" >&2; exit 2)
	@test "$$(git -C "$(FROZEN_STUDY)" rev-parse HEAD)" = "$(CONFIRMATORY_REVISION)" || (echo "Confirmatory revision mismatch" >&2; exit 2)
	@test "$(SHARD)" -ge 0 && test "$(SHARDS)" -gt "$(SHARD)" || (echo "Invalid SHARD/SHARDS" >&2; exit 2)
	@$(PYTHON) -c 'import json,sys; assert int(sys.argv[2]) == json.load(open(sys.argv[1]))["shards"] == 8, "Shard count differs from freeze"' "$(FREEZE)" "$(SHARDS)"

v4-allocation: v4-ready
	@test -n "$(ALLOCATION)" && test -f "$(ALLOCATION)" || (echo "Set ALLOCATION to the second binding" >&2; exit 2)
	@test -n "$(CRITERIA)" && test -f "$(CRITERIA)" || (echo "Set CRITERIA to the bound criteria" >&2; exit 2)

g0 g1b g1c: v4-ready
	cd "$(FROZEN_STUDY)" && $(UV) run --frozen python $(V4_RUNNER) --freeze "$(FREEZE)" --gate $(if $(filter g0,$@),G0,$(if $(filter g1b,$@),G1b,G1c)) --shard $(SHARD) --shards $(SHARDS)

g2 g2c: v4-allocation
	cd "$(FROZEN_STUDY)" && $(UV) run --frozen python $(V4_RUNNER) --freeze "$(FREEZE)" --gate $(if $(filter g2,$@),G2,G2c) --allocation "$(ALLOCATION)" --criteria "$(CRITERIA)" --shard $(SHARD) --shards $(SHARDS)

tier: v4-allocation
	cd "$(FROZEN_STUDY)" && $(UV) run --frozen python $(V4_CURVE) --freeze "$(FREEZE)" --allocation "$(ALLOCATION)" --criteria "$(CRITERIA)" --shard $(SHARD) --shards $(SHARDS)

release-on-completion: v4-allocation
	@test -n "$(WRAPPER_STUDY)" && test -n "$(RELEASE_RECORD)" && test -n "$(WRAPPER_SHA256)" || (echo "Set WRAPPER_STUDY, RELEASE_RECORD and the selected WRAPPER_SHA256" >&2; exit 2)
	@$(PYTHON) -c 'import hashlib,sys; assert hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest() == sys.argv[2], "Wrapper hash mismatch"' "$(WRAPPER_STUDY)/$(V4_WRAPPER)" "$(WRAPPER_SHA256)"
	cd "$(FROZEN_STUDY)" && $(UV) run --frozen python "$(WRAPPER_STUDY)/$(V4_WRAPPER)" --freeze "$(FREEZE)" --allocation "$(ALLOCATION)" --criteria "$(CRITERIA)" --record "$(RELEASE_RECORD)"

release-at-close:
	@echo "Use release-on-completion with the release amendment and the executed wrapper's hash; see README.md" >&2
	@exit 2

report:
	@test -n "$(REPORTING_STUDY)" && test -n "$(GATE_ROOT)" && test -n "$(CRITERIA)" && test -n "$(OUTPUT_DIR)" || (echo "Set REPORTING_STUDY, authorized GATE_ROOT, CRITERIA and a new OUTPUT_DIR; see the replay limitation in README.md" >&2; exit 2)
	cd "$(REPORTING_STUDY)" && $(UV) run --frozen python -m ic_study.analysis.detection_v4_report \
		--gate-root "$(GATE_ROOT)" --criteria "$(CRITERIA)" --out "$(OUTPUT_DIR)" \
		$(if $(CURVES),--curves "$(CURVES)" --release-record "$(RELEASE_RECORD)",) \
		$(if $(ALLOCATION),--allocation "$(ALLOCATION)",) $(if $(STAGE_SUCCESSOR),--stage-successor "$(STAGE_SUCCESSOR)",) \
		$(if $(SHP),--shp "$(SHP)",) $(if $(CROSSWALK),--crosswalk "$(CROSSWALK)",)

export:
	@test -n "$(REPORTING_STUDY)" && test -n "$(GATE_ROOT)" && test -n "$(CRITERIA)" && test -n "$(REPORT)" && test -n "$(MANUSCRIPT_COPY)" && test -n "$(VALUES)" && test -n "$(CATALOG)" || (echo "Set the same report inputs, REPORT, a separate MANUSCRIPT_COPY, VALUES and CATALOG" >&2; exit 2)
	cd "$(REPORTING_STUDY)" && $(UV) run --frozen python -m ic_study.analysis.v4_report_export \
		--gate-root "$(GATE_ROOT)" --criteria "$(CRITERIA)" --report "$(REPORT)" \
		--manuscript "$(MANUSCRIPT_COPY)" --values "$(VALUES)" --catalog "$(CATALOG)" --fill \
		$(if $(CURVES),--curves "$(CURVES)" --release-record "$(RELEASE_RECORD)",) \
		$(if $(ALLOCATION),--allocation "$(ALLOCATION)",) $(if $(STAGE_SUCCESSOR),--stage-successor "$(STAGE_SUCCESSOR)",) \
		$(if $(SHP),--shp "$(SHP)",) $(if $(CROSSWALK),--crosswalk "$(CROSSWALK)",)

project:
	@test -n "$(REPORTING_STUDY)" && test -n "$(GATE_ROOT)" && test -n "$(PUBLIC_AGGREGATES)" || (echo "Set REPORTING_STUDY, authorized GATE_ROOT and a new PUBLIC_AGGREGATES file" >&2; exit 2)
	cd "$(REPORTING_STUDY)" && $(PYTHON) -m ic_study.analysis.v4_public_aggregates project \
		--gate-root "$(GATE_ROOT)" --out "$(PUBLIC_AGGREGATES)" \
		$(if $(CRITERIA),--criteria "$(CRITERIA)",) \
		$(if $(CURVES),--curves "$(CURVES)" $(if $(RELEASE_RECORD),--release-record "$(RELEASE_RECORD)",),) \
		$(if $(ALLOCATION),--allocation "$(ALLOCATION)",) $(if $(STAGE_SUCCESSOR),--stage-successor "$(STAGE_SUCCESSOR)",) \
		$(if $(SHP),--shp "$(SHP)",) $(if $(CROSSWALK),--crosswalk "$(CROSSWALK)",) \
		$(if $(SYNTHETIC),--synthetic,)

short-path:
	@test -n "$(BUNDLE)" || (echo "Set BUNDLE to the directory containing public aggregates and expected-hashes.json" >&2; exit 2)
	cd "$(STUDY)" && $(PYTHON) publications/reproducibility/verify_short_path.py \
		--bundle "$(BUNDLE)" $(if $(EXPECTED_MANIFEST),--manifest "$(EXPECTED_MANIFEST)",) \
		$(if $(OUTPUT_DIR),--out "$(OUTPUT_DIR)",)
