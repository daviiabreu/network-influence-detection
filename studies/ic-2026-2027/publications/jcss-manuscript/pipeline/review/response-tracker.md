# Response-to-reviewers tracker

Reconciliado em 2026-09-30 para M03, na integração `f406ba64`, a partir dos commits de `integration/ic-20260928` desde 28/09 e das decisões 80–116 do log do coordenador. A revisão C continua sendo a de `2a4e034b` (SHA-256 `907ec932364ba35f6ca6463d59acd2199f13a8629a01e0de6e6b5af9fa4abfcd`); a resposta original foi integrada em `6b319516`, após Q7 em `eb4f6068`. A correção de texto não encerra uma objeção científica nem substitui a decisão do Research Owner. Os recibos mecânicos ao fim são históricos, de 29/09.

Nesta reconciliação foram consultados somente documentos permitidos e histórico Git. Nenhuma saída selada, microdado, log de gate/tier ou área restrita foi lida. Não houve análise, execução, commit ou push. A revisão original é `coord-20260925/codex-review-C-manuscript-2a4e034b.md`, fora do repositório.

`M/` = this manuscript directory; `X/` = `studies/ic-2026-2027/experiments/exploratory/detection-boundary-v4-exploratory/`; `Q/` = `studies/ic-2026-2027/research/questions/exploration/2026-09-24-parallel/`. Changes below refer to current files, not the older review line numbers. `RC01–RC52` in `claim-evidence.md` bind the altered empirical sentences.

`L n` identifica o item n de `owner-decisions-20260924-session-log.md`, em `coord-20260925`, consultado no intervalo 80–116. **Fechado no texto/implementação** exige commit ou decisão citados; **pós-liberação** aguarda evidência real; **Davi** exige decisão/atestação humana; **sem dono** significa que não há responsável documentado para a análise adicional. A coluna “Reviewer recheck” permanece pendente: `1127d5a8` preparou o [roteiro final](final-review-roteiro-2026-09-30.md), não executou M06 (L105(iv)).

O gate foi aprovado por inteiro: G2 em 30/09 às 10:01Z (700/700, zero falhas) e G2c às 16:44:54Z (142/142, zero falhas; L114), com os tiers iniciados às 16:46:33Z; não há resultados confirmatórios nem de X3/X4/X6/X7 fora do selo.

## Major review C findings

| Finding ID | Severity | Reviewer request | Author decision | Change and manuscript location | Evidence or test receipt | Reviewer recheck | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C-M1 | major | Preserve X1b censoring and point/band distinction | accept E/T | M/sections/supplement-exploratory-x1-x2.tex, Status; X/REPORT.md; EX13, RC01–RC06; generated/exploratory-x1b-boundaries.tex | `6b319516`, L83: correção conferida pelo coordenador; `46d20a05`, L115: tabela de todo r, duas fronteiras, intervalos e censura, catálogos sintéticos preservados | pending | fechado no texto e na tabela; geração real pós-liberação |
| C-M2 | major | Do not certify interior coverage with X6's criterion | accept T; new X not performed | M/sections/discussion.tex; [restrições X3–X7](x3-x7-reading-restrictions-2026-09-29.md), atualizadas após a resposta original | `6b319516` restringe cobertura; `30c10dc8` corrige regra/denominadores de X6; `99c59590`, L91, alinha nota e consequência no resumo. Nenhuma saída X6 lida; novo desenho nominal não demonstrado | pending | texto restrito; X6 pós-liberação; objeção nominal aberta, sucessor sem dono |
| C-M3 | major | Restrict X1a to its two-generator contrast | accept T; X not performed | M/sections/supplement-exploratory-x1-x2.tex, X1a and Limitations; EX04–EX06, EX11, RC07–RC12 | `6b319516`, L83: restrição conferida pelo coordenador. Recibo original de 51/72 intervalos preservado; controle que preserve forma não executado por esse commit | pending | fechado no texto; atribuição de mecanismo indisponível, controle sem dono |
| C-M4 | major | Incorporate release and G1c successors | accept E/T | M/sections/methods.tex, Inventory and Protocol history; verification.tex; appendix-odd.tex, Observation and Implementation; M85–M86, ODD40, VER15–VER16, RC32–RC43/RC47–RC50 | Q/detection-boundary-v4-release-amendment.md; release wrapper 1f74e902 and hash; public report README decision 46; coordinator-supplied G1c SHA-256 a945e8484791f886289d51b083886854b4f540f6b26dcf1463d8d4c9dcd9a4d6. Private successor and release records not read | pending | resolved in text; no execution or release outcome claimed |
| C-M5 | major | Synthesize X5 in discussion and conclusion | accept E/T | M/sections/discussion.tex, DS03/DS11/DS10; conclusion.tex; supplement X5; EX14–EX15, RC13–RC23/RC27–RC31 | X/results/x5.json: 72 finished, 36 estimates, 36 gaps; four condition-specific AUC ranges and all 36 interval_27729 values verified | pending | resolved in text |
| C-M6 | major | Restrict X4 power/calibration language | accept T; new X not performed | [Restrições X3–X7](x3-x7-reading-restrictions-2026-09-29.md), X4; referências de rejeição oraculares | `6b319516`/`99c59590` restringem linguagem; `30c10dc8` suspende potência sob calibração liberal/ausente (L81). Nenhum resultado X4 lido; teste operacional sob nula composta não demonstrado | pending | texto restrito; X4 pós-liberação; sucessor operacional sem dono |
| C-M7 | major | Separate SHP estimands and update freeze status | accept E/T; X not performed | M/sections/appendix-odd.tex, ODD39; discussion.tex, DS05; RC24–RC26/RC44–RC46 | `6b319516`, L83: coordenador conferiu registro de freeze e separação de estimandos. Nenhuma calibração empírica com propagação de incerteza demonstrada | pending | fechado no texto; âncora/crosswalk dependem do Davi e insumos; calibração adicional sem dono |
| C-M8 | major | Consolidate shell interpretation predicates before exposure | accept E/T | [Tabela datada de interpretação](../drafts/2026-09-28/results-interpretation-decisions-2026-09-29.md); shells e exportadores integrados | L82 fecha Q11/Q16/Q22, sem limiar novo de largura; L91 substitui Q8 de L82: frase entre mecanismos só com tier 2 completo e válido. `44b722dd`, `99c59590`; L99/L101 e `0083009f`/`00c8dc3d` fecham as contingências restantes; `29ee6422`, L112, fixa Discussão/Conclusão | pending | decisões e implementação fechadas; aplicação aos resultados pós-liberação |

## Minor review C findings

| Finding ID | Severity | Reviewer request | Author decision | Change and manuscript location | Evidence or test receipt | Reviewer recheck | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C-m1 | minor | Separate Gestefeld–Lorenz macro and micro fit | accept T | M/sections/related-work.tex, R24; RC51–RC52 | [Original article](https://www.jasss.org/26/4/9.html), §5.16 / equation (4), §5.19 / equation (5), §7.9; full text checked 2026-09-29 | pending | resolved in text |
| C-m2 | minor | Do not treat X3 numerical failure as impossibility | accept T | Dated X3–X7 restrictions: infeasibility, unsuccessful search and rejected validation separately; fit/train conditioning | Public declaration and X3 code; no X3 output read | pending | resolved in writing restriction |
| C-m3 | minor | Replace X7 ceiling language | accept T | Dated X3–X7 restrictions: far → gain relative to frozen-feature LDA; close → local equivalence; other states retained | Public declaration and X7 x7_reading code; no X7 output read | pending | resolved in writing restriction |
| C-m4 | minor | Complete AI disclosure and review provenance | accept E; Owner pending | [Inventário Q4](../drafts/2026-09-30/ai-disclosure-evidence.md), ligado a M54/M55; integration-log Q4 | `8ec31912` prepara papéis/sessões/modelos com incertezas; `6acb0e43` liga a fonte ao ledger; L97(ii). Nenhum deles registra atestação humana ou certificado de independência | Owner / reviewer | inventário preparado; divulgação final depende do Davi |
| C-m5 | minor | Complete submission package | accept E/T; Owner pending | [Checklist JCSS](jcss-submission-checklist-2026-09-30.md), declarações, carta e metadados preparados | `64838de5`/`7a5bc2cc` (L92/L97); `32e6445c` prepara pacote científico; `fb37e762` (L105(iii)) prepara carta; `61378726`/`444c337f` corrigem empacotadores (L106/L111). L109/L111 são ensaios sintéticos, sem submissão | Owner | preparação técnica fechada; pacote real pós-liberação e aceite do Davi |
| C-m6 | minor | Editorial residue, ledger header, tracker and figure labels | accept T | Resíduos e cabeçalhos corrigidos; eixos “nominal strength”/“signal share”; rastreio de texto fixo; estados reconciliados neste M03 | `6b319516` corrige resíduos; `7a5bc2cc`, L97(ii), fecha rótulos e amostras; `6acb0e43` fecha lacunas de rastreio; `74e3426d`/`daebe1ed`, L110/L113, corrigem redação/layout | pending | fechado no texto/geradores; revisão visual da arte real pós-liberação |

## Sixteen major objections from the internal report

The “Review C state” column reproduces the review's table verbatim. It is the assessment at `2a4e034b`, not a claim that this response has resolved the science. The original IDs are preserved.

| Objection | Review C state | Assessment carried from review C | Current text response / remaining evidence |
| --- | --- | --- | --- |
| R1-M1 | Parcial | X1a mixes network and distributional shape | `6b319516`, L83: X1a restrito à separabilidade; gêmeo implementado/relatado em `af0b9efb`/`a3a76a9a`. Objeção causal aberta; controle que preserve a forma sem dono (C-M3) |
| R1-M2 | Resolvida no texto | Rank transport, standardization and limited scope explicit | Existing limitations retained; no new empirical model claim |
| R1-M3 | Substancialmente atendida | X2 delivers the promised diagnostic, latent and per step | X2 text and its two denominators retained; no observed-scale interpretation |
| R1-M4 | Parcial | Lag-profile comparison with SHP absent | Limitação mantida por `6b319516`; comparação aguarda liberação e âncora do Davi, sem evidência de execução em L80–L116; calibração de rho sem dono |
| R1-M5 | Parcial | B/D depends on D and consolidated reading rules | Regras fechadas em L82/L91 e `99c59590`; nenhum desfecho de D lido. Aplicação pós-liberação, só com tier 2 completo e válido |
| R1-M6 | Atendida como limitação | Empirical validation / households absent but explicit | Limitação preservada em `6b319516`; gerador com domicílios e validação empírica sem dono/plano de execução demonstrado |
| R1-M7 | Resolvida no texto principal; parcial em X7 | X7 still used ceiling language | `6b319516` e `99c59590` restringem X7 a comparação de atributos, sem optimalidade; `46d20a05` inclui tabela completa. Leitura real pós-liberação |
| R2-M1 | Parcial | Known signal share explicit, X3 not yet an answer | X3 implementado em `cfe15198`, corrigido/lançado em `30c10dc8`/`3334ac0f` (L81–L90); resultado permanece selado. Leitura restrita em `99c59590`; resposta científica pós-liberação |
| R2-M2 | Parcial | Population target explicit, X4 retains oracle conditions | X4 implementado em `cfe15198`, corrigido/lançado em `30c10dc8`/`3334ac0f`; `6b319516`/`99c59590` restringem linguagem. Leitura pós-liberação; validação operacional de teste utilizável sem dono |
| R2-M3 | Resolvida no texto | Normal translation correct and conditional | Translation retained; X4 outcome not read |
| R2-M4 | Parcial | Frozen SHP successor, inferential crosswalk absent | `6b319516`, L83: freeze descrito e estimandos separados. Âncora/STARTS e execução do crosswalk dependem do Davi e dos insumos liberados; calibração inferencial adicional sem dono |
| R2-M5 | Análise atendida; síntese pendente | X5 available, discussion obsolete | Síntese fechada em `6b319516`, L83; obrigatória em todos os ramos de Discussão/Conclusão por L91 e `29ee6422`, L112. Comparação com a curva principal aguarda liberação (`47862fe8`, L89) |
| R2-M6 | Não resolvida | Nominal interior validity not demonstrated | `6b319516`/`99c59590` restringem a leitura; `30c10dc8` corrige regra/denominadores, sem demonstrar cobertura nominal. X6 pós-liberação; novo desenho de validação nominal sem dono |
| R2-M7 | Resolvida no texto | Across-r comparisons descriptive | Existing restriction retained; no global band claim |
| R2-M8 | Parcial | Early-release amendment missing | Texto fechado por `6b319516`, L83; implementação corrigida em `edbbf98b`/`9669b509`. `cd4411b7` prepara cronologia. Recibo, horário efetivo e fechamento da exposição pós-liberação (L116 ainda waiting-release) |
| R2-M9 | Substancialmente atendida no texto | Success / retries / gaps and X6 mixture need explicit denominators | `6b319516` materializa denominadores de X1b/X5; `30c10dc8`/`99c59590` corrigem X6; `46d20a05` completa tabelas. Retry/gaps e denominadores reais restantes pós-liberação |

## Pendências por dependência (M03, 2026-09-30)

### Dependem da liberação

| Item | Estado real e evidência | Responsável registrado / condição |
| --- | --- | --- |
| M01/M02: Results, resumo e conclusão finais; C-M8/R1-M5 | Shells decididos (`99c59590`, `0083009f`, `00c8dc3d`, L91/L99/L101) e Discussão/Conclusão pré-escritas (`29ee6422`, L112); nenhuma montagem real demonstrada. Contagem visível corrigida em `2e44c1ab`, L109 | Agente/coordenador; Davi no texto final. Seleção só pelos insumos e predicados vigentes |
| M03: evidência, exposição e cronologia efetiva; C-M4/R2-M8 | Preparação documental em `cd4411b7`; cadeia por evento em `c661809b` e reiniciada em `f406ba64`, L116. Recibo de liberação e cronologia final ainda ausentes no recorte | Agente/coordenador; este adendo encerra só a reconciliação pré-liberação |
| X1b/X3/X4/X5/X7 e C-M1/C-M6/C-m2/C-m3 | Comparações implementadas em `47862fe8` e ajustadas em `99c59590`; tabelas completas em `46d20a05`, L115. Implementação e ensaios não comprovam leitura real | Agente/coordenador, após exportação/validação; manter restrições de `6b319516` e L89/L91 |
| X6; C-M2/R2-M6/R2-M9 | Implementação corrigida em `30c10dc8`/`3334ac0f`, L81–L90; L91 obriga resumo sob o predicado registrado. Não há resultado aberto nesta tarefa | Agente/coordenador; distinguir failure/subnominal/inconclusive/ausente; não certificar cobertura nominal |
| R1-M4/R2-M4: comparação da âncora e crosswalk | Estimandos separados e freeze descrito em `6b319516`, L83; nenhum fechamento empírico em L80–L116 | Davi fornece/atesta âncora; agente integra só agregados autorizados e curvas liberadas |
| R2-M3, R2-M6(E), R2-M9(E), R2 minor 7, secundários 0.60/0.80 | Traduções, diagnósticos congelados, retries/gaps, tie rates e bandas reais continuam pendentes. Exportação preparada por `44b83909`/`a417f390`, regras em L91/L101 | Agente/coordenador; secundários somente no suplemento; não deduzir diagnósticos da aprovação pública do gate |
| M05/M06 e todas as colunas de recheck | Ensaios sintéticos registrados em L107/L109/L113; roteiro final em `1127d5a8`, L105(iv). Nenhuma revisão final dos PDFs reais executada | Agente revisor/coordenador; Davi lê/aceita. Regenerar figuras, conferir pacote e revisar após M01/M02 |
| C-m5: pacote científico e fonte editável finais | Preparação `32e6445c`/`7a5bc2cc`; guardas `61378726`/`444c337f` (L106/L111). Não há depósito/DOI/pacote real aceito | Agente monta com manifestos reais; Davi decide licenças, acesso e envio |

O pedido original de `G2 mean_shift` não tem fonte exportada demonstrada: `a417f390` retirou essa frase do shell por falta de registro lido pelo relatório. Não é uma promessa de preenchimento automático após liberação; permanece lacuna de evidência, sem responsável registrado para uma entrega adicional.

### Dependem do Davi

| Item | Estado real e evidência | O que permanece aberto |
| --- | --- | --- |
| Integration-log Q3/Q14; D03 | Título de trabalho e novidade delimitada; busca adicional em `e243e2a5`, L92, mantém o tema, sem ratificação humana | Título final e aceite da formulação limitada de novidade |
| Integration-log Q4; C-m4/D04 | Inventário com incertezas em `8ec31912`, ligado ao texto por `6acb0e43`; L97(ii). L105(v) registra lista de ações, não atestação | Modelos/versões ainda desconhecidos, supervisão, responsabilidade e divulgação final; independência não certificada |
| Integration-log Q9; D01/D02/D06 | L91–L101 fixam decisões delegadas; L105(v) registra adendo/lista de ações. Não há evidência de inspeção/ratificação do Davi | Aceite de pergunta, história v1/v4, emendas após exposição, mapa incompleto e evidência/texto finais |
| C-m5: autoria, declarações e submissão | `64838de5` prepara declarações; `fb37e762`, L105(iii), prepara carta/metadados com campos do Owner | Autores, afiliações, contatos, contribuições, agradecimentos, financiamento, conflitos, ética/consentimento, ORCID/Scholar, originalidade/exclusividade e aceite de todos |
| Editor/revisores sugeridos | L105(iii): lista confidencial preparada fora do Git; independência aguarda identidade do Davi e demais autores | Seleção final e verificação de conflitos; nenhuma sugestão enviada |
| Acesso/licença/versão e crédito SHP | Rota pública FORS/SWISSUbase fechada em `7a5bc2cc`, L97(ii); `6acb0e43` mantém pendências de contrato/versão | Atestar contrato aplicável, eventual uso, versão/ondas/DOI, crédito e agregados permitidos; nenhuma consulta a microdados nesta reconciliação |
| Código público, arquivo persistente e licenças | `32e6445c` prepara bundle; L111 registra higiene em `dbfed2a8`, mas histórico privado ainda requer decisão | Licenças e DOI/depósito; abrir histórico ou publicar pacote curado é decisão humana, sem evidência de publicação |
| M04: C36–C38/C40 e M61/M66/M69 | `6acb0e43` e [auditoria M04](claims-audit-2026-09-30.md) mantêm lacunas de fontes e alcance; não houve commit posterior de fechamento no recorte | Fontes primárias/apoio secundário autorizado, coluna adjacente se usada, prova/domínio de M61, fator de SE e limite de viés em soluções restritas |
| M04: abertura ODD e introdução a Submodels (§9.11) | `6acb0e43` registra cobertura da auditoria ODD, mas esses dois parágrafos ainda não têm marcador/linha próprios em `f406ba64` | Agente/coordenador completa rastreio; Davi aceita suporte. Não fechar a lacuna só pelo título do commit |
| Integration-log Q10: destino se gate falhar | L99(i) fecha forma do artigo, não periódico; L107 ensaia falha G2c, sem selecionar resultado | Destino e envio continuam humanos; a divergência com L114 acima não autoriza escolher um ramo aqui |

### Sem dono documentado para o trabalho adicional

Estes itens não são tarefas implicitamente atribuídas ao agente desta reconciliação. “Sem dono” não demonstra que a análise nunca existiu: conserva a ausência de execução/atribuição nas evidências consultadas.

| Item | Estado real / evidência delimitadora | Lacuna |
| --- | --- | --- |
| C-M3/R1-M1: controle que preserve a forma de um passo | `6b319516`, L83, fecha restrição de X1a; não implementa esse controle | Sucessor de mecanismo sem responsável/plano registrado |
| C-M2/R2-M6: validação nominal interior | `30c10dc8` corrige X6; `99c59590` restringe adequate e denominadores, L91 | Novo desenho com margem de equivalência e incerteza da verdade sem dono; X6 real sozinho não encerra a objeção |
| C-M6/R2-M2: teste operacional | `6b319516`/`99c59590` preservam condições oraculares | Validação de tamanho sob nula composta e teste utilizável sem dono |
| C-M7/R2-M4: calibração inferencial empírica | `6b319516`, L83, separa âncora/STARTS/compatibilidade | Propagação de incerteza adicional sem dono; diferente da âncora/crosswalk declarados |
| R1-M4(S): calibrar rho; R1-M6(S): domicílios; R2-M7(S): banda de 81 células | Limitações conservadas na resposta `6b319516`; L112 mantém próximo desenho como limite a declarar separadamente | Não planejados/sem dono; banda conjunta seria pós-hoc. Não marcar como concluídos pela existência de X3–X7 |
| Integration-log Q5(b/c): notas sucessoras de freeze | `cd4411b7` registra a história, mas não fecha expressamente as duas notas; abertura do README ainda contraditória em `f406ba64` | Sem evidência de fechamento ou responsável para as notas; não alterar bytes vinculados |
| Methods ledger 10: TOST/Holm; related-work ledger 5: limpeza de entradas não citadas | Nenhum fechamento específico no log/commits consultados; `7a5bc2cc` acrescenta referências, não comprova esses dois itens | Citações opcionais e limpeza sem dono documentado |

## Fechamentos documentais desde o rastreador anterior

Shell Q8/Q11/Q16/Q22 não são mais decisões abertas: L82/L91 e `44b722dd`/`99c59590` as fecham, sem limiar novo de largura; Q8 de L82 foi substituída, e não deve reaparecer como opção. Shell Q1–Q5/Q7/Q17/Q18 foram fechadas por L99/L101 e `0083009f`/`00c8dc3d`. Os IDs Q3/Q4/Q14 dos shells não são os mesmos do integration-log.

O pre-write do risk register (rank 6 do integration-log) tem Results/resumo em `99c59590`/`0083009f`/`00c8dc3d` e Discussão/Conclusão em `29ee6422`; ensaios e arte sintética estão registrados em L109/L113. A seleção e a montagem reais permanecem em M01/M02/M05. O gêmeo mean-field/X1b e o mapa de deriva X2 já foram relatados em `af0b9efb`/`a3a76a9a`/`3242b19b`, não são simulações ainda por iniciar. X3/X4 foram implementados e lançados (`cfe15198`, `30c10dc8`, `3334ac0f`, L81–L90), mas não entregaram resposta aberta neste escopo. O teste de má especificação X5 e sua síntese foram fechados em `4a372a71`/`2a4e034b`/`6b319516`, L83; sua comparação pós-liberação continua pendente.

A ausência de marcadores/linhas de texto fixo do integration-log §9.11 foi tratada parcialmente por `6acb0e43`: AB01–AB08, IN04–IN07, CN01 e SUP01–SUP13. A auditoria cobre ODD, mas sua abertura e introdução a Submodels continuam sem linha própria; não há fechamento demonstrado desses dois itens. Rastreio não é leitura integral de todas as fontes: C36–C38/C40 e M61/M66/M69 continuam abertos acima. A compilação histórica deixou de ser “não feita”: L83 registra 42 páginas/checker normal aprovado, e `6acb0e43` registra outra compilação de 42 páginas; isso não fecha a compilação final M05.

## Mechanical verification receipts (2026-09-29)

Both PDFs were compiled in temporary copies under `/private/tmp/manuscript-review-c-20260929/`, using `sn-jnl.cls` and `sn-mathphys-num.bst` from the coordinator's local Springer template. Command: `XDG_CACHE_HOME=/private/tmp/manuscript-review-c-20260929/cache nix shell nixpkgs#tectonic --command tectonic main.tex`. The scoped cache was needed because the default Nix cache is outside the writable sandbox. No vendor file was added to Git.

From each copy's manuscript root: `python3 pipeline/paper_check.py --venue jcss --pdf main.pdf`.

| Metric | Before (`20bdcaac`) | After corrections |
| --- | ---: | ---: |
| PDF pages | 41 | 42 |
| Extracted PDF words | 25,184 | 25,913 |
| Abstract words | 250 | 250 |
| Keywords | 5 | 5 |
| Used citation keys / bibliography entries | 54 / 73 | 54 / 73 |
| Placeholders | 19 | 19 |
| Normal checker | PASS | PASS |

The final compile has no overfull-box warning. The inherited 78.8613 pt column overflow was removed by making the existing search-log path breakable; underfull-box warnings remain. Rendered pages and the changed passages were inspected, including the final path correction. The PDF remains a pre-results draft with intentional placeholders. A normal checker pass does not clear final declarations, bound confirmatory results or Owner choices for submission.

Offline evidence assertions passed for X1b censoring/intervals/table maxima, X1a 51/72 intervals, and X5 36 estimates/36 gaps/all four AUC ranges/all 36 critical-2.7729 intervals. No simulation or model was run. All 52 RC sentence markers have unique ledger rows; the original corrected IDs have dated reasons; the tracker contains all 16 internal major objections and its local links resolve. The two documents bound by the SHP successor freeze match their recorded hashes. The G1c private successor hash is coordinator-supplied and was not independently recomputed.

`git diff --check` passed. Scope audit: 11 tracked files modified and two new notes, all prose/ledger/tracker. No immutable declaration, freeze-bound file, SHP successor file, results shell, shell notes, runbook, source module or test changed. `systematic-map.tex` matches its original bytes. HEAD remains `20bdcaac4c34f47cdb1c43dbea39573ec3f321d5`; no commit was made.
