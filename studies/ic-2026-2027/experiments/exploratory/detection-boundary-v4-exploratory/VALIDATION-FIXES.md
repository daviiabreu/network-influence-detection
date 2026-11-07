# Validação das correções na árvore solicitada

A revalidação atual está na seção final **Revalidação cética de 29/09/2026**: 372 testes focados passaram; as nove provas vermelho→verde usam o namespace vivo dos módulos. O registro anterior abaixo foi preservado.

A barreira do item 6 validada aqui, com recibos entre hosts, foi substituída no commit seguinte pela ordem registrada fixa em cada worker, sem barreira, e a agregação passou a aceitar a união de diretórios de hosts diferentes. O motivo e os testes estão em [IMPLEMENTATION-FIXES.md](IMPLEMENTATION-FIXES.md), seção "Ordem e barreiras de execução".

Diretório: `/Users/davi/Documents/github/worktrees/research-workbench/codex/x3x7-fixes`.

O código e os testes descritos aqui estão nesta árvore. Nesta execução não houve operação de commit, push ou SSH. Os testes red/green foram executados novamente neste checkout, com importação confirmada dos seus próprios módulos. Os resultados anteriores em outro diretório não foram usados como prova de entrega aqui.

Os arquivos `.command.json`, `.log` e `.exit` em `/Users/davi/.local/state/research-workbench/x3x7-tree-validation/` registram diretório, comando, PYTHONPATH, limites de threads, saída e código de retorno de cada execução.

## Itens, arquivos e testes

### Item 4: Manifesto e proveniência antes da reutilização

Código: [v4_exploratory_x3x7.py:748](../../../src/ic_study/simulation/v4_exploratory_x3x7.py); [v4_exploratory_x3x7.py:981](../../../src/ic_study/simulation/v4_exploratory_x3x7.py); [v4_exploratory_x3x7.py:716](../../../src/ic_study/simulation/v4_exploratory_x3x7.py).

Testes:

- `test_runner_rejects_mislabelled_cell_or_job` — [test_v4_exploratory_x3x7.py:750](../../../tests/unit/test_v4_exploratory_x3x7.py).
- `test_resume_and_aggregate_reject_foreign_records` — [test_v4_exploratory_x3x7.py:615](../../../tests/unit/test_v4_exploratory_x3x7.py).
- `test_output_manifest_rejects_revision_change_before_resume` — [test_v4_exploratory_x3x7.py:636](../../../tests/unit/test_v4_exploratory_x3x7.py).
- `test_aggregate_rejects_omitted_provenance` — [test_v4_exploratory_x3x7.py:801](../../../tests/unit/test_v4_exploratory_x3x7.py).
- `test_verification_copy_is_atomic_and_accepts_a_concurrent_winner` — [test_v4_exploratory_x3x7.py:772](../../../tests/unit/test_v4_exploratory_x3x7.py).

Vermelho: 7 failed, 5 passed, 58 deselected in 2.79s — item4-red.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item4-red.log`).

Verde: 30 passed, 80 deselected in 26.78s — item4-green.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item4-green.log`).

Os cinco casos verdes antes da mudança protegiam a implementação parcial recebida. Os sete casos de identidade falharam por aceitar unidade errada. A seleção verde inclui 14 casos de compatibilidade histórica e a rejeição de um store X7 substituído.

### Item 2: Busca de intervalo após platô dentro das 12 avaliações

Código: [v4_exploratory_x3.py:256](../../../src/ic_study/simulation/v4_exploratory_x3.py).

Testes:

- `test_outer_solver_searches_beyond_an_initial_plateau` — [test_v4_exploratory_x3.py:640](../../../tests/unit/test_v4_exploratory_x3.py).
- `test_outer_solver_does_not_infer_no_root_from_equal_samples` — [test_v4_exploratory_x3.py:648](../../../tests/unit/test_v4_exploratory_x3.py).

Vermelho: 2 failed, 28 deselected in 0.13s — item2-red.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item2-red.log`).

Verde: 5 passed, 25 deselected in 0.12s — item2-green.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item2-green.log`).

### Item 3: Unidades completas, mínimo de 100 e sensibilidade nas leituras de X6

Código: [v4_exploratory_x6.py:948](../../../src/ic_study/simulation/v4_exploratory_x6.py); [v4_exploratory_x6.py:625](../../../src/ic_study/simulation/v4_exploratory_x6.py); [v4_exploratory_x6.py:807](../../../src/ic_study/simulation/v4_exploratory_x6.py); [v4_exploratory_x6.py:866](../../../src/ic_study/simulation/v4_exploratory_x6.py).

Testes:

- `test_x6a_pointwise_requires_complete_units` — [test_v4_exploratory_x6.py:566](../../../tests/unit/test_v4_exploratory_x6.py).
- `test_secondary_coverage_and_bias_require_one_hundred_completes` — [test_v4_exploratory_x6.py:579](../../../tests/unit/test_v4_exploratory_x6.py).
- `test_truth_precision_applies_to_secondary_pointwise_band_and_bias` — [test_v4_exploratory_x6.py:601](../../../tests/unit/test_v4_exploratory_x6.py).
- `test_truth_precision_includes_conservative_classification` — [test_v4_exploratory_x6.py:627](../../../tests/unit/test_v4_exploratory_x6.py).

Vermelho: 3 failed, 15 deselected in 0.20s — item3-red.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item3-red.log`).

Verde: 6 passed, 13 deselected in 28.31s — item3-green-fixed.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item3-green-fixed.log`).

Também reproduzi a mudança apenas da marca conservadora: item3-conservative-red.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item3-conservative-red.log`). A primeira repetição encontrou uma expectativa antiga sem esse novo diagnóstico; ajustei a expectativa e os seis testes passaram na seleção verde indicada.

### Item 5: Desfecho rico durável antes da finalização congelada

Código: [v4_exploratory_x7.py:429](../../../src/ic_study/simulation/v4_exploratory_x7.py); [v4_exploratory_x7.py:478](../../../src/ic_study/simulation/v4_exploratory_x7.py).

Testes:

- `test_rich_terminal_error_survives_interruption_and_resume` — [test_v4_exploratory_x7.py:388](../../../tests/unit/test_v4_exploratory_x7.py).

Vermelho: 2 failed, 40 deselected in 0.29s — item5-red.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item5-red.log`).

Verde: 2 passed, 40 deselected in 0.29s — item5-green.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item5-green.log`).

### Item 7: Supervisor operacional do corte de execução

Código: [v4_exploratory_x3x7.py:1170](../../../src/ic_study/simulation/v4_exploratory_x3x7.py).

Testes:

- `test_supervisor_stops_a_running_worker_and_preserves_checkpoints` — [test_v4_exploratory_x3x7.py:827](../../../tests/unit/test_v4_exploratory_x3x7.py).
- `test_supervisor_does_not_start_after_close` — [test_v4_exploratory_x3x7.py:855](../../../tests/unit/test_v4_exploratory_x3x7.py).
- `test_cli_enforces_the_exploratory_cutoff` — [test_v4_exploratory_x3x7.py:870](../../../tests/unit/test_v4_exploratory_x3x7.py).

Vermelho: 4 failed, 70 deselected in 0.31s — item7-red.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item7-red.log`).

Verde: 4 passed, 70 deselected in 0.57s — item7-green.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item7-green.log`).

### Item 6: Ordem fixa e barreira por host

Código: [run-x3x7-stages.sh:17](run-x3x7-stages.sh).

Testes:

- `test_launcher_waits_for_every_local_shard_before_the_next_stage` — [test_v4_exploratory_launcher.py:86](../../../tests/unit/test_v4_exploratory_launcher.py).
- `test_launcher_does_not_advance_after_worker_failure` — [test_v4_exploratory_launcher.py:106](../../../tests/unit/test_v4_exploratory_launcher.py).

Vermelho: 3 failed in 4.27s — item6-red.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item6-red.log`).

Verde: 3 passed in 3.83s — item6-green.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item6-green.log`).

### Item 8: Leitura de X4b condicionada à calibração

Código: [v4_exploratory_x4.py:545](../../../src/ic_study/simulation/v4_exploratory_x4.py).

Testes:

- `test_declared_readings_and_the_sealed_aggregate` — [test_v4_exploratory_x4.py:295](../../../tests/unit/test_v4_exploratory_x4.py).

Vermelho: 1 failed, 12 deselected in 8.21s — item8-red.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item8-red.log`).

Verde: 4 passed, 9 deselected in 30.88s — item8-green.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item8-green.log`).

### Item 9: Censura específica por regra em X7

Código: [v4_exploratory_x7.py:662](../../../src/ic_study/simulation/v4_exploratory_x7.py).

Testes:

- `test_first_crossing_rules_ignore_unrelated_censoring` — [test_v4_exploratory_x7.py:437](../../../tests/unit/test_v4_exploratory_x7.py).
- `test_delta_and_close_rules_do_not_require_boundary_intervals` — [test_v4_exploratory_x7.py:447](../../../tests/unit/test_v4_exploratory_x7.py).
- `test_interval_rule_uses_only_its_two_uncensored_quantities` — [test_v4_exploratory_x7.py:459](../../../tests/unit/test_v4_exploratory_x7.py).

Vermelho: 5 failed, 42 deselected in 0.14s — item9-red.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item9-red.log`).

Verde: 6 passed, 41 deselected in 0.06s — item9-green.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item9-green.log`).

## Compatibilidade X5/X7 de c8e4861f

O caminho explícito de compatibilidade fica nos agregadores e é automático somente para diretórios legados sem manifesto. Exige a revisão produtora c8e4861f e os hashes fixados em [compatibility-c8e4861f.json](compatibility-c8e4861f.json): lockfile, freeze, declaração e módulos produtores. Os oito hashes de módulos das duas análises, assim como os demais pins, foram conferidos contra os blobs históricos. Nenhum output real foi lido.

O diretório deve conter `<kind>-precondition.json` original, com digest correspondente aos registros. A validação confere tamanhos, identidades, classe de host e os campos individuais de igualdade, proveniência e erros; não confia apenas no antigo `passed`. X7 recusa desfecho rico desconhecido e confere os selos dos stores antes da leitura.

O agregado identifica `compatibility.mode = aggregate-only`, revisão produtora e código agregador. Não altera registros históricos, não permite retomá-los com o runner novo e não repete simulações. X7 continua exigindo liberação. Teste: `test_legacy_aggregate_accepts_only_pinned_complete_evidence` — [test_v4_exploratory_x3x7.py:653](../../../tests/unit/test_v4_exploratory_x3x7.py). Os 14 casos passaram na seleção do item 4.

## Gates

- Ruff check nos 14 arquivos Python alterados: passou — ruff.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/ruff.log`).
- Ruff format --check nos 14 arquivos: passou — format.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/format.log`).
- uv run --locked mypy src tests: passou em 102 arquivos — mypy.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/mypy.log`).
- Preservação do item 1: seis testes passaram — item1-preserved.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item1-preserved.log`).
- Utilidades reaproveitadas X1a/X2 e X1b: 26 testes focados passaram — item4-reused-utilities.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/item4-reused-utilities.log`).
- 80 fontes Python congelados: nenhuma divergência — frozen-source-integrity.log (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/frozen-source-integrity.log`).
- `bash -n` nos dois scripts e `git diff --check`: passaram.
- README e declaração continuam byte a byte iguais aos bytes registrados.

Cada pytest usou um único processo, sem xdist, taskpolicy ou nice, com OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1. Não executei a suíte completa nem pré-condições em tamanho declarado. Os testes usaram dados sintéticos temporários. Não li estatísticas seladas, `sealed-v4-*`, logs de tiers ou `restricted/`. Não acrescentei dependências.

## Decisões e pendências

- Sem monotonicidade registrada, amostras finitas do mesmo sinal não demonstram ausência de raiz. A busca termina como `budget`; `family-limit` exige demonstração no domínio degenerado.
- X6 usa unidades completas no denominador principal; lacunas contam como misses apenas na leitura secundária, sem aumentar a elegibilidade. Sensibilidade T_D1 ± 2 EP alcança também a marca conservadora e o viés; diagnósticos nominais ficam preservados.
- X4b mantém taxas e diferenças numéricas, mas suspende classificação e contagem de perda de poder sob calibração liberal ou ausente.
- A barreira é por host. Para prioridade global, o coordenador deve selecionar um `STAGES` por vez em todos os hosts e conferir recibos/cobertura de shards antes de avançar.
- Outputs de hosts distintos permanecem separados, com sua evidência original. A compatibilidade não legitima proveniência ausente.
- O supervisor cobre o CLI e retorna 124 no corte, preservando checkpoints e registrando incompletude operacional, sem falha científica. `--deadline-worker` é interno. Workers antigos já ativos precisam ter seu corte garantido pelo coordenador.
- Suíte completa, novas pré-condições por classe de host e aceitação dos outputs reais após liberação continuam com o coordenador. Nenhuma decisão de implementação ficou bloqueada.

A documentação da implementação está em [IMPLEMENTATION-FIXES.md](IMPLEMENTATION-FIXES.md).

A presença dos arquivos na árvore está registrada em git-status.txt (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/git-status.txt`); seus SHA-256 finais estão em tree-files.json (`/Users/davi/.local/state/research-workbench/x3x7-tree-validation/tree-files.json`).

## Revalidação cética de 29/09/2026

Esta seção registra a nova validação da árvore `research/v4-x3x7-fixes`, ainda
baseada em `67d7789c66436cd3a9436ce1ecd6bb496bcb3661`, sem commit. Ela atualiza
as conclusões operacionais da sessão anterior acima, especialmente a barreira
entre hosts e a precisão desconhecida da verdade em X6. O trabalho anterior
foi preservado; as mudanças adicionais estão nos itens 3, 4 (testes) e 6.

Os caminhos Python abaixo são relativos a `studies/ic-2026-2027/`: código em
`src/ic_study/simulation/`, testes em `tests/unit/`. Os scripts ficam nesta pasta.

| Item | Código atual | Teste de regressão | Conclusão e alteração nesta sessão | Vermelho → verde |
| --- | --- | --- | --- | --- |
| 1 | `v4_exploratory_x3x7.py:582` | `test_v4_exploratory_x3x7.py:589`, `test_verify_rejects_identical_stores_with_incompatible_evidence` | Preservado: `equal` final combina stores, proveniência, erros e execução; a expansão de `comparison` não o sobrescreve. Seis ataques independentes. | 6 falharam → 6 passaram |
| 2 | `v4_exploratory_x3.py:256` | `test_v4_exploratory_x3.py:640`, `test_outer_solver_searches_beyond_an_initial_plateau`; `:648`, `test_outer_solver_does_not_infer_no_root_from_equal_samples` | Preservado: sondagem de extremos e bisseção após secante degenerada, máximo de 12 avaliações; amostras finitas sem raiz encontrada encerram como `budget`. | 2 falharam → 2 passaram |
| 3 | `v4_exploratory_x6.py:811`, `:876`, `:962` | `test_v4_exploratory_x6.py:566`, `test_x6a_pointwise_requires_complete_units`; `:579`, `test_secondary_coverage_and_bias_require_one_hundred_completes`; `:601`, `test_truth_precision_applies_to_secondary_pointwise_band_and_bias`; `:627`, `test_truth_precision_includes_conservative_classification`; novos `:640`, `:656`, `:682` | Mantidos os denominadores por unidade completa, elegibilidade separada de 100 completos, sensibilidade D1 ± 2 EP nas secundárias, viés e conservadorismo. Corrigida leitura conclusiva quando EP da verdade não é estimável; médias ficam descritivas e EP desconhecido não vira zero no matching. Acrescentados limites 99/100, mistura de completos/lacuna/erro e um único pipeline de verdade em X6a/X6b. | 9 falharam → 9 passaram |
| 4 | `v4_exploratory_x3x7.py:748`, `:791` | `test_v4_exploratory_x3x7.py:615`, `test_resume_and_aggregate_reject_foreign_records`; compatibilidade `:667`, `test_legacy_aggregate_accepts_only_pinned_complete_evidence` | Preservados manifesto, identidade, hashes e verificações antes da reutilização. Reforçado teste histórico com sucesso efetivo de X5 e grupo X7 completo, além de ataques a host, sementes, declaração, resultados e erros. | 4 falharam → 4 passaram; compatibilidade 26 casos verdes no portão focado |
| 5 | `v4_exploratory_x7.py:429`, `:443`, `:478` | `test_v4_exploratory_x7.py:388`, `test_rich_terminal_error_survives_interruption_and_resume` | Preservado: desfecho rico durável antes do resultado congelado, recuperação do erro, reparação dos dois selos e nenhuma nova tentativa rica oportunista. | 2 falharam → 2 passaram |
| 6 | `run-x3x7-stages.sh:18`; `v4_exploratory_x3x7.py:922`, `:955` | `test_v4_exploratory_launcher.py:131`, `test_split_hosts_require_one_stage_and_global_receipts`; `:138`, `test_split_host_does_not_start_without_every_predecessor_shard`; `:147`, `test_split_host_runs_only_the_stage_after_the_global_barrier`; foundation `:991`, `:1022` | Corrigido o avanço entre hosts: split parcial exige estágio único, sem `ONLY`, e recibos de todos os shards de todos os predecessores. Publicação exige cada unidade contabilizada, válida e dentro do prazo; código de saída do worker sozinho não basta. | 9 falharam → 9 passaram no launcher; 9 casos de conteúdo dos recibos no portão focado |
| 7 | `v4_exploratory_x3x7.py:1233` | `test_v4_exploratory_x3x7.py:962`, `test_cli_enforces_the_exploratory_cutoff`; supervisor `:919`, `:947` | Preservado: deadline nos dois comandos CLI, interrupção do grupo, checkpoints preservados, retorno 124 e recibo de incompletude operacional sem falha científica. | 2 falharam → 2 passaram no CLI; os dois testes do supervisor também incluídos no portão focado |
| 8 | `v4_exploratory_x4.py:508` | `test_v4_exploratory_x4.py:295`, `test_declared_readings_and_the_sealed_aggregate` | Preservado: calibração liberal/ausente suspende interpretação e contagem de perda de poder, mantendo taxas; conservadorismo é limite inferior. | 3 falharam e 1 passou → 4 passaram |
| 9 | `v4_exploratory_x7.py:662` | `test_v4_exploratory_x7.py:437`, `test_first_crossing_rules_ignore_unrelated_censoring`; `:447`, `test_delta_and_close_rules_do_not_require_boundary_intervals`; `:459`, `test_interval_rule_uses_only_its_two_uncensored_quantities` | Preservado: censura é avaliada somente para as quantidades exigidas por cada regra; a fronteira sustentada não bloqueia primeira travessia válida. | 5 falharam → 5 passaram |

A prova válida usa um único processo Python que chama pytest serialmente, sem
xdist, com `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1`. As funções defeituosas são extraídas por AST da base
`67d7789c` e instaladas apenas em memória, com o namespace vivo do módulo para
preservar os mocks. O item 4 reintroduz o comportamento antigo de validar apenas
tamanhos, adaptado à assinatura atual; o item 6 fornece o launcher histórico à
fixture temporária. As funções atuais são restauradas antes do verde. Não há
reversão temporária de arquivos da árvore. O ensaio anterior do harness, com
namespace copiado, foi descartado como prova para os itens 5 e 7 e está separado
da execução válida em `red-green-live-globals/`.

As duas lacunas novas foram reproduzidas antes da correção: X6 dava leitura
`subnominal` sem EP da verdade (dois casos), e cinco casos do launcher iniciavam
workers sem barreira global. Os testes adicionais passaram após a correção.
Uma expectativa nova do caso histórico X5 foi ajustada: `[0.55, 0.65]` recebe
`intermediate`, conforme a regra existente.

### Compatibilidade e limites operacionais atuais

`test_legacy_aggregate_accepts_only_pinned_complete_evidence` cobre 26 casos.
O caso X5 com sucesso verifica a classificação efetiva; X7 tem nove células,
scores, nuisance e selos sintéticos, completa ambas as curvas e verifica leitura
`close` com nove deltas pareados nulos. Os registros históricos sintéticos
permanecem byte a byte iguais. O runner continua recusando retomada legada.

Foram conferidos 13 hashes contra os blobs de `c8e4861f`: lockfile, README,
declaração, freeze e os módulos produtores. Os 80 fontes Python congelados não
divergiram e README/declaration registrados permanecem iguais a `85cdb8f2`.
Compatibilidade continua exclusivamente `aggregate-only`, com X7 exigindo
liberação. Nenhum output real foi aberto para comprovar sua validade.

O coordenador disponibiliza os recibos originais em `STAGE_RECEIPTS` antes do
próximo estágio, por armazenamento compartilhado ou sincronização de arquivos.
Sem esses recibos o launcher interrompe o avanço; não há sincronização remota
automática. Novas pré-condições por classe de host pertencem ao commit final.
Esta validação técnica não libera resultados nem autoriza uma execução científica.

### Portões desta revalidação

Executados a partir de `studies/ic-2026-2027/`, usando `uv run --locked` e cache
com escopo em `/Users/davi/.local/state/research-workbench/x3x7-validation-20260929/`.

```text
ruff check
All checks passed!

ruff format --check <14 arquivos Python tocados>
14 files already formatted

uv run --locked mypy src tests
Success: no issues found in 102 source files

uv run --locked pytest -q --tb=short <9 módulos focados>
372 passed in 969.82s (0:16:09)
```

O pytest focado inclui os módulos de teste `test_v4_exploratory_x3x7.py`,
`test_v4_exploratory_x3.py`, `test_v4_exploratory_x4.py`,
`test_v4_exploratory_x5.py`, `test_v4_exploratory_x6.py`,
`test_v4_exploratory_x7.py`, `test_v4_exploratory.py`,
`test_v4_exploratory_x1b.py` e `test_v4_exploratory_launcher.py`, integralmente,
em um único processo pytest sem xdist, com os quatro limites de threads em 1.
A suíte inteira não foi executada. `bash -n` nos dois scripts e
`git diff --check` também passaram.

Comandos, saídas e códigos de retorno: diretório de evidências (`/Users/davi/.local/state/research-workbench/x3x7-validation-20260929/`).
Prova válida: red-green-results.json (`/Users/davi/.local/state/research-workbench/x3x7-validation-20260929/red-green-live-globals/red-green-results.json`).
Pins: pins-and-freeze.json (`/Users/davi/.local/state/research-workbench/x3x7-validation-20260929/pins-and-freeze.json`).
Estado final: git-status.txt (`/Users/davi/.local/state/research-workbench/x3x7-validation-20260929/git-status.txt`).
Hashes finais: tree-files.json (`/Users/davi/.local/state/research-workbench/x3x7-validation-20260929/tree-files.json`).

Não houve commit, push, SSH, mudança no freeze ou na declaração. Não foram lidos
dados reais selados, `sealed-v4-*`, tier logs ou `restricted/`; os testes usam
dados sintéticos temporários. `git status` mantém os 13 arquivos rastreados
modificados e os seis arquivos novos visíveis na árvore para o coordenador.
