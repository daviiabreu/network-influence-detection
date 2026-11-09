# Mapa priorizado v5.1: agregados do encerramento (28/09/2026)

Esta pasta guarda as saídas agregadas do mapa sistemático priorizado v5.1. São contagens por categoria, o fluxo de triagem, os registros de saturação e as figuras. Nenhuma decisão por obra, título ou resumo sai do estado privado. O relato da execução, com decisões, incidentes e limites, está em [`run-records/2026-09-28-broad-map-v5-1-production.md`](../../run-records/2026-09-28-broad-map-v5-1-production.md).

| Arquivo                                                    | Conteúdo                                                                                         | Origem                                                                                   |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| [`report.md`](report.md)                                   | Fluxo tipo PRISMA e parcelas por dimensão, com intervalos de Wilson, sobre 4.056 obras primárias | `v5_production.py report`, cópia de `production-v5-1/v5-report.md` (SHA-256 `ae891297…`) |
| [`saturation-0014.json`](saturation-0014.json)             | Regra de parada nos lotes 12 a 14, antes da auditoria do restante                                | `production-v5-1/saturation-0014.json` (SHA-256 `61650abf…`)                             |
| [`saturation-0014-audit.json`](saturation-0014-audit.json) | A mesma regra com a auditoria de 400 obras do restante                                           | `production-v5-1/saturation-0014-audit.json` (SHA-256 `be85da14…`)                       |
| [`series.json`](series.json)                               | Série cumulativa por lote (`ic-study.map-saturation-series.v1`)                                  | `production.snapshots` sobre os lotes 1 a 14                                             |
| [`figures/`](figures/manifest.json)                        | M1 (trajetória de saturação), M2 (parcelas por categoria) e a tabela das transições              | `python -m ic_study.analysis.map_saturation_figures --series series.json --out figures`  |
| [`codebook-v1.1.json`](codebook-v1.1.json) | Livro de códigos da extração dos lotes: definições, exemplos e regras de decisão dos dez campos | `production-v5-1/codebook-v1.1.json` (SHA-256 `be492f99…`) |

O código de produção é o do ramo `research/broad-map-v5-production`, no commit `bc55e6d8`. Esse código entrou na integração pelo commit `227b4568`, no merge `e7c3a67c`, com uma única mudança de comportamento: os executores acrescentam falhas ao histórico em vez de sobrescrevê-lo, o que não altera nenhuma saída. O manifesto das figuras vincula a série, as saídas e o commit do estudo.

## Como ler

A triagem foi priorizada por relevância, não um censo. As parcelas descrevem as obras incluídas nos 14 lotes triados, e não a literatura inteira. Os intervalos de Wilson do relatório só têm leitura populacional para a amostra aleatória do restante. A saturação é conceitual: nenhuma categoria nova e deslocamentos de até 2 pp nas parcelas cumulativas. Ela não mede recall.

A regra de parada cumpriu as condições 1 e 2. A condição 3 ficou incompleta: 101 das 400 obras do restante continuam uncertain por falta de resumo (`saturation-0014-audit.json`). O limite superior da estimativa de relevantes não triados conta essas obras como positivas, por isso o intervalo é tão largo.

Sucessor documentado: [`successor-1/`](successor-1/README.md).
