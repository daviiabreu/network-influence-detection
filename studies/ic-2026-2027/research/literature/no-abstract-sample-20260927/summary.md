# Verificação amostral de obras sem resumo — 27/09/2026

Esta é a verificação amostral pré-declarada da decisão 35. Ela cobre obras do
mapa sistemático priorizado v5.1 que ficaram `uncertain` na triagem de
título/resumo por não terem resumo em nenhuma observação. A amostra tem 80 obras
sorteadas localmente antes desta sessão (semente `20260927`): 40 da camada 0
(revisões/surveys) e 40 do lote `batch-0001`. Os registros por obra estão em
[`results.jsonl`](results.jsonl).

## Método

- Critérios aplicados: os mesmos do protocolo v5.1 e das regras 1–4 de
  `screener-v6.md`, incluindo o esclarecimento v5.1 de que modelos canônicos de
  dinâmica de opiniões pertencem ao domínio humano, salvo aplicação explícita a
  sistemas não humanos. O juízo foi feito sobre texto integral ou página pública,
  não sobre título isolado.
- Fontes lícitas, nesta ordem: arXiv (abs/PDF); registro OpenAlex e seus locais
  OA; Semantic Scholar Graph API; Europe PMC; repositórios institucionais ou de
  autor vinculados a esses registros, incluindo a API pública de busca do HAL;
  e uma única leitura da página DOI pública. Não houve raspagem de editoras,
  contorno de desafios anti-bot (Springer, HAL/Anubis, BASE), acesso atrás de
  paywall nem uso de espelhos ilícitos.
- A API de consulta do arXiv respondeu HTTP 406 neste ambiente. Por isso, a
  procura de versões arXiv usou `externalIds` do S2, os locais do OpenAlex e a
  busca por título em `arxiv.org/search`.
- Houve no máximo cerca de 4 tentativas por obra. Uma obra sem texto lícito
  após essas tentativas foi marcada como `unresolvable_no_lawful_text`.
- Cada `evidence_quote` foi conferida por programa contra o texto obtido, após
  normalização de espaços. Ela inclui o local da citação, como página, seção ou
  registro.
- Campos adicionais em `results.jsonl`: `evidence_kind` (`full_text`,
  `public_page`, `abstract_in_public_api_record` ou `none`) e `resolved`
  (verdadeiro só para `include`/`exclude`).

## Contagens

| Fase | include | exclude | uncertain | unresolvable | Total |
|---|---:|---:|---:|---:|---:|
| layer0 | 2 | 21 | 1 | 16 | 40 |
| batch-0001 | 14 | 1 | 1 | 24 | 40 |
| Total | 16 | 22 | 2 | 40 | 80 |

## Taxa de inclusão entre obras resolvidas

Obras resolvidas são as julgadas `include` ou `exclude`. Os intervalos são de
Wilson a 95%.

| Fase | Inclusões / resolvidas | Taxa | IC 95% (Wilson) |
|---|---:|---:|---|
| layer0 | 2 / 23 | 8,7% | 2,4% – 26,8% |
| batch-0001 | 14 / 15 | 93,3% | 70,2% – 98,8% |

Parcela não resolvida:

- `unresolvable`: 16/40 (40%) na camada 0 e 24/40 (60%) no lote 1.
- Somando `uncertain`, ficam sem juízo 17/40 (42,5%) na camada 0 e 25/40 (62,5%)
  no lote 1.

Análises de sensibilidade:

- **Limite inferior.** Tratando toda obra não resolvida como não incluída, a
  inclusão sobre as 40 obras sorteadas fica em 2/40 = 5,0% (IC 1,4%–16,5%) na
  camada 0 e 14/40 = 35,0% (IC 22,1%–50,5%) no lote 1.
- **Sem teses.** No lote 1, três inclusões são teses: 354b3e34 e e37e67d0 são de
  doutorado, e 09c329de é de mestrado. O escopo declara
  `grey_literature_policy: exclude`, e os tipos registrados não incluem teses.
  Sem essas três obras, a taxa fica em 11/12 = 91,7% (IC 64,6%–98,5%). O
  enquadramento de teses é uma questão para o Owner, não uma decisão tomada
  aqui.

## Principais motivos de exclusão

- `no_computational_model` (20 obras, todas da camada 0): revisões clínicas e
  de saúde, surveys de LLM/agentes, educação, segurança de IoT, fusão de dados,
  questionários descritivos e resenha de livros.
- `outside_date_or_language` (1 obra, camada 0): bdc45fad, artigo em chinês.
- `not_human_opinion_domain` (1 obra, lote 1): 18532978, controle de formação
  por consenso em engenharia.

Observação: 4 das 40 obras da camada 0 não são revisões e parecem falsos
positivos do detector por palavras como "Review Exercise", "Paper Under
Review", "product review" e "survey data": 5051573d, 79f0e245, f6114947 e
0b4d3163.

## Obras incluídas

**Camada 0**

- 69398d24 — visão geral algorítmica de dinâmicas de consenso e formação de
  opinião, com protocolos populacionais em tempo discreto e contínuo. É estudo
  secundário.
- 0b4d3163 — ABM calibrado por survey sobre crenças vacinais com contágio
  social na Ucrânia. É estudo primário, não revisão.

**Lote 1**

- 64b05d3f — confiança limitada com líderes de opinião concorrentes.
- 7c70cb83 — dinâmica de média, do tipo DeGroot, entre populações, com
  entradas de jogo repetido.
- 4675187e — ABM acoplado de opinião e autoconfiança, com análise e simulação.
- c0d2d6e6 — variantes do modelo do votante em redes, reverso e por arestas.
- 354b3e34 — voter model adaptativo em redes dirigidas. Tese de doutorado.
- e37e67d0 — voter model adaptativo com moment closure. Tese de doutorado.
- 0611c2fb — opinião expressa e privada com confiança limitada (MEPO).
- 09a99996 — contraparte termodinâmica do modelo de Axelrod.
- d25b1e8b — consenso fracionário para dinâmica de atitudes.
- 09c329de — dinâmica contínua de opiniões em ABM espacial. Tese de mestrado.
- 2b322eae — SLANT, dinâmica de opiniões orientada por dados do Twitter. Tem
  variante de título no arXiv.
- 5f0220ab — dinâmica híbrida de líderes e seguidores com alcance de consenso.
- b9512558 — ABM de mudança de atitude pela Teoria do Julgamento Social.
- 6a085e5a — ABM de influência social online calibrado e validado com dados.

Casos `uncertain`:

- 79f0e245 — só o sumário dos anais PRIMA 2016 estava disponível.
- 53776a43 — o resumo não estabelece se há dinâmica de crenças.

## O que a estimativa sustenta e o que não sustenta

**Sustenta:**

- No lote 1, as obras sem resumo com texto lícito acessível são quase todas
  relevantes: 14 de 15 resolvidas. Manter essas obras como `uncertain` implica
  perda real de inclusões se elas forem descartadas ou deixadas sem
  recuperação.
- Na camada 0, a maioria das obras resolvidas é irrelevante: 21 de 23. A
  relevância é baixa, mas não nula.
- Muitas obras já não estão sem resumo. Em 22 obras, o juízo usou resumo
  presente hoje em registro público do OpenAlex, S2 ou Europe PMC. O Europe PMC
  não está entre as fontes de recuperação do pipeline. Isso sugere que uma nova
  rodada de recuperação de metadados resolveria parte do estrato na etapa de
  título/resumo.

**Não sustenta:**

- Não é adoção de decisões. Os juízos são recomendações de um único avaliador
  agente, sem A/B cego, sem adjudicação e sem verificação humana. Nenhuma obra
  muda de estado canônico por causa deste arquivo. Exclusões em texto integral
  seguem dependendo de Davi.
- Não é estimativa não viesada para o estrato inteiro. A resolvibilidade
  depende da editora e do acesso aberto: Elsevier e Springer quase nunca foram
  legíveis, e SSRN retornou 403. Vários itens não resolvidos do lote 1 têm
  títulos que sugerem modelos canônicos, como Hegselmann–Krause, DeGroot,
  Axelrod, voter de duas camadas e estimação em confiança limitada. Os não
  resolvidos da camada 0 incluem um survey explícito de dinâmica de opiniões
  (98d181c9). As taxas entre resolvidas valem só para a parte acessível. O
  intervalo real para o estrato está entre o limite inferior acima e a taxa
  entre resolvidas.
- Com n = 15 e n = 23 resolvidas, os intervalos são largos. A amostra não
  permite estimar subgrupos, como família de modelos ou editora.
- Parte dos juízos se apoia apenas em resumo, sem o texto integral. Isso vale
  para os casos `abstract_in_public_api_record` em `results.jsonl`. O juízo do
  título/resumo pode mudar no texto integral.
