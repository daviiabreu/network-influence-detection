# Diagnóstico de deduplicação v1: categorias arXiv e custo de comparação

Data: 2026-09-09 (America/Sao_Paulo).

Estado: diagnóstico reproduzido sobre observações reais de desenvolvimento.
Não é preparação do corpus da aquisição primária v2, correção aplicada,
adjudicação científica ou autorização para screening. O parser, a deduplicação,
o protocolo, os snapshots e os journals existentes permaneceram inalterados.

A deduplicação v1 une registros por categoria temática arXiv, porque o adaptador
retém `category:*` em `identifiers` e o algoritmo usa qualquer identificador
compartilhado. Em uma amostra de 512 observações, isso gerou um grupo com 160
identificadores e fez a construção de `ScholarlyWork` falhar antes do guard de
conflitos do corpus. A amostra completa de 2.467 observações reproduziu a mesma
falha, com 622 identificadores no primeiro grupo que excedeu o limite.

## Seleção e reprodução das entradas

Foram selecionadas somente páginas terminais `seed_recall_page_recorded` dos
pilotos sob
`/Users/davi/.local/state/research-workbench/claude-handoff-20260907/`:

| Fonte | Seleção | Páginas | Observações |
| --- | --- | ---: | ---: |
| OpenAlex | `openalex-volume-title-abstract-v1`, exceto `volume.openalex.q03`; para Q03, `openalex-consensus-volume-v3` / `probe.openalex.q03` | 10 | 10 |
| arXiv | `arxiv-pilot-v3`, os dez search IDs | 14 | 1.056 |
| DBLP | Pares `measurement_id` / `search_id` declarados no índice combinado | 21 | 1.401 |

O [índice DBLP](../search-design/2026-09-07/dblp-evidence-combined.json) delimita
as medições utilizadas e impede incorporar predecessores redundantes. Nenhum
evento de falha de provedor ou fixture forneceu registros. Os journals foram
carregados em modo somente leitura; `validate_bibliographic_page_bytes`
reproduziu os metadados das 45 páginas a partir dos bytes brutos, verificando
bindings da requisição e hashes dos artefatos públicos. Sucesso de uma página
não significa que sua consulta ou o conjunto de pilotos foi completo.

Cada ocorrência recebeu a projeção existente `observation.<hash>`, preservando
origem, protocolo do piloto, requisição, página, rank e registro original. Não
foram deduplicados IDs repetidos antes do ensaio. A lista conjunta é uma amostra
diagnóstica de diferentes protocolos de desenvolvimento, não uma projeção
aprovada de corpus. Seu hash canônico é
`e88fcb4279ba9447cb7975d85d9131944334dbed27fc0cb4ccf0196f3d2fce6f`.

O relatório privado com seleção por página, paths, hashes, metadados dos dois
registros mínimos, erros e medições está em
`/Users/davi/.local/state/research-workbench/deduplication-diagnostic-20260909/report.json`,
SHA-256 `dff5a500c99fe803c16929c17b90583693407ce3b1e099e526848f4f94c0289d`.
Nenhum título, resumo, corpo de fonte ou credencial foi incluído neste registro.

## Causa e exemplo mínimo

Em [bibliographic_search.py](../../../../../workbench/src/research_workbench/workflows/systematic_review/bibliographic_search.py),
`_normalize_arxiv` adiciona a categoria primária do Atom ao conjunto de
identificadores. Em
[deduplication.py](../../../../../workbench/src/research_workbench/workflows/systematic_review/deduplication.py),
`deduplicate_records` preenche `by_identifier` sem distinguir tipos e une todos
os registros que compartilham um valor; o argumento `policy` não restringe essa
união. O SHA-256 do módulo examinado é
`16e0b69ea644038905e1130622641fd90df57eee6d815c6572bc261487a0faf5`.

Dois registros reais, com títulos normalizados diferentes e sem identificador
de trabalho compartilhado, bastam para reproduzir a união:

| Identificadores originais | Localização no piloto arXiv |
| --- | --- |
| `arxiv:2605.20418`, `category:physics.soc-ph` | `search.arxiv.q02`, página 0, rank 53; observado em 2026-09-08T02:05:56.076086Z |
| `arxiv:1007.5391`, `category:physics.soc-ph`, `doi:10.1371/journal.pcbi.1000959` | `search.arxiv.q09`, página 0, rank 35; observado em 2026-09-08T02:07:36.833538Z |

O único valor compartilhado é `category:physics.soc-ph`. A função v1 emite um
work e nenhum candidato de adjudicação para esse par; o resultado tem hash
`930797f32e8ca21488acb921670c46fe78e11ff93baba2284fe2a87227774873`.
Uma categoria temática não estabelece identidade de trabalho.

| Evidência | SHA-256 |
| --- | --- |
| Atom Q02 | `2fbbc35291126559c7353764551d8977b0c1bc1f87cbadb6344c2b579f242d53` |
| Evento Q02 | `c5a1197b8ac2d49117e46495a5b33ab183f3b549bc2d4385559ec622dcbffd9f` |
| Atom Q09 | `90ddc4f59cd1593ce1446271b2268fcab3db62a732e5a6acd49dedece4181163` |
| Evento Q09 | `c502954ab1b120cdf0353f0e3aff20e2c3e1e9b2f0a428da1312e90ac68a50c4` |

Na amostra completa, `category:physics.soc-ph` conecta 436 observações arXiv
com 389 títulos normalizados distintos. As conexões adicionais por outros
identificadores levam a um grupo de 444 observações e 622 identificadores.
`category:cs.SI` conecta 165 observações arXiv; seu grupo final contém 172
observações e 187 identificadores. Esses são grupos intermediários produzidos
pelo algoritmo, não contagens aceitas de trabalhos científicos.

O [contrato ScholarlyWork](../../../../../workbench/src/research_workbench/workflows/systematic_review/contracts.py)
admite no máximo 100 identificadores. O erro real para as primeiras 512
observações, ordenadas por ID projetado, foi `Tuple should have at most 100
items after validation, not 160`. Na amostra completa, o valor foi 622.
`ReviewCorpusStageRuntime` chama a deduplicação antes de `_readiness_conflicts`,
portanto a exceção ocorre antes de produzir `deduplication_policy_conflict`.
O guard existente não torna essa entrada processável nem legitima essas uniões.

## Custo observado e experimento de agrupamento por título

O loop de candidatos compara todos os pares entre grupos distintos e normaliza
novamente os dois títulos em cada comparação. Para 22.362 observações, seriam
até 250.018.341 pares. Esse tamanho vem da
[estimativa de capacidade](2026-09-09-primary-acquisition-v2.md), não de um
corpus já adquirido.

O benchmark usou Python 3.12.13, arm64. Uma cópia da função modificada somente em
memória calculou títulos normalizados uma vez e comparou apenas pares dentro
do mesmo bucket. A formação dos grupos, exclusão de pares do mesmo work,
signals, IDs, ordenação, serialização e validação foram preservadas. O resultado
canônico completo foi comparado byte a byte com o original, incluindo seus
hashes. O recorte DBLP/OpenAlex foi usado porque passa o contrato de grupo;
retirar arXiv do corpus real não é uma solução proposta.

| Observações DBLP/OpenAlex | Original | Buckets em memória | Pares totais / mesmo título | Candidatos de adjudicação | Bytes iguais |
| ---: | ---: | ---: | ---: | ---: | --- |
| 256 | 0,283 s | 0,0074 s | 32.640 / 2 | 1 | sim |
| 512 | 1,408 s | 0,0173 s | 130.816 / 11 | 9 | sim |
| 1.024 | 4,960 s | 0,0323 s | 523.776 / 65 | 55 | sim |
| 1.411 | 10,072 s | 0,0451 s | 994.755 / 130 | 109 | sim |

No maior recorte, os dois resultados têm hash
`c5bc9c99583f05e44fb70f76c35d41380b3b5942e1545cb392ba5d6f3262fbab`.
Um recorte misto de 256 observações também produziu bytes iguais; isso preserva
inclusive as uniões inadequadas da v1, não constitui validação científica.

Extrapolar quadraticamente as medições DBLP/OpenAlex para 22.362 observações
produz aproximadamente 36–45 minutos por execução original. Essa é uma
estimativa de planejamento sobre entradas que passariam os contratos: a
amostra mista real falha antes do loop. As amostras não são aleatórias, OpenAlex
tem somente dez registros, a distribuição final de títulos é desconhecida e o
custo de serialização também cresce. Um bucket muito frequente ainda exige
comparações quadráticas dentro dele. Não foi medido o corpus completo nem se
estima aqui tempo garantido para a versão com buckets.

## Próximo limite de decisão

O [processo de corpus](../../../../../docs/process/systematic-review-corpus.md)
preserva explicitamente a v1 e registra a falta de semântica normativa para
`exact_identifier_priority`. O
[protocolo v2](../protocol/opinion-dynamics-systematic-map-v2.json) lista somente
`dblp` e `doi`, sem definir se são uma allowlist ou precedência, nem o tratamento
de identificadores incompatíveis. Essa decisão científica não é inferida deste
benchmark.

Uma correção futura deve manter categorias como metadados de classificação,
nunca como chaves de identidade. A menor opção local seria um sucessor
versionado que desconsidere `category:*` na união, preservando os registros
originais; isso, isoladamente, não resolve o significado de identificadores de
trabalho não listados na política. A alternativa é primeiro explicitar no
protocolo os tipos autorizados e sua precedência ou allowlist, e implementar
um sucessor que siga essa regra. A inclusão de arXiv entre chaves autorizadas,
se desejada, deve ser uma decisão registrada, não uma correção implícita.

Em ambos os casos, preservar parser e replay v1, observações lossless, snapshots
e runs concluídos. Não remover identificadores dos originais, aumentar o limite
de 100 para esconder a união ou substituir o algoritmo histórico silenciosamente.
Otimizar a enumeração por títulos pode ser uma mudança posterior que preserve
bytes; não resolve a identidade e não converte igualdade de título em auto-merge.

A preparação real deve consumir somente a aquisição primária replayada. Estes
pilotos e medições não substituem sua conclusão, sua aprovação de protocolo ou
a futura decisão sobre deduplicação. Nenhum código de runtime foi alterado por
este diagnóstico.

## Recomendação concreta para decisão do Research Owner

Recomenda-se interpretar a lista v2 `[dblp, doi]` como allowlist de tipos que
podem sustentar fusão automática, sem inventar precedência entre os dois.
Essa opção usa os tipos já declarados e preserva uma decisão explícita antes
de ampliar a automação. O texto abaixo é uma proposta para um sucessor
versionado; não está em vigor por constar neste relatório:

> Somente identificadores exatos dos tipos `dblp` e `doi` podem conectar registros
> para fusão automática. Categorias, incluindo `category:*`, são metadados de
> classificação: não definem identidade nem geram candidatos apenas por serem
> compartilhadas. Outros identificadores de trabalho, como arXiv e OpenAlex,
> permanecem evidência para exame ou candidatos de adjudicação, sem autorizar
> auto-merge. Um componente com múltiplos valores distintos de um tipo autorizado
> não é aceito automaticamente: preserva todos os registros e evidências para
> adjudicação do Research Owner, sem escolher um identificador vencedor.
> Igualdade de título normalizado também só pode gerar candidato; nunca prova,
> por si só, que duas observações representam o mesmo trabalho.

O sucessor precisa registrar como os identificadores não autorizados compõem
candidatos, sem expandir essa regra por inferência durante a implementação.
Autorizar arXiv ou OpenAlex para fusão automática seria uma alternativa material
à recomendação: exigiria aprovação explícita dos tipos e do tratamento de
conflitos, além do vínculo à nova versão de protocolo e algoritmo. Não se
converte a ordem canônica da lista em uma regra de precedência.

Manter arXiv fora da fusão automática tem custo operacional real. Nas 1.056
observações do piloto arXiv, 657 não têm DOI e correspondem a 592 identificadores
arXiv distintos. Há 62 identificadores sem DOI repetidos entre consultas,
abrangendo 127 observações e 68 pares; todos esses pares têm títulos
normalizados iguais. Sob a recomendação, a repetição do ID arXiv não bastaria
para consolidá-los automaticamente, e esses pares poderiam alimentar a fila
de adjudicação. Isso conserva a decisão de identidade, mas aumenta trabalho
de revisão e mantém repetições pendentes até a decisão. Não é uma contagem
da futura fila de produção nem autorização para excluir observações.

Essas contagens adicionais estão no arquivo privado
`/Users/davi/.local/state/research-workbench/deduplication-diagnostic-20260909/owner-decision-metrics.json`,
SHA-256 `fd1ec6a047a3d69a10c83997b25880cd5fbe99376403b98bf13c595363faffe5`.
Ele referencia o relatório-base sem sobrescrevê-lo. Nenhum registro original
foi modificado ou descartado para obter as contagens.

Pergunta proposta para apresentar ao Research Owner após esse contexto:

> Você aprova a deduplicação v2 com fusão automática somente por DOI ou DBLP,
> deixando categorias fora da identidade e encaminhando conflitos e repetições
> sem essas chaves para adjudicação, mesmo que isso aumente a fila de revisão?
