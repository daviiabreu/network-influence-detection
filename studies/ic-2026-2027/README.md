# IC 2026–2027 study

Research compendium of the undergraduate research project (IC) at Inteli that
produced _Limits of Detecting Network Influence in Attitude Panels_. The
[repository README](../../README.md) summarizes the paper and how to run the
checks.

The study began as open discovery in opinion dynamics. Two exploratory pilots
([fragmentation](experiments/exploratory/fragmentation-pilot-v1/README.md) and
[probabilistic forecast](experiments/exploratory/probabilistic-forecast-pilot-v1/README.md))
were closed on their observed evidence. The question that became the paper,
how strong network influence must be before panel data can distinguish it from
individual persistence, was then preregistered and run as the detection
boundary experiment.

## Where things are

- `src/ic_study/`: scientific package (models, simulation, metrics, analysis, validation);
- `experiments/`: experiment specifications, frozen inputs and released records;
  the paper's experiment is `exploratory/detection-boundary-v4/`, with later
  exploratory analyses in the sibling `detection-boundary-v4-*` folders;
- `research/`: research questions, the
  [frozen preregistration](research/questions/exploration/2026-09-24-parallel/detection-boundary-preregistration-frozen.md),
  its [v4 amendment](research/questions/exploration/2026-09-24-parallel/detection-boundary-amendment-v4.md)
  and literature positioning;
- `publications/`: the current journal manuscript (`jcss-journal/`), the earlier
  rule-assembled version (`jcss-manuscript/`) and the reproducibility release;
- `validation/`: clean-room re-implementations docked against the project code;
- `tests/`: computational and scientific verification;
- `data/manifests/`: descriptions and hashes of externally stored data;
- `notebooks/`: exploration that calls code from `src/`.

Completed records are immutable: corrections create a linked successor instead
of overwriting evidence. Many of these records were written in Portuguese and
are kept as they were frozen.
