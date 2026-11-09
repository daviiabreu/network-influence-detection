# Mapeamento sistemático priorizado v5.1: sucessor agregado com cobertura incompleta

## Resumo do produto

O mapa descreve famílias, mecanismos, representação de opiniões, topologias, desenhos de estudo, validação, dados, artefatos e lacunas relatadas. A busca preserva 54.570 observações e 49.333 registros-fonte, projetados em 43.906 propostas. Foram triadas 8.817 propostas; 4.724 receberam inclusão, 1.820 exclusão e 2.273 permaneceram incertas. A resolução de identidade reduz as inclusões em 557, resultando em 4.167 obras distintas em todas as fases. As 35.089 propostas não triadas não são exclusões.

Os 14 lotes produziram um conjunto mapeado de 4.056 obras, incluindo 70 codificadas como secundárias. O sucessor reaplica as contribuições por categoria e lote sem essas 70, obtendo 3.986 obras. Esse filtro não certifica todas as remanescentes como primárias elegíveis. A auditoria do restante tem 17 inclusões, 282 exclusões e 101 incertas entre 400 propostas. O encerramento foi operacional, com cobertura incompleta e regra de parada não satisfeita (`stop=false`).

## Perguntas, escopo e métodos

O produto amplo permite descrever os conceitos e os tipos de evidência de dinâmica computacional de opiniões antes de escolher uma pergunta de artigo. As perguntas do [protocolo JSON v5.1](../../../protocol/opinion-dynamics-systematic-map-v5-1-prioritized.json) tratam de famílias, representações e regras de interação (rq1); especificação, calibração, validação e comparação (rq2); artefatos para reprodução (rq3); e limites, conflitos e hipóteses pouco testadas (rq4). As dimensões do mapa descrevem rq1–rq3 e lacunas declaradas relacionadas a rq4. O pacote agregado não permite verificar conflitos ou relações por fonte, nem responder integralmente a rq4.

O escopo protocolar é inglês, de 01/01/1970 a 11/09/2026, com artigos de periódico, de conferência e preprints elegíveis; literatura cinzenta é excluída. Primárias são estudos analíticos, de simulação ou empíricos com modelos de dinâmica de opiniões humanas. Revisões e surveys pertinentes informam a camada 0 e não devem contar como primárias. O [protocolo v5](../../../protocol/opinion-dynamics-systematic-map-v5-prioritized.md) e o [adendo v5.1](../../../protocol/opinion-dynamics-systematic-map-v5-1-prioritized.md) preservam os critérios e documentam as emendas operacionais. A adoção metodológica foi delegada a agentes e permanece pendente de ratificação; não foi verificado um registro público do protocolo.

A aquisição efetivamente executada e suas estratégias estão ligadas pelo [run-record público da aquisição v3](../../../run-records/2026-09-11-broad-acquisition-v3.md) e pelo [registro por consulta](../../../searches/2026-09-12-v3-acquisition-results.json). Esse relato registra execução de 12/09/2026, encerrada às 06:02:23 UTC, com 1.027 consultas: 60 temáticas e 967 buscas por identificador em arXiv, DBLP, OpenAlex e Crossref. O limite de publicação em 11/09 é distinto da data de execução. A conferência desta documentação não foi um novo replay da aquisição, e não estabelece a inexistência de buscas posteriores.

A camada 0 precedeu os lotes priorizados de 500 propostas. O ranqueador lexical e Rocchio favoreceu a relevância às sementes adotadas; as emendas permitiram a preparação provisória do próximo lote usando apenas acordos A/B do predecessor pendente. Incertezas não são negativos de treino. A triagem priorizada não permite inferir prevalência na literatura inteira, e a estabilidade depende dessa ordem.

Os papéis registrados na produção foram A = `gpt-5.6-luna`, B = `claude-sonnet-5`, referências = `claude-opus-5-5` e `gpt-6-astra`, coordenação = `claude-opus-5-5`; auditoria cega = `gpt-6-sol` nos lotes e restante e `claude-opus-5-5` na camada 0. A extração dos lotes e restante foi de `gpt-6-astra`, com 10% em dupla extração por `claude-sonnet-5`; na camada 0 os papéis se inverteram. Esses papéis correspondem à proveniência do [run-record histórico](../../../run-records/2026-09-28-broad-map-v5-1-production.md), sem nova verificação humana. A sobreposição de famílias entre triadores e referências limita a independência.

A auditoria de produção registrou acordo de 668/700 nos lotes, 100/102 na camada 0 e 39/40 no restante. A dupla extração registrada cobre 471 propostas, com acordo exato por campo de 0,743 a 1,000. Esses números não são recall de calibração nem avaliação crítica da qualidade das fontes. Não há avaliação crítica por fonte demonstrada no pacote; sua execução ou ausência ainda precisa ser declarada pelo responsável científico.

## Calibração e proveniência ainda incompletas

A segunda coorte tem 200 propostas: 23 referências incluídas, 127 excluídas e 50 incertas. O [agregado sucessor de calibração](calibration-round2-aggregates.json) reproduz o JSON de gate registrado e publica somente contagens, incluindo os dez decis de 20 propostas. Os artefatos da primeira coorte só contribuíram às contagens de disposição da fase importada; suas métricas A/B não foram verificadas dentro do acesso autorizado.

| Métrica da segunda coorte | A | B |
| --- | ---: | ---: |
| Referências positivas | 23 | 23 |
| Positivas previstas estritamente como inclusão | 21 | 23 |
| Positivas retidas, incluindo `uncertain` | 22 | 23 |
| Fração estrita de inclusão | 0,913043 | 1,000000 |
| Fração retida, chamada `recall` no gate | 0,956522 | 1,000000 |
| Wilson 95% para a fração retida | 0,790088–0,992283 | 0,856883–1,000000 |
| Wilson 95% para a inclusão estrita | 0,732040–0,975820 | 0,856883–1,000000 |
| Falsas exclusões | 1 | 0 |
| Incertas entre as 200 previsões | 47 | 49 |

O gate integrado retorna `pass=true` com base em referências positivas não excluídas. O texto protocolar v5 define recall como inclusão prevista e afirma que `uncertain` não é acerto. A divergência é verificável: A retém 22/23, mas inclui estritamente 21/23. O sucessor expõe as duas métricas e mantém pendente a compatibilização entre protocolo, implementação e decisão de adoção; não declara retrospectivamente esse gate como cumprimento do recall estrito. O campo `authorizes_execution=false` do relatório de métricas também é preservado.

O protocolo histórico nomeia Claude Fable, enquanto a produção registra Opus. O vínculo de substituição com autorização e configuração não foi verificado no escopo desta entrega. Curvas recall@k dos conjuntos conhecidos, com seus denominadores completos, também não foram verificadas ou produzidas.

O run-record informa codebook v1 no lote 1 e v1.1 depois. Entretanto, os recibos `extraction-frame.json` dos lotes 1 e 2 apontam ambos para o hash v1.1 `be492f99a2a0f8ed4981fb69b9b046e57d004fc1adbfe67182603d61e8689173`, e os 14 snapshots mantêm o frame `5ddc759c6063ef40102f409ae5113992abfea55e21eee9a5f064601d9834a160`. Um frame com os mesmos códigos não comprova definições idênticas de extração. Essa discrepância documental permanece pendente; o filtro do sucessor não recodifica o lote 1 nem resolve a comparabilidade inicial.

## A1: reconciliação do fluxo

A [tabela completa por fase](comparison.md) publica triadas, incluídas, excluídas, incertas, reduções de identidade dentro e entre fases, novas inclusões distintas e total acumulado. As 557 são 449 reduções dentro das fases + 108 sobreposições com fases anteriores. A resolução integrada validou as auditorias e seus vínculos; a causa não foi presumida a partir da subtração.

A diferença de 63 decorre de 48 inclusões distintas da calibração + 17 do restante − 2 fusões na camada 0. A camada 0 histórica conta 48 propostas incluídas, equivalentes a 46 obras distintas. O total fecha como 48 + 46 + 4.056 + 17 = 4.167. As recuperações já adotadas da camada 0 e dos lotes 1–3 também estão decompostas na comparação.

Há motivo estruturado comum a A/B para 1.171 exclusões; o motivo final de outras 649 não foi verificado. Entre as incertas, 2.147 não têm resumo na tarefa vinculada, 71 têm resumo e 55 não tiveram disponibilidade verificada. A ausência de resumo permanece pendência, sem exclusão inferida.

## A2: denominador e parcelas sucessoras

Antes do filtro, o recálculo reproduziu todos os totais e as 49 contagens dos 14 snapshots originais. A união de códigos por identidade seguiu o comportamento integrado, e `category_report` foi reaplicado às obras restantes. O conjunto final de 70 obras com `study_design/secondary` foi retirado de todos os prefixos para impedir regressão artificial quando um código secundário aparece em uma manifestação posterior. Isso é uma projeção retrospectiva do conjunto final, sem nova classificação por obra.

As [49 comparações](comparison.md) e seus [limites completos](category-comparison.csv) expõem tanto numeradores quanto denominadores. A maior mudança absoluta é −1,725838 pp na categoria secundária; entre as outras categorias, é −0,764894 pp em método de validação não relatado. O mínimo numérico de 500 permanece no lote 2, agora com 606 obras. A primeira janela de duas transições estáveis termina no lote 13, como no histórico. As transições 12→13 e 13→14 mudam de 1,370658 e 1,197389 pp para 1,351022 e 1,204718 pp.

Continuam pendentes as três inclusões apontadas para correção, uma inclusão dependente de texto integral e uma incerteza que o run-record indica para possível reclassificação. Essas cinco situações foram apenas registradas como pendências agregadas. Nenhum desses juízos foi modificado, nem as 70 secundárias transferidas para a camada 0. Assim, 3.986 é a contagem após o filtro, não uma contagem certificada de todas as primárias elegíveis. A condição 3 não foi revalidada para o novo snapshot, e o recibo histórico não foi religado a ele.

## A3: alcance da ausência de informação

No conjunto histórico, 3.139/4.056 (77,4%) foram classificadas como sem dados empíricos relatados no título/resumo (`no_empirical_data_reported`), e 4.016/4.056 (99,0%) não relatam disponibilidade de artefatos no título/resumo (`reproducibility_artifacts/not_reported`). Esses códigos não comprovam ausência de dados, código ou ambiente no trabalho completo. Após o filtro, as contagens são 3.111/3.986 (78,0%) sem dados empíricos relatados e 3.949/3.986 (99,1%) sem disponibilidade de artefatos relatada.

O código `not_reported` indica ausência de informação suficiente naquele campo do título/resumo; difere de uma evidência de ausência e de uma extração pendente. O codebook permite classificar representação e mecanismo pelas propriedades padrão de um modelo canônico nomeado, salvo declaração contrária no texto. Essa simplificação não equivale à leitura dos métodos completos. A união de códigos entre manifestações segue o histórico e não foi convertida em nova verificação de evidência.

Essas qualificações também se aplicam às interpretações históricas utilizadas na decisão de tema. A decisão e o run-record permanecem snapshots imutáveis; a presente qualificação ligada corrige sua leitura sem reescrever seus bytes.

## A4: restante e envelope de cenários

A auditoria sorteou, sem reposição, 400 propostas de um quadro congelado de 35.489, com semente 20260925. Restam 35.089 não triadas. As 101 incertas não foram resolvidas nem convertidas em negativas.

| Cenário de elegibilidade da amostra | Numerador / 400 | Estimativa fora da amostra | Wilson 95% escalado |
| --- | ---: | ---: | ---: |
| Somente inclusões confirmadas | 17 | 1.491,2825 | 936,9358–2.351,0351 |
| Todas as incertas também positivas | 118 = 17 + 101 | 10.351,2550 | 8.857,4809–11.981,8776 |

A faixa arredondada 937–11.982 é um envelope aproximado dos extremos de Wilson de dois cenários, não o intervalo bilateral de uma única proporção. A estimativa de 1.491 usa somente as 17 inclusões confirmadas. Os cálculos são descritivos e aproximados, sem correção de população finita, sem garantia simultânea em auditorias repetidas e sem significado de recall. Contam propostas; identidade tardia pode reduzir o número de obras. Os cenários permanecem vinculados à auditoria histórica e não são uma estimativa nova de primárias após o filtro.

## A5–A7: reprodução, checklist e leitura

As [instruções de reprodução](REPRODUCIBILITY.md) distinguem o código histórico de produção `bc55e6d88f1c6366230243b587e1a3db0bc2907b`, a série depositada em `5edc9d590a89062d0b6e5957df64b16cd6b40f44` e o gerador registrado no manifesto em `10ae2af51eb21fc07f903aa1300805ba69942c13`. O recálculo sucessor usa os módulos integrados de `8c3f667d2c972126a4d8d943f8a3b615880eafc4`, sem alterá-los. O ambiente histórico completo das figuras não está registrado no manifesto; a reprodução histórica byte a byte permanece sem execução nesta entrega.

O [checklist PRISMA-ScR](PRISMA-ScR.md) identifica o que o pacote cobre e o que falta. Os [nomes em PT-BR e as legendas externas](glossary-and-captions.md) acompanham as figuras históricas, explicam multilabel, ausência de relato e o alcance restrito da marca de aprovação de transição. As figuras originais permanecem intactas.

## Interpretação e próximos passos

O mapa caracteriza um conjunto selecionado por relevância, com forte presença de extração teórica/computacional e pouca disponibilidade de artefatos relatada no título/resumo. Isso informa a descrição de conceitos e práticas em rq1–rq3, mas não estima frequências na literatura nem demonstra novidade de uma pergunta científica. A frequência de uma lacuna declarada não mede a inexistência de trabalho sobre ela.

A reconciliação encerra as duas diferenças aritméticas da revisão. O filtro quantifica a contaminação por secundários, mas a conclusão científica continua limitada pela elegibilidade pendente, auditoria incompleta, referências de agentes sem verificação humana, versões de extração e discrepância na métrica de calibração. Resolver essas questões exige sucessores próprios com evidência e autorização apropriadas. Características e resultados por fonte não são públicos neste pacote agregado. Financiamento da revisão, papel de financiadores e financiamento das fontes incluídas não foram verificados; faltam declarações do responsável, sem presumir ausência de financiamento.
