# Sanitized exploratory aggregates

These copies preserve the tracked exploratory results except for the fields
listed below. Sources are the identically named files in
`studies/ic-2026-2027/experiments/exploratory/detection-boundary-v4-exploratory/results/`.

Host, hostname, kernel, CPU (including timing), user and absolute-path
fields are removed, as are absolute paths and strings containing home
directories. Site-specific keys and strings are removed when they match
a supplied private pattern. Every retained JSON value and its type are
unchanged; object order and retained array order are preserved.
Whitespace is serialized anew.

Removed paths use RFC 6901 JSON pointers into each original source, with
zero-based array indices. A removed parent path includes its whole subtree.

Every reported table and figure regenerates from the archived aggregates
with the archived scripts, except the X1a and X2 tables of Online Resource 1
(Tables S20/S21), whose values are transcribed from the sanitized records
in this folder.

Random seeds derive from text labels and do not depend on the platform.
The `seed_material_sha256` field is a cache key that hashes numeric
parameters; it can differ across platforms without changing the seeds.
In the recorded cross-host replay of three zero-strength fitting-check
tasks on Linux x86-64, states, decisions and counts were identical, and
1,331,544 continuous values agreed within 7.9e-12 in absolute terms.
The pre-declared equivalence criterion nevertheless failed on the
`seed_material_sha256` field (4,448 divergences); platform, interpreter
and host fields also differed as expected. This component replay was
for equivalence only, not gate evidence; full-release bitwise replay
has not been independently demonstrated. The frozen runners refuse
to start outside the recorded bound environment.

Regenerate these sanitized files with the study environment:

```sh
python -m ic_study.analysis.v4_journal_export --sanitize-exploratory SRC_DIR OUT_DIR --private-pattern 'SITE_REGEX'
```

Replace SITE_REGEX privately with a site-specific regular expression.
The optional --private-pattern REGEX argument is repeatable and matches
case-insensitively; omit it to use only the generic field/path rules.
Patterns are supplied only at runtime and are not recorded in the archive.

## x1a.json

Mean-field twin versus the influence arm (paired AUCs).

- Source SHA-256: `04e92b6c8b6594c87f98bbc9c639f257a545b5f38d9fc16fd6dfb5cdefec6c6f`
- Sanitized SHA-256: `70303eed7148a526e9b4340130b588088aacee3914be7b3c65a01dbc76a6bdbf`

Removed JSON paths:

- `/host`
- `/timing/cpu_seconds_total`
- `/cells/0/timing/cpu_seconds`
- `/cells/1/timing/cpu_seconds`
- `/cells/2/timing/cpu_seconds`
- `/cells/3/timing/cpu_seconds`
- `/cells/4/timing/cpu_seconds`
- `/cells/5/timing/cpu_seconds`
- `/cells/6/timing/cpu_seconds`
- `/cells/7/timing/cpu_seconds`
- `/cells/8/timing/cpu_seconds`
- `/cells/9/timing/cpu_seconds`
- `/cells/10/timing/cpu_seconds`
- `/cells/11/timing/cpu_seconds`
- `/cells/12/timing/cpu_seconds`
- `/cells/13/timing/cpu_seconds`
- `/cells/14/timing/cpu_seconds`
- `/cells/15/timing/cpu_seconds`
- `/cells/16/timing/cpu_seconds`
- `/cells/17/timing/cpu_seconds`
- `/cells/18/timing/cpu_seconds`
- `/cells/19/timing/cpu_seconds`
- `/cells/20/timing/cpu_seconds`
- `/cells/21/timing/cpu_seconds`
- `/cells/22/timing/cpu_seconds`
- `/cells/23/timing/cpu_seconds`
- `/cells/24/timing/cpu_seconds`
- `/cells/25/timing/cpu_seconds`
- `/cells/26/timing/cpu_seconds`
- `/cells/27/timing/cpu_seconds`
- `/cells/28/timing/cpu_seconds`
- `/cells/29/timing/cpu_seconds`
- `/cells/30/timing/cpu_seconds`
- `/cells/31/timing/cpu_seconds`
- `/cells/32/timing/cpu_seconds`
- `/cells/33/timing/cpu_seconds`
- `/cells/34/timing/cpu_seconds`
- `/cells/35/timing/cpu_seconds`
- `/cells/36/timing/cpu_seconds`
- `/cells/37/timing/cpu_seconds`
- `/cells/38/timing/cpu_seconds`
- `/cells/39/timing/cpu_seconds`
- `/cells/40/timing/cpu_seconds`
- `/cells/41/timing/cpu_seconds`
- `/cells/42/timing/cpu_seconds`
- `/cells/43/timing/cpu_seconds`
- `/cells/44/timing/cpu_seconds`
- `/cells/45/timing/cpu_seconds`
- `/cells/46/timing/cpu_seconds`
- `/cells/47/timing/cpu_seconds`
- `/cells/48/timing/cpu_seconds`
- `/cells/49/timing/cpu_seconds`
- `/cells/50/timing/cpu_seconds`
- `/cells/51/timing/cpu_seconds`
- `/cells/52/timing/cpu_seconds`
- `/cells/53/timing/cpu_seconds`
- `/cells/54/timing/cpu_seconds`
- `/cells/55/timing/cpu_seconds`
- `/cells/56/timing/cpu_seconds`
- `/cells/57/timing/cpu_seconds`
- `/cells/58/timing/cpu_seconds`
- `/cells/59/timing/cpu_seconds`
- `/cells/60/timing/cpu_seconds`
- `/cells/61/timing/cpu_seconds`
- `/cells/62/timing/cpu_seconds`
- `/cells/63/timing/cpu_seconds`
- `/cells/64/timing/cpu_seconds`
- `/cells/65/timing/cpu_seconds`
- `/cells/66/timing/cpu_seconds`
- `/cells/67/timing/cpu_seconds`
- `/cells/68/timing/cpu_seconds`
- `/cells/69/timing/cpu_seconds`
- `/cells/70/timing/cpu_seconds`
- `/cells/71/timing/cpu_seconds`

## x1b.json

Mean-field twin versus matched persistence (AUCs and boundaries).

- Source SHA-256: `f4f156c51a500fe427ea01bcb48a1e166983909e46827df63b1c8a34785547aa`
- Sanitized SHA-256: `3b5786af11233741dbae737c9b836231cf735d0d812819a39acb33b1a4fd6f20`

Removed JSON paths:

- `/host`
- `/timing/cpu_seconds_total`
- `/cells/0/timing/cpu_seconds`
- `/cells/1/timing/cpu_seconds`
- `/cells/2/timing/cpu_seconds`
- `/cells/3/timing/cpu_seconds`
- `/cells/4/timing/cpu_seconds`
- `/cells/5/timing/cpu_seconds`
- `/cells/6/timing/cpu_seconds`
- `/cells/7/timing/cpu_seconds`
- `/cells/8/timing/cpu_seconds`
- `/cells/9/timing/cpu_seconds`
- `/cells/10/timing/cpu_seconds`
- `/cells/11/timing/cpu_seconds`
- `/cells/12/timing/cpu_seconds`
- `/cells/13/timing/cpu_seconds`
- `/cells/14/timing/cpu_seconds`
- `/cells/15/timing/cpu_seconds`
- `/cells/16/timing/cpu_seconds`
- `/cells/17/timing/cpu_seconds`
- `/cells/18/timing/cpu_seconds`
- `/cells/19/timing/cpu_seconds`
- `/cells/20/timing/cpu_seconds`
- `/cells/21/timing/cpu_seconds`
- `/cells/22/timing/cpu_seconds`
- `/cells/23/timing/cpu_seconds`
- `/cells/24/timing/cpu_seconds`
- `/cells/25/timing/cpu_seconds`
- `/cells/26/timing/cpu_seconds`
- `/cells/27/timing/cpu_seconds`
- `/cells/28/timing/cpu_seconds`
- `/cells/29/timing/cpu_seconds`
- `/cells/30/timing/cpu_seconds`
- `/cells/31/timing/cpu_seconds`
- `/cells/32/timing/cpu_seconds`
- `/cells/33/timing/cpu_seconds`
- `/cells/34/timing/cpu_seconds`
- `/cells/35/timing/cpu_seconds`
- `/cells/36/timing/cpu_seconds`
- `/cells/37/timing/cpu_seconds`
- `/cells/38/timing/cpu_seconds`
- `/cells/39/timing/cpu_seconds`
- `/cells/40/timing/cpu_seconds`
- `/cells/41/timing/cpu_seconds`
- `/cells/42/timing/cpu_seconds`
- `/cells/43/timing/cpu_seconds`
- `/cells/44/timing/cpu_seconds`
- `/cells/45/timing/cpu_seconds`
- `/cells/46/timing/cpu_seconds`
- `/cells/47/timing/cpu_seconds`
- `/cells/48/timing/cpu_seconds`
- `/cells/49/timing/cpu_seconds`
- `/cells/50/timing/cpu_seconds`
- `/cells/51/timing/cpu_seconds`
- `/cells/52/timing/cpu_seconds`
- `/cells/53/timing/cpu_seconds`
- `/cells/54/timing/cpu_seconds`
- `/cells/55/timing/cpu_seconds`
- `/cells/56/timing/cpu_seconds`
- `/cells/57/timing/cpu_seconds`
- `/cells/58/timing/cpu_seconds`
- `/cells/59/timing/cpu_seconds`
- `/cells/60/timing/cpu_seconds`
- `/cells/61/timing/cpu_seconds`
- `/cells/62/timing/cpu_seconds`
- `/cells/63/timing/cpu_seconds`
- `/cells/64/timing/cpu_seconds`
- `/cells/65/timing/cpu_seconds`
- `/cells/66/timing/cpu_seconds`
- `/cells/67/timing/cpu_seconds`
- `/cells/68/timing/cpu_seconds`
- `/cells/69/timing/cpu_seconds`
- `/cells/70/timing/cpu_seconds`
- `/cells/71/timing/cpu_seconds`
- `/cells/72/timing/cpu_seconds`
- `/cells/73/timing/cpu_seconds`
- `/cells/74/timing/cpu_seconds`
- `/cells/75/timing/cpu_seconds`
- `/cells/76/timing/cpu_seconds`
- `/cells/77/timing/cpu_seconds`
- `/cells/78/timing/cpu_seconds`
- `/cells/79/timing/cpu_seconds`
- `/cells/80/timing/cpu_seconds`

## x2.json

Variance explained by influence and its spline-adjusted contrast.

- Source SHA-256: `073632af8a21f4f715bf961cd3d968546447f889ddef96882cd78a81af5fcba1`
- Sanitized SHA-256: `820ae6a09ba1575caac7ad8ecb418b89a18f78fa8bdc12742b5b998ca3a23b56`

Removed JSON paths:

- `/host`
- `/timing/cpu_seconds_total`

## x5.json

Response-channel misspecification with influence switched off.

- Source SHA-256: `88e78a38ed7e5f07a48e6f0a18fab254abc7a21f684da8885e18b1b7870bcf36`
- Sanitized SHA-256: `3ae7cffc51e3e50726682b5cb67da59fa2a99b55bd5bcf17d63b3ce4520fc08b`

Removed JSON paths:

- `/host`
- `/timing/cpu_seconds_total`
