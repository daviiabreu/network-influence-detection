# JCSS manuscript toolchain

The manuscript sources live in
`studies/ic-2026-2027/publications/jcss-journal/`. `build.py` compiles the
article and Online Resource 1 in a temporary copy and runs `check.py`.
`package.py` prepares a submission kit from a complete build and compares the
text of the recompiled PDF with the build. No command sends anything to the
journal.

Install Python 3.12, Tectonic and Poppler (`pdftotext` and `pdfinfo`). The
original environment used Tectonic 0.17.0; use that version when you need to
compare against the historical build with the same engine. The
[official Tectonic installation guide](https://tectonic-typesetting.github.io/book/latest/getting-started/install.html)
lists the available distributions.

Download the article template from the
[Springer Nature LaTeX author support page](https://www.springernature.com/gp/authors/campaigns/latex-author-support/see-where-our-services-will-take-you/18782940)
and extract `sn-jnl.cls` and `sn-mathphys-num.bst` into a folder outside Git.
Keep the version and SHA-256 you obtained. The template was not copied or
relicensed by this repository. During staging, the packager applies to the
`.bst` the editorial transformation already defined in the study.

```sh
cd studies/ic-2026-2027/publications/jcss-journal
python3 build.py --template /path/to/springer-template \
  --tectonic /path/to/tectonic --cache /path/to/tectonic-cache \
  --out /path/to/scratch-build
python3 package.py --template /path/to/springer-template \
  --tectonic /path/to/tectonic --cache /path/to/tectonic-cache \
  --build /path/to/scratch-build --out /path/to/new-submission-kit
```

The same values can come from `IC_STUDY_SPRINGER_TEMPLATE`,
`IC_STUDY_TECTONIC` and `IC_STUDY_TECTONIC_CACHE`; explicit options take
precedence. `TECTONIC_CACHE_DIR` is also accepted for the cache. Without
configuration, the engine comes from `PATH`, the template from
`$XDG_DATA_HOME/ic-study/springer-template` and the cache from
`$XDG_CACHE_HOME/ic-study/tectonic`, with the usual XDG defaults. For
compatibility with the original machine, existing template and cache folders
under `.local/state/research-workbench/` and the original Nix engine are local
fallbacks; they are not needed elsewhere.

Both commands use `--only-cached` by default. On a new machine, run `build.py`
once with `--allow-downloads` to fill the chosen cache, then run it without
that option. The
[Tectonic manual](https://tectonic-typesetting.github.io/book/latest/getting-started/first-document.html)
explains the first download and the cache variable.

`build.py --submission` enables the stricter editorial checks, such as failing
on open `[AT SUBMISSION …]` markers. A normal successful build may still
contain pending declarations. Builds and kits stay outside the sources: the
build folder is replaced on every run and the kit folder must be new. Do not
commit external templates, caches, scratch PDFs or private data.
