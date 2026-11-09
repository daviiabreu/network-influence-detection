# Resultado das consultas por fonte

A coluna OpenAlex combina Q01–Q10 em título e resumo com o Q03 corrigido. Cada consulta dessa fonte foi intersectada com os 16 identificadores conhecidos; portanto, a posição dentro desse conjunto não é a posição na busca completa. As colunas arXiv e DBLP registram correspondências nas páginas dos pilotos. A lista foi usada para desenvolver as consultas e não é um holdout.

| Seed | Papel | OpenAlex: título/resumo | arXiv: piloto | DBLP: piloto |
| --- | --- | --- | --- | --- |
| axelrod1997 | primário | Q05 | não observado* | não observado* |
| castellano2009qvoter | primário | Q04 | Q04 | não observado* |
| castellano2009rmp | secundário | nenhuma | não observado* | não observado* |
| chuang2024 | primário | Q01, Q10 | Q01†, Q10† | Q10 |
| clifford1973 | sentinela de linhagem | nenhuma | não observado* | não observado* |
| dandekar2013 | primário | Q01, Q08 | Q08 | Q08 |
| deffuant2000 | primário | Q01, Q02 | não observado* | Q02 |
| degroot1974 | primário | Q03 | não observado* | não observado* |
| flache2017 | secundário | Q09 | não observado* | não observado* |
| friedkin1990 | primário | Q03 | não observado* | não observado* |
| hegselmann2002 | primário | Q01, Q02 | não observado* | não observado* |
| holme2006 | primário | Q01, Q06 | Q06 | não observado* |
| lorenz2007 | secundário | Q01, Q02 | Q02 | não observado* |
| martins2008 | primário | Q01, Q05 | Q05 | não observado* |
| moussaid2013 | primário | Q01, Q09 | Q01, Q09 | não observado* |
| sznajd2000 | primário | Q01, Q04 | Q04 | não observado* |

*“Não observado” nos pilotos arXiv/DBLP não prova ausência na fonte, pois algumas consultas atingiram o teto. † indica coincidência de título ainda sujeita a adjudicação. O OpenAlex mede pertinência por IDs conhecidos; arXiv/DBLP examinam páginas da busca irrestrita. São diagnósticos diferentes, não estimativas diretamente comparáveis de recall.

No OpenAlex, foram recuperados 12/12 seeds primários e 2/3 secundários. Castellano 2009 (review) permanece na rota suplementar de seed secundário; Clifford 1973 continua visível como sentinela de linhagem. Nenhum resultado foi alterado para declarar cobertura.

As dez famílias permanecem no protocolo; um conjunto mínimo que cobre apenas os seeds conhecidos não representa toda a área. Os relatórios e seus hashes, os totais por consulta, as requisições e os hashes dos bytes estão em [openalex-evidence.json](openalex-evidence.json). Todos os seis diagnósticos do OpenAlex tiveram resultado offline idêntico ao online.

O [piloto do arXiv](arxiv-evidence.json) é uma busca sem filtro por identificador, limitada a duas páginas por consulta. Recuperou 1.056 registros em 14 páginas, antes de deduplicação. Sete consultas esgotaram os resultados; Q01, Q03 e Q04 atingiram o teto de 200 registros. Há dez pares seed/consulta com coincidência, incluindo coincidências de título que exigem adjudicação. A reprodução offline foi idêntica. Esses dados não autorizam declarar ausência para os pares ainda incompletos.

Os pilotos anteriores permanecem vinculados na evidência. A falha do parser do arXiv foi reproduzida em respostas que declaravam `itemsPerPage=100` com menos entradas na página final. O sucessor aceita essa forma apenas quando todas as entradas restantes estão presentes. A interpretação usa os bytes observados e o mapeamento entre paginação e `max_results` no [manual oficial](https://github.com/arXiv/arxiv-docs/blob/develop/source/help/api/user-manual.md#3112-start-and-max_results-paging).

## DBLP: diagnóstico concluído

Os blocos com timeout no servidor foram divididos sem mudar a união dos termos. As respostas expuseram DOIs múltiplos e a pontuação SICI; as duas correções preservam identificadores e mantêm as falhas anteriores nos respectivos journals. A projeção abaixo seleciona cada consulta de seu diagnóstico mais recente e vinculado. Não constitui uma aquisição única nem um corpus aprovado.

| Consulta | Total informado | Registros no resultado | Estado |
| --- | ---: | ---: | --- |
| Q01 | 1267 | 200 | teto de 200 |
| Q02 | 159 | 159 | esgotada |
| Q03A | 90 | 90 | esgotada |
| Q03B | 26 | 26 | esgotada |
| Q03C | 0 | 0 | esgotada |
| Q04A | 101 | 101 | esgotada |
| Q04B | 129 | 129 | esgotada |
| Q05 | 14 | 14 | esgotada |
| Q06A | 1164 | 200 | teto de 200 |
| Q06B | 9 | 9 | esgotada |
| Q07 | 12 | 12 | esgotada |
| Q08 | 61 | 61 | esgotada |
| Q09 | 1068 | 200 | teto de 200 |
| Q10 | 318 | 200 | teto de 200 |

Foram preservados 1.401 registros em 21 páginas aceitas, antes de deduplicação. Quatro consultas continuam incompletas pelo teto deliberado do piloto. Os pares confirmados como ausentes são apenas das consultas esgotadas; nenhuma ausência global ou recall do DBLP é afirmado.

A [projeção rastreável](dblp-evidence-combined.json) registra a origem de cada consulta e célula. Os resultados online e offline de [v2](dblp-evidence-v2.json), [v3](dblp-evidence-v3.json), [v4](dblp-evidence-v4.json) e [v5](dblp-evidence-v5.json) foram idênticos. Em v4, a primeira página Q04b permaneceu no checkpoint, mas a falha da segunda fez o harness emitir um outcome de erro sem registros; a projeção usa o sucessor e não reescreve esse resultado. As notas de [divisão dos blocos](dblp-split-pilot-v3.md) e [correções do adaptador](../../../../../../docs/research/dblp-sparql-adapter-2026-09-07.md) preservam as causas e os hashes.
