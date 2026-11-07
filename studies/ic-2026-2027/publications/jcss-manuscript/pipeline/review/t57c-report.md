# T57c — decisões do coordenador sobre as revisões da montagem sintética passed-shp

Data: 01/10/2026. Base: integração `7641979d`. Autoridade: decisões delegadas do coordenador (decisão 161). Fontes: `coord-20260925/review-20261001/claude-review.md` (C, com o número do item ou da reescrita) e `codex-review.md` (X, com o número do item).

Escopo:
- Tudo foi aplicado antes da liberação de qualquer resultado dos tiers.
- Nenhum dado selado, log de tier, diretório restricted ou dado SHP foi aberto, e nada do fechamento congelado mudou.
- O texto fixo (`sections/*.tex`, corpo de `main.tex`, ODD e suplementos) ficou com o coordenador e não foi tocado. Os itens desta tarefa foram resolvidos nos shells, nas regras, no shell do resumo e na composição.

## 1. Detalhe exploratório fora da Discussão (C1; X3; X10; X6)

Saíram da Discussão 27 regras e seus blocos:
- D-X1B e D-X1B-NO-RELEASE;
- D-X3-SCOPE, -READINGS, -GAPS, -LOST e -DOMAIN;
- D-X3-LOCAL-R050 a R090 e D-X3-LOCAL-NOTE;
- D-X4-SCOPE, -NORMAL, -PAIRED, -SIZE e -DOMAIN;
- D-POST-AVAILABILITY;
- D-X7-SCOPE, -GAIN, -CLOSE e -OTHER-STATES.

No lugar deles, o DS10 recebe um único bloco, D-EXPLORATORY-SUPPLEMENT. Ele é selecionado exatamente quando a seção exploratória é montada (condição `E.status-and-scope`) e diz:

> "The declared exploratory analyses X1b and X3--X7 are reported with their denominators, states and restrictions in the Supplementary Material (X1b and X3--X7). They do not enter the confirmatory reading; X5 and X6 appear in this Discussion only as limits on its interpretation."

Os blocos de X5 e X6 continuam como estavam.

No suplemento:
- **Título da seção.** E.status-and-scope passa a começar pelo título da seção, com `\label{supp:x3-x7}`. Esse título ficava fora de toda regra e nunca chegava à montagem: no PDF revisado, os parágrafos de X3–X7 apareciam dentro de "Implementation verification".
- **E.x3-design (novo, X3 e X10).** Explica o desenho antes das leituras:
  - B escolhe a própria fração de sinal $r_B$, ajustada com os dois parâmetros de persistência aos momentos das defasagens 1 a 3;
  - por isso os dois contrastes treinam a LDA só nas defasagens 4 e 5, ao contrário do discriminador principal, que usa as defasagens 3 a 5;
  - o contraste de fração conhecida usa o B congelado no r da célula, ambos usam os mesmos painéis sociais, e cada célula traz a diferença pareada com intervalo bootstrap, lida contra a margem declarada.

  Ele também traz a ressalva comum, dita uma vez: os intervalos são condicionais aos ajustes aceitos e aos discriminadores treinados, omitem a incerteza do matching de três parâmetros e os contrastes não estimam a fronteira congelada. Essa ressalva saiu de E.x3-reduced-separation e de E.x3-local-equivalence, e a margem passou para o parágrafo de desenho.
- **E.x7-scope (novo).** Diz o que X7 compara (sementes pareadas, todo r, tabelas x7, x7-boundaries e x7-deltas). Também diz que erros e lacunas do braço expandido ficam à parte e que a mudança de dimensão afeta estimação e regularização, de modo que uma LDA mais rica não estabelece teto de informação nem otimalidade de Bayes. Essas frases saíram de E.x7-inconclusive-comparison e E.x7-incomplete-comparison, onde dependiam de contagem positiva.
- **Ressalvas que só a Discussão tinha, agora movidas:**
  - "nem o poder atingível do analista" e o domínio declarado de X4b foram para E.x4-conditional-rejection-references; o domínio aponta para a Tabela v4x-x4b, sem números soltos, porque o catálogo exploratório não carrega os IDs de protocolo confirmatórios;
  - "compatibilidade não estabelece calibração sobre o nulo composto" foi para E.x4-zero-strength-compatibility;
  - as regras de seleção (ponto ausente ou censurado não seleciona célula; ponto finito com extremo censurado seleciona a célula exata) foram para E.available-local-readings;
  - estados fora do domínio excluídos das contagens indisponíveis, e nenhuma célula vizinha substituindo a = 0, foram para E.partial-and-unavailable-readings;
  - o isolamento da dependência de rede foi para E.twin-and-expanded-feature-boundaries, que também passa a dizer "places the twin" e "response signal shares".

Ramos sem PASS: os blocos E.* exigem PASS, e o exportador exploratório exige as comparações vinculadas à liberação. Portanto EX3, EX4 e EX7 nunca valem sem PASS. O único bloco removido que valia sem PASS era D-X1B-NO-RELEASE, e sua afirmação já está no suplemento fixo de X1, em EX13 e EX12 ("Comparison … is restricted to authorized releases").

### Verificação afirmação por afirmação

Em cada linha, "→" indica onde a afirmação está no suplemento depois da T57c.

| Bloco removido | Afirmação | Onde fica |
| --- | --- | --- |
| D-X1B | contagens disponível/indisponível do gêmeo | E.twin (mesmos IDs) |
| D-X1B | todo r, primeiro e sustentado, intervalos, estados, censuras; não restrito a atingidos | E.twin; legenda da tabela x1b-boundaries |
| D-X1B | relato arquivado é fonte separada; registro inválido não é substituído | E.twin |
| D-X1B | sementes diferentes, sem teste entre curvas | E.twin; legenda boundary-comparisons |
| D-X1B | não isola a dependência de rede | movido para E.twin |
| D-X1B-NO-RELEASE | sem curva liberada não há comparação | suplemento fixo de X1 (EX13/EX12) |
| D-X3-SCOPE | inventário de X3 | E.status-and-scope; tabela status |
| D-X3-SCOPE | condicional a ajuste e treino, LDA em L4–L5, incerteza do matching omitida | E.x3-design; legenda da tabela x3 |
| D-X3-SCOPE | sem correção de multiplicidade nem leitura de curva inteira | E.status-and-scope |
| D-X3-SCOPE | não estima a fronteira congelada | E.x3-design; legenda selected-comparisons |
| D-X3-READINGS | contagens por rótulo, inclusive zero | E.x3-* (contagem positiva); tabela x3 traz o rótulo de cada célula; catálogo traz as contagens |
| D-X3-READINGS | leituras locais e condicionais | E.x3-design |
| D-X3-READINGS | todo intervalo negativo com magnitude | tabela x3 (ΔAUC e intervalo por célula) |
| D-X3-READINGS | nem equivalência de mecanismos nem de leis | E.x3-local-equivalence |
| D-X3-GAPS | erros, lacunas conhecidas e livres; tentativas retidas | E.x3-execution-errors, -known-fit-gaps, -free-fit-gaps; tabela x3-attempts |
| D-X3-GAPS | desfechos distintos; rótulo de busca não prova inviabilidade | legenda x3-attempts (dois braços); E.x3-free-fit-gaps |
| D-X3-LOST | sinalizador lost_crossing, sem cruzamento de banda | E.x3-paired-cell-flag |
| D-X3-DOMAIN | a = 0 fora do domínio de X3 | E.partial-and-unavailable-readings; legenda comparison-states |
| D-X3-DOMAIN | nenhuma célula vizinha substitui | movido para E.partial-and-unavailable-readings |
| D-X3-LOCAL-R* | magnitude, intervalo e rótulo por r | tabela selected-comparisons; o a é o primeiro ponto de T1 e boundary-comparisons |
| D-X3-LOCAL-NOTE | margem declarada | E.x3-design |
| D-X3-LOCAL-NOTE | validade da curva principal | coluna Global valid de boundary-comparisons; E.partial; P4/B02 em Results |
| D-X3-LOCAL-NOTE | ressalva de ajuste e treino; não estima fronteira | E.x3-design; legenda selected-comparisons |
| D-X4-SCOPE | direção oráculo, tamanhos, denominadores, falhas como não rejeição | E.x4-conditional-rejection-references |
| D-X4-SCOPE | nem validade composta nem poder atingível do analista | movido para E.x4-conditional-rejection-references |
| D-X4-NORMAL | contagens describes/overstates/understates | E.x4 (contagem positiva); tabela x4-normal |
| D-X4-NORMAL | compatibilidade no próprio AUC não valida a teoria normal | legenda x4-normal |
| D-X4-PAIRED | contagens removes-power, no-material-change, inconclusive | E.x4; tabela x4-paired |
| D-X4-PAIRED | combina ajuste, precisão e falhas; não isola uma objeção nem dá limite universal | legenda x4-paired; E.x4-negative-paired-difference; legenda x4-failures |
| D-X4-SIZE | contagens calibrated/liberal/conservative | blocos E.x4 de força zero; tabela x4-calibration |
| D-X4-SIZE | rótulos valem para suas células | E.x4-zero-strength-compatibility; legenda x4-calibration |
| D-X4-SIZE | compatibilidade não calibra o nulo composto | movido para E.x4-zero-strength-compatibility |
| D-X4-SIZE | sinais não dão limite universal de poder | E.x4-below-nominal; legenda x4-failures |
| D-X4-DOMAIN | domínio declarado de X4b | movido para E.x4-conditional-rejection-references |
| D-POST-AVAILABILITY | contagens de disponibilidade de X3 e X4 | E.available-local-readings; E.partial-and-unavailable-readings; tabelas comparisons |
| D-POST-AVAILABILITY | fora do domínio fica fora das contagens indisponíveis | movido para E.partial-and-unavailable-readings |
| D-POST-AVAILABILITY | ponto ausente ou censurado e ponto com extremo censurado | movido para E.available-local-readings |
| D-POST-AVAILABILITY | sem interpolação nem fronteira sustentada; marca global mantida | E.available-local-readings; E.partial; legenda boundary-comparisons |
| D-X7-SCOPE | inventário de X7 | tabela status (linha x7); E.x7-incomplete-comparison |
| D-X7-SCOPE | braço expandido à parte; sementes pareadas; todo r | E.x7-scope; legendas x7 e x7-boundaries |
| D-X7-SCOPE | curva liberada como contexto | legenda boundary-comparisons |
| D-X7-SCOPE | dimensão afeta estimação; nem teto nem Bayes | E.x7-scope; legenda x7 |
| D-X7-GAIN | ganho sob o critério pareado e regra de censura | E.x7-gain-under-the-paired-criterion |
| D-X7-CLOSE | equivalência local; não estabelece discriminação ótima | E.x7-local-equivalence-near-the-boundary; E.x7-scope |
| D-X7-OTHER-STATES | contagens dos demais estados, inclusive zero | E.x7-* (contagem positiva); tabela x7 traz o estado de cada unidade |
| D-X7-OTHER-STATES | gate inválido sem leitura; censuras e incompletude distintas | E.x7-invalid, -censored, -unavailable, -incomplete; legenda x7-boundaries |

## 2. Listas de r repetidas (C2)

As listas ficam no resumo e em Results. Nos blocos D-H-BD, C-H-BD, D-D-AFTER-B03, C-D-AFTER-B03, D-PERMISSION, C-PERMISSION, D-BD-PERSISTENCE, C-BD-PERSISTENCE, D-BD-INCONCLUSIVE, D-BD-BOTH, D-BD-NO-CROSSING, D-BE-PERSISTENCE e D-BC-PERSISTENCE, cada lista passa a remeter ao conjunto relatado em Results ("the common gap-free set of response signal shares reported in Results").

Nenhum bloco da Discussão ou da Conclusão usava um conjunto que Results não traga. As listas de inconclusivos, cruzamento duplo e ausência de cruzamento estão em P6-c, P6-d e P6-e, sob as mesmas condições, então nenhum binding precisou ficar.

## 3. Contagens B/D em um só lugar (C3; X7)

As contagens de B/D, B/E e B/C ficam em Results. A Discussão e a Conclusão dão a leitura congelada uma vez cada, sem contagens:
- D-BD-PERSISTENCE e C-BD-PERSISTENCE; a Conclusão funde as duas formulações da leitura;
- D-BE e D-BC.

D-H-BD, C-H-BD, D-D-AFTER-B03 e C-D-AFTER-B03 passam a remeter às classificações de Results.

A frase "This extends the comparison of rival accounts…" saiu de C-B02 e de C-BD-PERSISTENCE. Ela fica em C-H-BD, C-H-B e C-B03, que nunca coexistem. Um teste cobre H-BD, H-B, B02 + H-B, B03 + D-after-B03 e falha de gate: aparece no máximo uma vez.

D-H-B e C-H-B (só B, sem permissão) ainda mostram as contagens de B, como Results. O item 3 trata de B/D, por isso não mudaram.

## 4. Redação

| Bloco | Mudança | Fonte |
| --- | --- | --- |
| B00 P3 (P3.1) | inventário em inglês, com os quatro rótulos em português numa só nota | C, reescrita 3 |
| B00 P1 (P1.1) | abertura: gate e inventário primeiro porque decidem o que pode ser lido | C, reescrita 10 |
| B10 (B10.bd.3) | "An upper band below the target shows only that this discriminator did not reach the target against D on this grid; D could still be separable at a lower AUC or by another discriminator, and failing to reach the target does not establish equivalence." | C5 e reescrita 5; X5 |
| D-SHP-ADMISSIBLE | sai a frase que repetia DS05 | C, reescrita 6 |
| D-X7-OTHER-STATES e D-X4-SIZE | blocos removidos (item 1); no suplemento cada estado já é um parágrafo guardado por contagem positiva, sem enumeração de zeros, então a reescrita 7 não tem contrapartida | C, reescrita 7; C15 |
| D-X5-POST-UNAVAILABLE | "These X5 results come from the stress test itself. Its planned comparison with the released B curve is not reported, because no X5 aggregate was supplied for the release." | X6; C15 |
| texto do X1b | "this projection" saiu com D-X1B; E.twin não usa a expressão | X6 |
| C-IMPLICATION | sai "The particular follow-up design remains to be declared." | X11 |
| C-EVALUATION-PASS e -REQUIRED | slot novo `CN01-join`: a composição junta a frase ao parágrafo fixo do CN01 que antecede C3 ("…partial calibration exposure. Evaluation used new seeds.") | C15 |

## 5. Resumo (X1; C, reescrita 4)

**Qualificação da AUC.** A frase de desenho passa a "the expected panel-level area under the receiver operating characteristic curve (AUC), given a validated fit, reaches 0.70". A forma completa ("over matching, validation and training") não cabe: a composição B03 + D-after-B03 + B06 + X6 já tinha 246 palavras, e quatro é o máximo que ela absorve. Methods (M23) mantém a definição completa.

**Lista de D.** A reescrita 4 literal acrescenta 13 palavras e levaria H-BD + B10 + B06 + X6 a 255 mesmo sem a qualificação. Adotei uma forma rotulada pareada, que acrescenta 3 palavras: "the first boundary was small at [n] against trait-plus-autoregressive persistence and [n] against state-dependent persistence, large at [n] and [n], not attained at [n] and [n], and censored or indeterminate at [n] and [n]."

**Orçamento** (`check_v4_abstract_budget.py`, receipt `t57c-abstract-budget.json`):
- 46 composições obrigatórias, com máximo de 250 (B03 + D-after-B03 + B06 + X6); o máximo com H-BD é 249;
- casos de concordância 0, 1, 2 e 9 dentro de 250;
- fallbacks agora 262, 261, 257 e 250, porque o primeiro (a terminação elíptica de H-BD) foi substituído.

**Oráculos atuais regenerados:**

| Caso | Palavras |
| --- | --- |
| passed-shp | 230 |
| failed-G0 | 179 |
| invalid-main | 200 |
| incomplete-tier2 | 184 |
| casos X6 | 230 ou 241 |
| casos G2c | 183 |

O rascunho do resumo em `main.tex` (texto do coordenador) deve receber a mesma qualificação.

## 6. X6 e demais blocos (item 6)

Uma varredura das montagens dos 12 casos e da variante B03 procurou frases repetidas a até três frases de distância. Na Discussão e na Conclusão não há repetição literal, então nada foi removido.

Há uma quase-repetição, não literal: "no partner-drift interpretation to their relative boundary positions" (D-H-BD) e "…to this class or to the order of the two boundaries" (D-BD-BOTH). Ela só aparece com n_both > 0.

## 7. Subtítulos em Results — não aplicado

A composição não sustenta os seis subtítulos em limites de slot sem mudar a ordem registrada:
- P7 começa por P7-a (figuras de A, C e E) e P7-b (unidades inválidas do tier 2), que pertencem à comparação com outros nulos, antes dos controles do tier 3;
- P9 (diagnósticos do valor crítico e da covariância) e P10 (variação descritiva em r, B07 e a unidade exposta em r = 0,70) vêm depois da âncora SHP e não cabem em nenhum dos seis títulos.

Para aplicar sem reordenar, seria preciso ancorar os títulos em regras (por exemplo, antes de P7-c/B11) e acrescentar um sétimo título para P9–P10.

## Registros

- `t57c-shell-repin-receipt.json`: os quatro shells, com aceite explícito dos 33 blocos de texto visível alterado e 3 mudanças só de comentário. Locators explícitos em E.status-and-scope (12–18) e E.x6-matching-diagnostics (154–157): os intervalos fixados terminavam no comentário do bloco seguinte, e o diff punha dentro deles os parágrafos novos de X3 e X7.
- `t57c-abstract-notes-repin-receipt.json`: notas do shell do resumo, sem regra alterada.
- `t57c-x4-domain-repin-receipt.json`: a frase do domínio de X4b.
- `t57c-selection-changes.json`:
  - 27 regras removidas;
  - 3 novas (D-EXPLORATORY-SUPPLEMENT, E.x3-design e E.x7-scope);
  - 2 mudanças de slot (C-EVALUATION-PASS e -REQUIRED para `CN01-join`);
  - 1 extensão de locator (E.status-and-scope, para incluir o título);
  - os SHA-256 do registro em cada etapa.
- `t57c-abstract-budget.json`.
- Ajustes de ferramenta:
  - `check_v4_abstract_budget.py` sem o fallback de H-BD e com saída nova;
  - `audit_v4_manuscript_assembly.py` passa a ler os nove IDs exigidos em E.twin, iguais aos de D-X1B;
  - `current_shell_oracles.json` com resumos regenerados.

## Verificação

Testes com `nice -n 15` e BLAS em uma thread: 643 aprovados e nenhuma falha. Montador 189: saíram os 10 casos das notas de célula X3 e o teste do domínio X4 da Discussão; entraram 11 casos (ponteiro com e sem seção exploratória; desenho de X3 e escopo de X7 ditos uma vez; contagens só em Results e leitura única em cinco variantes de manchete; frase das novas sementes junto do parágrafo de exposição, em PASS e em falha; redação nova; domínio de X4b no suplemento). Derivação 84, exportador 80, relatório 95 (inclui `test_frozen_files_are_untouched`), exploratório 58, projeção pública 93, gate-only 15, propagation 24 e sucessor v4.4 5. Ruff (check e format) e mypy passam nos arquivos Python tocados; `scripts/check_repository.py` passa nas 7 checagens. A primeira rodada da matriz falhou em `test_cli_fills_shells_and_merged_values_pass_real_checker`, porque a frase do domínio de X4b vinculava IDs confirmatórios que o catálogo exploratório não tem; corrigido em `b178fe3e`.

Montagens sintéticas compiladas com `tectonic --only-cached` (classe Springer de `compile-v44`), todas com exit 0, sem erro LaTeX, sem overfull e sem referência indefinida:

| Montagem | Palavras no resumo |
| --- | --- |
| passed-shp | 230 |
| i-comparison-failed (falha G2c) | 183 |
| failed-G0 | 179 |

## Para o coordenador (texto fixo, fora deste escopo)

- DS02 ainda está no futuro e com "suppose" (C4, X8, X2).
- A frase "Final interpretation must be based on…" em DS10 (X8).
- "after release" em EX15 (X8).
- A qualificação da AUC no rascunho do resumo de `main.tex`.
