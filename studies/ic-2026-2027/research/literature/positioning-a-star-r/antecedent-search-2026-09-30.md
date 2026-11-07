# Busca nova de antecedentes de a*(r) — 30/09/2026

**Nenhum dos candidatos lidos nesta busca foi identificado como ocupando a conjunção dos cinco elementos.** Há sobreposições parciais importantes, inclusive trabalhos ausentes dos documentos de entrada. Esse resultado é restrito às consultas, manifestações e profundidades de leitura registradas abaixo; não demonstra prioridade nem ausência de antecedentes.

Busca exploratória complementar solicitada por Davi, produzida por Codex com duas frentes de pesquisa de agentes. Não é atualização da revisão sistemática, exclusão canônica ou ratificação científica. Execução em 30/09/2026 UTC, iniciada em 29/09/2026 no fuso America/Sao_Paulo. Worktree `research/antecedent-search-20260930`, HEAD/base `31090f59f3dce56a6420775081aa2400976dddb2`; estado inicial limpo. Nenhum commit foi feito.

## Escopo e critérios

Antes da busca foram lidos [dossier.md](dossier.md), [search-log.json](search-log.json), o [desafio de novidade](../preparation/2026-09-25/claude-novelty-challenge.md) e [related-work.tex](../../../publications/jcss-manuscript/sections/related-work.tex). A avaliação usa a conjunção operacional do fim do dossiê e do parágrafo R59 do manuscrito:

| Elemento | Condição procurada |
| --- | --- |
| E1 | Gerador de influência entre pessoas, sem usar uma rede/exposição observada para discriminar mecanismos. |
| E2 | Erro de resposta separado da dinâmica latente; confiabilidade/sinal `r` fixado externamente e variado. |
| E3 | Nulas sem influência de persistência/traço+AR, pareadas às marginais e aos mesmos momentos observados de curto lag. |
| E4 | Discriminador fixo, com AUC cuja unidade é o painel inteiro. |
| E5 | Menor força de influência em uma grade, como curva censurada `a*(r)` para um alvo de desempenho. |

`Sim` exige a condição inteira; `parcial` indica um análogo que difere em parte decisiva; `não` indica um objeto ou desenho explicitamente distinto no material lido; `incerto` indica que a evidência acessível não resolve a condição. As classificações e os vereditos são interpretações desta busca, não afirmações dos autores. Ausência no resumo não estabelece ausência no artigo. O veredito **não sobrepõe** significa que a fonte lida não oferece antecedente operacional para a pergunta, embora possa compartilhar o tema geral; **sobreposição parcial** identifica um antecedente metodológico ou científico de algum componente. Só cinco `sim` permitiriam **ocupa a conjunção**.

O recorte principal é 2025–2026, até o instante da consulta, com recuperação adicional de antecedentes anteriores omitidos. Preprint e artigo não contam automaticamente como dois trabalhos; ligações entre manifestações são indicadas quando verificadas. “Novo” abaixo significa ausente dos quatro documentos de entrada, e não desconhecido de todo o repositório ou inédito na literatura. Consultas adaptativas, em inglês, privilegiaram identificabilidade, observação ruidosa, persistência e metodologia de surveys, além das expressões usadas na busca anterior.

Foram usados apenas endpoints públicos e páginas abertas. Não houve autenticação, contorno de paywall, CAPTCHA ou restrição de robots. Resumos públicos de artigos fechados são identificados como tal. Falhas de acesso não contam como zero resultados ou exclusão científica. Respostas brutas das APIs, textos abertos selecionados e recibos com URL, horário e SHA-256 foram preservados fora do Git em `/Users/davi/.local/state/research-workbench/antecedent-search-20260930/`.

## Consultas e contagens

As contagens são registros retornados pelas fontes, antes de deduplicação. `Total` é o total declarado pela API para sua semântica de busca, e não o número de trabalhos pertinentes. `Lidos/triados` distingue os títulos recuperados da leitura aprofundada dos candidatos. Crossref faz recuperação por relevância, não conjunção lógica dos termos; os totais muito grandes expõem baixa precisão. Uma primeira página não cobre o universo declarado.

### OpenAlex e Crossref: recuperação temática

Endpoints públicos: [OpenAlex `/works`](https://api.openalex.org/works) e [Crossref `/works`](https://api.crossref.org/works). Nas seis consultas recentes: OpenAlex `search=<texto>`, `filter=from_publication_date:2025-01-01,to_publication_date:2026-09-30`, `per-page=25,page=1`; Crossref `query.bibliographic=<texto>`, `filter=from-pub-date:2025-01-01,until-pub-date:2026-09-30`, `rows=25,offset=0`. Os recibos `root-lane/oa-*.json` e `cr-*.json` contêm os URLs completos codificados.

| ID | Consulta literal | UTC em 30/09/2026 | HTTP | Total | Retornados / títulos triados |
| --- | --- | --- | --- | ---: | ---: |
| OA01 | `"opinion dynamics" measurement` | 00:45:45 | 429 | não disponível | 0 / 0 |
| OA02 | `"opinion dynamics" identifiability` | 00:45:47 | 429 | não disponível | 0 / 0 |
| OA03 | `"social influence" persistence` | 00:45:48 | 429 | não disponível | 0 / 0 |
| OA04 | `"social influence" detectability` | 00:45:49 | 429 | não disponível | 0 / 0 |
| OA05 | `"political trust" reliability` | 00:45:51 | 429 | não disponível | 0 / 0 |
| OA06 | `"opinion dynamics" null` | 00:45:52 | 200 | 290 | 25 / 25 |
| OA07 | `"opinion dynamics" identification noise` — sem filtro de data | 00:45:55 | 429 | não disponível | 0 / 0 |
| OA08 | `"political trust" measurement error` — sem filtro de data | 00:45:57 | 429 | não disponível | 0 / 0 |
| OA01-R | Repetição literal de OA01 | 00:46:40 | 429 | não disponível | 0 / 0 |
| CR01 | `"opinion dynamics" measurement` | 00:45:45 | 200 | 258.913 | 25 / 25 |
| CR02 | `"opinion dynamics" identifiability` | 00:45:48 | 200 | 187.008 | 25 / 25 |
| CR03 | `"social influence" persistence` | 00:45:51 | 200 | 617.299 | 25 / 25 |
| CR04 | `"social influence" detectability` | 00:45:53 | 200 | 609.992 | 25 / 25 |
| CR05 | `"political trust" reliability` | 00:45:56 | 200 | 160.228 | 25 / 25 |
| CR06 | `"opinion dynamics" null` | 00:45:58 | 200 | 188.521 | 25 / 25 |
| CR08 | `query.title=opinion dynamics`; mesmo filtro de data, `rows=50` | 00:46:37 | 200 | 147.157 | 50 / 50 |

OpenAlex: sete consultas falharam por HTTP 429; uma repetição espaçada também falhou. Não se atribui causa ou orçamento específico sem evidência do serviço. A fonte permanece com cobertura incompleta. O único conjunto recuperado não trouxe candidato mais próximo que os obtidos nas demais fontes.

### JCSS e JASSS

| ID | Consulta/varredura | UTC em 30/09/2026 | Resultado e títulos triados |
| --- | --- | --- | --- |
| CR07 | Crossref `query.bibliographic=opinion influence persistence measurement`, filtro `issn:2432-3993`, 2025–2026, `rows=50` | 00:46:01 | HTTP 200, total 0; **consulta inválida para JCSS: ISSN incorreto**, descartada como evidência negativa. |
| JCSS01 | Crossref `filter=issn:2432-2725,from-pub-date:2025-01-01,until-pub-date:2026-09-30`, sem termos, `rows=500` | 00:47:02 | HTTP 200, total 142, retornados 142, títulos triados 142; inclui correções e não equivale a 142 estudos elegíveis. |
| JASSS01 | [Índice por fascículo](https://jasss.org/index_by_issue.html), volumes 28(1–4) e 29(1–3) | 30/09/2026, leitura web e recibo da cópia aberta | 53 entradas, todas triadas por título, incluindo editoriais/corrigenda; sete fascículos disponíveis até a busca. |

O ISSN eletrônico correto de JCSS, `2432-2725`, foi conferido na [página do periódico](https://link.springer.com/journal/42001). A correção da consulta criou outro registro; a tentativa errada foi preservada. JCSS01 cobre os depósitos Crossref com esse ISSN e datas, não garante todos os artigos do periódico. JASSS01 identificou três controles temáticos recentes detalhados abaixo; Tang et al. (2025) foi redescoberto e já constava dos insumos.

### Descoberta web complementar da frente principal

Motor web, consultas literais abaixo; total indexado não informado. As contagens são links visíveis devolvidos ao agente, incluindo manifestações repetidas, resultados fora do recorte e fontes secundárias. Apenas os primários efetivamente abertos sustentam as descrições dos candidatos. Data: 30/09/2026 UTC. Os resultados de W01 foram devolvidos em um lote de quatro consultas; o serviço não separou a contagem por consulta.

| ID | Consulta literal | Links visíveis |
| --- | --- | ---: |
| W01a–d | `"opinion dynamics" "measurement error" 2025 2026`; `"social influence" "detectability" 2025 2026`; `"opinion dynamics" "identifiability" 2025 2026`; `"political trust" "reliability" panel measurement 2025 2026` | 22 no lote; por consulta não disponível |
| W02 | `"opinion dynamics" "identification" "noise" 2025 2026` | 19 |
| W03 | `"opinion dynamics" "measurement" "inference" 2025 2026` | 14 |
| W04 | `"social influence" "measurement error" "panel"` | 18 |
| W05 | `site:link.springer.com/article/10.1007/s42001 2025 opinion inference` | 13 |
| W06 | `"Interacting Particle Systems on Networks" joint inference` | 20 |
| W07 | `site:link.springer.com/article/10.1007/s42001 "opinion" "2025"` | 14 |
| W08 | `site:link.springer.com/article/10.1007/s42001 "opinion" "2026"` | 14 |
| W09 | `site:jasss.org/29/ opinion` | 16 |
| W10 | `"Inference of Interaction Kernels in Mean-Field Models of Opinion Dynamics"` | 15 |
| W11 | `"Rational forecasts or social opinion dynamics" identification interaction effects` | 15 |

As consultas com `site:` também devolveram links de outros periódicos; o filtro foi conferido na seleção, não presumido perfeito. W10/W11 serviram para reidentificar manifestações e fontes abertas, não para medir recall. A busca preliminar em lote `site.jasss.org 2025 2026 opinion measurement validation identifiability` e `site.link.springer.com/journal/42001 2025 2026 opinion influence inference` devolveu 17 links conjuntos e motivou as varreduras dos periódicos.

### Sociological Methods & Research, Psychological Methods e surveys

Crossref público, consultas `query=<texto>` nos endpoints de cada ISSN, filtro comum `from-pub-date:2025-01-01,until-pub-date:2026-09-30`, `rows=30`; na segunda página PM04, `rows=33,offset=30`. Todos HTTP 200. URLs completos e respostas em `panel-lane/query-log.json`. Os periódicos foram confirmados nos registros retornados.

| ID | Fonte | Consulta literal | UTC em 30/09/2026 | Total API | Retornados / títulos-metadados triados |
| --- | --- | --- | --- | ---: | ---: |
| SM01 | `/journals/0049-1241/works` | `panel reliability measurement error` | 00:45:46 | 7 | 7 / 7 |
| SM02 | `/journals/0049-1241/works` | `social influence detection` | 00:45:48 | 18 | 18 / 18 |
| PM03 | `/journals/1082-989X/works` | `STARTS trait state error` | 00:45:49 | 16 | 16 / 16 |
| PM04 | `/journals/1082-989X/works` | `measurement error longitudinal social influence` | 00:45:50 | 63 | 30 / 30 |
| SV05 | `/works` | `political trust panel reliability` | 00:45:51 | 205.951 | 30 / 30 |
| SV06 | `/works` | `political trust trait state error` | 00:45:52 | 479.902 | 30 / 30 |
| PM04b | `/journals/1082-989X/works`, página 2 | `measurement error longitudinal social influence` | 00:46:54 | 63 | 33 / 33 |

São 164 registros devolvidos, 142 DOIs distintos, 122 após retirar identificadores de suplementos; não são 122 textos lidos. PM04 foi paginada até os 63 resultados da consulta, sem representar varredura de todo o periódico. SV05/SV06 ficaram nos primeiros 30 resultados. Complemento web desta frente, todo em 30/09/2026 UTC: 31 consultas em oito lotes. O motor só forneceu contagem conjunta por lote; o total indexado e a decomposição por consulta não estavam disponíveis.

| Lote | Consultas literais | Blocos visíveis triados |
| --- | --- | ---: |
| WP01 | `"political trust" reliability panel measurement error 2025 2026`; `"trust" "reliability" "panel" "2025" survey measurement`; `"STARTS" "2025" "measurement error"`; `"Psychological Methods" "2025" "social influence" measurement` | 21 |
| WP02 | `"political trust" "reliability" "panel" -"human-AI" -"Trust Formation"`; `"political trust" "measurement error" "2026"`; `"Fitting Single- and Multiple-Indicator STARTS Models" Ozkok`; `"Sociological Methods & Research" "2025" "panel" "measurement error"` | 18 |
| WP03 | `"Political Trust and Sophistication: Taking Measurement Seriously" authors`; `"Fitting Single- and Multiple-Indicator STARTS" pdf -tandfonline.com`; `"The Many Reliabilities of Psychological Dynamics"`; `"Within-person reliability of composite scores or single-item responses"` | 13 |
| WP04 | `"10.1037/met0000865"`; `"10.1037/met0000778"`; `"Dynamic factor analysis" "error-corrected" Zhang Lee Li Ong`; `"A time-varying interaction map approach for longitudinal assessments"` | 15 |
| WP05 | `"The many reliabilities of psychological dynamics" Castro-Alvarez Bringmann pdf`; `"Assessing intra- and inter-individual reliabilities" 10.1037/met0000608`; `"STARTS" "Nestler" "2415420" -tandfonline.com -researchgate.net`; `"political trust" "reliability" "2025" "panel" -tpmap.org -Human -AI -Violence` | 18 |
| WP06 | `"Fitting single" "Nestler" STARTS models dynamic structural equation models pdf`; `"Unlocking nonlinear dynamics and multistability from intensive longitudinal data" met0000623`; `"Simulation-based design optimization for statistical power" Zimmer Debelak`; `"Measurement error and person-specific reliability in multilevel autoregressive modeling"` | 15 |
| WP07 | `"Simulation-based design optimization for statistical power" "10.1037/met0000611"`; `"Unlocking nonlinear dynamics and multistability" "38095993"`; `"Modeling within-level latent interaction effects in multilevel vector-autoregressive models"` | 18 |
| WP08 | `"political trust" "trait" "measurement error" panel reliability`; `"political trust" "reliability" 2026 2025 quasi simplex`; `"social influence" "measurement error" "Psychological Methods"`; `"social influence" "measurement error" "Sociological Methods" 2025 2026` | 15 |

WP02 preserva um nome provisório errado (`Ozkok`) usado para localizar o título; a identidade foi corrigida pelos registros primários para Nestler, Robitzsch e Lüdtke. Não se inferiram autores a partir daquela consulta.

### arXiv API e Semantic Scholar


O endpoint arXiv funcionou, ao contrário da rodada anterior. Consultas A1 e A3 limitadas à data de primeira submissão em 2025–2026; A2/A4 sem restrição temporal para buscar anteriores omitidos. O filtro por submissão não cobre novas revisões de artigos antigos: a revisão 2025 de Lenti foi recuperada por busca web de título, não por A1. Ordenação arXiv `submittedDate`, decrescente. Páginas1 `start=0,max_results=25`, páginas 2 `start=25,max_results=100`. Todos os resultados dessas quatro consultas foram percorridos por título: 220 ocorrências, 202 arXiv IDs únicos após deduplicação. Resumos/textos foram lidos nos candidatos descritos abaixo, não nos 202 artigos integrais.

Consultas completas:

- A1: `(all:"opinion dynamics" OR all:"bounded confidence") AND (all:identifiability OR all:inference OR all:validation) AND submittedDate:[202501010000 TO 202609302359]`.
- A2: `(all:"social influence" OR all:"opinion dynamics") AND (all:detectability OR all:"measurement error" OR all:"observation noise")`.
- A3: `(all:"opinion dynamics" OR all:"social influence") AND (all:"null model" OR all:persistence OR all:"state-space") AND submittedDate:[202501010000 TO 202609302359]`.
- A4: `(all:"political trust" OR all:"trust in government") AND (all:reliability OR all:"measurement error" OR all:panel)`.
- S1: `opinion dynamics identifiability`; S2: `social influence observation noise`; S3: `opinion dynamics model selection`; S4: `political trust reliability panel`.

Semantic Scholar: `/graph/v1/paper/search`, `year=2025-2026`, `limit=25`, fields `title,year,abstract,externalIds,url,publicationDate`. Cada consulta recebeu HTTP 429; uma única repetição normal, cerca de 80 segundos depois, também 429. Contagem total e itens retornados são **desconhecidos**, não zero. Nenhuma conclusão usa resumos do Semantic Scholar desta rodada.

| ID/página | UTC real | HTTP | Total API | Retornados/títulos examinados | URL exata |
| --- | --- | --- | --- | --- | --- |
| A1 tentativa 1 | 2026-09-30T00:45:44.929225+00:00 | 200 | 98 | 25 | [requisição](https://export.arxiv.org/api/query?search_query=%28all%3A%22opinion+dynamics%22+OR+all%3A%22bounded+confidence%22%29+AND+%28all%3Aidentifiability+OR+all%3Ainference+OR+all%3Avalidation%29+AND+submittedDate%3A%5B202501010000+TO+202609302359%5D&start=0&max_results=25&sortBy=submittedDate&sortOrder=descending) |
| A2 tentativa 1 | 2026-09-30T00:45:50.762555+00:00 | 200 | 75 | 25 | [requisição](https://export.arxiv.org/api/query?search_query=%28all%3A%22social+influence%22+OR+all%3A%22opinion+dynamics%22%29+AND+%28all%3Adetectability+OR+all%3A%22measurement+error%22+OR+all%3A%22observation+noise%22%29&start=0&max_results=25&sortBy=submittedDate&sortOrder=descending) |
| A3 tentativa 1 | 2026-09-30T00:45:56.677242+00:00 | 200 | 43 | 25 | [requisição](https://export.arxiv.org/api/query?search_query=%28all%3A%22opinion+dynamics%22+OR+all%3A%22social+influence%22%29+AND+%28all%3A%22null+model%22+OR+all%3Apersistence+OR+all%3A%22state-space%22%29+AND+submittedDate%3A%5B202501010000+TO+202609302359%5D&start=0&max_results=25&sortBy=submittedDate&sortOrder=descending) |
| A4 tentativa 1 | 2026-09-30T00:46:02.433938+00:00 | 200 | 4 | 4 | [requisição](https://export.arxiv.org/api/query?search_query=%28all%3A%22political+trust%22+OR+all%3A%22trust+in+government%22%29+AND+%28all%3Areliability+OR+all%3A%22measurement+error%22+OR+all%3Apanel%29&start=0&max_results=25&sortBy=submittedDate&sortOrder=descending) |
| S1 tentativa 1 | 2026-09-30T00:46:07.918892+00:00 | 429 | não disponível | não disponível | [requisição](https://api.semanticscholar.org/graph/v1/paper/search?query=opinion+dynamics+identifiability&year=2025-2026&limit=25&fields=title%2Cyear%2Cabstract%2CexternalIds%2Curl%2CpublicationDate) |
| S2 tentativa 1 | 2026-09-30T00:46:17.527267+00:00 | 429 | não disponível | não disponível | [requisição](https://api.semanticscholar.org/graph/v1/paper/search?query=social+influence+observation+noise&year=2025-2026&limit=25&fields=title%2Cyear%2Cabstract%2CexternalIds%2Curl%2CpublicationDate) |
| S3 tentativa 1 | 2026-09-30T00:46:27.164593+00:00 | 429 | não disponível | não disponível | [requisição](https://api.semanticscholar.org/graph/v1/paper/search?query=opinion+dynamics+model+selection&year=2025-2026&limit=25&fields=title%2Cyear%2Cabstract%2CexternalIds%2Curl%2CpublicationDate) |
| S4 tentativa 1 | 2026-09-30T00:46:36.751072+00:00 | 429 | não disponível | não disponível | [requisição](https://api.semanticscholar.org/graph/v1/paper/search?query=political+trust+reliability+panel&year=2025-2026&limit=25&fields=title%2Cyear%2Cabstract%2CexternalIds%2Curl%2CpublicationDate) |
| A1P2 tentativa 1 | 2026-09-30T00:46:45.817375+00:00 | 200 | 98 | 73 | [requisição](https://export.arxiv.org/api/query?search_query=%28all%3A%22opinion+dynamics%22+OR+all%3A%22bounded+confidence%22%29+AND+%28all%3Aidentifiability+OR+all%3Ainference+OR+all%3Avalidation%29+AND+submittedDate%3A%5B202501010000+TO+202609302359%5D&start=25&max_results=100&sortBy=submittedDate&sortOrder=descending) |
| A2P2 tentativa 1 | 2026-09-30T00:46:52.370419+00:00 | 200 | 75 | 50 | [requisição](https://export.arxiv.org/api/query?search_query=%28all%3A%22social+influence%22+OR+all%3A%22opinion+dynamics%22%29+AND+%28all%3Adetectability+OR+all%3A%22measurement+error%22+OR+all%3A%22observation+noise%22%29&start=25&max_results=100&sortBy=submittedDate&sortOrder=descending) |
| A3P2 tentativa 1 | 2026-09-30T00:46:58.687471+00:00 | 200 | 43 | 18 | [requisição](https://export.arxiv.org/api/query?search_query=%28all%3A%22opinion+dynamics%22+OR+all%3A%22social+influence%22%29+AND+%28all%3A%22null+model%22+OR+all%3Apersistence+OR+all%3A%22state-space%22%29+AND+submittedDate%3A%5B202501010000+TO+202609302359%5D&start=25&max_results=100&sortBy=submittedDate&sortOrder=descending) |
| S1 tentativa 2 | 2026-09-30T00:47:25.598409+00:00 | 429 | não disponível | não disponível | [requisição](https://api.semanticscholar.org/graph/v1/paper/search?query=opinion+dynamics+identifiability&year=2025-2026&limit=25&fields=title%2Cyear%2Cabstract%2CexternalIds%2Curl%2CpublicationDate) |
| S2 tentativa 2 | 2026-09-30T00:47:35.407575+00:00 | 429 | não disponível | não disponível | [requisição](https://api.semanticscholar.org/graph/v1/paper/search?query=social+influence+observation+noise&year=2025-2026&limit=25&fields=title%2Cyear%2Cabstract%2CexternalIds%2Curl%2CpublicationDate) |
| S3 tentativa 2 | 2026-09-30T00:47:44.954249+00:00 | 429 | não disponível | não disponível | [requisição](https://api.semanticscholar.org/graph/v1/paper/search?query=opinion+dynamics+model+selection&year=2025-2026&limit=25&fields=title%2Cyear%2Cabstract%2CexternalIds%2Curl%2CpublicationDate) |
| S4 tentativa 2 | 2026-09-30T00:47:54.723611+00:00 | 429 | não disponível | não disponível | [requisição](https://api.semanticscholar.org/graph/v1/paper/search?query=political+trust+reliability+panel&year=2025-2026&limit=25&fields=title%2Cyear%2Cabstract%2CexternalIds%2Curl%2CpublicationDate) |

Brutos e logs fora Git: `/Users/davi/.local/state/research-workbench/antecedent-search-20260930/arxiv-lane`. `search-log.json`: 8 tentativas iniciais; `pages-log.json`: 3 páginas adicionais; `retry-log.json`: 4 repetições S2; `all-arxiv-entries.json`: 202 IDs únicos; `sources-log.json`: páginas primárias com data, status, bytes e SHA-256.

Busca web suplementar, usada para descoberta/metadados primários e localização de textos, sem substituir a API arXiv bem-sucedida. As oito consultas iniciais foram repetidas individualmente para registrar contagens: `arxiv-lane/web-searches-verified.json` preserva resultados brutos, horários e URLs. Total do índice não disponível; as contagens abaixo são apenas blocos visíveis retornados, incluindo duplicatas.

| ID | Consulta literal | UTC em 30/09/2026 | Blocos visíveis |
| --- | --- | --- | ---: |
| WA01 | `"Variational Inference of Parameters in Opinion Dynamics Models"` | 01:01:25 | 16 |
| WA02 | `site:arxiv.org "opinion dynamics" "measurement" "2025"` | 01:01:47 | 1 |
| WA03 | `site:arxiv.org "social influence" "identifiability" 2026` | 01:01:49 | 0 |
| WA04 | `"Social System Inference from Noisy Observations" Mao DOI` | 01:01:50 | 17 |
| WA05 | `"Detecting Social Influence in Event Cascades" proceedings PMLR` | 01:01:52 | 17 |
| WA06 | `site:arxiv.org "opinion dynamics" "reliability" 2025 2026` | 01:01:54 | 4 |
| WA07 | `site:arxiv.org "social influence" "observation noise" 2025 2026` | 01:01:58 | 0 |
| WA08 | `site:arxiv.org "opinion dynamics" "response error"` | 01:02:00 | 0 |

São 55 blocos nas repetições. Os três zeros são respostas bem-sucedidas explicitamente vazias, sem representar ausência bibliográfica. No lote inicial das três últimas consultas, quatro links primários únicos (2606.00268, 1304.3518, 1207.5261, 1102.2336) foram percorridos como pistas sem produzir candidato próximo: confiabilidade de agente/informação não é confiabilidade de resposta `r`. Uma [conferência auxiliar por `id_list`](https://export.arxiv.org/api/query?id_list=1802.06138%2C2012.03075%2C2509.17625%2C2403.05358%2C2509.06858%2C2409.08004%2C2608.18235%2C2609.28340%2C2501.13215%2C2601.16226%2C2609.05560&max_results=20) recebeu HTTP 429 em 30/09/2026 01:02:56 UTC, total indisponível, sem registros legíveis (`identity-check.json`); as identidades abaixo foram conferidas nas páginas primárias abertas.

## Candidatos novos: inferência, observação e identificabilidade

### C01 — Lang, Wang, Lu e Maggioni (2026; preprint inicial 2024)

*Interacting particle systems on networks: Joint inference of the network and the interaction kernel*. DOI [10.1016/j.acha.2026.101867](https://doi.org/10.1016/j.acha.2026.101867); [arXiv:2402.08412v2](https://arxiv.org/abs/2402.08412v2), revisão de 23/03/2026. Descoberta W01/W06.

Lidos: resumo da editora e [HTML aberto v2](https://arxiv.org/html/2402.08412v2), §§1.1–1.2, 3, 4.4, 5.2 e B.3. Inferem conjuntamente rede ponderada desconhecida e kernel de interação a partir de múltiplas trajetórias. Condições de coercividade asseguram identificabilidade; testam opinião líder–seguidor. B.3 separa força estocástica do processo e ruído de observação, variando o segundo com processo determinístico. É um antecedente direto de inferência com rede não observada e observações ruidosas. O alvo é erro de estimação de rede/kernel, sem contraste traço+AR pareado ou fronteira de força por AUC. `r` não é a confiabilidade externa desta pergunta. **E1 sim; E2 parcial; E3 não; E4 não; E5 parcial** — limiares de tamanho amostral/identificabilidade, não `a*(r)`. **Veredito: sobreposição parcial.**

### C02 — Chu, Li e Porter (2024; preprint 2022)

*Inference of Interaction Kernels in Mean-Field Models of Opinion Dynamics*. DOI [10.1137/22M1544415](https://doi.org/10.1137/22M1544415); [arXiv:2212.14489v2](https://arxiv.org/abs/2212.14489v2). Descoberta W03/W10.

Lidos: resumo da editora e [PDF publicado depositado pelo autor](https://math.ucla.edu/~mason/papers/weiqi-inverse-published-2024.pdf), §§3.1–3.4, pp. 1100–1104; conferência no HTML do preprint. Inferem o kernel de um modelo mean-field de confiança limitada usando observações parciais da distribuição acumulada. Demonstram unicidade sob condições de desenho e falhas com distribuição inicial concentrada ou simétrica em torno do limiar de observação. “Limiar de medida” é um ponto da escala/CDF, não força mínima detectável. Não são trajetórias de um painel individual com canal de resposta `r`. **E1 sim; E2 parcial** — observação parcial e estabilidade da inversão, sem grade de confiabilidade; **E3 não; E4 não; E5 parcial** — condições de identificabilidade. **Veredito: sobreposição parcial.**

### C03 — Lux (2009; working paper 2007/2008)

*Rational forecasts or social opinion dynamics? Identification of interaction effects in a business climate survey*. DOI [10.1016/j.jebo.2009.07.003](https://doi.org/10.1016/j.jebo.2009.07.003). Descoberta W02/W11.

Lidos: resumo público da editora e [resumo do instituto autor](https://www.kielinstitut.de/publications/rational-forecasts-or-social-opinion-dynamics-identification-of-interaction-effects-in-a-business-climate-survey-9808/). Estima parâmetros de formação estocástica de opiniões binárias por verossimilhança de observações discretas da média agregada; aplica a um índice de clima empresarial. É antecedente anterior de inferir interação a partir de surveys agregados sem exposição registrada. A leitura foi **somente de resumos**, não permite excluir estruturas adicionais no texto integral. **E1 parcial; E2 incerto; E3 incerto; E4 não** — o estimador descrito é verossimilhança agregada; **E5 incerto**. **Veredito: sobreposição parcial, provisório à profundidade de resumo.**

### C04 — Kawahata (2026), controle de “limiar” com outro significado

*Information Phase Transitions and Epistemic Injustice in Massive Data: Validating the Signal Cliff Based on the Ising Model of Opinion Dynamics*. DOI [10.3390/e28060612](https://doi.org/10.3390/e28060612). Descoberta W02.

Lido: **resumo depositado pela editora no [Crossref](https://api.crossref.org/works/10.3390/e28060612)**. As tentativas de abertura de MDPI/PMC falharam no cliente web; nenhum texto integral foi lido. Simula uma transição na diversidade de informação/entropia conforme cresce `N`, com pressão de conformidade e viés sistêmico. O “Signal Cliff” descrito é descarte de sinais minoritários na formação coletiva, não detecção estatística de influência contra persistência sob erro de resposta. **E1 parcial; E2 incerto; E3 incerto; E4 não; E5 não** — o limiar exposto é de escala populacional/diversidade. **Veredito: não sobrepõe a fronteira operacional descrita, limitado ao resumo.**

## Controles recentes recuperados nos periódicos

Estes trabalhos foram examinados para distinguir modelagem de opinião em si de detecção de mecanismos. Não substituem os antecedentes mais próximos já no dossiê. As leituras abaixo foram de **resumos primários**, salvo a introdução indicada; condições não descritas ficam incertas.

| ID / trabalho | Identificador e fonte lida | O que a fonte faz | E1 / E2 / E3 / E4 / E5 | Veredito |
| --- | --- | --- | --- | --- |
| C05 — Horn et al. 2026, *Success-Driven User Activity Contributes to Online Polarization* | [10.18564/jasss.5947](https://www.jasss.org/29/2/1.html), resumo e introdução ¶¶1.1–1.8 | Compara Axelrod original com extensão em que sucesso aumenta atividade; o reforço modifica a própria dinâmica, e ambos os geradores têm influência. | parcial / não / não / não / não | não sobrepõe o contraste procurado |
| C06 — Mathias, Huet e Muneepeerakul 2025, *Triadic Transitions of Opinion Dynamics in a Bounded Confidence Model* | [10.18564/jasss.5634](https://www.jasss.org/28/2/6.html), resumo | Estuda abertura, fechamento e transição de tríades durante convergência em confiança limitada. | parcial / incerto / incerto / não / não | não sobrepõe a fronteira descrita |
| C07 — Ramaswamy et al. 2025, *Exploring the Influence of Open-Mindedness and Social Identity on Opinion Polarization in a Modified Hegselmann-Krause Model* | [10.18564/jasss.5661](https://www.jasss.org/28/3/3.html), resumo | Varia abertura `ε`, granularidade de identidade e suas distribuições para explicar polarização; `ε` não é confiabilidade da resposta. | parcial / não / incerto / não / não | não sobrepõe a fronteira descrita |
| C08 — Desmarchelier, Djellal e Gallouj 2025, *Filter bubbles as a vector of tradition? Decoding opinion dynamics with agent-based modelling* | [10.1007/s42001-025-00422-7](https://link.springer.com/article/10.1007/s42001-025-00422-7), resumo e introdução §1 | Simula bolhas de filtro, câmaras de eco e conhecimento fortuito; examina consenso/fragmentação, sem avaliação de separabilidade no objetivo exposto. | parcial / incerto / incerto / não / não | não sobrepõe a fronteira descrita |
| C09 — Kareeva e Sedakov, online 2025 / volume 2026, *Opinion dynamics game in conservation discourse* | [10.1007/s42001-025-00430-7](https://link.springer.com/article/10.1007/s42001-025-00430-7), resumo | Integra jogos e dinâmica de opinião em três cenários de conflito/compromisso entre empresas e organizações ambientais. | parcial / incerto / incerto / não / não | não sobrepõe a fronteira descrita |

## Candidatos novos: painéis, traço–estado–erro e poder

### C10 — Holtmann e Koslowski (2025)

*Modeling within-level latent interaction effects in multilevel vector-autoregressive models*. DOI [10.3758/s13428-025-02694-3](https://doi.org/10.3758/s13428-025-02694-3), publicado em 05/09/2025. Recuperado em WP07.

Lido: **[texto aberto da editora](https://link.springer.com/article/10.3758/s13428-025-02694-3)**, modelos, “Simulation study I, effect of reliability” e discussão. Estende VAR multinível a moderação latente intra-pessoa, com traços/médias pessoais e modelos de medida. Simula confiabilidade 0,90/0,72/0,50 e avalia viés, cobertura, MSE e poder. Omitir o modelo de medida pode enviesar autorregressão, cross-regressão e moderação; indicadores latentes corrigem boa parte disso. Os efeitos são entre variáveis da mesma pessoa, não entre pessoas. **E1 não; E2 sim; E3 parcial** — traço+AR, sem nulo pareado; **E4 parcial** — poder por parâmetro; **E5 não. Veredito: sobreposição parcial.** É precedente recente diretamente útil para a sensibilidade à confiabilidade.

### C11 — Lafit, Ariens e Artner (2026)

*Shedding some light on the relationship between measurement error and statistical power in multilevel models applied to intensive longitudinal designs*. DOI [10.1111/bmsp.70040](https://doi.org/10.1111/bmsp.70040), online 25/02/2026. Recuperação dirigida na frente de painéis.

Lido: **[resumo da editora](https://bpspsychub.onlinelibrary.wiley.com/doi/10.1111/bmsp.70040)**; abertura do texto integral falhou. Deriva viés assintótico e precisão da MLE de efeitos fixos em modelos multinível com erro aditivo e erros intra-pessoa AR(1), incluindo preditores variantes/invariantes no tempo e poder de interações entre níveis. O resumo não resolve se há grade externa de `r` ou limiar de força. **E1 não; E2 parcial; E3 parcial** — autorregressão, sem contraste descrito com influência entre pessoas; **E4 parcial** — poder analítico; **E5 incerto. Veredito: sobreposição parcial**, com leitura restrita ao resumo.

### C12 — Nestler, Robitzsch e Lüdtke (2025; DOI/online 2024)

*Fitting Single- and Multiple-Indicator STARTS Models as Dynamic Structural Equation Models*. DOI [10.1080/10705511.2024.2415420](https://doi.org/10.1080/10705511.2024.2415420), *Structural Equation Modeling* 32(3):529–540. Recuperado em WP01–WP06.

Lido: **[resumo primário institucional dos autores](https://www.leibniz-ipn.de/en/research/publications/fitting-single-and-multiple-indicator-starts-models-as-dynamic-structural-equation-models)**. Não houve leitura integral; a rota da editora falhou. Implementa STARTS com um/múltiplos indicadores como DSEM, com aplicação e três simulações de estimadores Bayesianos. Decompõe componente estável, componente autorregressivo e estado específico. **E1 não; E2 parcial** — erro/decomposição, grade `r` não demonstrada; **E3 parcial** — construção de traço+AR, sem nulo pareado; **E4 não; E5 incerto. Veredito: sobreposição parcial.** Antecedente da forma e estimação do nulo, não evidência de uma curva `a*(r)`.

### C13 — Schuurman e Hamaker (2019; online 2018)

*Measurement Error and Person-Specific Reliability in Multilevel Autoregressive Modeling*. DOI [10.1037/met0000188](https://doi.org/10.1037/met0000188), *Psychological Methods* 24(1):70–91. Recuperado em WP06.

Lido: **[texto publicado aberto no repositório Utrecht](https://research-portal.uu.nl/ws/portalfiles/portal/239229399/Measurement_Error_and_Person-Specific_Reliability_in_Multilevel_Autoregressive_Modeling.pdf)**, resumo p.70 e consequências de ignorar erro/Fig.2 p.78. Separa inovações da dinâmica e erro de medida no VAR(1), propõe MEVAR e confiabilidades pessoais/intra/entre pessoas. Ignorar erro pode produzir caminhos cruzados espúrios, atenuar, exagerar ou inverter sinais. Exemplos tratam de variáveis afetivas dentro da pessoa; “rede psicológica” não é rede de influência social. **E1 não; E2 parcial; E3 parcial** — AR e heterogeneidade; **E4 não; E5 não nos trechos lidos. Veredito: sobreposição parcial.**

### C14 — Holm, Hjorth-Trolle e Andersen (2025; online 2023)

*Lagged Dependent Variable Predictors, Classical Measurement Error, and Path Dependency: The Conditions Under Which Various Estimators are Appropriate*. DOI [10.1177/00491241231176845](https://doi.org/10.1177/00491241231176845), *Sociological Methods & Research* 54(1):140–172. Recuperado em WP02; o filtro Crossref por primeira publicação recente não recuperou seu online de 2023.

Lido: **[texto aberto da editora](https://journals.sagepub.com/doi/10.1177/00491241231176845)**, erro clássico, efeitos fixos em modelos LDV e tabelas 2–3. Compara estimadores com variável defasada, média histórica e instrumentos em processos Markov/semi-Markov com erro clássico; propõe FDIV, que requer ao menos cinco ondas. Simulações e aplicação a desempenho escolar tratam de persistência e consistência de estimação. **E1 não; E2 parcial; E3 parcial** — persistência/efeito fixo; **E4 não; E5 não. Veredito: sobreposição parcial.** Não é um contraste de influência entre pares contra geradores nulos pareados.

### C15 — McNeish (2026)

*Within-person reliability of composite scores or single-item responses with missing intensive longitudinal data*. DOI [10.1037/met0000865](https://doi.org/10.1037/met0000865), *Psychological Methods*, online 20/08/2026. Recuperado em PM04/WP03–WP04.

Lido: **[resumo dos autores no PubMed](https://pubmed.ncbi.nlm.nih.gov/42622853/)**, sem texto integral. Examina confiabilidade intra-pessoa com dados ausentes; estende autorregressão com erro de medida por um modelo de seleção Diggle–Kenward para sensibilidade MNAR. As simulações recuperam confiabilidade populacional; não estimam força de interação entre pessoas. **E1 não; E2 parcial** — confiabilidade estimada, não externa; **E3 parcial** — AR no modelo de medida; **E4 não; E5 incerto pelo resumo. Veredito: sobreposição parcial.** É fonte recente para limites de estimar confiabilidade de item único, sem medir confiança política.

## Candidatos novos: confiança política e influência empírica

### C16 — Devine e Valgarðsson (2024; online 2023)

*Stability and change in political trust: Evidence and implications from six panel studies*. DOI [10.1111/1475-6765.12606](https://doi.org/10.1111/1475-6765.12606), *European Journal of Political Research* 63(2):478–497. Recuperado na ampliação de surveys.

Lido: **[texto aberto da editora](https://onlinelibrary.wiley.com/doi/10.1111/1475-6765.12606)**, “Data and methods”, Table 1, estratégia empírica e conclusão. Estuda estabilidade individual em seis painéis/cinco países, incluindo **o item de confiança no governo federal do SHP**, escala 0–10, período 1999–2018 e 14 ondas de confiança. Usa mudanças absolutas, correlações, crescimento e decomposição entre/dentro de pessoa; discute erro de item único, sem estimar sua confiabilidade. **E1 não; E2 parcial; E3 parcial** — estabilidade versus atualização; **E4 não; E5 não. Veredito: sobreposição parcial.** É precedente direto do mesmo item, além de Gestefeld–Lorenz; não muda a geometria declarada de onze ondas do simulador.

### C17 — Turper e Aarts (2017; online 2015)

*Political Trust and Sophistication: Taking Measurement Seriously*. DOI [10.1007/s11205-015-1182-4](https://doi.org/10.1007/s11205-015-1182-4), *Social Indicators Research* 130(1):415–434. Recuperado em WP02–WP03.

Lido: **[texto aberto da editora](https://link.springer.com/article/10.1007/s11205-015-1182-4)**, §§2.2, 3.1, 3.3.2, Fig.2 e nota 3. A rota PMC apresentou CAPTCHA e foi interrompida. Usa ESS holandês e painel de quatro ondas; CFA/invariância e simplex autorregressivo latente com itens de parlamento, políticos e partidos, separando erro para comparar sofisticação política. A nota 3 cita confiabilidades MTMM de um experimento ESS2: parlamento 0,82, sistema legal 0,85, políticos 0,84. **Não são estimativas do SHP. E1 não; E2 parcial; E3 parcial** — simplex; **E4 não; E5 não. Veredito: sobreposição parcial.** Confiança política com erro em painel já tem antecedente explícito.

### C18 — Lugtig (2017)

*The Relative Size of Measurement Error and Attrition Error in a Panel Survey. Comparing Them With a New Multi-Trait Multi-Method Model*. DOI [10.18148/srm/2017.v11i4.7170](https://doi.org/10.18148/srm/2017.v11i4.7170), *Survey Research Methods* 11(4):369–382. Recuperação dirigida de confiabilidade política.

Lido: **[PDF oficial aberto](https://ojs.ub.uni-konstanz.de/srm/article/download/7170/6532)**, pp.373–375, §§2–4.3 e Table 2. O MTMM de confiança no parlamento/sistema legal/polícia foi aplicado **uma vez**, em dezembro de 2008 no LISS (`n=2.873`). Segue retenção até dezembro de 2011 e reestima a medida inicial entre remanescentes, assumindo erros constantes: não são 35 medidas repetidas de confiança. A Table 2 informa confiabilidade do parlamento 0,95/0,82/0,90, conforme formato. **E1 não; E2 parcial; E3 não; E4 não; E5 não. Veredito: sobreposição parcial em confiabilidade do domínio.** Não transportar esses valores ao SHP ou à razão de variâncias do simulador.

### C19 — Pham e Sewell (2026)

*Homophily-adjusted social influence estimation*. DOI [10.1002/cjs.70069](https://doi.org/10.1002/cjs.70069), *Canadian Journal of Statistics*, online 05/08/2026. Recuperação dirigida de influência e erro.

Lido: **[texto aberto da editora](https://onlinelibrary.wiley.com/doi/10.1002/cjs.70069)**, §§2, 3.1–3.2 e 4. Deriva condições de estimação da influência linear `rho` com **rede observada**, homofilia latente e efeito individual persistente. Usa processo longitudinal estabilizado para inferência transversal; compara viés, MSE e cobertura com modelos convencionais. §3.1, “Stochasticity”, deixa erro de observação fora do resultado teórico e discute um canal separado. **E1 parcial; E2 não; E3 parcial** — traço, sem nulo pareado; **E4 não; E5 não. Veredito: sobreposição parcial.** O artigo aproxima influência e traços, mas não mede detectabilidade com `r` de resposta.

### C20 — Högberg e Bortes (2026)

*Stress contagion in school: A multiverse analysis of social influence on school-related stress*. DOI [10.1371/journal.pone.0348437](https://doi.org/10.1371/journal.pone.0348437), *PLOS ONE* 21(5):e0348437, publicado em 04/05/2026. Descoberta W04.

Lido: **[texto aberto](https://pmc.ncbi.nlm.nih.gov/articles/PMC13138672/)**, resumo e “Materials and methods”, incluindo modelo, estimando e erro de medida. Painel sueco de duas ondas, item único ordinal 1–5, com 9.240 especificações de efeitos fixos, LDV, coorte e escola. Considera erros nos atributos dos colegas e limiares de completude das turmas (>50%/>75%), não uma grade da confiabilidade do item. **E1 parcial; E2 parcial; E3 parcial** — FE/LDV, sem geradores pareados; **E4 não; E5 não. Veredito: sobreposição parcial.** Ajuda a discutir limites empíricos, não define uma fronteira de força em painéis simulados.

### Leituras auxiliares da frente de painéis

| Trabalho | Identificador / leitura primária | Disposição e cinco elementos |
| --- | --- | --- |
| Castro-Alvarez et al., online 2025 / volume 2026, *The many reliabilities of psychological dynamics: An overview of statistical approaches to estimate the internal consistency reliability of intensive longitudinal data* | [10.1037/met0000778](https://doi.org/10.1037/met0000778), [resumo institucional Groningen](https://research.rug.nl/nl/publications/the-many-reliabilities-of-psychological-dynamics-an-overview-of-s/) | Panorama de confiabilidades multinível/VAR/fatores dinâmicos; **sobreposição parcial**. E=(não, parcial, não, não, incerto). Há erratum DOI `10.1037/met0000811`; nenhum resultado numérico é usado aqui. |
| Jeon e Schweinberger 2026, *A time-varying interaction map approach for longitudinal assessments* | [10.1037/met0000825](https://doi.org/10.1037/met0000825), [resumo dos autores exibido no índice PubMed](https://pubmed.ncbi.nlm.nih.gov/42080874/) | Interação pessoa–item, não pessoa–pessoa; **não sobrepõe**. E=(não, incerto, não, não, incerto). |
| Zhang et al. 2025, *Dynamic factor analysis with multivariate time series of multiple individuals: An error-corrected estimation method* | [10.1037/met0000722](https://doi.org/10.1037/met0000722), [resumo dos autores no PubMed](https://pubmed.ncbi.nlm.nih.gov/39786826/) | Erro de estimação de parâmetros individuais, diferente do erro no canal de resposta; **não sobrepõe**. E=(não, não, incerto, não, incerto). |
| Cui et al., online 2023 / volume 2026, *Unlocking nonlinear dynamics and multistability from intensive longitudinal data: A novel method* | [10.1037/met0000623](https://doi.org/10.1037/met0000623), [resumo dos autores exibido no índice PubMed](https://pubmed.ncbi.nlm.nih.gov/38095993/) | Recuperação de dinâmica psicológica/bistabilidade de uma pessoa; **sobreposição parcial** na inferência dinâmica. E=(não, incerto, não, não, incerto). |
| Zimmer e Debelak, online 2023 / volume 2025, *Simulation-based design optimization for statistical power: Utilizing machine learning* | [10.1037/met0000611](https://doi.org/10.1037/met0000611), [resumo dos autores no PubMed](https://pubmed.ncbi.nlm.nih.gov/38095992/) | Otimização genérica de desenho por simulação e aprendizado de máquina; **sobreposição parcial** no planejamento de poder. E=(não, incerto, não, parcial, incerto). Não fornece antecedente de mecanismo de opinião. |

## Candidatos novos: testes discriminativos e estados latentes

### C21 — Soni, Ramirez e Eisenstein (2019; preprint 2018)

*Detecting Social Influence in Event Cascades by Comparing Discriminative Rankers*. [arXiv:1802.06138v2](https://arxiv.org/abs/1802.06138v2); [PMLR 104:78–99](https://proceedings.mlr.press/v104/soni19a.html). A página editorial não informa DOI. Recuperado em A2 e por localização do título.

Lido: **PDF aberto v2**, §§3.3, 4.1 e 4.4, pp.5–8. Compara rankers com/sem atributos de influência por MRR fora da amostra e teste de permutação. Simulações Hawkes incluem autoexcitação `a`, influência interpessoal `b` e heterogeneidade/homofilia basal: `b=0` é nula; `b` varia de 0 a 1 em passos 0,1. A Fig.2 mostra poder versus força; também há censura de eventos. É o novo antecedente mais próximo do uso de discriminação para detectar influência além de persistência/heterogeneidade. Porém usa rede conhecida e eventos/cascatas, sem erro de resposta com `r`, nulas traço+AR pareadas ou AUC por painel. **E1 parcial; E2 não; E3 parcial; E4 parcial; E5 parcial. Veredito: sobreposição parcial.**

### C22 — Mao, Hovakimyan, Abdelzaher e Theodorou (2024; preprint 2020/2021)

*Social System Inference From Noisy Observations*. DOI [10.1109/TCSS.2022.3229599](https://doi.org/10.1109/TCSS.2022.3229599); [arXiv:2012.03075v2](https://arxiv.org/abs/2012.03075v2). O [registro institucional dos autores](https://experts.illinois.edu/en/publications/social-system-inference-from-noisy-observations/) confirma TCSS 11(1):639–651, 2024. Recuperado em A2.

Lido: **HTML aberto do preprint v2**, introdução, §II-C, equações 7/9, §III-D e §V; não a versão editorial. Infere rede e vieses de uma trajetória de opiniões: separa `x(k+1)=alpha+W x(k)+p(k)` de `y(k)=x(k)+o(k)`. Há erro de observação e ruído de processo. Deriva comprimento amostral suficiente para precisão/confiança prescritas, por estimação autorregressiva; a extensão não linear requer excitação por fontes de opiniões extremas. Não procura força mínima contra persistência pareada. **E1 parcial; E2 parcial; E3 não; E4 não; E5 não** — limite de amostra não é `a*(r)`. **Veredito: sobreposição parcial.**

### C23 — Kolic, Monti, De Francisci Morales e Pangallo (2025; revisão 2026)

*Comparing Data Assimilation and Likelihood-Based Inference on Latent State Estimation in Agent-Based Models*. [arXiv:2509.17625v3](https://arxiv.org/abs/2509.17625v3), submissão 22/09/2025, revisão 29/04/2026; sem DOI editorial indicado. Recuperado em A1.

Lido: **[HTML aberto v3](https://arxiv.org/html/2509.17625v3)**, §§2.1, 4.2, 4.5 e Figs.1–2. Compara Ensemble Kalman Filter com inferência por verossimilhança no BCM. Opiniões são latentes, mas eventos de interação são observados. A simetria `x` versus `1-x` pode impedir distinguir estados pelo operador de observação; avalia recuperação e previsão. O ruído variado em §4.5 é somado à **atualização latente**, não à resposta. Assim, “latente” e “ruído” no título/desenho não estabelecem E2. **E1 parcial; E2 não; E3 não; E4 não; E5 não. Veredito: sobreposição parcial**, em estimabilidade de opiniões/mecanismos observados.

### C24 — Lenti, Silvestri e De Francisci Morales (2025/2026)

*Variational Inference of Parameters in Opinion Dynamics Models*. [ICWSM 2025, DOI 10.1609/icwsm.v19i1.35963](https://ojs.aaai.org/index.php/ICWSM/article/view/35963); [arXiv:2403.05358v2](https://arxiv.org/abs/2403.05358v2), revisão 03/12/2025. Extensão TCSS identificada por DOI [10.1109/TCSS.2025.3640692](https://doi.org/10.1109/TCSS.2025.3640692). Recuperado por CR08 e busca de título.

Lidos: **resumo editorial ICWSM e HTML aberto do preprint v2**, §§IV–V. Estima atributos/regras de confiança limitada com repulsão por inferência variacional e relaxação diferenciável, comparando recuperação/custo com ABC/MCMC. Em §V, pares e resultados de interação, além de `x0`, são observados; estimar velocidade `mu` fica como trabalho futuro. Não contrasta influência com nula de persistência sob confiabilidade. **E1 parcial; E2 não; E3 não; E4 não; E5 não. Veredito: sobreposição parcial.** O resumo público indexado da extensão institucional foi localizado, mas a página direta retornou 403 e seu PDF restrito não foi acessado. Não se atribui leitura da versão editorial TCSS; manifestações relacionadas não são duas descobertas independentes.

### C25 — Brockers, Ehrlich e Priesemann (2025; revisão 2026)

*Disentangling Interaction and Bias Effects in Opinion Dynamics of Large Language Models*. [arXiv:2509.06858v2](https://arxiv.org/abs/2509.06858v2), submissão 08/09/2025, revisão 22/05/2026; sem DOI editorial indicado. Recuperado em W01/W03 e por localização do título.

Lido: **[HTML aberto v2](https://arxiv.org/html/2509.06858v2)**, §§2.1, 2.3 e apêndices D–F. Duas LLMs discutem; sondas de opinião entre rodadas não realimentam a memória. Modelo Bayesiano separa interação linear de vieses/ancoragem, com ablações e recuperação sintética. Avalia LOO-R² e teto de variância explicável por repetições; entropia da resposta representa incerteza. A sonda sem feedback aproxima a separação entre observação e dinâmica, mas não define confiabilidade externa variada. **E1 parcial; E2 parcial; E3 parcial** — ablações de vieses, sem persistência pareada; **E4 não; E5 não. Veredito: sobreposição parcial.** São agentes LLM, não respondentes de um painel de opinião humana simulado desta forma.

### C26 — Xing, Bizyaeva e Johansson (2024)

*Learning Communities from Equilibria of Nonlinear Opinion Dynamics*. [arXiv:2409.08004v2](https://arxiv.org/abs/2409.08004v2), revisão 13/09/2024; sem DOI editorial verificado nesta busca. Recuperado em A2.

Lido: **HTML aberto v2**, §§II-A, III, IV-A–B e Teorema 1. Recupera comunidades de uma rede SBM latente por equilíbrios de dinâmica não linear saturada, com pesos próprios/interpessoais. Delimita recuperação quase exata e falhas por simetria/sinal da influência; interação forte não garante recuperação melhor. §IV-A pressupõe equilíbrio exato e deixa observações ruidosas para o futuro. O mecanismo de opinião é assumido; o alvo são comunidades. **E1 sim; E2 não; E3 não; E4 parcial** — classificação de nós; **E5 parcial** — regiões de recuperação, não `a*(r)`. **Veredito: sobreposição parcial**, em limites de inferência por dinâmica de opinião.

### C27 — Valle e Ruz (2026)

*Classifying Directional Trajectories Near Criticality in the Three-State Majority-Vote Model with Deep Belief Networks and Bidirectional GRUs*. [arXiv:2608.18235v1](https://arxiv.org/abs/2608.18235v1), 18/08/2026; sem DOI editorial indicado. Recuperado em A2 e A3.

Lido: **HTML aberto v1**, resumo, introdução, metodologia e resultados. Simula majority-vote de três estados e classifica direções de trajetória perto de uma transição ordem/desordem, usando DBN para snapshots e Bi-GRU para sequências. O parâmetro `q` é dissenso no processo; não erro na observação. O classificador distingue fases/direções de um mecanismo, sem comparador de persistência nem força mínima por confiabilidade. **E1 parcial; E2 não; E3 não; E4 parcial; E5 não. Veredito: sobreposição parcial** em classificação de trajetórias simuladas.

### Pistas adicionais da triagem arXiv

| Identificador / fonte lida | Evidência e cinco elementos | Veredito |
| --- | --- | --- |
| Sienkiewicz e Chmiel 2026, *Dynamics-structure interchangeability in binary opinion models on multiplex networks*, [arXiv:2609.28340v1](https://arxiv.org/abs/2609.28340v1), HTML §§II–IV | Relaciona heterogeneidade de parâmetros e sobreposição de nós em camadas; compara soluções estacionárias/linhas críticas. Seu `r` é sobreposição estrutural, não confiabilidade. E=(parcial, não, não, não, não). | não sobrepõe o estimando |
| Vendeville 2025, *Voter model can accurately predict individual opinions in online populations*, [10.1103/PhysRevE.111.064310](https://doi.org/10.1103/PhysRevE.111.064310), [arXiv:2501.13215v3](https://arxiv.org/abs/2501.13215v3), HTML/resumo e suplemento §III.1/Table 2 | Ajusta voter com zealots a opiniões políticas no Twitter e classifica com rede de retweets observada; baseline de ligações diretas a zealots não é traço+AR. E=(parcial, não, não, parcial, não). | sobreposição parcial em validação/classificação |
| Achitouv et al. 2026, *D-MODD: A Diffusion Model of Opinion Dynamics Derived from Online Data*, [arXiv:2601.16226v2](https://arxiv.org/abs/2601.16226v2), HTML §§I.2–I.3 e II.1–II.2 | Infere drift/difusão de coordenadas de opinião em redes de retweet e ajusta Langevin. Difusão faz parte do processo. E=(não, não, não, não, não). Trabalho distinto de `2609.23690` já no manuscrito. | não sobrepõe o contraste de influência entre pares |
| Araújo 2026, *Response-Aware Coarse-Graining in Summary-Mediated Opinion Dynamics*, [arXiv:2609.05560v1](https://arxiv.org/abs/2609.05560v1), **somente resumo** | Resumos endógenos/compressão afetam a dinâmica; fronteira de estabilidade, não resposta com `r`. E=(parcial, não, incerto, não, não). | não sobrepõe o estimando na leitura disponível |

## O que esta busca acrescenta ao posicionamento

Soni (C21) torna mais forte o precedente de testar influência por discriminação contra autoexcitação e heterogeneidade. Lang (C01) e Mao (C22) mostram que inferência de interação com rede desconhecida e erro de observação também tem antecedentes. Holtmann (C10), Schuurman (C13) e Lafit (C11) aproximam confiabilidade, autorregressão, erro e poder. Portanto, a contribuição não pode ser apresentada como primeira discriminação de influência contra persistência, primeira análise de ruído observado ou primeira sensibilidade de detecção à confiabilidade. A diferença candidata continua sendo o contraste específico de todos os cinco elementos, com a cobertura limitada desta busca.

Devine (C16) acrescenta um antecedente do **mesmo item de confiança do SHP**. Turper–Aarts (C17) e Lugtig (C18) acrescentam estimativas publicadas de confiabilidade de itens de confiança política, que faltavam à discussão do domínio. Isso permite distinguir “há estimativas para confiança política” de “há uma estimativa transportável para este item do SHP”. Nenhum desses textos fornece a calibração externa da razão de sinal `r` no simulador; método, população, escala, nível de variância e hipótese de estabilidade do erro precisam ser comparados antes de qualquer transporte.

Foram redescobertos Ureña-Carrion, Borile, Moor-Smith–Carpentras, Carpentras–Quayle, Achitouv `2609.23690` e Tang, já presentes nos insumos. Não foram contabilizados como candidatos novos. Albi–Alla–Calzola `2603.15927` também já constava da triagem do dossiê; sua releitura confirmou ruído no processo e inferência de kernels, sem canal `r` ou nula pareada. O relatório não reabre ou reescreve as decisões antigas.

## Limites da conclusão

A fronteira continua sendo uma comparação condicionada ao gerador, à família de nulas e ao discriminador declarado. Separar estatisticamente esses processos simulados não identifica influência causal em um painel sem exposição observada. Não alcançar a AUC-alvo não estabelece indistinguibilidade geral.

A busca foi adaptativa e não exaustiva. O recorte temporal aumenta a visibilidade de publicações recentes, mas não resolve o viés de indexação; resultados de periódicos dependem dos depósitos e das páginas disponíveis. Resumos, versões abertas dos autores e texto publicado têm profundidades diferentes. Falhas de API e artigos sem leitura integral permanecem lacunas. Nenhuma conclusão desta entrega altera os protocolos congelados, o dossiê anterior, os resultados experimentais ou o manuscrito.

## Proveniência dos insumos preservados

SHA-256 antes da busca, para conferir que os documentos usados não foram reescritos:

| Insumo | SHA-256 |
| --- | --- |
| `dossier.md` | `3e0c86d1b14208948a154c6518b761483b34709e9842ab644e7feaced5cdcfdf` |
| `search-log.json` | `af45831881dfc90096b6644ea227982fca4056189e06be76e3e70a00269433cc` |
| `claude-novelty-challenge.md` | `1a4c99935f352f4dc9e4930414cf2df1e7f0d8711c8b7831b675f6487a8e4107` |
| `related-work.tex` | `73b79773351580474c3d949f6adee140ba0e3b18388e1a058a64f353c22aa7d9` |

## Verificação da entrega

Os quatro hashes foram reconferidos após a busca, sem alteração. Os quatro links locais do relatório resolvem; os 27 identificadores de candidatos são únicos e consecutivos; a checagem de whitespace não apontou problemas. A comparação de DOI/arXiv com os quatro insumos não encontrou repetição entre os candidatos apresentados como novos. Essa comparação complementa a leitura dos insumos, sem garantir deduplicação de toda a literatura.

A checagem estrutural `scripts/check_repository.py`, executada com Python 3.12, falhou nos links Markdown já existentes de `experiments/exploratory/detection-boundary-v4-exploratory/VALIDATION-FIXES.md`. Conferência individual: seis dos sete checks passaram; todas as violações do check de links pertencem àquele arquivo, cujo conteúdo é idêntico ao da base. Os links problemáticos incluem caminhos absolutos para outro worktree e diretório local de validação. O gate geral permanece com falha preexistente. O único arquivo novo no Git é este relatório; branch e HEAD permanecem os indicados no início, sem commit.
