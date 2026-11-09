# Produção do mapa priorizado v5.1 (27 e 28/09/2026)

A produção executou o protocolo v5.1 (`protocol/opinion-dynamics-systematic-map-v5-1-prioritized.md` e o JSON de contexto de triagem) sobre o corpus deduplicado de 43.906 propostas. O orquestrador do ramo `research/broad-map-v5-production` (commit final `bc55e6d8`) conduziu as fases. A camada 0 de revisões foi adotada em 27/09; os lotes 1 a 14, de 500 obras cada, e a amostra do restante foram adotados até 28/09 17:19 UTC. Todos os juízos são de agentes sob a delegação de Davi (log privado, itens 20 a 53), sem verificação humana. Os agregados estão em [`synthesis/map-v5-1-2026-09-28`](../synthesis/map-v5-1-2026-09-28/README.md).

## Papéis

- Triador A: gpt-5.6-luna.
- Triador B: claude-sonnet-5.
- Referências nas discordâncias e incertezas: claude-opus-5-5 e gpt-6-astra.
- Coordenador: claude-opus-5-5, que adjudicou os casos em que as referências não concordavam.
- Auditoria cega de uma amostra aleatória por fase: gpt-6-sol nos lotes e no restante; claude-opus-5-5 na camada 0.
- Extração a partir de título e resumo: gpt-6-astra, com 10% em dupla extração por claude-sonnet-5, seguindo o livro de códigos v1.1, nos lotes e no restante. Na camada 0, antes do livro v1.1, a extração foi de claude-sonnet-5, com dupla extração por gpt-6-astra.

Cada fase passou pela auditoria de identidade antes da adoção.

## Fluxo

| Etapa                                                                |  Obras |
| -------------------------------------------------------------------- | -----: |
| Observações preservadas                                              | 54.570 |
| Registros-fonte distintos                                            | 49.333 |
| Propostas deduplicadas                                               | 43.906 |
| Triadas por título e resumo (inclui calibração, camada 0 e restante) |  8.817 |
| Incluídas em todas as fases, após identidade | 4.167 |
| Primárias mapeadas                                                   |  4.056 |
| Incluídas na camada 0 (revisões)                                     |     48 |
| Não triadas depois da amostra do restante                           | 35.089 |

Por lote, as inclusões caíram de 410 no lote 3 para 231 no lote 14, e as exclusões subiram de 4 para 83. As incertezas ficaram entre 84 e 196 por lote, a maioria por falta de resumo. A auditoria cega concordou com o julgamento final em 668 de 700 obras nos lotes 1 a 14 (95,4%), em 100 de 102 na camada 0 e em 39 de 40 no restante. As discordâncias foram mantidas pelo procedimento, com nota do coordenador. Três inclusões que o auditor contestou com razão ficaram registradas para correção por sucessor: um livro no lote 8, uma polarização só socioeconômica no lote 12 e um pooling de opiniões feito uma única vez no lote 14. Uma quarta, um processo de médias ligado ao modelo de Deffuant, também do lote 14, aguarda leitura do texto integral. As notas registram ainda uma incerteza do lote 8 que a leitura do critério de domínio adotada no lote 10 reclassificaria como inclusão.

## Regra de parada

A condição 1, pelo menos 500 primárias, foi cumprida no lote 2.

A condição 2 exige duas transições consecutivas sem categoria nova e com deslocamento máximo de até 2 pp. Ela foi cumprida pela primeira vez no lote 13 e de novo no 14. Os deslocamentos máximos por transição foram 9,49; 7,06; 8,26; 6,64; 4,42; 4,07; 2,95; 2,76; 2,56; 2,23; 1,37; 1,37 e 1,20 pp. Da transição para o lote 6 em diante, todos estiveram em `opinion_representation/continuous`. A única categoria nova apareceu no lote 4.

O lote 15 não foi preparado, conforme a verificação somente leitura da decisão 42. O lote 14 era provisório, já estava triado e foi concluído, como manda a emenda operacional.

A condição 3 é a auditoria aleatória de 400 obras de um quadro de 35.489 propostas ainda não triadas, com semente 20260925. Ela ficou incompleta. Foram 17 inclusões, 282 exclusões e 101 incertas, e nenhuma categoria das inclusões falta no mapa. As incertas são registros sem resumo. Pela regra 1, a triagem por título e resumo não pode excluí-las por modelo ou domínio, e a produção v5.1 não tem etapa de texto integral para resolvê-las. A estimativa de propostas relevantes não triadas é de 1.491, com intervalo de 937 a 11.982. O limite superior conta as 101 incertas como positivas.

Uma leitura descritiva dos 101 títulos, que não é decisão de elegibilidade, classificou 68 como fora do domínio, 12 como do domínio de opinião com desenho excluído (levantamento, experimento ou medição sem modelo) e 21 como plausivelmente elegíveis. O mapa foi encerrado com cobertura declarada incompleta e confiança reduzida (log, item 52). O relatório não afirma que a regra foi cumprida.

## Achados que o relatório deve discutir

A estabilidade das parcelas cumulativas depende da ordem que o ranqueador impôs, e as sementes adiantaram obras de confiança limitada. A parcela de `model_family/bounded_confidence` caiu de 52% no lote 1 para 19% no lote 14, e a de opinião contínua, de 68% para 33%. Nos últimos lotes, a regra fecha principalmente porque o n cresce: a parcela contínua ainda caía cerca de 1,4 pp por lote. A parcela `not_reported` em representação de opinião subiu de 13% depois do lote 1 (9% depois do lote 2) para 34%, efeito dos resumos menos detalhados nos lotes mais profundos. As figuras M1 e M2 mostram essas trajetórias.

Entre as 4.056 primárias, 77,4% não usam dado empírico. A validação empírica aparece em 3,6% no nível micro e em 4,6% no macro. Em 99,0% não há artefato de reprodutibilidade relatado. Lacunas declaradas pelos autores sobre validação macro e comparação de modelos aparecem em 32 e 14 obras.

## Incidentes e sucessores

- **Extração do lote 10 com configuração errada.** Depois de um reinício sem variáveis de ambiente, a extração do lote 10 rodou com a configuração errada. Os arquivos foram retirados para `superseded/` e a extração foi refeita (log, item 48). O orquestrador passou a ser iniciado só por `start-orchestrator.sh`.
- **Adjudicação do lote 13 corrigida antes da aprovação.** Quatro adjudicações da primeira versão foram corrigidas; a versão 1 ficou em `superseded/` (item 49). Nenhuma estava na amostra de auditoria.
- **Pausas por limite de uso.** Os limites de sessão do Claude pausaram passos resumíveis sem perda de dados.
- **Estado privado.** Todo o estado de produção fica em `~/.local/state/research-workbench/broad-map-v5-20260925/production-v5-1`, com permissões privadas.

## Limites

- Todos os juízos são de agentes e as famílias de modelo se sobrepõem entre triadores e referências.
- A extração usou só título e resumo; um campo ausente significa "não relatado no título e no resumo". A dupla extração de 471 obras (lotes, recuperações e restante) teve concordância exata por campo entre 0,743 (método de validação) e 1,000 (artefatos de reprodutibilidade); o lote 1 usou o livro de códigos v1, e os seguintes, o v1.1.
- Das 4.056 primárias mapeadas, 70 foram codificadas como estudo secundário (revisão ou survey). Pelo protocolo elas não deveriam contar como primárias; o denominador do relatório as inclui, o que desloca cada parcela em no máximo 1,7 pp.
- A triagem priorizada não permite inferir prevalência na literatura inteira.
- A cobertura ficou incompleta pela auditoria do restante.
- As decisões do papel Owner foram tomadas sob delegação e aguardam ratificação.
