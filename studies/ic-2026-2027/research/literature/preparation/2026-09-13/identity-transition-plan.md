# Transição mínima para adjudicação dos pares de identidade

Diagnóstico de 13/09/2026. Recomendo uma única transição vinculada que derive uma subfila de identidade compatível com a adjudicação existente, conservando o resultado v3 integral como pai e o corpus agregado `incomplete`. A projeção foi confirmada em memória; não houve persistência de resultados, escolhas humanas ou promoção. A proposta de contrato abaixo ainda precisa de revisão antes de implementação.

## Bloqueio comprovado e recorte possível

O bloqueio de software é real e intencional no contrato atual. `DeduplicationResult` aceita apenas schemas 1/2 e exige `works` ([deduplication.py:60](../../../../../../workbench/src/research_workbench/workflows/systematic_review/deduplication.py)); a fila nativa o reabre diretamente em `_canonical_inputs` e `_load_queue` ([review_adjudication.py:291](../../../../../../workbench/src/research_workbench/orchestration/review_adjudication.py)). O resolvedor produz somente `ScholarlyWork`, cujo título é obrigatório, e procura um título presente ao unir grupos ([adjudication.py:100](../../../../../../workbench/src/research_workbench/workflows/systematic_review/adjudication.py), [contracts.py:232](../../../../../../workbench/src/research_workbench/workflows/systematic_review/contracts.py)).

Reproduzi a rejeição do result-3 real pelo contrato legado e da fila de metadados por `ReviewAdjudicationQueue`. Um registro original sem título também produz `IncompleteBibliographicMetadataError` no agrupamento policy-2 legado. Os testes existentes exigem essas rejeições ([test_review_corpus_metadata.py:165](../../../../../../workbench/tests/workflow/test_review_corpus_metadata.py)); elas não devem ser removidas para fazer o corpus parecer completo.

Entretanto, nenhum dos nove registros em propostas integralmente sem título participa dos 20.964 pares de identidade deste corpus. Removê-los **somente da entrada da subfila**, preservando-os no pai, permite executar `deduplicate_records` com a mesma policy-2. A reprodução determinística levou 5,322 s e confirmou igualdade integral das obras tituladas e dos candidatos, incluindo IDs, membros e sinais:

| Propriedade | Resultado |
| --- | ---: |
| Registros no pai | 54570 |
| Registros na subfila de identidade | 54561 |
| Registros conservados fora dessa subfila | 9 |
| Obras tituladas exatamente iguais ao result-3 | 46391 |
| Candidatos de identidade exatamente iguais ao result-3 | 20964 |
| Hashes distintos de fonte, pai e subfila | 1536 em ambos |
| Pendências globais conservadas | 9 de metadados e 10 conflitos de prontidão |

As duas partições são disjuntas e sua união cobre todos os IDs originais. Não há exclusão canônica dos nove registros. O result-3 pai permanece `41a54060be2206d88b13aa8d0026acca6b6f27342cb77391c8c3462f97b66a53`; seu receipt-2 permanece `6b16e1cb9954ee505a592121d697fb58c56b444e3c430c8360301625ceb4dd82`, ligado à preparação `fa934b8b065880228373d76040527a76fc7cdced9c92ebb69a31891485ccf4fa`. Os hashes desses bytes CAS foram conferidos.

As projeções calculadas, **não gravadas**, são: registros da subfila, 116448380 bytes, SHA-256 `d9e9289e18df4d2db4d9554ca707bc7385025950c20a437daae7d7d58c200c9e`; result-2 correspondente, 29383919 bytes, SHA-256 `52db5c30e794937c45478c8677c47ee85aebbded1789add8d963128c000adb39`. Não são hashes de um novo corpus aceito.

## Menor alteração recomendada

Adicionar em [review_corpus_metadata.py](../../../../../../workbench/src/research_workbench/orchestration/review_corpus_metadata.py) um contrato específico de recibo da transição de identidade e um par preparar/replay, reutilizando `ReviewOperationStore`. O recibo deve vincular o receipt-2 pai, contexto sucessor, projeção de registros, result-2, fila nativa e referências às pendências preservadas. Seu estado agregado deve permanecer `incomplete`, sem `screening_ready`, e ele não pode validar como `CorpusStageReceipt` ou substituir o outcome global por um outcome da subfila.

Antes de gravar, o preparador deve reproduzir o pai por `ReviewCorpusMetadataStageRuntime.replay` (linha 363), validar protocolo/revisão/linhagem e recalcular a partição. Exigir: nenhum candidato toca a partição sem título; o result-2 reproduz exatamente `titled_works` e todos os candidatos; a cobertura de registros é completa e disjunta; as fontes são precisamente as exigidas pelos registros. Se qualquer condição falhar em outro corpus, a ponte deve recusar essa projeção. Isso evita introduzir suporte geral a adjudicar uniões de obras sem título nesta alteração.

Com essas condições, reutilizar sem alteração `DedupeQueueInputs`, `prepare_adjudication_queue` (linha 412), `prepare_dedupe_adjudication` (linha 324), `resolve_dedupe_adjudication` (linha 355), `record_adjudication` (linha 541) e `replay_adjudication` (linha 578). Novos hashes da subfila devem constar dos pedidos; decisões futuras precisam aprovar esse pedido exato. Não reutilizar uma decisão sobre outros bytes. O contexto da subfila deve ser distinto e vinculado ao pai; seu eventual `completed` significa apenas pares adjudicados, nunca corpus concluído. Não conectá-lo diretamente como conclusão de `CORPUS_STAGING` no controller. O pai terminal `incomplete` não é reaberto ou sobrescrito.

Não é necessário ampliar `ScholarlyWork`, `UntitledScholarlyWork`, `DeduplicationResultV3` ou o resolvedor legado para esse recorte comprovado. A ausência de título e seus vínculos ficam preservados no pai e no recibo sucessor. A aquisição real já usa CAS limitado a 512.000.000 bytes (`run-corpus-v3-metadata-successor-1.py:230`, privado); as projeções acima exigem esse perfil de corpus, não o limite de 20 MB da CLI de calibração.

## O que essa ponte resolve

Abertura da fila, reprodução, normalização dos identificadores já reconhecidos, ordenação e preservação dos vínculos são operações determinísticas. A policy-2 atual já agrupa identificadores exatos permitidos quando não há conflito; título igual apenas gera candidato, e componentes com identificadores conflitantes são separados ([deduplication_v2.py:80](../../../../../../workbench/src/research_workbench/workflows/systematic_review/deduplication_v2.py)). Reexecutar a mesma regra não resolve automaticamente candidatos restantes.

`merge`, `distinct` e `defer` continuam escolhas da adjudicação nativa, sujeitas à decisão original do Research Owner sobre pedido e evidência exatos ([adjudication.py:78](../../../../../../workbench/src/research_workbench/workflows/systematic_review/adjudication.py), linha 305). Agrupar cartões de pares, reconhecer uma correspondência sintática arXiv/DOI ou encontrar uma relação editorial explícita ajuda a preparar evidência; não aplica outra regra automática de identidade. Conferência, preprint e periódico continuam preservados como manifestações.

Esta ponte permite revisão e posterior registro **dos pares**. Não registra títulos confirmados, não distingue por si só título ausente de cabeçalho ou livro resenhado e não promove semântica de alias. `DedupeChoice` só contém ID do candidato e disposição: não há campos para uma correção de metadados vinculada a uma nova fonte. Transcrever um título ou registrar a presença de um alias explícito pode ser verificável deterministicamente; decidir sua aplicação ao registro canônico ainda precisa de uma transição de metadados própria, com fonte, campo, predecessor e disposição registrados, sem alterar observações históricas. O mecanismo atual não oferece essa operação.

Mesmo após todos os pares decididos, restam os nove títulos e dez conflitos de prontidão. O caminho legado recusa adjudicação para um corpus com esses conflitos em [review_corpus_stage.py:433](../../../../../../workbench/src/research_workbench/orchestration/review_corpus_stage.py). Portanto, a dependência não é apenas obter cliques humanos: há uma operação de metadados ainda ausente. Não proponho implementá-la junto da ponte de identidade.

## Verificação exigida para a futura alteração

Adicionar casos focados em `test_review_corpus_metadata.py`: projeção completa e sem perda, igualdade de todos os candidatos, recusa quando uma proposta sem título participa de um par, adulteração de pai/contexto/hash/fonte, replay sem escrita e idempotência. Exercitar a subfila pelos testes nativos de adjudicação: escolhas parciais cumulativas, `defer`, contradição transitiva e decisão sobre bytes incorretos. Acrescentar um caso em que todos os pares estão resolvidos, mas as nove pendências continuam nulas e o agregado permanece incompleto. Preservar o teste que proíbe substituir receipt-2 por corpus/adjudicação legados e atualizar os processos de corpus/adjudicação para declarar a semântica limitada da subfila.

Este diagnóstico executou validações de contratos e uma derivação determinística em memória. Não executou a suíte completa, não criou fila CAS, não alterou protocolo, não coletou decisões e não utilizou modelos ou rede. O próximo passo concreto é revisar e implementar somente essa transição vinculada; a preparação dos nove títulos e dez conflitos continua evidência proposta, sem resolução canônica.
