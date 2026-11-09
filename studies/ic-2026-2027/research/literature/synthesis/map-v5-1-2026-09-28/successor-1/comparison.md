# Reconciliação e comparação dos agregados

Contagens verificadas em 30/09/2026, sem novos juízos. As inclusões, exclusões e incertezas desta tabela contam propostas triadas; as duas colunas de identidade contam reduções entre propostas incluídas e obras distintas. As novas obras são atribuídas à primeira fase em que aparecem, na ordem calibração, camada 0, lotes e restante. Essa atribuição serve à reconciliação, sem alterar a ordem histórica de seleção. “Total final” é o acumulado de inclusões distintas após cada fase. Exclusões e incertezas continuam em unidade de proposta, sem uma fusão presumida.

## Fluxo por fase

| Fase | Triadas | Incluídas | Excluídas | Incertas | Redução dentro da fase | Sobreposição com fases anteriores | Novas distintas | Total final |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Calibração (duas coortes) | 400 | 48 | 247 | 105 | 0 | 0 | 48 | 48 |
| Camada 0 | 1017 | 48 | 857 | 112 | 2 | 0 | 46 | 94 |
| Lote 1 | 500 | 307 | 14 | 179 | 0 | 0 | 307 | 401 |
| Lote 2 | 500 | 386 | 6 | 108 | 69 | 0 | 317 | 718 |
| Lote 3 | 500 | 417 | 9 | 74 | 56 | 11 | 350 | 1068 |
| Lote 4 | 500 | 407 | 6 | 87 | 43 | 10 | 354 | 1422 |
| Lote 5 | 500 | 390 | 14 | 96 | 34 | 9 | 347 | 1769 |
| Lote 6 | 500 | 362 | 19 | 119 | 37 | 15 | 310 | 2079 |
| Lote 7 | 500 | 353 | 16 | 131 | 30 | 8 | 315 | 2394 |
| Lote 8 | 500 | 345 | 22 | 133 | 37 | 8 | 300 | 2694 |
| Lote 9 | 500 | 318 | 24 | 158 | 22 | 14 | 282 | 2976 |
| Lote 10 | 500 | 309 | 42 | 149 | 18 | 6 | 285 | 3261 |
| Lote 11 | 500 | 296 | 51 | 153 | 22 | 5 | 269 | 3530 |
| Lote 12 | 500 | 243 | 68 | 189 | 23 | 6 | 214 | 3744 |
| Lote 13 | 500 | 247 | 60 | 193 | 31 | 8 | 208 | 3952 |
| Lote 14 | 500 | 231 | 83 | 186 | 25 | 8 | 198 | 4150 |
| Amostra do restante | 400 | 17 | 282 | 101 | 0 | 0 | 17 | 4167 |
| Total | 8.817 | 4.724 | 1.820 | 2.273 | 449 | 108 | 4.167 | 4.167 |

As 557 propostas não explicadas pelo fluxo publicado correspondem exatamente a 449 reduções dentro das fases + 108 sobreposições entre fases. A resolução integrada de identidade validou as auditorias e seus vínculos nativos; não se inferiu a causa a partir da diferença aritmética. Assim, 4.724 + 1.820 + 2.273 = 8.817 propostas triadas e 4.724 − 557 = 4.167 inclusões distintas. As 35.089 não triadas completam as 43.906 propostas e não recebem razões de exclusão.

A decomposição das inclusões distintas é 48 da calibração + 46 da camada 0 + 4.056 dos lotes + 17 do restante = 4.167, sem sobreposição entre esses quatro grupos. A camada 0 publicada conta 48 propostas incluídas; duas fusões resultam em 46 obras. Portanto, a diferença publicada de 63 é 48 da calibração + 17 do restante − 2 da identidade na camada 0, e não uma fase desconhecida.

## Recuperações já adotadas

As recuperações históricas da camada 0 e dos lotes 1–3 foram aplicadas pela função integrada `effective_adopted`, com verificação dos hashes de adoção e evidência. Elas promovem 34 antigas incertas a inclusão e 46 a exclusão, reduzindo as incertezas em 80. Nenhuma recuperação foi executada nesta entrega.

| Fase | Inclusões antes da recuperação | Inclusões efetivas | Redução de identidade, incluindo sobreposição | Acréscimo distinto |
| --- | ---: | ---: | ---: | ---: |
| Camada 0 | 45 | 48 | 2 | 46 |
| Lote 1 | 296 | 307 | 0 | 307 |
| Lote 2 | 373 | 386 | 69 | 317 |
| Lote 3 | 410 | 417 | 67 | 350 |
| Lote 14, sem recuperação | 231 | 231 | 33 | 198 |

## Razões de exclusão e incertezas

O estado adotado não contém um campo canônico de motivo final para todas as exclusões. Foi possível verificar um motivo estruturado comum a A e B em 1.171 exclusões adotadas por acordo direto. As restantes 649, incluindo as 247 da calibração, ficam com motivo final não verificado nesta entrega. Não se transformaram justificativas livres ou sugestões de referências em novos motivos de exclusão.

| Motivo estruturado verificado nos acordos A/B | Propostas excluídas |
| --- | ---: |
| Sem modelo computacional (`no_computational_model`) | 1.014 |
| Fora do domínio de opinião humana (`not_human_opinion_domain`) | 133 |
| Sem produto acadêmico (`no_scholarly_product`) | 12 |
| Fora de data ou idioma (`outside_date_or_language`) | 12 |
| Motivo final não verificado | 649 |
| Total | 1.820 |

Entre as 2.273 incertas, 2.147 não têm resumo nas tarefas vinculadas, 71 têm resumo e 55 não tiveram disponibilidade verificada. Esses 55 pertencem à primeira coorte de calibração; não foram abertas suas tarefas externas ao conjunto autorizado. A ausência de resumo é uma condição observável da tarefa, não uma nova interpretação do motivo individual. A amostra do restante mantém suas 101 incertas, todas sem resumo nas tarefas vinculadas.

## Denominadores por lote

O conjunto histórico de 4.056 obras mapeadas contém 70 codificadas como secundárias. O sucessor retira toda obra com `study_design/secondary` na união final de códigos das manifestações, em todos os prefixos da série. As demais contribuições de cada prefixo continuam sendo somente as disponíveis até aquele lote. O filtro não certifica todas as remanescentes como primárias elegíveis e não transfere ou recodifica os secundários na camada 0.

| Lote | Conjunto histórico | Secundárias retiradas | Conjunto sem secundárias codificadas |
| --- | ---: | ---: | ---: |
| 1 | 307 | 7 | 300 |
| 2 | 624 | 18 | 606 |
| 3 | 974 | 20 | 954 |
| 4 | 1328 | 25 | 1303 |
| 5 | 1675 | 29 | 1646 |
| 6 | 1985 | 34 | 1951 |
| 7 | 2300 | 38 | 2262 |
| 8 | 2600 | 41 | 2559 |
| 9 | 2882 | 47 | 2835 |
| 10 | 3167 | 51 | 3116 |
| 11 | 3436 | 59 | 3377 |
| 12 | 3650 | 62 | 3588 |
| 13 | 3858 | 66 | 3792 |
| 14 | 4056 | 70 | 3986 |

## Comparação das 49 parcelas

Todas as parcelas usam o denominador indicado na tabela anterior. Os limites de Wilson completos estão em [category-comparison.csv](category-comparison.csv) e em [category-shares-without-secondary.json](category-shares-without-secondary.json). As parcelas dos lotes priorizados e seus limites são descritivos; não estimam prevalência na literatura. A diferença é sucessor menos histórico, em pontos percentuais.

| Dimensão / código | Contagem histórica | Contagem sucessora | Histórico, % | Sucessor, % | Diferença, pp |
| --- | ---: | ---: | ---: | ---: | ---: |
| `empirical_grounding/experiment` | 76 | 72 | 1,8738 | 1,8063 | -0,067445 |
| `empirical_grounding/no_empirical_data_reported` | 3139 | 3111 | 77,3915 | 78,0482 | +0,656650 |
| `empirical_grounding/not_reported` | 302 | 268 | 7,4458 | 6,7235 | -0,722227 |
| `empirical_grounding/observational_data` | 465 | 459 | 11,4645 | 11,5153 | +0,050807 |
| `empirical_grounding/other_data` | 117 | 117 | 2,8846 | 2,9353 | +0,050658 |
| `evidence_gaps/macro_level_validation` | 32 | 29 | 0,7890 | 0,7275 | -0,061408 |
| `evidence_gaps/model_comparison` | 14 | 12 | 0,3452 | 0,3011 | -0,044114 |
| `evidence_gaps/not_reported` | 3269 | 3226 | 80,5966 | 80,9333 | +0,336619 |
| `evidence_gaps/other_author_stated_gap` | 776 | 752 | 19,1321 | 18,8660 | -0,266119 |
| `influence_mechanism/assimilation` | 1462 | 1436 | 36,0454 | 36,0261 | -0,019274 |
| `influence_mechanism/bounded_assimilation` | 835 | 819 | 20,5868 | 20,5469 | -0,039871 |
| `influence_mechanism/not_reported` | 1001 | 976 | 24,6795 | 24,4857 | -0,193787 |
| `influence_mechanism/other_mechanism` | 983 | 972 | 24,2357 | 24,3853 | +0,149649 |
| `influence_mechanism/repulsion` | 310 | 307 | 7,6430 | 7,7020 | +0,058959 |
| `influence_mechanism/social_learning` | 251 | 244 | 6,1884 | 6,1214 | -0,066938 |
| `model_family/bounded_confidence` | 765 | 749 | 18,8609 | 18,7908 | -0,070179 |
| `model_family/linear_averaging` | 501 | 493 | 12,3521 | 12,3683 | +0,016218 |
| `model_family/not_reported` | 950 | 930 | 23,4221 | 23,3317 | -0,090430 |
| `model_family/other_named_family` | 1509 | 1479 | 37,2041 | 37,1049 | -0,099275 |
| `model_family/voter` | 638 | 621 | 15,7298 | 15,5795 | -0,150255 |
| `network_topology/adaptive_network` | 379 | 375 | 9,3442 | 9,4079 | +0,063746 |
| `network_topology/complete` | 449 | 445 | 11,0700 | 11,1641 | +0,094055 |
| `network_topology/not_reported` | 1965 | 1911 | 48,4467 | 47,9428 | -0,503946 |
| `network_topology/other_topology` | 913 | 907 | 22,5099 | 22,7546 | +0,244779 |
| `network_topology/spatial` | 302 | 298 | 7,4458 | 7,4762 | +0,030407 |
| `network_topology/synthetic_network` | 490 | 485 | 12,0809 | 12,1676 | +0,086719 |
| `opinion_representation/continuous` | 1356 | 1329 | 33,4320 | 33,3417 | -0,090257 |
| `opinion_representation/discrete` | 1002 | 980 | 24,7041 | 24,5861 | -0,118091 |
| `opinion_representation/not_reported` | 1367 | 1338 | 33,7032 | 33,5675 | -0,135670 |
| `opinion_representation/other_representation` | 484 | 470 | 11,9329 | 11,7913 | -0,141669 |
| `reported_outcomes/consensus` | 1499 | 1487 | 36,9576 | 37,3056 | +0,347976 |
| `reported_outcomes/not_reported` | 358 | 327 | 8,8264 | 8,2037 | -0,622717 |
| `reported_outcomes/other_outcome` | 2638 | 2618 | 65,0394 | 65,6799 | +0,640432 |
| `reported_outcomes/persistent_diversity` | 766 | 753 | 18,8856 | 18,8911 | +0,005517 |
| `reported_outcomes/polarization` | 808 | 793 | 19,9211 | 19,8946 | -0,026473 |
| `reproducibility_artifacts/data` | 7 | 7 | 0,1726 | 0,1756 | +0,003031 |
| `reproducibility_artifacts/environment` | 38 | 35 | 0,9369 | 0,8781 | -0,058810 |
| `reproducibility_artifacts/not_reported` | 4016 | 3949 | 99,0138 | 99,0718 | +0,057944 |
| `study_design/analytical` | 2022 | 2010 | 49,8521 | 50,4265 | +0,574422 |
| `study_design/empirical` | 457 | 453 | 11,2673 | 11,3648 | +0,097518 |
| `study_design/not_reported` | 503 | 503 | 12,4014 | 12,6192 | +0,217786 |
| `study_design/secondary` | 70 | 0 | 1,7258 | 0,0000 | -1,725838 |
| `study_design/simulation` | 2325 | 2304 | 57,3225 | 57,8023 | +0,479823 |
| `validation_method/analytical` | 1940 | 1928 | 47,8304 | 48,3693 | +0,538918 |
| `validation_method/empirical_macro` | 185 | 184 | 4,5611 | 4,6162 | +0,055013 |
| `validation_method/empirical_micro` | 147 | 145 | 3,6243 | 3,6377 | +0,013472 |
| `validation_method/not_reported` | 667 | 625 | 16,4448 | 15,6799 | -0,764894 |
| `validation_method/numerical` | 2243 | 2224 | 55,3008 | 55,7953 | +0,494495 |
| `validation_method/robustness` | 484 | 481 | 11,9329 | 12,0672 | +0,134296 |

A maior mudança absoluta é a retirada da própria categoria secundária: −1,725838 pp. Nas outras 48 categorias, a maior mudança é −0,764894 pp em ausência de método de validação relatado (`validation_method/not_reported`). Isso caracteriza apenas o efeito do filtro de secundários, sem validar as correções de elegibilidade pendentes.

## Transições de saturação

| Transição | Deslocamento máximo histórico, pp | Deslocamento máximo sucessor, pp |
| --- | ---: | ---: |
| 1→2 | 9,485405 | 9,844884 |
| 2→3 | 7,061154 | 7,175623 |
| 3→4 | 8,261949 | 8,334339 |
| 4→5 | 6,639948 | 6,605888 |
| 5→6 | 4,418662 | 4,326005 |
| 6→7 | 4,069981 | 4,125477 |
| 7→8 | 2,946488 | 2,923162 |
| 8→9 | 2,764853 | 2,776341 |
| 9→10 | 2,562391 | 2,572171 |
| 10→11 | 2,226798 | 2,221685 |
| 11→12 | 1,369034 | 1,399344 |
| 12→13 | 1,370658 | 1,351022 |
| 13→14 | 1,197389 | 1,204718 |

O mínimo numérico de 500 é atingido no lote 2 em ambas as séries (624 e 606). A primeira janela de duas transições compatíveis com a condição 2 termina no lote 13 em ambas. A aparição de `reproducibility_artifacts/data` no lote 4 permanece. As definições do quadro têm o mesmo identificador nas transições finais, mas a proveniência do codebook do lote 1 continua pendente. A condição 1 exige ainda primárias elegíveis e identidade; os limiares numéricos não resolvem os casos de elegibilidade.

A auditoria de 400 propostas continua ligada ao snapshot histórico. O sucessor não religa esse recibo à série filtrada nem revalida a condição 3. As 101 incertas e `stop=false` são preservados; o encerramento permanece operacional, com cobertura incompleta.
