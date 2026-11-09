# Propostas de identidade do corpus v3

Esta é a execução histórica v3.1. O
[sucessor para auditoria após C2 v2](../2026-09-24/c2-v2-execution-result.md)
foi gerado em 24/09/2026; nenhuma versão das propostas registra decisão C3.

Data: 17/09/2026, com as execuções registradas em 18/09/2026 (America/Sao_Paulo).
Este documento registra propostas geradas por regra para os 20.964 pares de
identidade do corpus v3. Nenhuma escolha foi registrada como decisão do Research
Owner, nenhum pedido C3 foi submetido e nenhum artefato de evidência foi alterado.

A versão vigente é a 3.1.0 do gerador
[`identity_proposals.py`](../../../../src/ic_study/literature/identity_proposals.py),
executada na revisão `df10980c` com semente 20260917. Ela substitui as versões
1.0.0, 2.0.0 e 3.0.0, cujos arquivos continuam preservados e são descritos ao
final. O gerador verifica o SHA-256 de cada entrada antes de ler, exige que a
fila reproduza exatamente os candidatos do result-3 e confere a normalização de
identificadores da política 2 nas 46.400 obras propostas. Cada execução grava
uma única vez em um diretório privado novo.

## Entradas

| Artefato                        | SHA-256                                                            |
| ------------------------------- | ------------------------------------------------------------------ |
| Observações projetadas          | `772afb69e868ef3fc6cf94e79d3c1b422f11f8fba453621c0092fc65028fa5a1` |
| Deduplicação result-3           | `41a54060be2206d88b13aa8d0026acca6b6f27342cb77391c8c3462f97b66a53` |
| Fila de metadados e identidades | `f979fdc89063fe3f38ce63dd828540b2a756cacedf68f9066e9b64275d0b9e41` |
| Recorte temático (escopo)       | `2b0fbe123e84566800a064e8318e03f981531f6c67ddf8f678f78cde88ef28a6` |

O recorte temático está em
`/Users/davi/.local/state/research-workbench/corpus-resolution-20260917/focused-scope-draft-2026-09-18.json`,
e as execuções com escopo apontam para esse caminho.

## Regras

Cada cartão reúne os pares de observações entre duas obras propostas. As regras
são conjuntivas e avaliadas nesta ordem; o texto exato está em `RULES` e
`DEFINITIONS` no código e é copiado para o manifesto.

| Regra                                   | Condições principais                                                                                                                                                                                                                                                                                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `T1.shared_identifier`, `T1.arxiv_link` | Identificador tipado compartilhado, ou mesmo arXiv entre ID, DOI 10.48550 e chave CoRR do DBLP; título igual nas normalizações ASCII e com escrita original; Jaccard de sobrenomes ≥ 0,8; anos a no máximo 1; as observações que carregam o vínculo são da mesma classe de manifestação; sem divergência de DOI, sem contradição e resumo compatível. |
| `T1.title_year_authors`                 | Título não genérico, não reutilizado por equipes disjuntas e sem perda de escrita; mesmo ano; sobrenomes idênticos; se o conjunto for um único sobrenome, resumo com Jaccard ≥ 0,5; mesma classe, que não pode ser cópia de repositório; sem divergência de DOI, sem contradição e resumo compatível.                                                 |
| `T2.version`                            | Não T1; título inequívoco; anos a no máximo 2; Jaccard de sobrenomes ≥ 0,8; sem vínculo de identificador, a coincidência não pode repousar num único sobrenome sem resumo ≥ 0,5; sem contradição e resumo compatível. As notas dizem por que não é T1.                                                                                                |
| `T3.disjoint_authors`                   | Sem vínculo de identificador; nenhum token de nome em comum, nem sobrenome contido no nome concatenado do outro lado; resumo ausente ou Jaccard < 0,3.                                                                                                                                                                                                |
| `T3.generic_title_without_match`        | Sem vínculo; título genérico ou reutilizado; um lado sem autores; resumo ausente ou divergente; e ao menos um fato distintivo (anos a mais de 2, contradição, divergência de DOI ou resumo divergente).                                                                                                                                               |
| `T4.*`                                  | Todo o resto, com o primeiro motivo aplicável: identificadores contraditórios, conferência contra periódico, vínculo de identificador incompleto, título ambíguo, anos, resumo divergente, autoria de um só sobrenome sem apoio do resumo ou autoria parcial.                                                                                         |

Contradição significa DOIs registrados distintos, arXiv distintos, chaves DBLP
de publicação distintas ou conferência contra periódico. Há divergência de DOI
quando os dois lados têm identificadores de cópia e nenhum em comum. Contam os
DOIs fora de 10.48550 e os IDs arXiv, de modo que o DOI arXiv e o ID arXiv do
mesmo trabalho coincidem.

Cada observação tem uma de três classes de manifestação. É pré-print quando o
tipo, a fonte arXiv ou a chave CoRR o indicam, ou quando todos os seus DOIs são
arXiv ou de repositório (Zenodo, SSRN, OSF, Research Square e os demais
prefixos do manifesto). É cópia de repositório quando vem do OpenAlex sem DOI
nem chave DBLP e o local de publicação não é um índice ou plataforma de
periódicos (DOAJ, PubMed, Dialnet, Neliti, DergiPark, Project Muse, OAPEN,
CyberLeninka). Além disso, o local precisa nomear um serviço de repositório
(repository, ePrints, HAL, DSpace, Digital Commons, RePEc, LA Referencia,
CONICET e os demais termos do padrão no manifesto), terminar com a instituição
entre parênteses, como "(University of X)", ou ter página em host de
repositório. Nos demais casos é publicada. Uma obra é publicada se alguma
observação for; senão, cópia de repositório se alguma for; senão, pré-print.
Regras por título tratam como questão de versão qualquer diferença de classe e
qualquer cópia de repositório (nota `repository_copy`). Nem mesmo duas cópias de
repositório se unem em T1 só pelo título, porque podem ser versões distintas.

As cadeias de autores são separadas em pessoas: separadores `;`, `and` e `&`,
listas unidas por vírgula, a forma "Sobrenome, Nome", acentos LaTeX, entidades
HTML, observações entre parênteses, afiliações, ORCID e títulos acadêmicos.
Títulos descartam o `\n` literal seguido de espaço.

Depois da classificação, os grupos de fusão são fechados transitivamente. Um
grupo T1 que una duas obras com contradição, autores disjuntos ou anos a mais de
2 perde seus cartões T1 para `T4.transitive_merge_contradiction`. Um grupo T1
que apenas una manifestações diferentes passa seus cartões para T2 com a nota
`mixed_manifestation_group`. São diferentes a divergência de DOI, classes
distintas ou duas cópias de repositório sem vínculo de mesma classe, e anos a 2
de distância. No cenário T1+T2, os grupos com contradição, autores disjuntos ou
mais de 2 anos retêm os cartões T2. Nenhum cartão T3 liga obras unidas por fusão
proposta, o que o código verifica.

## Unidades de adoção

T1 foi dividido em duas unidades que podem ser adotadas separadamente, cada uma
com arquivo de escolhas, amostra de auditoria e cenário de escolhas de
identificador próprios. `T1-identifier` reúne as fusões apoiadas em
identificador. `T1-title` reúne as fusões por título, ano e sobrenomes idênticos,
sem vínculo de identificador. Os cenários calculados são `T1-identifier`, `T1`
(as duas unidades) e `T1+T2`.

## Resultado do corpus completo

| Unidade       | Cartões | Pares de observações | Amostra de auditoria | Variação desde a v2 (cartões / pares) |
| ------------- | ------: | -------------------: | -------------------: | ------------------------------------: |
| T1-identifier |   2.429 |                6.115 |                  143 |                              +2 / +15 |
| T1-title      |     863 |                1.740 |                  132 |                            −61 / −134 |
| T2            |   4.116 |                8.018 |                  145 |                            +58 / +117 |
| T3            |   1.218 |                1.289 |                  137 |                                 0 / 0 |
| T4            |   2.128 |                3.802 |                    — |                               +1 / +2 |
| Total         |  10.754 |               20.964 |                  557 |                                       |

Da v2 para a v3.1, 60 cartões de T1-title passaram a T2 com a nota
`repository_copy`, e um passou a T4 por retenção transitiva; todos envolvem uma
cópia de repositório. Os locais mais frequentes são RePEc, CERN Document Server,
HAL, CONICET, ORA, LA Referencia, UCL Discovery e ePrints. Dois cartões
`T1.arxiv_link` voltaram de T2 para T1. Na v2 eles tinham saído só porque o
grupo incluía, por um vínculo de título, a cópia de repositório; esse vínculo
agora está em T2. A revisão independente estimou 20 cartões (2 no closure); a
detecção por nome do serviço, instituição entre parênteses e host encontra 60
(11 no closure).

T1-identifier tem 2.171 vínculos arXiv e 258 identificadores compartilhados.
Dos 863 cartões de T1-title, 163 não têm resumos comparáveis; a amostra os trata
como estrato próprio (25 cartões). As notas de T2 se sobrepõem: 2.382 pré-print
contra publicado, 107 cópias de repositório, 3.494 divergências de DOI, 1.469
diferenças de ano, 51 variações de autoria e 77 cartões vindos de grupos T1
mistos. Em T4 há 528 identificadores contraditórios, 61 conferência contra
periódico, 146 vínculos incompletos, 330 títulos ambíguos, 225 anos, 61 resumos
divergentes, 275 autorias de um só sobrenome sem apoio do resumo, 300 autorias
parciais e 202 retenções transitivas (10 no cenário T1 e 192 no T1+T2).

Adotar `T1-identifier` deixaria 44.163 obras; `T1`, 43.629; `T1+T2`, 40.811.
Nenhum cartão fica unido por fusões de `T1-identifier` ou de `T1` sem ter sido
escolhido. No cenário T1+T2, 14 cartões T4 ficariam com as duas obras unidas;
para eles só fusão ou adiamento são coerentes.

## Recorte temático

O escopo opcional projeta o resultado completo sobre os cartões que tocam um
conjunto de obras. As regras e as retenções transitivas vêm da execução
completa; escolhas, grupos, escolhas de identificador, lista T4 e amostra são
recalculados para o recorte. O arquivo de escopo contém apenas IDs de obras
propostas. `FOCUSED` tem 2.051 obras que casam com os termos de confiança
limitada, parada e fragmentação. `closure` tem 2.186 obras, os componentes de
identidade completos dessas obras.

| Unidade       | FOCUSED (cartões / pares) | closure (cartões / pares) |
| ------------- | ------------------------: | ------------------------: |
| T1-identifier |               476 / 1.671 |               479 / 1.677 |
| T1-title      |                 115 / 320 |                 116 / 321 |
| T2            |               430 / 1.933 |               436 / 1.944 |
| T3            |                     0 / 0 |                     0 / 0 |
| T4            |                 221 / 713 |                 226 / 727 |
| Total         |             1.242 / 4.637 |             1.257 / 4.669 |

As amostras do closure têm 123, 73 e 123 cartões em T1-identifier, T1-title e
T2 (FOCUSED: 123, 72 e 121). Para decidir o recorte sem deixar pares soltos
dentro de um componente, o `closure` é a unidade mais segura.

## Validação C3

Para a v3.1, a função pura `resolve_identity_choices` do workbench aceitou os
cenários T1-identifier, T1, T1+T3, T1+T2 e T1+T2+T3 das execuções completa,
FOCUSED e closure. Os conflitos dos grupos fundidos coincidiram exatamente com
os propostos e os totais de obras com os manifestos. O formato das escolhas não
mudou desde a v2, quando o `prepare_request` real, somente leitura e sem gravar
os pedidos, aceitou os cenários T1-identifier e T1+T2+T3 (recibo
`c3-dry-run-v2/receipt.json`). As escolhas de identificador propostas na v3.1
são 341 (T1-identifier), 754 (T1) e 2.969 (T1+T2). Um grupo com dois DOIs
registrados fica pendente em todos os cenários, e oito conflitos preexistentes
em obras não fundidas continuam pendentes.

## Sequência até a triagem

O pedido que o C3 aceita hoje é de identidade versão 1, vinculado ao protocolo
v3 pela preparação `fa934b8b…`. A ponte para o protocolo v4
(`review_corpus_screening_bridge_v2.py`) recusa recibos de identidade versão 1.
Ela exige identidade versão 2 com um recibo de metadados versão 2 resolvido,
nenhum par pendente, nenhum conflito pendente e nenhum metadado sem solução.
`prepare_request_v2` não pôde ser exercitado. A busca no estado privado só
encontrou recibos `corpus-metadata-resolution-2` sintéticos, nenhum deste
corpus. O formato das escolhas é o mesmo nas duas versões.

A ordem correta é esta. Primeiro, resolver os nove títulos ausentes pela via de
metadados versão 2, com decisão do Owner. Adiar um título mantém o corpus
incompleto e bloqueia a ponte. Segundo, reexecutar o gerador sobre o resultado,
porque títulos resolvidos podem criar pares novos por título
(`dedupe.overlay.*`). Para isso o gerador ainda precisa ler o overlay de
metadados versão 2; hoje ele lê só os candidatos do result-3. Terceiro, auditar
as amostras e construir o pedido com `prepare_request_v2`, com o protocolo v3
como origem e o v4 como destino. Quarto, aprovar esse digest exato por
`OwnerDecision` e seguir para a ponte C4. Nenhum pedido pronto para decisão foi
produzido. Os pedidos da versão 1 (`c3-dry-run/request-*.json`) são de
identidade versão 1 e não servem ao caminho v4.

## Testes e revisão

Uma revisão independente pediu sete mudanças, todas conferidas nos dados antes
da correção e implementadas com um teste falhando primeiro. A nova revisão
aprovou a v2, sem fusões erradas em 110 cartões conferidos, e pediu que cópias
de repositório sem DOI deixassem T1. Uma primeira implementação tratou essas
cópias como pré-print (versão 3.0.0, `proposals-v3*`). Ela moveu 56 cartões para
T2, mas também levou para T1 doze pares entre uma cópia de repositório e um
depósito em outro servidor, como arXiv, SSRN, OSF ou CoRR. Por isso a 3.1.0
separou a classe de cópia de repositório. Cada caminho de detecção e cada uso da
classe tem teste próprio; removendo cada um, o teste correspondente falha (18
mutações no código final, todas detectadas). A suíte do estudo tem 115 testes; ruff e
mypy passam.

## Arquivos privados

Diretório: `/Users/davi/.local/state/research-workbench/corpus-resolution-20260917`.

| Arquivo                                           | SHA-256                                                            |
| ------------------------------------------------- | ------------------------------------------------------------------ |
| `proposals-v3.1/manifest.json`                    | `5ac043f51ca2aee7b70aac5623bbffa2068b9e4de265f2c64dcdd76f8714de14` |
| `proposals-v3.1/choices/t1-identifier-merge.json` | `098b3b05e2a85a07f26e9acea51fb61335e1bf45c02915bc6346282b9f24d1ea` |
| `proposals-v3.1/choices/t1-title-merge.json`      | `6477eed97d75be809aec8ce3aae3dd6ce811afe590bea5fcb7e384f83cb2a9e0` |
| `proposals-v3.1/choices/t2-merge.json`            | `5c6860c5127dc35a780443817bbf3c9bd12220be5faf78acabc28976410964ae` |
| `proposals-v3.1/choices/t3-distinct.json`         | `f1d232231884b6a7a783055225300504cf212077daee467993f6c3f7bb691aad` |
| `proposals-v3.1/t4-worklist.json`                 | `6e4703a3bf954210c6a5bf5f1891d7376a33fed80ae33967826489d28acf6d86` |
| `proposals-v3.1/audit-sample.json`                | `cf38d2c96e88824419cf5867f59d836b9cd84772b0f08b5447fd5bc36b2501f4` |
| `proposals-v3.1-focused/manifest.json`            | `1c87899fcd4fc800267ba120f4fb43d459cbd74bfd5129b4c8d447efe71070e9` |
| `proposals-v3.1-focused-closure/manifest.json`    | `f35090ead7f57256fe0f2abaf0c85ca8e061cac00e7e9331930a9a6c3eb5f6e4` |
| `focused-scope-draft-2026-09-18.json`             | `2b0fbe123e84566800a064e8318e03f981531f6c67ddf8f678f78cde88ef28a6` |

Cada manifesto lista os hashes de todos os seus arquivos, incluindo as escolhas
de identificador e os conflitos pendentes dos três cenários, e os padrões de
detecção de repositório. Os arquivos não contêm resumos, apenas a indicação de
sua existência e as similaridades calculadas.

## Versões substituídas

Todos os arquivos anteriores permanecem intactos e não devem ser usados para
decisão.

A versão 3.0.0 (revisão `2c6d5bb`) gravou `proposals-v3/` (manifesto
`7141c9c0…`), `proposals-v3-focused/` (`4f3e68aa…`) e
`proposals-v3-focused-closure/` (`30a6f743…`). Ela tratava cópias de repositório
como pré-print, o que é substituído pela classe própria da 3.1.0.

A versão 2.0.0 (revisão `4ab3cab`) gravou `proposals-v2/` (manifesto
`5abc6800…`) e os recortes `proposals-v2-focused*`, além do recibo
`c3-dry-run-v2/` (`f39b423c…`). Seus números eram T1-identifier 2.427, T1-title
924, T2 4.058, T3 1.218 e T4 2.127 cartões.

A versão 1.0.0 (revisão `1b0a3ca`) gravou `proposals/` (manifesto
`05f5479a595dbe92d2c0f7cd3bbb0734c0cc7683c835d1893d955d9cf11fb9ad`) e
`c3-dry-run/`, com T1 3.496, T2 4.079, T3 1.218 e T4 1.961 cartões. O primeiro
registro dizia que 27 cartões T4 ficariam com as obras unidas no cenário T1. Na
verdade, eram 27 cartões T2 dentro de grupos T1, o defeito que levou à regra de
grupos mistos.

## Decisões necessárias do Research Owner

O protocolo mantém `title_only_auto_merge=false` e
`fuzzy_match_requires_adjudication=true`, e nenhuma proposta vale sem um
`OwnerDecision` sobre o digest exato de um pedido de identidade versão 2. Antes
disso, Davi precisa auditar as amostras das unidades que quiser adotar e
rejeitar ou revisar a unidade em que houver erro. Precisa decidir se versões
contam como uma obra: pré-print e publicada, cópias em repositório, anos até
dois de distância, variações de autoria e grupos mistos. Sem isso, T2 vira
julgamento individual. Cabe também decidir se aceita distinções por regra (T3)
e julgar ou adiar os cartões T4. As escolhas de identificador só valem para o
cenário cujas fusões forem aprovadas. Resolver os nove títulos pela via de
metadados versão 2 vem antes de tudo isso.
