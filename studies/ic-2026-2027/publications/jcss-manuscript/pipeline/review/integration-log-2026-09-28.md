# Integration log — 2026-09-28

Branch `integration/ic-20260928`. This log records how the 2026-09-28 section drafts were integrated and how the text-only items of `referee-report-2026-09-28.md` (cited as **RR**) were applied. The v4 gate and the confirmatory tiers were still running. No gate outcome, AUC estimate of the estimand, boundary, $a^*(r)$ value or SHP anchor value was written anywhere. Result slots keep `[to be filled from validated outputs]` or the existing bracketed placeholders. The frozen design (`freeze-v4.json`, commit `37513841`) was not touched: every sentence describes what the frozen code implements.

## Estado reconciliado em 2026-09-30 — M03

Base `f406ba64`, ramo `docs/response-tracker-20260930`. As seções numeradas abaixo registram o estado histórico de 28/09 e seus adendos; “Open”, “not run” e “not compiled” nesses registros não são o estado vigente. A [resposta aos pareceres](response-tracker.md) passa a reunir o estado atual, as dependências e as lacunas sem dono. Esta seção altera somente o estado do rastreador, sem nova decisão científica.

Evidência desta reconciliação: commits de `integration/ic-20260928` desde 28/09 e itens 80–116 de `owner-decisions-20260924-session-log.md` (`L n`), no diretório do coordenador. Nenhuma fonte proibida foi consultada. G0/G1b/G1c/G2 estão aprovados no estado público informado para esta tarefa; G2 passou às 10:01Z de 30/09 (700/700, zero falhas). O gate foi aprovado por inteiro: G2c às 16:44:54Z (142/142, zero falhas; L114), com início dos tiers às 16:46:33Z. L116 mantém a cadeia em `waiting-release`; não comprova liberação, resultado confirmatório ou resultado aberto de X3/X4/X6/X7.

| Pendência histórica | Estado vigente e evidência |
| --- | --- |
| §5 R1-M1(S), ranked 4: gêmeo mean-field | Implementado/relatado em `af0b9efb`, `a3a76a9a`, `3242b19b`; leitura de X1a/X1b corrigida em `6b319516`, L83. Comparação com a curva principal pós-liberação; controle que preserve a forma continua sem dono |
| §5 R1-M3(S), ranked 5: mapa de deriva | X2 relatado em `af0b9efb`, integrado em `ba5205a0`. Não é execução ainda por iniciar, nem medida na escala observada |
| §5 R1-M4(E): lag-profile/âncora | Aberto: depende de insumos liberados e da âncora atestada pelo Davi; `6b319516` separa estimandos, não executa calibração |
| §5 R1-M4(S): calibrar rho | Sem dono/plano de execução demonstrado; limitação preservada em `6b319516` |
| §5 R1-M5(E): tier 2 | Aberto pós-liberação; L91 substitui Q8 de L82 e exige tier 2 completo e válido para frase entre mecanismos; `99c59590` implementa |
| §5 R1-M6(S): gerador com domicílios | Futuro trabalho sem dono, não plano executado; `6b319516` conserva limitação |
| §5 R2-M1(S): parcela de sinal livre | X3 implementado em `cfe15198`, corrigido/lançado em `30c10dc8`/`3334ac0f`, L81–L90; leitura científica ainda pós-liberação |
| §5 R2-M2(S): painel único/bootstrap | X4 implementado em `cfe15198`, corrigido/lançado em `30c10dc8`/`3334ac0f`; linguagem oracular restrita em `6b319516`/`99c59590`. Resultado pós-liberação; teste operacional utilizável continua sem dono |
| §5 R2-M3(E), ranked 2: tradução de AUCs | Aberto pós-liberação; `a417f390` prepara exportação, sem curva real liberada no recorte |
| §5 R2-M4(S), ranked 3: crosswalk/STARTS | Declaração/freeze descritos por `6b319516`, L83; execução/atestação empírica dependem do Davi e dos insumos. Calibração inferencial adicional sem dono |
| §5 R2-M5(S): má especificação | X5 relatado em `4a372a71`/`2a4e034b`; síntese fechada em `6b319516`, L83. L91/`29ee6422` tornam X5 obrigatório na Discussão/Conclusão; comparação real pós-liberação |
| §5 R2-M6(E), ranked 8: diagnósticos | Diagnósticos exportáveis aguardam liberação; aprovação pública não fornece os valores. `a417f390` retirou a frase de mean_shift selado sem fonte no relatório; não prometer esse diagnóstico como entrega automática |
| §5 R2-M7(S): banda de 81 células | Sem dono; análise não planejada e seria pós-hoc, sem evidência de execução no recorte |
| §5 R2-M9(E): retries/gaps | Aberto para inventário real; `a417f390` exporta diagnósticos por célula, sem conferir resultados selados |
| §5 R2 minor 7(E): ties | Aberto pós-liberação; não deduzir tie rates de pass/fail do gate |
| §5 secundários 0.60/0.80 | Regra fechada por L91/`99c59590`: sempre suplemento. Valores reais pós-liberação |
| §6 Q1: compromisso exploratório | Planejamento do §8 é histórico; X1/X2 e X5 já relatados, X3/X4/X6/X7 implementados e lançados (L81–L90). Leituras/síntese seguem L89/L91 e `29ee6422`; não equivale a fechamento científico |
| §6 Q2: sucessor SHP antes de exposição | Estado de freeze descrito por `6b319516`, L83; preparação fechada, âncora/STARTS/crosswalk empíricos não encerrados |
| §6 Q3/Q14: título e novidade | Davi; `e243e2a5`, L92, mantém tema com busca adicional, sem ratificar título ou prioridade |
| §6 Q4, F6, Methods ledger 8 | `8ec31912` prepara inventário por papel/sessão; `6acb0e43` liga a fonte ao ledger. Divulgação/atestação humana abertas; não inferir modelo de trailer nem independência de personas |
| §6 Q5(a/b/c), F8 | Q5(a) já decidido no §8. `cd4411b7` registra freeze/cronologia, mas não comprova fechamento específico de Q5(b/c); contradição da abertura do README persiste. Notas sucessoras sem dono documentado |
| §6 Q6, F9 | Decisão já executada no §8: exposição reduzida pública impressa. Rastreio atualizado em `6acb0e43`; exposição e cronologia finais de M03 aguardam liberação |
| §6 Q7 | Correção delimitada em `eb4f6068`, integrada em `20bdcaac`; leitura integral das cinco obras não concluída. Não reabrir como redação pendente nem certificar acesso integral |
| §6 Q8/Q12/Q13 | Decididas no §8; terminologia/censura explicitadas em `6b319516`. Não confundir com IDs iguais dos shells; leitura real pós-liberação |
| §6 Q9 | Ratificação humana aberta; L105(v) registra adendo/lista de ações, não inspeção/aceite do Davi |
| §6 Q10 | L99(i)/`0083009f` fecham forma do artigo de falha, não periódico. Destino continua Davi; não selecionar ramo a partir de ensaio |
| §6 Q11 | Separação implementada em `a417f390`: diagnósticos e tabelas de gaps; `v4_report_export.py` distingue screened, profile limit, solver e validation. Conferência das contagens reais pós-liberação |
| Ranked 6 e risk register | Shells de Results/resumo fechados por L91/L99/L101 e `99c59590`/`0083009f`/`00c8dc3d`; Discussão/Conclusão pré-escritas em `29ee6422`, L112. Ensaios em L109/L113; seleção real não executada |
| Methods ledger 10; related-work ledger 5 | TOST/Holm opcionais e limpeza de entradas não citadas: sem fechamento ou dono documentado. `7a5bc2cc` não prova execução desses dois itens |
| Related-work ledger 4/6 e §9.10: fontes | `6acb0e43` reavalia cobertura e acrescenta rastreio, inclusive IN06/Lersch; não certifica leitura integral geral. C36–C38/C40 e alcance M61/M66/M69 permanecem no Davi, conforme auditoria M04 |
| §9.11: resumo, abertura, conclusão, suplemento e ODD sem rastreio | Fechamento parcial em `6acb0e43` (AB01–AB08, IN04–IN07, CN01, SUP01–SUP13). Auditoria cobre ODD, mas abertura e introdução a Submodels ainda sem linha/marcador próprios; agente/coordenador em M04, Davi aceita suporte. Valores futuros e pendências de suporte continuam abertos |
| Related-work ledger 10; §7/§9.12: compilação | Compilação histórica feita (L83: 42 páginas/checker normal; outra em `6acb0e43`). Compile e revisão final dos arquivos reais M05/M06 ainda pós-liberação; roteiro `1127d5a8` não é revisão executada |
| C-m5 e responsabilização | Rota pública SHP fechada em `7a5bc2cc`; contrato/versão, autoria, declarações, DOI/acesso e envio continuam Davi. Preparação em `32e6445c`/`fb37e762`, guardas em `61378726`/`444c337f`; L111 não registra publicação |

### Rótulos do registro histórico

- **Edited:** changed, with the file and marker.
- **Already fixed:** fixed on this branch before this integration.
- **Open:** not done, with the reason. Every (S) and (E) item is open, because nothing was run.
- **Owner decision:** the Research Owner must decide. The decision is stated as a question.

Paths are relative to `studies/ic-2026-2027/publications/jcss-manuscript/` unless they start with `studies/`, `src/`, `research/`, `validation/` or `experiments/`. The last four are relative to `studies/ic-2026-2027/`.

## 1. Files changed

| File | Change |
| --- | --- |
| `sections/methods.tex` | Replaced by the Methods draft, with the draft-verification corrections applied. New subsection "What the design can identify". Referee text fixes added. Markers M01–M84. |
| `sections/verification.tex` | Replaced by the Verification draft, with narrowings applied. `\label{sec:verification}` kept. New marker VER14. VER05 retired. |
| `main.tex` | Working title, abstract (236 words) and keywords revised. The availability draft replaced the "Data and code availability" statement (markers AV01–AV10). |
| `sections/related-work.tex` | Replaced by the Related-work draft, with narrowings applied. Trait–state–error paragraph added (R60–R62) and search-record sentence added (R63). |
| `sections/introduction.tex` | Paragraphs 4 and 5 replaced as the positioning draft specifies (IP01–IP09; IN01). Paragraphs 6–7 revised (IN02–IN03). Paragraphs 1–3 and 8 unchanged. |
| `sections/background.tex` | Removed the voter, Sznajd and $q$-voter subsection, the macro-outcome material and the repeated-observation subsection. A01, A04 and A07 reworded. |
| `sections/discussion.tex` | Rewritten around the frozen interpretation regions, the B-and-D headline and the (X) limitations. Markers DS01–DS10. |
| `sections/conclusion.tex` | Terminology and placeholders aligned with the B-and-D headline. |
| `sections/supplement.tex` | Systematic-map `\input` lines removed (files kept). False partial-$R^2$ sentence removed. Main-curve rule aligned with the code. Post-freeze docking exposure added without values. New subsection "Positioning search record (reconstructed)". |
| `sections/appendix-odd.tex` | Pointer to the nonexistent reconciliation notes replaced. Terminology changed (ODD02, ODD06, ODD15, ODD36, ODD37). ODD08 bound qualified. F18 note added to ODD35. Single-machine note added to ODD37. |
| `sections/results.tex`, `generated/auc-heatmaps.tex` | Terminology only. |
| `references.bib` | The three draft additions merged. Five trait–state–error records and the SHP User Guide added. No duplicate keys or DOIs. |
| `claim-evidence.md` | New sections "Methods v4", "Verification v4", "Code and data availability", "Related work v4", "Introduction" and "Discussion" (all "integrated 2026-09-28"). Bibliographic rows added for the new keys. Retired rows marked: C08–C15, A03, C20, C21, C24–C30, A05, C42–C46, A08, R01–R22, VER05. V01–V17 and V22 marked superseded. Paths corrected (F15). ODD08, ODD35, ODD37 and ODD38 rows updated. |

The drafts in `pipeline/drafts/2026-09-28/` are kept unchanged as the record of what was integrated.

## 2. Verification of draft sentences before moving them

Four read-only checks re-opened every locator cited by the draft ledgers:

- the code under `src/ic_study/`, whose cited files are unchanged since `37513841`;
- the amendment, v1, SPEC and DRD files;
- the three validation reports and `freeze-v4.json`;
- the positioning dossier and `search-log.json`.

The Crossref records of the new references were fetched directly, and the SHP User Guide PDF was read at the FORS URL already used in `claim-evidence.md`.

| Marker | Outcome | What changed |
| --- | --- | --- |
| M25 | **Failed, corrected** | The draft said a sustained boundary directly above a gap is censored. The code (`detection_boundary_v4.py:698-715`, `value > limit`) retains it. What it censors is a sustained crossing that extends below the last gap. The sentence now says this. |
| M20 | Narrowed | The `ill-conditioned` test runs before the sign test. A `boundary` fit of A, C or a control validates lag one only. |
| M30 | Narrowed | The v4 band is a re-implementation of the v1 readings, not v1 code "carried over unchanged". The v1 floor is recomputed from the number of strengths; v4 fixes it at 2.7729. |
| M35 | Narrowed | The G2 covariance diagnostic also re-evaluates the training and reference streams. |
| M40 | Corrected (RR F12) | The rule stops execution before G2, not "before the remaining gates". |
| M44 | Narrowed | The freeze binds an environment (a platform string), not a host. |
| M10, M12, M28 | Narrowed | Wording made more exact. |
| VER06 | Narrowed | Only the phase-1 readings preceded source access. The timing probe is now disclosed. |
| VER08 | Narrowed | Resolution is stated in ordinal lag-correlation units. Persistent style added to the not-docked list. |
| VER09 | Narrowed | Reporting-only exceptions named. |
| VER10 | Narrowed | States that the report's 17/22 is corrected in `RECONSTRUCTION.md`. Case identifiers listed. |
| AV04 | Narrowed | Platform string, not one host. Environment mismatch of any kind, not "any other recorded environment". |
| AV05 | Narrowed | No macOS test-run record exists. Hashed Python files added after the freeze are named. |
| AV06 | Narrowed | Only the three failures are stated to reproduce on the clean worktree. The macOS origin of the hashes is part of the hypothesis. |
| AV07 | Narrowed | "Linux" comes from `result.json`. That host ran a different build of Python 3.12.13. |
| AV09 | Narrowed | Stated as a plan ("are to be run"). |
| R30, R54, R59 | Narrowed | One-parameter nulls match lag one only. |
| R33 | Narrowed | "Pure measurement-error account" changed to the abstract's "the measurement-error model". |
| R55, IP09 | Rewritten (RR R1-M7) | Population quantities, complete valid grid, likely loose. |
| R56 | Narrowed | "Five records of four works". Declaration and run dates separated. |
| IP01 | Narrowed | The distributions are ESS, not SHP. |
| IP05 | Narrowed | Joint dependence attributed to Dang–Ma only. Mulder is abstract-only. |

All other M, VER, AV, R and IP rows were confirmed as written. Row-level evidence and limits are in `claim-evidence.md`.

## 3. Referee report

### Referee 1, major concerns

| Item | Status | Where / reason |
| --- | --- | --- |
| R1-M1 (T) mean-field argument, linear control, what the discriminator can and cannot see | Edited | `methods.tex` subsection "What the design can identify", M60–M64. Linear-control non-attainment from v1 at M63. Title and abstract reframed (`main.tex`). Discussion DS02. |
| R1-M1 (X) | Edited | DS02, M64. |
| R1-M1 (S) mean-field twin null | Open | Not run. Named in the single planning sentence DS10. See Owner decision Q1. |
| R1-M2 (T) honest generator description, lost macro behaviour | Edited | M04, M57; `background.tex` A04; ODD02, ODD08; abstract; IN01. |
| R1-M2 (X) | Edited | DS04. |
| R1-M3 (T) remove the false partial-$R^2$ sentence | Edited | `supplement.tex` "Panel channels and null mechanics". Replaced by a statement that no such diagnostic is computed. M68 states the v1 promise and its absence in v4. |
| R1-M3 (S) partial-$R^2$ map | Open | Not run. Named in DS10. See Q1. |
| R1-M4 (T) what the 24-step scenario changes | Edited | M58 ($0.85^{24}\approx0.02$). |
| R1-M4 (X) single configuration | Edited | DS04. |
| R1-M4 (E) compare the SHP anchor's $\hat\phi$ and lag one with matching targets | Open | Requires anchor and tier outputs. |
| R1-M4 (S) calibrate $\rho$ to SHP | Open | Successor analysis; not planned in the text. |
| R1-M5 (T) pre-commit B and D side by side whenever tier 2 is complete and valid | Edited | M79 (Methods, Inventory); DS02; abstract; conclusion placeholder. |
| R1-M5 (X), (E) | Edited (X); Open (E) | X: M43, DS02. E: tier-2 outputs pending. |
| R1-M6 (T) qualify "no exposure observed" | Edited | M03 ("Apart from household co-residence"); M56; IN02. Support: SHP User Guide §2.3 (`voorpostel2025shp`). |
| R1-M6 (X), (S) | Edited (X, naming the future work); Open (S) | M56, DS04. The household-coupled generator is named as future work, not as planned. |
| R1-M7 (T) bound applies to population quantities and is likely loose | Edited | R55, IP09, ODD08. The claim no longer rests on the missing Methods sentence (F7). |
| R1-M7 (X) | Edited | Same sentences. |

### Referee 2, major concerns

| Item | Status | Where / reason |
| --- | --- | --- |
| R2-M1 (T) estimand as "detectability at a known signal share" (the report's "known response reliability", renamed per R2 minor 2) | Edited | M65, R62, IN01; abstract ("known to both arms"); title. |
| R2-M1 (X) | Edited | DS03. Trait–state–error literature added: R60–R61, M65. |
| R2-M1 (S) free-$r$ B null | Open | Named in DS10. See Q1. |
| R2-M2 (T) remove single-panel wording; population-moment target | Edited | M66, IN02, DS03, abstract. The introduction's motivation paragraphs 1–3 were kept. IN02 now says the boundary is not single-panel power. |
| R2-M2 (X) | Edited | DS03. |
| R2-M2 (S) single-panel parametric bootstrap | Open | Named in DS10. See Q1. |
| R2-M3 (T) normal-theory translation of 0.60/0.70/0.80 | Edited | M70 and Table `tab:auc-translation` in `methods.tex`: δ = 0.36/0.74/1.19; one-sided single-panel power = 0.10/0.18/0.32. Labelled as a translation under stated assumptions. The report's 0.33 for AUC 0.80 is 0.325 when computed and is printed as 0.32. |
| R2-M3 (E) re-express released AUCs | Open | Requires released curves. |
| R2-M3 (X) scores not guaranteed normal | Edited | M70 and the table caption. |
| R2-M4 (T) discuss the 2004 refreshment wave | Edited | DS05 (`voorpostel2025shp` §2.1: SHP_II added in 2004). The same paragraph states the anchor–simulation differences, including the trait bias with a worked Heise example. |
| R2-M4 (S) crosswalk; STARTS successor to the SHP prereg | Open | The crosswalk is named in DS10. The SHP-prereg successor must be registered before the anchor value is seen. See Q2. |
| R2-M5 (X) stationary, MCAR, correctly specified arms | Edited | DS03. |
| R2-M5 (S) misspecification stress test | Open | Named in DS10. See Q1. |
| R2-M6 (T) implemented studentization, G1b zero-nuisance scope, 95.17% ± 0.39 pp, bias outside the variance | Edited | Studentization: M28–M30, with the 2.1× plug-in sensitivity in M30. G1b scope: M76. Calibration: M77 (AMD lines 405, 409–412). Bias outside $V_{\mathrm{nuis}}$: M69. Also DS06. |
| R2-M6 (E) frozen diagnostics (max-$t$ exceedance, covariance-Jacobian flags, FD medians, projected fraction, G2 `mean_shift`) | Open | Require gate and tier outputs. |
| R2-M6 (X) | Edited | DS06. |
| R2-M7 (T) shape-in-$r$ statements descriptive | Edited | M73, DS01. |
| R2-M7 (S) 81-cell band | Open | Would be post hoc; not planned. |
| R2-M8 (T) chance and clock invalidation | Edited | Clock: M46. Chance: M75 (≤ about 0.0056 per unit; up to about 4.9% over nine units; author computation). Supplement main-curve rule aligned. DS06. |
| R2-M9 (T) estimand depends on the procedure and is conditional on success | Edited | M69, M65. |
| R2-M9 (E) retry and gap rates per cell | Open | Requires fit records. |

### Minor concerns

| Item | Status | Where / reason |
| --- | --- | --- |
| R1 minor 1 (T) off-topic background | Edited | `background.tex`: C08–C15 and A03 (voter, Sznajd, $q$-voter), C20, C21, C24, C25–C30 and A05 (macro outcomes) removed. C42–C46 and A08 removed as duplicates of the Introduction and Related work. |
| R1 minor 2 (T) systematic map in the supplement | Edited | `supplement.tex`: the three `\input` lines removed; the files `sections/systematic-map*.tex` are unchanged. |
| R1 minor 3 (T) frozen v1 interpretation regions | Edited | M71, DS01. |
| R1 minor 4 (T/X) coarse grid; $a^*$ as grid indices | Edited | M72 (v1 precision planning 43.9%/19.2%, labelled "not a power statement"). |
| R1 minor 5 (T) reading of $\omega=1$ units | Edited | M58. |
| R1 minor 6 (T) one term for the mechanism | Edited | **Partner drift** is used throughout: `main.tex` title and abstract, IN01 (defined), M01, M04, M60–M64, A01, R45, R58, R59, ODD02, ODD08, ODD15, DS02, conclusion. "Interaction arm" remains the name of the arm. "Influence" remains only where other literature is described. |
| R1 minor 7 (T/X) late tiers; do not promise controls | Edited | IN03 (promise removed); M80 (256 h vs 726 h projection). |
| R1 minor 8 (T) title | Edited | New working title in `main.tex`. See Owner decision Q3. |
| R2 minor 1 (T) features ignore ordinal structure | Edited | M67. |
| R2 minor 2 (T) $r$ as the signal share of the continuous response channel | Edited | Keywords ("measurement error"); abstract; IN01; M06, M12, M34, M45, M53; A07; R30, R46, R58; ODD02, ODD06, ODD36, ODD37; supplement; results subsection title; heatmap placeholder. "Reliability" is kept for survey estimates and the SHP anchor. |
| R2 minor 3 (T) conditioning is not a panel-conditioning model | Edited | M59 (`kraemer2025`; v1 lines 116–119). |
| R2 minor 4 (X) Wald standard errors of the anchor | Edited | DS05. |
| R2 minor 5 (T/X) sharp waste guard | Edited | M78 (inference docking component 7: about 0.445 with one gap in 54 fits). |
| R2 minor 6 (T) trait–state–error literature | Edited | R60–R61 (`kenny1995tse`, `kenny2001starts`, `cole2005tso`, `ludtke2018starts`); R40 (`hamaker2015critique`); M65; DS03. All five Crossref records were confirmed on 2026-09-28, so none is listed as unresolved. The full texts were not read. Sentences stay at title or recorded-abstract level; see Q7. |
| R2 minor 7 (E) tie rate with the AUC | Open | Requires gate and tier outputs. ODD14 and ODD34 already say the tie rate is recorded. |

### Factual inconsistencies

| Item | Status | Where / reason |
| --- | --- | --- |
| F1 stop-rule threshold 0.95 in the supplement | Already fixed | Commit `5d6a608a`. `supplement.tex` "Gate accounting and execution" reads "below 0.80 stops before G2". Confirmed. |
| F2 supplement calls the amendment a draft | Already fixed | Commit `5d6a608a`. "Protocol provenance and exposure" says the amendment was frozen at `37513841`. Confirmed. |
| F3 docking "in progress" | Edited | VER05 retired; VER06–VER14 in `verification.tex`; ledger updated. |
| F4 partial-$R^2$ diagnostic claimed | Edited | `supplement.tex` sentence removed; M68. |
| F5 shards on other hosts | Edited | M44 (single machine), M82 (the delta decision prevails over the amendment and SPEC wording), ODD37, AV09. |
| F6 model identities inconsistent | Edited in part; Owner decision | Removing the systematic-map sections from the supplement removes the manuscript-internal inconsistency. M54–M55 now also cover the docking implementations and this integration. Exact model identifiers per role were not written. See Q4. |
| F7 R21 cites a missing sentence | Edited | R01–R22 retired with a note on R21. The claim rests on R55 and ODD08. |
| F8 amendment bytes say "Sem congelamento v4" | Edited | M81. The contradiction inside the v4 README (`experiments/…/README.md` lines 3–5 against 153–155) is outside the folder this integration may edit. See Q5. |
| F9 exposure list incomplete | Edited, without values | M84 and `supplement.tex` "Protocol provenance and exposure" disclose the two post-freeze docking AUC cells, their sizes and the timing probe. The AUC values are not printed, because the integration rule forbids AUC values while the gate runs. See Q6. |
| F10 platform dependence | Edited | VER14; AV04–AV06. |
| F11 preflight cannot pass on this branch | Edited | AV05, AV10 (nine post-freeze Python files, confirmed by `git diff --stat 37513841 HEAD -- src tests`); ODD38 row corrected. |
| F12 stop point of the waste guard | Edited | M40. |
| F13 calibration target stated as met | Edited | M77, DS06. |
| F14 v1 gate language in the Introduction | Edited | IN03 (six-stage hash-bound gate). |
| F15 ledger paths that do not resolve | Edited | `claim-evidence.md`: the "Successor v4 manuscript claims" intro and V21 now point to files in this repository. |
| F16 strict or inclusive crossing | Edited | M74 (inclusive inversion governs the reported boundaries; "crossing" in claims is reserved for a lower band above 0.70). See Q8. |
| F17 tier-1 incompleteness | Edited | M46; `supplement.tex` band paragraph. |
| F18 G2 substitution wording | Edited | ODD35 sentence and ledger row: the amendment and the code prevail over SPEC D7. |
| F19 scope of the supplement | Edited | As R1 minor 2. |

### Ten ranked changes

| Rank | Status | Where / reason |
| --- | --- | --- |
| 1 Reframe what is identified (T) | Edited | Mean-field argument M60–M64; linear control M63; generator M04, M57; retitle and abstract; B-and-D headline M79, DS02. |
| 2 Oracle assumptions and translation (T + E) | T edited; E open | T: M65, M66, M69, M70 and the table. E (re-expressing released AUCs) needs outputs. |
| 3 SHP crosswalk (S) | Open | Not run; named in DS10; see Q1, Q2. |
| 4 Mean-field twin null (S) | Open | Not run; named in DS10; see Q1. |
| 5 Make $a$ interpretable (S + T) | T edited; S open | T: supplement sentence removed, M68. S: named in DS10. |
| 6 Pre-write every risk-register branch (T) | Open | Not in this task's list of ranked changes (1, 2, 7, 8, 9, 10). Several branches are now pre-committed in the text: rows 2 (M46, M75), 7 (M73), 10 (M79, DS02), 12 (M58) and 16 (ODD34). Figures A/B and Table U from synthetic fixtures are not produced. |
| 7 Factual-consistency sweep (T) | Edited | F1–F19 above. The docking Part C AUCs are disclosed without values (Q6). |
| 8 Inference disclosure (T; E diagnostics) | T edited; E open | M28–M30, M69, M73, M75–M77, DS06. |
| 9 Cut and re-aim the literature (T) | Edited | Background cuts; systematic map removed; trait–state–error literature added. Positioning against Moor-Smith–Carpentras (R27–R30), Mulder and Dang–Ma (R38–R39, R44–R46) and Ureña-Carrion (R49–R51) comes from the draft. |
| 10 Reproducibility and accountability (T + X) | Edited | Frozen tree as the confirmatory code, released separately from the report code (AV02, AV10); macOS-only bitwise claim (AV05); Linux failures (AV06, VER14); failed host equivalence (AV07–AV08); no ratification record found (M83, M51). See Q9. |

### Pre-results risk register

The register is not a list of text fixes. Its rows are mapped only where this integration pre-committed text:

- row 2: M46, M75, DS06;
- row 3: DS01;
- row 4: M69, M72;
- row 5: M24;
- row 6: M25, DS01;
- row 7: M73;
- row 8: M11–M13;
- row 9: M72;
- row 10: M79, DS02;
- row 12: M58, M80;
- row 13: DS05;
- row 16: ODD34;
- row 17: M53.

Rows 1, 11, 14 and 15 need result-dependent text. The decision in row 1 on where to submit a gate-failure paper is Q10.

## 4. Draft-ledger unresolved items

### `methods-v4-ledger.md`

| # | Item | Status | Where / reason |
| --- | --- | --- | --- |
| 1 | ODD reconciliation notes 1–12 not in the repository | Edited | `appendix-odd.tex` opening paragraph now points to Methods and the docking reports instead. Every rule was checked directly in the code (section 2). |
| 2 | Solver agreement 16/22 vs 17/22 | Edited in part; Owner decision | The text uses 16/22 and says the report is corrected in `RECONSTRUCTION.md` (VER10). The brief already says 16/22 (commit `72387f04`). A linked successor note to the immutable `validation/inference-docking-v4/REPORT.md` is outside this folder. See Q5. |
| 3 | Separation of family-limit cells in reports (M12) | Owner decision | See Q11. |
| 4 | "Sustained boundary covers reversals" (M24) | Owner decision | Kept, narrowed ("requires the estimate at every higher available strength"). See Q12. |
| 5 | Main-curve rule vs "any eligible r" (M46) | Edited; Owner decision | The text follows the code. See Q13. |
| 6 | Supplement stale on the stop rule and freeze status | Already fixed | Commit `5d6a608a` (F1, F2). |
| 7 | Overlap of Methods and ODD on band and seeds | Edited | Methods keeps the full band construction (M28–M30), because RR R2-M6 asks for it in Methods. ODD33 and ODD36 stay as the reimplementation reference. |
| 8 | AI-disclosure scope (M55) | Owner decision | See Q4. |
| 9 | No macOS test-run record | Edited | AV05 says "without a separate test-run record". No claim is made that the Linux failures pass on macOS. |
| 10 | Citations for TOST and Holm | Open | Not added: no key exists and none was verified. Optional before submission. |
| 11 | Keep `\label{sec:verification}` | Edited | Kept in `verification.tex`. Referenced from M30, M55 and the ODD opening paragraph. |

### `related-work-v4-ledger.md`

| # | Item | Status | Where / reason |
| --- | --- | --- | --- |
| 1 | Search record not recovered | Edited | Reconstructed on 28 Sep (dossier "Registro de execução"; `search-log.json`, commit `9abe9eb2`). R63, IP08 and the new supplement subsection say it was reconstructed and list its gaps. |
| 2 | Declaration commit `9ae16947` vs `987acded` | Edited | Resolved in the dossier (commit `6415a8bb`): `987acded` is the local reconstruction of sandbox commit `9ae16947`. The supplement says so. |
| 3 | Search date 27 vs 28 Sep | Edited | R56 separates the declaration (27 Sep) from the runs ("one session on 27–28 September"). The supplement gives the OpenAlex run times (28 Sep, 00:01–00:16 UTC). Semantic Scholar and arXiv run times were never recorded. |
| 4 | Carried-over works outside the dossier matrix | Open | Their CE rows (R02, R06, R11, R15–R17) were not re-read. The claims are unchanged from the verified 2026-09-25 ledger. |
| 5 | Keys that become uncited (`bollen2021`, `kustov2021`, `kim2024`) | Edited in part | `kim2024` is cited again (M56). `bollen2021` and `kustov2021` remain in `references.bib` but are uncited. Uncited entries are not printed; the background cuts also leave the keys of the removed sentences uncited. Removing them is left to the bibliography cleanup. |
| 6 | Introduction ¶3, Lersch supplement wave counts | Open | Unchanged. The claim rests on the earlier CE R01 and C43 reading of the supplement (Part B, pp. 45–49), which was not re-read. |
| 7 | Overlap with Background C42–C46 | Edited | C42–C46 and A08 removed from `background.tex`. |
| 8 | Human approval of the novelty wording | Owner decision | See Q14. |
| 9 | Ledger integration | Edited | R01–R22 retired; R23–R63 and IP01–IP09 added. |
| 10 | Not compiled | Open | See section 6. |

## 5. Open (S) and (E) items

Nothing was run or invented. The only text added for them is the single planning sentence DS10, which names six labelled exploratory analyses. Whether that sentence stays is Q1.

| Item | Class | Why it is open |
| --- | --- | --- |
| R1-M1 mean-field twin null; ranked 4 | S | Requires tier-1-scale compute on fresh seeds. |
| R1-M3 partial-$R^2$ map; ranked 5 | S | Requires a new diagnostic run. |
| R1-M4 SHP lag-profile comparison | E | Requires anchor and tier fit outputs. |
| R1-M4 calibration of $\rho$ | S | Successor analysis. |
| R1-M5 tier-2 outputs | E | Pending tiers. |
| R1-M6 household-coupled generator | S | Future work; named, not planned. |
| R2-M1 free-$r$ B null | S | New null family. |
| R2-M2 single-panel parametric bootstrap | S | New analysis. |
| R2-M3 re-expression of released AUCs; ranked 2 (E part) | E | Pending released curves. |
| R2-M4 crosswalk; STARTS successor to the SHP prereg; ranked 3 | S | New analysis; the prereg successor must be registered before the anchor is seen. |
| R2-M5 misspecification stress test | S | New analysis. |
| R2-M6 frozen diagnostics; ranked 8 (E part) | E | Pending gate and tier outputs. |
| R2-M7 81-cell band | S | Would be post hoc. |
| R2-M9 retry and gap rates | E | Pending fit records. |
| R2 minor 7 tie rate | E | Pending outputs. |
| Secondary 0.60 and 0.80 boundaries from released bands | E | Pending outputs. |

## 6. Owner decisions

- **Q1.** Should the manuscript commit to the six exploratory analyses named in DS10 (mean-field twin null, free-signal-share B null, single-panel parametric bootstrap, misspecification stress test, anchor-estimator crosswalk, partial-$R^2$ map)? Should any be dropped, or should the sentence be removed until each has a dated plan?
- **Q2.** Will a linked successor to the SHP reliability preregistration add a trait–state–error sensitivity before the anchor value is opened, or will any such analysis be declared post hoc?
- **Q3.** Is the new working title, "How much nominal partner drift separates opinion-panel trajectories from matched persistence at a known response signal share?", acceptable? Is "partner drift" the term the Owner wants for the mechanism?
- **Q4.** Which exact model identifiers should Methods list for each role, including design drafting, literature search, the two docking implementations, source checks, drafting and this integration? Do the authors approve extending the AI disclosure to the docking implementations and to integration editing (M55)? The model-docking `RECONSTRUCTION.md` and the inference-docking commit trailers record the model used for docking. The Codex model behind "GPT-6" is not recorded in the files read.
- **Q5.** Should linked successor notes be written outside this folder for three items? (a) The inference docking report's 17/22 count. (b) The contradiction inside the v4 README about the freeze. (c) The amendment's "Sem congelamento v4" line.
- **Q6.** Once the gate and tiers have finished, should the exposure disclosure print the two post-freeze docking AUC values? D8 requires cumulative disclosure. The integration rule forbade printing them now.
- **Q7.** The five trait–state–error references were cited at title or recorded-abstract level only. **Atualização 2026-09-29:** verificação e correções concluídas; Kenny–Zautra 1995 e Hamaker 2015 lidos integralmente. Kenny–Zautra 2001, Cole 2005 e Lüdtke 2018 ficaram inacessíveis pelas rotas verificadas; os dois últimos tiveram os resumos originais conferidos. R40 mantida; R60 cita apenas 1995; R61, M65, R62 e DS03 restringidas. A leitura integral das cinco obras permanece incompleta, sem impedir estas correções. Rotas, páginas/seções, vereditos e limite para o Owner em [q7-tse-full-text-check-2026-09-29.md](q7-tse-full-text-check-2026-09-29.md).
- **Q8.** Is the reading of F16 correct? Under it, the reported boundaries and intervals use the code's inclusive inversion, and the word "crossing" is reserved for a lower band strictly above 0.70 (M74).
- **Q9.** Will v1 and v4, and the delegated agent decisions, be ratified by a human before submission? If they are not, is the plain statement in M51 and M83 the wording to keep?
- **Q10.** If the gate fails, will a gate-failure methods paper still go to JCSS, or to JASSS or a methods note instead? (RR risk register row 1.)
- **Q11.** Should the separation of screened family-limit cells from solver and validation gaps be implemented in the results exporter, or only in the manuscript tables (M12)?
- **Q12.** Is it right that the sustained boundary carries any AUC reversal "whatever its source", including one that follows a solver hump (M24)?
- **Q13.** Is it intended that the main curve is invalidated by any tier-1 unit that is not complete valid, with no eligibility exemption, including a unit whose $a=0$ cell is infeasible (M46)? The amendment and DRD say "any eligible r".
- **Q14.** Does the Owner approve the bounded novelty wording (R58, R59, IP06–IP09)?

## 7. Checks

- **Markers.** A script over `main.tex` and all `sections/*.tex` found 237 `% ID` markers. Each has exactly one row in `claim-evidence.md`, and no retired row is still marked. The `systematic-map*.tex` files carry no markers.
- **Citations.** All 55 distinct `\cite` keys in the manuscript sources exist in `references.bib`. The bibliography has no duplicate key or DOI.
- **Balance.** Braces, `\begin`/`\end` environments, `$` delimiters and `\bigl`/`\bigr` pairs balance in every `.tex` file under `sections/` and `generated/` and in `main.tex`. Comments and escaped braces were excluded.
- **Abstract length.** 236 words, inside the JCSS range of 150–250. "ROC" is spelled out, because JCSS asks for no undefined abbreviations in the abstract. When the placeholders are replaced with results, the final abstract must stay within 250 words.
- **Compilation.** Not done. The Springer Nature class `sn-jnl.cls` and style `sn-mathphys-num.bst` are not in the repository, so the manuscript was not compiled, and `pipeline/paper_check.py` was not run on a PDF. The new table in `methods.tex` uses `\toprule`, `\midrule` and `\botrule`, which the Springer template provides. Check these on the first compile.
- **Frozen tree.** No file under `experiments/`, `src/`, `tests/`, `validation/` or `research/` was changed.

## 8. Coordinator decisions under delegation (2026-09-28)

The coordinating agent took these decisions under Davi's operational delegation. Scientific acceptance stays with the Research Owner.

- **Q1.** DS10 now names only the three analyses that were actually declared before any confirmatory result:
  - the mean-field twin and the drift R² map, declared in `experiments/exploratory/detection-boundary-v4-exploratory/` (commit `12ef78f1`);
  - the anchor-estimator crosswalk, declared in SHP successor 1 (commit `fd37e701`).

  The free-signal-share B null, the single-panel bootstrap and the misspecification stress test are stated as limitations, not planned.
- **Q2.** Yes. SHP preregistration successor 1 was registered on 2026-09-28 with the restricted directory empty. It adds the STARTS sensitivity, the synthetic crosswalk and the 2004-wave description. ODD39 now states this, and the successor's freeze record follows code review.
- **Q3.** The new title is kept as a working title. The final title is for the Owner.
- **Q4.** Open. The exact model identifiers per role will be compiled from the decision logs before submission.
- **Q5.**
  - (a) No further note is needed. `validation/inference-docking-v4/RECONSTRUCTION.md` already records 16/22 next to the report.
  - (b) and (c) A successor note on the v4 freeze status is to be added outside this folder. The bound amendment bytes stay unchanged.
- **Q6.** The two post-freeze docking AUC means are now printed in the supplement's exposure paragraph, labelled as reduced-size verification outputs. D8 asks for cumulative disclosure, and the values were already public in `validation/docking-v4/REPORT.md`.
- **Q7.** Deferred on 2026-09-28. **Atualização 2026-09-29:** o pedido posterior do Owner foi executado; ver resultado e limite de acesso na entrada Q7 acima e na [nota de verificação](q7-tse-full-text-check-2026-09-29.md). A busca não autoriza declarar os cinco textos integralmente verificados.
- **Q8.** Yes. Reported boundaries use the code's inclusive inversion, and "crossing" is reserved for a lower band strictly above 0.70. This describes the implemented rule.
- **Q9.** For the Owner.
- **Q10.** Deferred until a gate outcome exists. JASSS or a methods note would be the realistic venue for a gate-failure paper.
- **Q11.** The separation goes into the results exporter and tables, not only into manuscript prose. The report-module review of 2026-09-28 (defect 6) will implement it.
- **Q12.** Yes. The sustained boundary is defined on the AUC-by-strength curve regardless of what causes a reversal, so it covers reversals that follow a solver hump.
- **Q13.** Yes, as implemented. The frozen `_close_inventory` has no eligibility exemption, and the text describes the code. The difference from the amendment's "any eligible r" wording is recorded as a deviation.
- **Q14.** For the Owner.

## 9. Claim-audit fixes (2026-09-28)

Source: `pipeline/review/claim-audit-2026-09-28.md` (cited as **CA**), written at HEAD `32737380`. The fixes were applied on `integration/ic-20260928` at `dc61b5ca`, after the merges that brought in the X1/X2 declaration and SHP successor 1. The v4 gate and tiers were still running. No gate outcome, AUC estimate of the estimand, boundary, $a^*(r)$ value or SHP anchor value was written. The frozen tree and every file outside this manuscript folder were left unchanged, and `pipeline/drafts/` was not touched.

**Rule followed.** Before each replacement, the cited evidence was opened at the stated lines: code under `src/ic_study/` and `experiments/exploratory/detection-boundary-v4/`, the V1, AMD, SPEC, DRD, COV and SHP files, the validation reports, the dossier and `search-log.json`. Where the evidence supports different wording from CA's suggestion, the evidence wording was used. Each difference is listed in 9.2 under "Deviation" and in the ledger row. The model code was not executed. The mean-field numbers were recomputed in pure Python.

### 9.1 What the audit counts

- CA's summary gives 51 O and 21 U rows (19 U-l, 2 U-n). Its tables list all 21 U rows, but only 50 O rows. The summary counts 5 O rows for the Introduction, and the table lists 4 (IP01, IP03, IP06, IN02). No fifth row is named. The other Introduction rows (IP02, IP04, IP05, IP07–IP09, IN01, IN03) were re-read against their ledger evidence, and none needed a change. The discrepancy is recorded here, not guessed at.
- CA also lists three ledger-only count corrections (AV05, AV10, ODD38), twelve locator corrections on S rows (section 2.6), nine groups of X rows (section 3) and eleven unmarked-sentence notes (section 4). All are mapped below.

### 9.2 O and U findings

"Text" means the manuscript sentence changed; "Ledger" means only `claim-evidence.md` changed. Every changed sentence keeps its marker, and every changed row records the change.

| Finding | Class | Action | Deviation from CA's suggestion |
| --- | --- | --- | --- |
| M04 | O | Text: "eight directed partner slots … self-loops and repeated partners are possible though rare". Ledger: V1:150-151; "rare" computed (about 8 self-loops per panel; about 0.26% of people with a repeated partner). | None. |
| M05 | U-l | Ledger locators added. | None. |
| M07 | U-l | Ledger locators added. | V1 lines 44-45 and 246-249, not 43-44 and 245-249 (actual line numbers). |
| M12 | O | Text: "will be reported separately". | None. |
| M15 | U-l | Ledger: V1 lines 73-75 for the second sentence. | SPEC D2 line 35 kept only for the shared-seed condition; it does not state the non-identifiability point. |
| M18 | O | Text and ledger as CA. | Ledger also cites DB4:240-243 (the Jacobian probes go through the counted `at`). |
| M19 | O | Text as CA. | None. |
| M20 (l. 86) | O | Text as CA. | None. |
| M20 (l. 88) | O | Text as CA. | None. |
| M21 | U-l | Ledger: supplement line 13. | None. |
| M22 | O | Text as CA. | None. |
| M30 | O | Text as CA; ledger adds DB:349-354. | None. |
| M31 | U-l | Ledger: V1 lines 295-305. | None. |
| M36 | U-l | Ledger: SPEC line 106; AMD lines 294, 307-310. | None. |
| M40 | U-l | Ledger: AMD 390-394; SPEC 113-114; `run_gate.py:61-66`. | None. |
| M41 | U-l | Ledger: SPEC 108-109. | None. |
| M49 | O | Text as CA; ledger locators widened. | None. |
| M50 | U-l | Ledger: AMD line 113 and the solver, inference and gate sections. | Sections named by their AMD headings, not by D numbers alone. |
| M52 | U-l | Ledger: V1 lines 32-34; SPEC D8 lines 169-174. | None. |
| M54 | U-n | Text: lists only roles recorded in repository files; the ledger gives the file or commit for each; "The complete list of the models used in each role is pending." Q4 stays open. | CA's bracketed GPT-6 roles were dropped, because no file records them. Roles CA did not list but files record were added: novelty review and memo critique, amendment proposals and cross-critiques with Codex (ratification list line 7), the positioning search and dossier (`dossier.md` line 3), and the ledger audit (`cc28df93` trailer). No model identifiers are printed. |
| M61 | O | Text rewritten (section 9.3). | CA's sentence ("pull a person toward them, but … nearly cancels") replaced by the decomposition, the sign and monotonicity statement and the $b=0$ contrast. |
| M62 | O | Text: "odd, nonlinear function …, close to zero near the centre and growing in the tails"; "S-shaped" dropped. | CA's "close to linear near the centre" not used: $m(0.5)=0.0128$ against a tangent value of about 0.0008, so "close to zero" is what the numbers support. "After rank transport it is a nonlinear, state-dependent persistence process" kept as the valid core. |
| M63 | O | Text as CA. | None. |
| M66 | U-l | Ledger: SPEC lines 15, 64; DV4:322. | None. |
| M67 | O | Text as CA. | None. |
| M69 | O | Text as CA. | None. |
| M82 | O | Text rewritten from SPEC D9, AMD 260-261, 325, 522-524, DRD item 4 and FRZ. | CA's "the later review decision … prevails" not used: the amendment and the delta decision agree on eight local shards, so the sentence states what each document says. |
| M83 | O | Text as CA. | None. |
| VER02 | O | Text as CA. | None. |
| VER03 | O | Text as CA. | None. |
| VER04 | O | Text as CA, plus the measured G0 gap rate. | `allocation_preflight` also checks `g0_gap_binding` (lines 747-749), which CA omitted. |
| VER06 | U-l | Ledger: original commits do not resolve; reconstructed commits listed. | None. |
| VER09 | O | Text: IDA A26 appended. | None. |
| VER10 | U-l | Ledger: `RECONSTRUCTION.md` lines 36-40. | None. |
| VER14 | O | Text as CA. | None. |
| AV01 | O | Text rewritten (section 9.5). | CA's wording kept the anchor's estimation abstract. The text now says who computes it, where, and what leaves, and uses "is to be computed", because no microdata had been accessed. |
| AV08 | U-l | Ledger: HE lines 8 and 11. | None. |
| ODD01 | U-n | Text: hash replaced (section 9.8). | None. |
| ODD02 | O | Text as CA. | None. |
| ODD03 | O | Text as CA. | None. |
| ODD10 | O | Text as CA. | None. |
| ODD14 | O | Text as CA. | None. |
| ODD15 | O | Text as CA. | None. |
| ODD21 | O | Text as CA. | None. |
| ODD27 | O | Text as CA. | None. |
| ODD38 | O | Text as CA, with G0 matching diagnostics named. | "Statuses, counts, criteria values" extended with "the per-fit matching diagnostics of G0", which `run_gate.py` prints (`fit_record`, `v4_gate.py:198-220`). |
| ODD39 | U-l | Text: "declared before any SHP microdata were accessed and not yet bound by its own freeze record". Ledger: cited by path. | CA's "committed … and not yet frozen" became "declared …", the file's own status (`declared-before-microdata-access`). CA's branch-and-commit note was not used; the files are now in this branch. |
| R24 | O | Text as CA. | None. |
| R26 | U-l | Ledger: CE "Frozen-design" row and recheck note; focused report line 111; "retweet exposures" marked external, check not recorded. | None. |
| R29 | O | Text as CA. | None. |
| R31 | O | Text as CA. | None. |
| R32 | O | Text as CA. | None. |
| R37 | U-l and O | Text and ledger as CA. | None. |
| R38 | O | Text as CA. | None. |
| R40 | O | Text as CA. | None. |
| R42 | U-l | Ledger as CA. | None. |
| R45 | O | Text as CA. | None. |
| R56 | O | Text (section 9.7). | CA's wording extended with the HTTP 406 cause, as the task requires. |
| R57 | O | Text as CA. | None. |
| R59 | O | Text as CA. | None. |
| R60 | O | Text as CA's first option. | None. |
| R62 | O | Text as CA. | None. |
| R63 | O | Text and ledger as CA. | Recount confirmed from `search-log.json` (200/200 OpenAlex hits and 24/160 S2 hits without DOI; 100 truncated and 60 placeholder S2 ids). |
| IP01 | O | Text as CA. | None. |
| IP03 | O | Text as CA. | None. |
| IP06 | O | Text as CA. | None. |
| IN02 | O | Text as CA. | None. |
| DS01 | O | Text as CA. | None. |
| DS03 (a), (b) | O | Text as CA. | None. |
| DS06 | O | Text as CA. | None. |
| DS10 | U-l | Ledger: the four declaration files cited by path; branch and commit names removed. | CA's pointer-status note is obsolete, because the files are merged. |
| C40 | O | Text: "polychoric" removed. Ledger: the 0.6634/0.6764 conflict recorded as unresolved (external). | None. |

**Ledger-only count corrections.** AV05, AV10 and ODD38 no longer say "nine" or "six … three". They cite `git diff --name-status 37513841 HEAD -- src tests` and give its count at `dc61b5ca`: eleven files, seven `analysis/` modules and four tests. The manuscript text states no number, so it stays true.

**Related-work header.** The header comment of `related-work.tex` now says "R23--R63".

### 9.3 Mean-field argument (M60–M64, DS02, abstract)

With $Z\sim N(0,1)$, $D=Z-z$ and $f(g)=g$ for $\lvert g\rvert\le1$ and $-0.25g$ otherwise:

- $m(z)=\mathbb E[D\,1\{\lvert D\rvert\le1\}]-0.25\,\mathbb E[D\,1\{\lvert D\rvert>1\}]=1.25\,\mathbb E[D\,1\{\lvert D\rvert\le1\}]+0.25z$.
- $\mathbb E[D\,1\{\lvert D\rvert\le1\}]=-z[\Phi(1+z)-\Phi(z-1)]+\varphi(z-1)-\varphi(z+1)$, which is negative for $z>0$. This is the pull toward the centre.
- Values from quadrature and from the closed form: $m(0.5)=0.0128$, $m(1)=0.0846$, $m(2)=0.4037$.
- $m$ is strictly increasing on a 100,000-point grid in $(0,8]$ and tends to $0.25z$ beyond it. It is odd by symmetry.
- At $b=0$, $m(1)=-0.132$.

These match CA. The Methods passage now shows the decomposition. It says that at $b=0.25$ the conditional drift mean pushes a person away from the population centre, more strongly in the tails, and that only the $b=0$ sensitivity pulls toward the centre. "S-shaped" is gone.

V1 lines 147-188, AMD D2 and the kernel and transport code were searched for any statement of what the outward push does under the per-step rank transport. None exists, so the text states only the sign and monotonicity.

The valid core is kept: to first order, partner drift is an own-state function plus partner-sampling noise, and after rank transport the arm is a nonlinear, state-dependent persistence process.

The abstract, M64 and DS02 now say the same thing. The abstract adds "that pushes people away from the centre, more strongly in the tails".

### 9.4 Pointers

- DS10 and ODD39 now cite, by path only, `experiments/exploratory/detection-boundary-v4-exploratory/README.md` and `declaration.json`, and `research/questions/exploration/2026-09-24-parallel/shp-reliability-successor-1.md` and `.json`. All four files are in this branch.
- Section 8 above names the commits `12ef78f1` and `fd37e701`. Both are now reachable from this branch through the merges `dc61b5ca` and `7a9ea26e`. Section 8 was left as written.
- The Q2 entry in section 8 says the successor "was registered". Its own freeze record is still future (successor line 55), so ODD39 now says "declared".
- VER06's ledger row no longer cites the unreachable original phase commits as evidence.

### 9.5 Microdata statement (AV01, ODD16, ODD17, ODD39)

- AV01 now says that the simulation uses no survey microdata. It also says that the secondary SHP reliability anchor is to be computed locally by the Research Owner, from licensed microdata that the licence does not allow to be redistributed.
- Only aggregate estimates, standard errors, fit statistics and counts leave the restricted environment.
- Evidence: SHP preregistration lines 3, 16-18, 88-91 and 119; `shp-reliability-guide.md` lines 1-13; successor 1 line 51.
- ODD16 now states the same thing. ODD17 already describes the anchor as preregistered, with its value pending, and needed no change. ODD39 says "declared".
- Whether the redistribution wording matches the contract text is for the Owner to confirm.

### 9.6 AI disclosure (M54)

The roles and their records are in the M54 ledger row. The text says that the complete list of the models used in each role is pending. **Q4 stays open.**

### 9.7 Positioning search (R56, supplement)

- R56 now says that the queries ran without rewording on OpenAlex and Semantic Scholar. On arXiv they ran as the pre-declared Boolean translations through the arXiv site search, because the arXiv export API returned HTTP 406. The source is dossier "Condições de execução", lines 470-475, and the notes in `search-log.json`.
- The supplement's paragraph now says the same, and adds that the site search is the closest available substitute, not the declared API route.
- The supplement's DOI clause was corrected to the recount: 200/200 OpenAlex hits and 24/160 Semantic Scholar hits lack a DOI.

### 9.8 ODD01

The printed code-closure hash is now `db9d6ead b5019d69 1a8c7370 3d511d03 37dc4983 4bb219d1 68a27693 df0e0acd`. Joined, the eight blocks equal `code_sha256` in `experiments/exploratory/detection-boundary-v4/freeze-v4.json` (line 93), both at HEAD and at `37513841`. This was checked by script before writing. The freeze record's own SHA-256 was also recomputed and is still `99c4277235d4…0837`.

### 9.9 Locator corrections on S rows (CA 2.6)

All twelve were applied in the ledger: M27, M37, M39, M44, M45, M51, M55, M59, M65, M84, R61 and DS05. Each was checked at the cited line first. The M84 note "Values deliberately not printed" was replaced, because the supplement prints the two docking means after Q6.

### 9.10 X rows (CA 3)

- The ledger now has a "Check provenance of the external rows" note under the background table.
- Rows with a recorded check now carry how and when:
  - `manski1993` and `shalizi2011`: abstracts read 2026-09-24 (`reliability-and-prior-art.md` lines 236-241).
  - Kenny–Zautra 1995: abstract read 2026-09-24 (lines 218-223).
  - R26: locators checked 2026-09-25.
- Everything else is marked *external, check not recorded*:
  - the reading level and checker of C01–C07, C16–C19, C22, C23 and C31–C41;
  - the Hamaker and Lüdtke content;
  - "retweet exposures";
  - the private adversarial report;
  - the per-role model logs.
- M03, M56 and DS04 were already recorded.

### 9.11 Unmarked factual sentences (CA 4)

| Item | Status |
| --- | --- |
| Abstract without markers | **Open.** A `%` marker would comment out the rest of the one-line `\abstract{…}` argument. Splitting the abstract into marked lines, or adding an "Abstract" ledger row, is left to the next integration. The abstract's mean-field clause now rests on M61–M62. |
| Methods display equations (M23) | Edited: `% M23` added after `\end{align}`. |
| Table `tab:auc-translation` (M70) | Edited: `% M70` added after `\end{table}`. |
| Introduction ¶1–3 (Flache; Heise, Wiley–Wiley, Achen; Kiley–Vaisey; Lersch supplement) | **Open.** No marker or row added. The Achen wording differs from C37, and the Lersch supplement claim rests on retired rows (section 4, item 6). |
| Conclusion and `results.tex` line 2 | **Open.** Covered only by V18. |
| Supplement: no markers | **Open** for markers. The two problematic sentences were fixed: line 7 now reads "raises an error and is not assigned a variance share", checked against DP:41-42 (`ValueError`) and the absence of a gap handler. The line-39 arXiv sentence was fixed (9.7). |
| ODD opening paragraph and Submodels introduction | **Open.** No rows added. |
| ODD Submodel 13, second paragraph | No action; audited as part of ODD33 (S). |

### 9.12 Recount and checks

- **Markers.**
  - A script over `main.tex`, `sections/*.tex` and `generated/*.tex` finds **238 distinct `% ID` markers** in 335 occurrences. At `dc61b5ca` there were 328 occurrences.
  - The seven new occurrences are M54 ×2, M61 ×2, M23, M70 and AV01, and all reuse existing IDs.
  - By group: M 84, ODD 39, R 41, C 24, VER 13, AV 10, DS 10, IP 9, A 5, IN 3.
  - Every ID has exactly one row in `claim-evidence.md`, and no retired row is marked.
  - Section 7's count of 237 was one short, as CA noted.
- **Citations.** 55 distinct `\cite` keys, all present in `references.bib`. No duplicate keys. No key was added or removed.
- **Balance.** Braces, `\begin`/`\end`, inline `$` and `\bigl`/`\bigr` balance in all 19 `.tex` files under `sections/` and `generated/` and in `main.tex`. Comments and escaped characters were excluded.
- **Abstract length.** 248 whitespace-separated tokens, placeholders and inline math included (224 without the two bracketed placeholders). This is within the JCSS limit of 250. The `main.tex` comment was updated. Replacing the placeholders with results must keep the total at or below 250, which now leaves little room.
- **Compilation.** Not done, for the reason in section 7. `pipeline/paper_check.py` was not run.
- **Scope.** Only `main.tex`, `claim-evidence.md`, `sections/{appendix-odd,background,discussion,introduction,methods,related-work,supplement,verification}.tex` and this log were changed.
