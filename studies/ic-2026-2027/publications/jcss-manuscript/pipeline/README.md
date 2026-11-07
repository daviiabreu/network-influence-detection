# Manuscript writing and review pipeline

This kit prepares sections and review without deciding the IC question. The current detection-boundary paper is a draft, not a confirmed result; a different question may be selected from the systematic map. JCSS is the working primary venue and JASSS the alternative. Before submission, reread the official pages in `venue-source-notes.md` and update the checklist.

## Parallel section workflow

Assign one brief under `briefs/` per drafter, each in a separate branch or worktree. Give the drafter the brief, its named source files, and the specified ledger rows only. Draft a new section file, not the shared `main.tex` or `claim-evidence.md`. The integrating editor verifies every empirical sentence against its ledger ID and original source, resolves overlapping prose, then links the section from the manuscript. Do not infer novelty, map completion, scientific approval, public availability, or confirmatory results from a draft or agent agreement. The Research Owner chooses the question and humans approve final claims.

Each returned section should include: (1) the `.tex` text, (2) a short claim-to-ledger list by sentence or paragraph, (3) unresolved evidence and decisions. If a source does not support the sentence, narrow or remove the sentence. Keep restricted evidence outside agent prompts and Git.

## Checks

Compile in a temporary copy with the current official Springer Nature `sn-jnl.cls` and `sn-mathphys-num.bst` (do not add the vendor package to Git):

```sh
nix shell nixpkgs#tectonic --command tectonic main.tex
python3 pipeline/paper_check.py --venue jcss --pdf main.pdf
python3 pipeline/paper_check.py --venue jcss --pdf main.pdf --submission --result-values /path/to/validated-result-values.json
```

Run `--venue jasss` for the alternative venue. The PDF must be from the same source snapshot. The script reports extracted PDF word and page counts, abstract words, keyword count, required statement headings, unresolved citation keys, and (in `--submission` mode) placeholders and numeric result bindings. PDF text extraction is an estimate of length and includes front matter, references, and supplements. There is no JCSS numeric page cap in the consulted guidelines; JASSS's 5,000–8,000 words is described as typical, so it is an advisory.

The results exporter (`python -m ic_study.analysis.v4_report_export`, see `experiments/exploratory/detection-boundary-v4/report/RELEASE-RUNBOOK.md` in the study) creates the JSON object `{"values": {"stable_result_id": "0.812"}}` from the validated report outputs, with each value as printed. Every numerical result in `sections/results.tex` and included `generated/*.tex` must use `\resultnum{stable_result_id}{0.812}`, protocol constants included (`v4.protocol.*`); `main.tex` defines `\resultnum` as an identity macro. The checker compares printed literals to the JSON and rejects other numeric literals in those result files. Cite the exact results manifest and ledger row in prose. The rule also applies when results are repeated in the abstract, discussion, or conclusion: copy the bound macro and verify those locations editorially. Do not create values merely to make the gate pass.

This is a mechanical gate, not scientific validation. A pass does not establish that a source file is an accepted run or that a claim is warranted. Run the project quality gates and the review kit before submission.
