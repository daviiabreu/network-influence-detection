# T41d — redação natural e valores da montagem

Base conferida: `c5b38650`, igual à integração no início; T41c commitada em `75dbab7a`. Worktree limpo no início, sem merge adicional necessário. Nenhum commit ou push feito.

Todos os exemplos e números deste relatório são dos ensaios públicos **sintéticos**, não resultados do estudo. Fontes do Owner não foram seguidas; nenhum selo, microdado ou diretório proibido foi aberto.

Aplicação por shell:

| Shell | Aplicação | Retenções |
| --- | --- | --- |
| Resumo | 24 regras com texto visível revisto; baseline em main.tex idêntico, 103 palavras | Frases de estágio mantidas quando a consolidação não pediu mudança; limitação preservada |
| Results | 75 trechos em todos os 31 blocos da T53 | Dois trechos antigos de B05/P1 não aplicados para conservar a T41c |
| Discussion/Conclusion | 64 dos 66 blocos de shell da T54: 50 Discussion e 14 Conclusion | C-EVALUATION-PASS e D-X1B mantidos pela T41c |
| Exploratórios | 13 dos 14 blocos da T54 | E.twin mantido pela T41c |

Dez propostas para seções fixas ficaram fora do escopo. As 15 propostas não aplicadas e as questões de sentido, binding, seleção e composição estão em [t41d-human-decisions.md](t41d-human-decisions.md). B05, B11 e a repetição da exposição já corrigidos na T41c são identificados como resolvidos, não como novos pendentes. Cada proposta aplicada conserva afirmação e força. [t41d-scope-proof.json](t41d-scope-proof.json) prova os mesmos resultnum/placeholder, todos os marcadores e os comentários de controle nos três shells não abstratos; em main.tex mudou somente o argumento de abstract. Em claim-evidence.md mudaram apenas as linhas AB/DS/CN pertinentes; não havia linha RS correspondente nessa tabela. Seções fixas, exportadores, figuras, tabelas e fechamento congelado permaneceram intactos.

Mudanças de condição e ordem: [t41d-selection-conditions.md](t41d-selection-conditions.md) e [registro estruturado](t41d-selection-changes.json). A.B04 exige n_first_low > 0; A.B06 exige n_first_ne_sustained > 0; A.B08 exige ambas as contagens de gap > 0. A.B05/A.B11 já tinham seus guards positivos, conferidos sem mudança. Somente a seleção do resumo muda. A.new-seeds conserva condição e ação, com order 16 → 950. O compositor mantém também os opcionais antes dessa ressalva; a prioridade first-fit não muda.

Orçamento: 46 composições obrigatórias distintas; máximo 246. A composição B03/D-after-B03 com diferença somente de intervalos entre primeira e sustentada permanece incluída. B03 com B10 positivo é incompatível com o critério registrado. Máximos depois de cada fallback, na ordem autorizada: 258 → 257 (H-BD elíptico) → 257 (B10 sem aposto) → 253 (X6 compacto) → 246 (frase original de região). Nenhuma obrigatória passa de 250. As 24 montagens efetivas têm 175–234 palavras. [Prova reproduzível](t41d-abstract-budget.json), gerada por `check_v4_abstract_budget.py`, sem execução científica.

O montador oferece `--values arquivo-novo.json`, no formato dos exportadores e somente com os IDs citados pela árvore montada. Recusa IDs ausentes, valores divergentes e colisões de destino; uma falha remove a cópia incompleta. O recibo registra arquivo, digest e contagem. ASSEMBLY.md documenta a saída, o paper_check, a reexportação manual alternativa e os nomes v4-allocation.json, G1c-aggregate-successor.json, shp-aggregate-successor-1.json e --crosswalk.

Repinagem: [recibo verificado](t41d-shell-repin-receipt-verified.json), com aceite explícito dos 167 IDs de regras de texto visível. Revisão antiga dos quatro shells: c5b38650. Linhas adjacentes com prosa revista são remapeadas somente quando mantêm exatamente os bindings e marcadores por linha; trocas de binding continuam ambíguas e recusadas. Inserção anterior, comentário interno, alteração visível, remoção e alinhamento por binding são cobertos pelos testes. Hash final das regras: `0ca7b86f45c9b7a024e5f0e8b1f88162930b3da6dd3e9fbd79fff2fa69da2b79`. As 267 identidades permanecem, sem regra nova.

Auditoria: 24/24 ready, agora também com valores restritos validados. Cobertura permanece 267/267 expressáveis; no início histórico da T41 eram 78/264. Divergências literais: 661 → 1375; 714 novas, 310 com texto revisto e nenhuma desaparecida. As novas diferenças vêm da redação atual nos mesmos blocos selecionados; o montador segue o shell repinado e as montagens históricas conservam sua redação. Todas as ocorrências, com caso, ID, linha, classificação e lado que segue as regras, estão no [JSON de auditoria](v4-manuscript-assembly-audit-2026-09-30.json); [tabela por ID](t41d-divergences.md). Os 24 catálogos confirmatórios mantêm todos os IDs antigos byte a byte após projetar os 15 IDs de veredito, como a auditoria anterior. O oráculo histórico não mudou; o oráculo atual foi atualizado.

Três exemplos completos de resumo e trechos selecionados seguem abaixo. Os arquivos completos ficam em `/private/tmp/v4-shell-assembly-audit-9klj18d2`; as palavras usam a fórmula do paper_check, incluindo valores exibidos e retirando nomes de comandos TeX.

## release-day/passed-shp — resumo: 223 palavras

When exposure is unobserved, opinion panels can show patterns consistent with partner drift or persistence. We map the nominal partner-drift strength $a$ that a fixed lag-based discriminator needs to separate synthetic panels from matched no-network persistence. Eleven-wave panels approximate the Swiss Household Panel's observation pattern. Both processes share a known response signal share $r$, and persistence is matched to drift on short-lag population correlations. The detection boundary $a^*(r)$ is the first grid strength at which the expected panel-level area under the receiver operating characteristic curve (AUC) reaches 0.70 against trait-plus-autoregressive persistence. Small and large denote interval-based regions divided at 0.03. The validation gate passed; 45 of 414 units were complete and valid. At the 9 shares with both comparisons gap-free ($r=$ 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90), the first boundary against trait-plus-autoregressive persistence was small at 9, large at 0, not attained at 0 and censored or indeterminate at 0; against state-dependent persistence, 0, 0, 9 and 0. At 9 of those shares trait-plus-autoregressive but not state-dependent persistence was separated, compatible with non-Gaussian persistence without specific evidence of interaction. After partial calibration exposure and protocol amendment, evaluation used new seeds. Separation is conditional on the declared laws, response channel and discriminator and does not identify causal social influence.

Results — trecho, 46 palavras:

```tex
Within this common set, the first boundaries against B were small at 9 values, large at 0, not attained at 0 and censored/indeterminate at 0. Against D, they were small at 0 values, large at 0, not attained at 9 and censored/indeterminate at 0.
```

Discussion — trecho, 100 palavras:

```tex
Of the 9 common gap-free pairs ($r=$ 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90), 9 met the frozen persistence criterion ($r=$ 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90): B's lower band exceeded 0.70 at some strength, whereas D's upper band stayed strictly below it over the entire grid.
Under the frozen interpretation, this result is compatible with non-Gaussian persistence and gives no specific evidence of interaction. It does not establish equivalence between D and the interaction law.
```

## release-day/x6-failure — resumo: 234 palavras

When exposure is unobserved, opinion panels can show patterns consistent with partner drift or persistence. We map the nominal partner-drift strength $a$ that a fixed lag-based discriminator needs to separate synthetic panels from matched no-network persistence. Eleven-wave panels approximate the Swiss Household Panel's observation pattern. Both processes share a known response signal share $r$, and persistence is matched to drift on short-lag population correlations. The detection boundary $a^*(r)$ is the first grid strength at which the expected panel-level area under the receiver operating characteristic curve (AUC) reaches 0.70 against trait-plus-autoregressive persistence. Small and large denote interval-based regions divided at 0.03. The validation gate passed; 45 of 414 units were complete and valid. At the 9 shares with both comparisons gap-free ($r=$ 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90), the first boundary against trait-plus-autoregressive persistence was small at 9, large at 0, not attained at 0 and censored or indeterminate at 0; against state-dependent persistence, 0, 0, 9 and 0. At 9 of those shares trait-plus-autoregressive but not state-dependent persistence was separated, compatible with non-Gaussian persistence without specific evidence of interaction. An exploratory check at $r=0.70$ found below-nominal interior coverage. After partial calibration exposure and protocol amendment, evaluation used new seeds. Separation is conditional on the declared laws, response channel and discriminator and does not identify causal social influence.

Results — trecho, 46 palavras:

```tex
Within this common set, the first boundaries against B were small at 9 values, large at 0, not attained at 0 and censored/indeterminate at 0. Against D, they were small at 0 values, large at 0, not attained at 9 and censored/indeterminate at 0.
```

Discussion — trecho, 51 palavras:

```tex
The exploratory interior check found below-nominal coverage under the declared primary criterion (reported classification \texttt{failure}). The Wilson upper endpoint, 0.766038, was below 0.9.
This is evidence of undercoverage for the stated procedural truth and success-conditioned denominator. The dispersion gate does not remove this limitation or certify nominal interior validity.
```

## dress/invalid-main — resumo: 196 palavras

When exposure is unobserved, opinion panels can show patterns consistent with partner drift or persistence. We map the nominal partner-drift strength $a$ that a fixed lag-based discriminator needs to separate synthetic panels from matched no-network persistence. Eleven-wave panels approximate the Swiss Household Panel's observation pattern. Both processes share a known response signal share $r$, and persistence is matched to drift on short-lag population correlations. The detection boundary $a^*(r)$ is the first grid strength at which the expected panel-level area under the receiver operating characteristic curve (AUC) reaches 0.70 against trait-plus-autoregressive persistence. Small and large denote interval-based regions divided at 0.03. The validation gate passed; 44 of 414 units were complete and valid. The main curve was not validated: not all nine of its units finished complete and valid. Against trait-plus-autoregressive persistence, the first boundary was small at 8 shares, large at 0, not attained at 0 and censored or indeterminate at 0. The prespecified conditions for comparing separation across persistence models were not met. After partial calibration exposure and protocol amendment, evaluation used new seeds. Separation is conditional on the declared laws, response channel and discriminator and does not identify causal social influence.

Results — trecho, 30 palavras:

```tex
The main curve against B is not validated: 1 of the nine tier-1 units were not both complete and valid at the effective release (Table~\ref{tab:v4-T4}, Fig.~\ref{fig:v4-F5}).
```

Discussion — trecho, 63 palavras:

```tex
The main B curve was not validated: 1 units were not both complete and valid. These included 1 zero-strength gate failures, 0 zero-strength gaps and 0 units not started or only partially completed at the close.
The remaining complete valid B units describe local boundaries that retain the main-invalidation mark, rather than a validated whole curve. Invalid units provide no positive boundary finding.
```

## Portões e recursos

| Checagem | Resultado |
| --- | --- |
| ruff check | PASS, cinco Python tocados |
| ruff format --check | PASS, mesmos cinco arquivos |
| mypy | PASS, cinco arquivos, sem erros |
| test_v4_manuscript_assembly.py | 155 passed, 7,77 s |
| test_v4_manuscript_assembly_derive.py | 84 passed, 15,65 s |
| test_frozen_files_are_untouched | 1 passed, 1,54 s, verificação final do fechamento |
| Tectonic --only-cached | Uma compilação, exit 0; dependências existentes do ensaio T51, sem download |
| paper_check com assembled-values.json | PASS, modo rascunho; 5.139 IDs, resumo 223 palavras, dois placeholders do Owner |
| git diff --check | PASS |

Checks sequenciais; um pytest por processo/arquivo, variáveis OMP_NUM_THREADS/OPENBLAS_NUM_THREADS/MKL_NUM_THREADS/VECLIB_MAXIMUM_THREADS em 1. `nice -n 15` foi tentado e recusado pelo macOS (`setpriority: Operation not permitted`); os comandos executaram normalmente. Não houve segunda compilação. O PDF sintético tem 90 páginas e 51.127 palavras extraídas, com advertências de caixas LaTeX; não é avaliação de prontidão de submissão. AV03 e Other declarations ficaram para o Owner. Uma primeira execução de teste detectou que a fixture de catálogo omitia IDs das tabelas que só entram após a montagem; a origem sintética foi completada a partir das próprias tabelas exportadas e o portão foi repetido, passando. Ruff detectou oito linhas longas e mypy uma anotação ausente; corrigidos antes dos portões finais.

## git diff --stat

```text
 .../publications/jcss-manuscript/claim-evidence.md |    36 +-
 .../publications/jcss-manuscript/main.tex          |     2 +-
 .../jcss-manuscript/pipeline/ASSEMBLY.md           |    62 +-
 .../drafts/2026-09-28/results-shells-abstract.md   |    60 +-
 .../pipeline/drafts/2026-09-28/results-shells.tex  |   150 +-
 .../2026-09-30/discussion-conclusion-shells.tex    |   216 +-
 .../2026-09-30/exploratory-results-shells.tex      |    32 +-
 .../review/audit_v4_manuscript_assembly.py         |    51 +-
 .../review/repin_v4_manuscript_assembly.py         |    30 +-
 .../v4-manuscript-assembly-audit-2026-09-30.json   | 55338 +++++++++++++++++--
 .../ic_study/analysis/v4_manuscript_assembly.py    |   166 +-
 .../analysis/v4_manuscript_assembly_rules.json     |    16 +-
 .../current_shell_oracles.json                     |    28 +-
 .../tests/unit/test_v4_manuscript_assembly.py      |   286 +-
 14 files changed, 50314 insertions(+), 6159 deletions(-)
```

Arquivos novos sob pipeline/review/ permanecem não rastreados; não foram staged nem commitados.

## git status --short

```text
 M publications/jcss-manuscript/claim-evidence.md
 M publications/jcss-manuscript/main.tex
 M publications/jcss-manuscript/pipeline/ASSEMBLY.md
 M publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-shells-abstract.md
 M publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-shells.tex
 M publications/jcss-manuscript/pipeline/drafts/2026-09-30/discussion-conclusion-shells.tex
 M publications/jcss-manuscript/pipeline/drafts/2026-09-30/exploratory-results-shells.tex
 M publications/jcss-manuscript/pipeline/review/audit_v4_manuscript_assembly.py
 M publications/jcss-manuscript/pipeline/review/repin_v4_manuscript_assembly.py
 M publications/jcss-manuscript/pipeline/review/v4-manuscript-assembly-audit-2026-09-30.json
 M src/ic_study/analysis/v4_manuscript_assembly.py
 M src/ic_study/analysis/v4_manuscript_assembly_rules.json
 M tests/fixtures/v4_manuscript_assembly/current_shell_oracles.json
 M tests/unit/test_v4_manuscript_assembly.py
?? publications/jcss-manuscript/pipeline/review/check_v4_abstract_budget.py
?? publications/jcss-manuscript/pipeline/review/t41d-abstract-budget.json
?? publications/jcss-manuscript/pipeline/review/t41d-compilation.json
?? publications/jcss-manuscript/pipeline/review/t41d-divergences.md
?? publications/jcss-manuscript/pipeline/review/t41d-editorial-proposals.json
?? publications/jcss-manuscript/pipeline/review/t41d-human-decisions.md
?? publications/jcss-manuscript/pipeline/review/t41d-report.md
?? publications/jcss-manuscript/pipeline/review/t41d-scope-proof.json
?? publications/jcss-manuscript/pipeline/review/t41d-selection-changes.json
?? publications/jcss-manuscript/pipeline/review/t41d-selection-conditions.md
?? publications/jcss-manuscript/pipeline/review/t41d-shell-repin-receipt-final.json
?? publications/jcss-manuscript/pipeline/review/t41d-shell-repin-receipt-verified.json
?? publications/jcss-manuscript/pipeline/review/t41d-shell-repin-receipt.json
?? publications/jcss-manuscript/pipeline/review/t41d-synthetic-successors.json
```
