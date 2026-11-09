# Public selection

`network-influence-detection` holds the scientific implementation, protocols,
specifications and manuscript sources of the paper. It starts a clean history
from a selection of the private monorepo at commit `cbf7d721`. Being tracked in
the original repository was not treated as permission to publish.

Agent histories, evaluations, promotions, private approvals, execution
coordination and runtime contracts stayed in the private preservation archive.
So did the venue search, which only informed where to submit. None of these
are needed to install the package, run the hermetic suite or compile the
manuscript. The agent framework
is maintained separately and is not a Python dependency of this study.

The systematic literature map in `research/literature/` (protocols, search
design, run records, preparation and synthesis) was restored unchanged after
the first extraction. Its records quote third-party sources only in short
excerpts; abstracts, full texts and corpus snapshots stayed in external state.

Protocols and scientific records keep their original identity. Some of them
link to files that are not here: framework code and process notes
(`workbench/`, `docs/process/`), now in the separate workflow repository, and
the private `research/venues/`, `research/agents/` and `research/decisions/`
records. Those links are historical references to the original monorepo; they do not become
a record of authorization or execution in this repository. The [extraction map](../provenance/origin-map.json) records the
selection and its hashes.

Swiss Household Panel data, raw, interim and processed data, sealed runs,
private holdouts, credentials and provider state stay external. The Springer
template is obtained separately, as described in the
[toolchain guide](publication-toolchain.md).

This repository uses the same terms as the Zenodo archive: the MIT License for
code, data and documentation and CC BY 4.0 for manuscript texts and figures, as
set out in the [README](../README.md#licences). Neither extends to
third-party texts, source snapshots, templates or Swiss Household Panel data.
Any further release needs its own selection of content and rights.

`POST-RELEASE.md` and the historical dossier `ai-disclosure-evidence.md`, which
contained private operational and audit locators, were omitted without changing
their originals. Their links and hashes remain in the private preservation. The
final editorial AI disclosure and the scientific protocols are intact. The
published research lifecycle contains only the generic lines 1–48 of its
source.
