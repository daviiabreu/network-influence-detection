# Glossário e legendas externas

## Unidades e leitura

Uma observação é uma ocorrência preservada na busca; um registro-fonte é a identidade bibliográfica de um provedor. Uma proposta deduplicada é uma unidade candidata antes da resolução tardia de identidade. Uma obra distinta é o resultado da identidade adotada, que pode reunir várias propostas ou manifestações. “Triadas”, “excluídas” e “incertas” no fluxo contam propostas, enquanto o conjunto mapeado conta obras distintas dos lotes. As reduções de identidade não são novas exclusões.

O conjunto histórico mapeado contém 4.056 obras, das quais 70 codificadas como secundárias. O conjunto sucessor contém 3.986 após esse filtro; sua elegibilidade completa continua pendente. “Primárias” nos eixos originais e no campo herdado `included_primary` deve ser lido com essa qualificação.

Multilabel significa que uma obra pode receber mais de um código de uma dimensão. Cada parcela usa todas as obras do conjunto como denominador; as parcelas podem somar mais de 100%. No histórico, os códigos de resultados relatados somam aproximadamente 149,6%. Isso não é uma partição de probabilidades.

`not_reported` significa informação insuficiente no título/resumo para aquele campo. Não comprova ausência no trabalho completo, nem substitui extração pendente. `other_*` registra algo identificável fora das categorias listadas. `no_empirical_data_reported` é a classificação de descrição teórica/computacional sem dados empíricos relatados no título/resumo; difere da impossibilidade de determinar uso de dados, expressa por `not_reported`.

O livro de códigos classifica propriedades padrão de modelos canônicos nomeados, salvo indicação contrária no título/resumo: confiança limitada implica opinião contínua e assimilação limitada; média linear implica contínua e assimilação; modelos voter, majority rule, Sznajd e q-voter implicam discreta e assimilação; Axelrod implica representação por vetores de traços. A regra é uma simplificação de codificação, não confirmação por leitura integral.

Wilson é o intervalo bilateral de 95% de uma proporção. Nos lotes priorizados, sua apresentação é descritiva. Na amostra aleatória do restante, os limites são escalados para as propostas não triadas; o envelope combina dois cenários e não mede recall. Ponto percentual (pp) é a diferença absoluta entre duas porcentagens.

## Dimensões e códigos

As definições detalhadas permanecem no [codebook v1.1 histórico](../codebook-v1.1.json). Os nomes em português abaixo são legendas de leitura, sem mudar os códigos ou as extrações.

| Dimensão em PT-BR | Campo técnico | Códigos e leitura |
| --- | --- | --- |
| Família de modelo | `model_family` | Confiança limitada (`bounded_confidence`); média linear (`linear_averaging`); família voter (`voter`); outra família identificada (`other_named_family`); não relatada (`not_reported`). |
| Mecanismo de influência | `influence_mechanism` | Assimilação (`assimilation`); assimilação limitada por similaridade (`bounded_assimilation`); aprendizado social (`social_learning`); repulsão (`repulsion`); outro mecanismo (`other_mechanism`); não relatado (`not_reported`). |
| Representação de opinião | `opinion_representation` | Contínua (`continuous`); discreta (`discrete`); outra representação estruturada (`other_representation`); não relatada (`not_reported`). |
| Topologia de interação | `network_topology` | Completa ou mistura homogênea (`complete`); espacial (`spatial`); rede sintética (`synthetic_network`); adaptativa (`adaptive_network`); outra topologia identificada (`other_topology`); não relatada (`not_reported`). |
| Resultados relatados | `reported_outcomes` | Consenso (`consensus`); diversidade persistente (`persistent_diversity`); polarização (`polarization`); outro resultado (`other_outcome`); não relatado (`not_reported`). |
| Desenho de estudo | `study_design` | Analítico (`analytical`); simulação (`simulation`); empírico (`empirical`); secundário (`secondary`); não relatado (`not_reported`). |
| Método de validação | `validation_method` | Analítico (`analytical`); numérico (`numerical`); empírico agregado (`empirical_macro`); empírico individual (`empirical_micro`); robustez ou sensibilidade (`robustness`); não relatado (`not_reported`). |
| Fundamentação empírica | `empirical_grounding` | Experimento com pessoas (`experiment`); dados observacionais (`observational_data`); outros dados (`other_data`); sem dados empíricos relatados no título/resumo (`no_empirical_data_reported`); indeterminado no título/resumo (`not_reported`). |
| Artefatos de reprodução | `reproducibility_artifacts` | Disponibilidade de dados relatada (`data`); disponibilidade de código, software ou implementação relatada (`environment`); disponibilidade não relatada (`not_reported`). O código `environment` não certifica um ambiente executável. |
| Lacunas declaradas | `evidence_gaps` | Validação agregada (`macro_level_validation`); comparação de modelos (`model_comparison`); outra lacuna explicitamente declarada (`other_author_stated_gap`); lacuna não relatada (`not_reported`). |

## M1 — trajetória histórica de saturação

Legenda externa de [M1 original](../figures/M1_saturation_trajectory.png): deslocamento máximo, em pp, entre parcelas cumulativas de lotes consecutivos no conjunto histórico de 4.056 obras ao final, incluindo 70 secundárias. Cada marca verde de `passes` indica apenas uma transição compatível com a condição 2: deslocamento de até 2 pp, nenhuma categoria nova e quadro com o mesmo identificador. A primeira janela de duas transições termina no lote 13. A figura não representa a condição 3, não demonstra recall e não significa aprovação da regra completa. A auditoria continua incompleta, com 101 incertas e `stop=false`. A trajetória filtrada é publicada numericamente em [comparison.md](comparison.md), sem redesenhar ou alterar M1.

## M2 — parcelas históricas por categoria

Legenda externa de [M2 original](../figures/M2_category_shares.png): parcelas cumulativas extraídas de título/resumo, com codificação multilabel. O denominador de cada categoria é o total de obras mapeadas até aquele lote, encerrando em 4.056, incluindo 70 secundárias. Os eixos históricos que dizem primárias não certificam essa população. Ausência de relato não demonstra ausência no texto integral; propriedades de modelos canônicos podem ser codificadas por definição. A seleção priorizada impede leitura como prevalência na literatura. O sucessor publica numeradores e parcelas sem secundárias, com denominador final 3.986, em [category-comparison.csv](category-comparison.csv).

## T_M1 — transições históricas

Legenda externa da [tabela original em CSV](../figures/T_M1_transitions.csv) e [LaTeX](../figures/T_M1_transitions.tex): cada linha descreve uma transição entre snapshots históricos e o código de maior deslocamento. `passes` se refere à transição individual; saturação provisória exige uma janela de duas transições e o mínimo numérico de 500. A categoria nova detectada na série é `reproducibility_artifacts/data`, no lote 4. Ausência de categoria nova não prova sua ausência no universo. A condição 3 e as 101 incertas do restante não estão na tabela; a regra completa permanece não satisfeita. Esta ressalva deve acompanhar a tabela renderizada, não apenas seu comentário de origem.
