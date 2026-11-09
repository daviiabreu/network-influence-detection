# Auditoria integral da fila de identidades do corpus v3

Data: 13/09/2026. Revisão executada a partir de `b1f8bea6574137ce176ddfd5aecab5d158e93c1f`. Artefato derivado de preparação; nenhuma escolha `merge`, `distinct` ou `defer`, decisão humana, exclusão científica ou alteração do corpus foi registrada.

A fila foi reproduzida integralmente: **20.964 pares de observações correspondem a 10.754 pares de obras propostas em 4.990 componentes de revisão**. É possível reduzir a apresentação para 10.754 cartões, preservando todos os IDs e evidências, uma redução de 48,70% das unidades repetidas. O protocolo e o código atuais não autorizam resolver automaticamente nenhum candidato remanescente com os mesmos dados. Os componentes organizam a revisão; não representam 4.990 obras científicas nem 4.990 decisões suficientes.

## Entradas e verificação

| Artefato | SHA-256 |
| --- | --- |
| Protocolo v3 | `fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f` |
| Deduplicação result-3, algoritmo 2 | `41a54060be2206d88b13aa8d0026acca6b6f27342cb77391c8c3462f97b66a53` |
| Fila de metadados e identidades | `f979fdc89063fe3f38ce63dd828540b2a756cacedf68f9066e9b64275d0b9e41` |
| Observações projetadas | `772afb69e868ef3fc6cf94e79d3c1b422f11f8fba453621c0092fc65028fa5a1` |

As entradas estão no CAS privado `~/.local/state/research-workbench/broad-research-20260911/acquisition-v3/artifacts`. Os hashes dos quatro artefatos e dos dez snapshots brutos usados nos exemplos de DOI foram verificados. A execução de `deduplicate_records_v3` com todas as 54.570 observações e a política do protocolo reproduziu exatamente o objeto CAS, incluindo os títulos, IDs, partição, 20.964 candidatos e nove pendências de título. A fila reproduz os mesmos candidatos. A divergência entre o hash das observações projetadas e `input_record_sha256` do resultado é esperada: este último vincula a serialização canônica ordenada, reproduzida no cálculo.

| Contagem conferida | Resultado |
| --- | ---: |
| Observações adquiridas preservadas | 54.570 |
| Obras propostas | 46.400 |
| Com título / sem título | 46.391 / 9 |
| Obras propostas em componentes de identidade | 12.025 |
| Observações dessas obras | 15.950 |
| Componentes com duas / três / quatro obras | 3.492 / 1.168 / 254 |
| Maior componente | 44 obras, 989 pares de observações, 946 pares de obras |

A política já reuniu 13.723 observações em 5.553 propostas por identificador exato, reduzindo 8.170 ocorrências na projeção. Essa redução já está incluída nas 46.400 propostas; não é uma nova redução disponível.

## Categorias exclusivas para revisão

| Categoria de evidência | Pares de observações | Cartões de pares de obras |
| --- | ---: | ---: |
| `exact_identifier_conflict` | 442 | 442 |
| `syntactic_arxiv_bridge` | 4.750 | 1.951 |
| `title_only` | 15.772 | 8.361 |
| Total | 20.964 | 10.754 |

A classificação aplica esta precedência: identificador tipado compartilhado; depois ponte sintática entre `arxiv:BASE` e `doi:10.48550/arxiv.BASE`; depois somente título. A ponte foi contada como pista de investigação, sem afirmar equivalência bibliográfica dos pares. A [documentação oficial do arXiv](https://blog.arxiv.org/2022/02/17/new-arxiv-articles-are-now-automatically-assigned-dois/), consultada em 13/09/2026, confirma a regra geral `arXiv:ID` → `10.48550/arXiv.ID`, distingue esse DOI do DOI editorial informado pelo autor e informa que ele aponta à versão canônica mais recente. Não foram conferidos individualmente os registros DataCite ou páginas de destino dos 1.951 pares. Em 194 cartões, parte das observações tem a ponte e outra parte tem apenas o título; o cartão preserva as contagens de ambas. Os 1.757 demais cartões de ponte contêm somente essa categoria. Nenhuma evidência foi descartada para tornar as categorias exclusivas.

Pelos sinais originais do algoritmo, há 20.522 pares sem identificador tipado compartilhado e 442 com compartilhamento. Destes últimos, 298 também compartilham título normalizado e 144 não. Todos os 442 têm o sinal de conflito. A subdivisão sintática acima organiza os 20.522; não muda a fila original.

O gerador confirma igualdade entre os conjuntos de `candidate_id` anteriores e posteriores, unicidade e cardinalidade: **20.964 de 20.964 IDs preservados uma vez**, distribuídos em 10.754 cartões. Os cartões mantêm o mapeamento para observações, obras propostas, componentes e snapshots de origem.

## O que gera o bloqueio por identificador

A [política e implementação de identidade](../../../../../../workbench/src/research_workbench/workflows/systematic_review/deduplication_v2.py) admitem DOI, arXiv, DBLP e OpenAlex sem precedência. A normalização de DOI apenas ignora diferenças ASCII entre maiúsculas e minúsculas; arXiv remove o sufixo de versão. O código não converte DOI arXiv em um identificador do tipo `arxiv`.

A implementação primeiro conecta identificadores exatos. Se o componente contiver mais de um valor de qualquer tipo, divide **todas** as observações em propostas individuais. Foram encontrados 121 componentes exatos nessa condição, com 334 observações: 111 por pluralidade OpenAlex, oito por DOI, um por DOI e OpenAlex, e um por arXiv. Essa contagem inclui bloqueios que não geram um par na fila.

Dos 442 pares com ID compartilhado, 231 não apresentam pluralidade no próprio par: o conflito vem de outras observações do componente. Os outros 211 apresentam pluralidade direta: 193 OpenAlex, 17 DOI e um arXiv. Os sinais `conflicting_*` do candidato descrevem o componente original, portanto não devem ser lidos como prova de uma contradição particular entre os dois registros.

Há ainda 85 pares em 25 componentes com todos os metadados bibliográficos comparados iguais, incluindo o resumo apenas dentro do processo privado; diferem nos campos de aquisição. Exemplo: `dedupe.v2.09992b9861267a8417c08dca`, duas ocorrências de “Cascade-driven opinion dynamics on social networks”, `arxiv:2506.16302` e `doi:10.1109/tcss.2026.3669247`. Elas herdaram um conflito OpenAlex de outro membro. Isso é evidência útil para a revisão, mas a política atual não possui uma exceção que permita retirar esses pares automaticamente.

Existe uma colisão de metadados concretamente demonstrada: `dedupe.v2.d0600a85fb102dce9e3db87f` liga `arxiv:1205.3943` e `arxiv:1306.6813`, títulos diferentes, pelo DOI `10.1103/physreve.88.022152`. O DOI está presente nos dois feeds brutos, respectivamente nas entradas 4 e 80 (índices iniciados em zero), snapshots `f6e9936dfb8df0199f8f97e87d97665fe2a577b356e5e3acad9b4d0ecdc1268f` e `9f7fc7e669dd31b7f08d07ddafeeedb27220b4d286bb28519e2b6c569b0d816a`. Não foi decidido se isso representa erro de depósito, sucessão de manifestação ou outra relação; essa conclusão exige evidência adicional e disposição registrada.

## Os dez bloqueios de prontidão não demonstram dez erros

Todos provêm de observações DBLP com dois DOI; os valores foram conferidos diretamente nos bindings SPARQL brutos. São nove IDs DBLP porque `conf/sigmetrics/MukhopadhyayMR16` aparece em duas buscas. Seis dos dez bloqueios estão fora dos componentes de pares de identidade: revisar apenas os 20.964 pares não os resolveria.

| ID DBLP | DOI preservados |
| --- | --- |
| `series/synthesis/2009Gay` | `10.1007/978-3-031-02187-9`; `10.2200/s00135ed1v01y200905hci004` |
| `conf/sca/BuchsbaumB05` | `10.1145/1073368.1073370`; `10.2312/sca/sca05/009-018` |
| `conf/sigmetrics/SankararamanGS20` | `10.1145/3393691.3394217`; `10.1145/3410048.3410065` |
| `conf/alife/Pacheco16` | `10.1162/978-0-262-33936-0-ch007`; `10.7551/978-0-262-33936-0-ch007` |
| `conf/alife/000116` | `10.1162/978-0-262-33936-0-ch051`; `10.7551/978-0-262-33936-0-ch051` |
| `conf/isca/ChienK92` | `10.1109/isca.1992.753323`; `10.1145/139669.140383` |
| `conf/sigcse/Lucas76` | `10.1145/800107.803455`; `10.1145/952989.803455` |
| `conf/sigmetrics/MukhopadhyayMR16` (duas ocorrências) | `10.1145/2896377.2901488`; `10.1145/2964791.2901488` |
| `conf/alife/MarriottC14` | `10.1162/978-0-262-32621-6-ch118`; `10.7551/978-0-262-32621-6-ch118` |

O [diagnóstico público](identity-audit.json) fornece os dez IDs de obra e observação, hashes dos snapshots e índices dos bindings de cada DOI. Os pares podem refletir aliases ou formas publicadas relacionadas. O que foi demonstrado é sua presença na fonte e o bloqueio pela regra atual; nenhum DOI foi removido e nenhuma equivalência foi presumida.

## Título e tipo de publicação não bastam para identidade

Os pares sem ID compartilhado incluem 8.111 combinações de preprint com outro tipo, 131 combinações de `conference_paper` com `article`/`journal_article`, e 691 pares com diferença de pelo menos dez anos. São categorias sobrepostas. Os rótulos dos provedores foram preservados: `article` não prova sozinho uma publicação em periódico. Igualdade de autores não resolve a identidade: 11.580 pares sem ID compartilhado têm listas não vazias de autores exatamente iguais.

Exemplo de manifestação que precisa de conferência: `dedupe.v2.0380c4639e8ef835f3359793`, “Non-Bayesian Social Learning with Observation Reuse and Soft Switching”, DOI `10.1109/icc.2017.7996912` (2017, `conference_paper`) e `10.1145/3199513` (2018, `article`). O título sugere uma relação; não determina se a contribuição científica deve contar como a mesma obra.

O maior componente, `identity-component.56675585445b3561389a96b7`, reúne variações de “The Name Game” de 1970 a 2017. Outros componentes grandes têm “WITHDRAWN” (13 propostas), “Introduction” (13) e “New Books” (11). O componente `identity-component.cf9abdf87025306b919b5713` reúne 12 propostas cujos cinco títulos japoneses distintos perdem os caracteres japoneses na normalização ASCII, conservando fragmentos numéricos iguais. Isso demonstra ruído no sinal normalizado, não uma disposição científica automática. Nenhum desses componentes deve ser tratado como uma obra.

## Redução operacional e transição necessária

1. Usar os 10.754 cartões e os 4.990 agrupamentos de contexto já gerados, mantendo os 20.964 IDs. A redução de apresentação é determinística e não altera a unidade científica.
2. Investigar primeiro as 1.951 relações com ponte sintática arXiv. O exemplo `dedupe.v2.00014f5d902dc7fe832fd884` contém `arxiv:2607.05597` de um lado e `doi:10.48550/arxiv.2607.05597` do outro. Confirmar e registrar uma ponte de identificadores ou mudar sua normalização precisa produzir uma versão sucessora; trocar somente a função de comparação quebraria a reprodução da política atual. A consulta externa foi limitada à documentação geral; nenhuma aquisição bibliográfica individual foi executada nesta auditoria.
3. Tratar os conflitos exatos com a evidência completa do componente, distinguindo colisões diretas dos 231 pares com bloqueio herdado. Não usar preferência OpenAlex/DOI inventada, regra por título ou remoção silenciosa de DOI plural.
4. Resolver em separado as nove pendências de título e os dez conflitos de prontidão. Esses bloqueios não desaparecem com a apresentação compacta.

Há uma limitação de representação comprovada, além das decisões científicas pendentes. A [fila de metadados](../../../../../../workbench/src/research_workbench/orchestration/review_corpus_metadata.py) declara que é apenas uma proposta. O [runtime de adjudicação](../../../../../../workbench/src/research_workbench/orchestration/review_adjudication.py) consome `ReviewAdjudicationQueue` e `DeduplicationResult` dos schemas 1/2. A validação de ambos contra os artefatos v3 desta auditoria foi executada e os rejeitou: campos incompatíveis, `works` ausente e versão 3 não permitida. Converter chaves, eliminar as obras sem título ou fabricar um recibo de decisão não constitui uma transição válida.

As [escolhas de deduplicação](../../../../../../workbench/src/research_workbench/workflows/systematic_review/adjudication.py) exigem `OwnerDecision` vinculado ao Research Owner, protocolo, solicitação e evidências exatas. O resultado mantém pendente cada candidato sem escolha explícita; uma fusão transitiva não remove automaticamente as demais pendências. Antes de consumir decisões desta fila, é necessário um sucessor compatível que preserve a linhagem e os bloqueios de metadados. Esta auditoria não implementou nem simulou decisões humanas.

## Entregáveis e reprodução

O [sumário JSON](identity-audit.json) contém contagens, exemplos metadata-only, índices de evidência, verificação e os hashes abaixo. O diagnóstico integral e os cartões ficam fora do Git, em `/Users/davi/.local/state/research-workbench/corpus-preparation-20260913/identity-audit`. Não contêm resumos ou texto integral; comparações desses campos são booleanos calculados localmente.

| Arquivo privado | SHA-256 | Bytes |
| --- | --- | ---: |
| `diagnostic.json` | `eaa2780fcb94e3f7b1d4abd35ac32628704bd1ccaacf5266d095856ee9b65981` | 20713111 |
| `review-cards.json` | `4779f20d33072b10d68c18e4535555ad7684b7e1333c4c5441a9ec525059086f` | 19879926 |
| `generate-review-cards.py` | `f91d25c1b8b16a263313a03f12253f1b39d5adb696d39e371b0e703192d61b04` | 6183 |

Para reconstruir os cartões, executar a partir da raiz do repositório:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=workbench/src workbench/.venv/bin/python \
  /Users/davi/.local/state/research-workbench/corpus-preparation-20260913/identity-audit/generate-review-cards.py
```

Duas execuções do gerador produziram o mesmo SHA-256 dos cartões. O gerador verifica hashes das entradas, revalida a partição result-3 e a fila, calcula as três categorias exclusivas, recompõe os componentes e exige preservação de todos os `candidate_id`. A auditoria adicional reproduziu a deduplicação completa e verificou os 14 hashes de entrada/fontes citadas. Não houve edição de código de produção, alteração dos artefatos CAS, execução de modelos, aquisição bibliográfica de rede ou matriz completa de testes. O resultado continua sendo preparação para adjudicação e calibração, sem corpus canônico ou revisão sistemática concluída.
