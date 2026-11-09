# Sucessor 1 do mapa sistemático priorizado v5.1

Preparado em 30/09/2026 sobre `8c3f667d2c972126a4d8d943f8a3b615880eafc4`, em resposta aos achados A1–A7 da revisão do pacote de 28/09. Este é um sucessor documental e de agregação, sujeito à revisão do coordenador. Não constitui ratificação do protocolo nem nova decisão de elegibilidade. Os artefatos concluídos do [pacote histórico](../README.md) e o [run-record](../../../run-records/2026-09-28-broad-map-v5-1-production.md) permanecem preservados.

O denominador histórico é um conjunto mapeado de 4.056 obras que contém 70 codificadas como secundárias. A projeção sucessora contém 3.986 obras após retirar essas 70 de todos os snapshots, sem mudar juízos por obra. As correções de elegibilidade já apontadas continuam pendentes. A auditoria do restante mantém 101 incertas; o mapa foi encerrado operacionalmente com cobertura incompleta e regra de parada não satisfeita.

| Documento ou agregado | Conteúdo |
| --- | --- |
| [report.md](report.md) | Métodos, interpretação corrigida, limites e tratamento de A1–A7 |
| [comparison.md](comparison.md) | Reconciliação por fase, razões agregadas verificáveis, 49 parcelas e transições |
| [PRISMA-ScR.md](PRISMA-ScR.md) | Checklist dos 22 itens, com cobertura e pendências |
| [glossary-and-captions.md](glossary-and-captions.md) | Vocabulário em PT-BR, códigos e legendas externas para as figuras históricas |
| [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | Revisões históricas, ambiente, instruções de reprodução e limites verificados |
| [flow-reconciliation.json](flow-reconciliation.json) | Contagens por fase e reduções de identidade |
| [series-without-secondary.json](series-without-secondary.json) | Série agregada filtrada; o campo herdado `included_primary` não certifica elegibilidade |
| [category-shares-without-secondary.json](category-shares-without-secondary.json) | Parcelas e Wilson descritivo após o filtro |
| [category-comparison.csv](category-comparison.csv) | Todas as parcelas originais e sucessoras, contagens e limites |
| [denominators-comparison.json](denominators-comparison.json) | Denominadores e secundárias retiradas por lote |
| [stopping-comparison.json](stopping-comparison.json) | Condições numéricas 1–2, auditoria não revalidada e dois cenários do restante |
| [calibration-round2-aggregates.json](calibration-round2-aggregates.json) | Métricas agregadas de A/B e contagens por decil da segunda coorte |
| [provenance.json](provenance.json) | Hashes de entradas e saídas e revisões do recálculo |
| [rebuild_aggregates.py](rebuild_aggregates.py) | Contagem e agregação offline, com verificação dos originais |
| [verification.md](verification.md) | Resultado das checagens pontuais desta entrega |

O sucessor publica apenas agregados e hashes de arquivos. Títulos, resumos, textos, identificadores de obras e juízos individuais não integram os novos artefatos. Não houve chamadas de modelos, triagem, extração, recuperação ou alteração do estado de produção.
