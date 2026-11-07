# Mapa das afirmações dos pilotos exploratórios

16/09/2026. Os dois pilotos terminaram suas matrizes previstas e recomendaram
encerrar as expansões delimitadas. A evidência permite conservar os resultados
abaixo; ainda não sustenta uma pergunta final da IC. Este mapa organiza os
artefatos existentes e a conferência atual. Não registra aceite científico,
novidade ou superioridade geral de uma linha de pesquisa.

[A: fragmentação](../../experiments/exploratory/fragmentation-pilot-v1/README.md)
examina observadores de parada no DW simétrico em redes fixas.
[B: previsão probabilística](../../experiments/exploratory/probabilistic-forecast-pilot-v1/README.md)
compara avaliações de histogramas sintéticos com população reinicializada a
cada onda. Os mecanismos, unidades e critérios são diferentes; não há ranking
quantitativo válido entre os resultados dos dois pilotos.

## Afirmações e fronteiras

Os seletores abaixo se referem ao `analysis-input.json` de
[A](../../experiments/exploratory/fragmentation-pilot-v1/analysis-input.json) ou
[B](../../experiments/exploratory/probabilistic-forecast-pilot-v1/analysis-input.json).
Os manifestos de [A](../../experiments/exploratory/fragmentation-pilot-v1/run-manifest.json)
e [B](../../experiments/exploratory/probabilistic-forecast-pilot-v1/run-manifest.json)
identificam por hash os JSONLs completos. Índices de trajetória começam em zero.

| ID | Observação sustentada | Localizador e unidade | Limite da interpretação |
| --- | --- | --- | --- |
| A1 | 148 trajetórias: 142 certificadas e seis censuradas. O principal contém 112, das quais 108 certificadas e quatro censuradas. | A `/phase_counts`; JSONLs `benchmark`, `control`, `pilot`, `sensitivity`, campo `result.status`. | Os braços e a sensibilidade reutilizam entradas; 148 não representa redes independentes. Censura não é ausência de discrepância. |
| A2 | No principal, somente o caso 35 apresentou cruzamento posterior e partição final diferente para o observador que conserva grupos antigos. | A `/phase_counts/pilot/cached`, `/adverse_case`; JSONL `pilot`, `trial_index=35`. | Uma ocorrência nesse desenho; não estima uma frequência populacional de falha. |
| A3 | O caso 35 declarou 13 grupos na tentativa 10.500; o estado final certificado tinha 12, na tentativa 10.790. Na sensibilidade pareada, os três observadores pararam em 12.270 com 12 grupos. | A `/adverse_case`; JSONLs `pilot:35` e `sensitivity:3`, `result.cached_stop`, `diameter_stop`, `certified_stop`, `endpoint_partition`. | A repetição usa o mesmo caso com tolerância menor. Não prova que reduzir a tolerância resolva o problema em geral. |
| A4 | Nenhuma das 108 paradas principais do observador que recalcula os componentes apresentou cruzamento posterior ou partição final diferente. | A `/phase_counts/pilot/diameter`; JSONL `pilot`, observações com `diameter_stop` presente. | As quatro censuras não chegaram a essa parada e ficam fora do denominador. Zero ocorrências observadas não demonstra correção universal. |
| B1 | Há 1.440 linhas analíticas: 480 principais, 480 repetições de precisão e 480 confirmações. São 960 identidades de dados distintas; os 32 benchmarks ficam separados. | B manifesto `/runs`; identidade de dados e conjuntos completos conferidos pelo validador offline. | A repetição de precisão não aumenta a quantidade de dados. Integridade das identidades não prova independência estatística dos sorteios. |
| B2 | Nenhuma das oito células dinâmicas satisfez o contraste central no principal, precisão ou confirmação. | B `/primary_criterion_cells_by_phase` e `/criterion_replicated_all_three`; 16 células por lote, oito dinâmicas, 30 trajetórias por célula. | O critério é simultaneamente ES favorável e média W1 desfavorável além de 1% do baseline, pelos intervalos pontuais. O resultado negativo é restrito a este desenho. |
| B3 | Na confirmação sem atualização, ES selecionou dinâmica em 40 de 120 trajetórias. No principal foram 42/120 e na precisão 36/120. | B `/controls`, células com `truth=constant`; JSONLs analíticos, `selected_on_train.energy`. | Duas ondas de treino tornam a seleção frágil. Escolher dinâmica não demonstra influência causal nem risco esperado menor que o oracle. |

As observações A2–A4 descrevem os registros preservados. O agregador não foi
usado como prova de que toda partição seja matematicamente correta. A
[revisão original de A](../../experiments/exploratory/fragmentation-pilot-v1/results-review.md)
registra a reconstrução independente das partições e a regeneração dos dois
casos centrais; esta conferência atual não repetiu as simulações. A
[revisão original de B](../../experiments/exploratory/probabilistic-forecast-pilot-v1/results-review.md)
registra seu escopo de reprodução numérica e os limites dos intervalos.

## O que falta para usar isso na escolha do tema

A serve como evidência de uma diferença entre implementações do observador,
com alcance empírico estreito. B não alcançou seu próprio critério de
continuidade. Preservar esses resultados evita retomar como promessa de artigo
uma hipótese que o piloto já delimitou, mas nenhum deles refuta uma área inteira.

Uma próxima pergunta precisa ligar uma lacuna da síntese bibliográfica a uma
contribuição verificável de modelagem matemática, com hipótese, unidade de
análise, dados e critério de abandono definidos. O corpus, a calibração e a
síntese da revisão continuam pendentes no
[acompanhamento da entrega](../../../../docs/research/systematic-review-delivery.md).
Não se deve ampliar parâmetros dos pilotos concluídos para procurar um sinal
favorável; outra campanha exige justificativa e protocolo sucessor.

As venues permanecem comparáveis pelo
[inventário exploratório](../venues/search-design/2026-09-11-broad-web/reviewed-results.md)
e pelas [checagens de política](../venues/source-checks/2026-09-12-review-summary.md).
A preferência registrada é participação remota de nível pelo menos 2, com
prioridade aos níveis maiores. A adequação ao artigo continua adiada até existir
um artigo; esses pilotos não selecionam uma venue.

## Conferência e identidade das fontes

Em 16/09, o validador `ic_study.validation.experiments.validate_experiment`
reabriu os nove objetos completos e seus vínculos de revisão, ambiente e
código. Os contadores A1–A4 foram recalculados das linhas, mantendo censuras.
Os três lotes analíticos de B foram resumidos novamente pela implementação
`ic_study.analysis.forecast_pilot.summarize` e coincidiram integralmente com
`all_cell_summaries`; o contraste B2 foi aplicado novamente aos intervalos e
baselines. B3 foi contado diretamente em `selected_on_train`. Isso verifica a
reprodução dos resumos com os scores retidos; não constitui uma auditoria
independente do algoritmo de scoring, nova simulação ou nova medição de tempo.

O recibo privado `autonomous-review-20260915/audits/exploratory-claim-audit-v1.json`
tem SHA-256 `cbe901afb1800a50501fe35df5a86cef7cc1ce2f9a666e3f8b5619e68131ace7`.
Todos os artefatos concluídos permaneceram inalterados. Para reproduzir a
integridade em outra máquina, use o
[CLI de validação offline](../../../../docs/specs/offline-experiment-validation.md)
com cada manifesto e os objetos por hash. Para conferir as afirmações, aplique
os seletores da tabela aos JSONLs validados; B2 exige o limite superior da
diferença de ES abaixo de −1% do baseline e o limite inferior da diferença de
média W1 acima de +1%, na mesma célula e em cada lote.

| Fonte | SHA-256 A | SHA-256 B |
| --- | --- | --- |
| `run-manifest.json` | `14161a72a02036264e0e99eb75782c94a5a1765bd8c56d6e110c7c8c2f7b30e5` | `0021bcc6c7b433b72bd7c23fe8120e8062e3cd1a703b534d9fb06209895bf60c` |
| `analysis-input.json` | `7422ee1e161825ecc768ba840559ff64e5626aeda3396d24683af2e952af4a01` | `376fec9728358d1f26ca9f42b5beb3e21afb3395031f6ed5aec19e7326d619cb` |
| `protocol.md` | `5811b352c68c9ebb57d6072c1a1100f4d14f11831a861b603ae5aaf47b541278` | `53cda076c6c818792a7331bcde1f631dcabffe72fefaf1b540041b4fbfb72150` |
| `spec.json` | `4fc30997b27ee759e69e39e4a922a8c79f2342367cb29a664639bafcb37efe8c` | `7e8e0d4b8d61a2d64e3b9d32102ab905045d4d583fad40f5c71212ac4b3f054b` |
| `results-review.md` | `546ae4524931a20fa0875d42e5a39fb2363b17aa8613df602268cbca7b1f7423` | `f0df5b2ab630c049f6cec5451ed58817c1802b238b77cac8b4e1d85d0ad97faa` |

A revisão isolada deste mapa reabriu os nove JSONLs e os hashes das fontes,
recontou A1–A4 e B1/B3 e recalculou B2 com uma implementação independente das
médias pareadas, intervalos t e limiar de 1%. Não encontrou divergências nem
links locais quebrados. O relatório privado é
`autonomous-review-20260915/audits/exploratory-claim-map-review.md`.
Essa revisão por agente não constitui aceite científico do Research Owner.
