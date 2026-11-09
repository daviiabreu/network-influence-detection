# Verificação da preparação

Data local: 13/09/2026, America/Sao_Paulo. Os recibos detalhados e logs ficam em
`~/.local/state/research-workbench/corpus-preparation-20260913/integration-checks/`.
São evidências de preparação e engenharia; não são resultados de calibração
ou de triagem científica.

## Correção do limite da CLI

A revisão `2bfa4ea33b637fa1a3fc61cdffac8ad3ffba4ded` passou em
`UV=/Users/davi/.local/bin/uv just quality`, num checkout separado, limpo antes
e depois da execução. O comando começou em 14/09/2026 às 00:52:16 UTC e
terminou às 01:04:39 UTC com código zero. Esses horários correspondem à noite
de 13/09 no fuso local.

| Verificação | Resultado |
| --- | --- |
| Estrutura | 7 verificações passaram |
| Ruff e mypy | Ambos os projetos passaram |
| Workbench | 3.502 testes passaram em 733,65 s |
| Estudo IC | 34 testes passaram em 0,55 s |
| Distribuição | As duas wheels foram construídas, instaladas e passaram no smoke test |

O aviso do pytest veio do teste que constrói deliberadamente um ZIP com
nome duplicado para verificar sua rejeição. O teste passou. O build do estudo
também informou que o pacote não declara dependências de runtime; a instalação
e o smoke test passaram. O log integral é
`quality-2bfa4ea.log`; `quality-2bfa4ea.json` registra comando, revisão, horários,
checkout e estado do Git.

No material real, a seleção de 12.416.114 bytes gerou 101 tarefas pela CLI.
IDs de caso e papéis coincidem com a preparação final. Essa reprodução ficou
separada e não substitui o pool de 28 locators do extractor preparado.
A suíte de 14.256.404 bytes foi lida e recusada por sentinelas de autoria,
com código 2. O recibo `native-calibration-limit-recheck.json` tem SHA-256
`4063ca336d6872f1a7c3176458f038578c28dc65eedd196c655807fbd9c88af3`.
Não houve inferência de modelo ou preenchimento de referência científica.

## Artefatos e fontes

A coordenação recontou a fila a partir dos JSON originais, com uma reconstrução
independente do grafo, e conferiu a cobertura de todos os candidatos pelos
cartões. Os três títulos Springer foram reconferidos nas páginas editoriais.
Os hashes das 60 projeções de fontes de metadados e os vínculos dos nove títulos
e dez conflitos foram verificados. Uma afirmação sobre autoria institucional
foi corrigida após a revisão independente, sem alterar a fonte original.

O HTTP do formulário v3 retorna o HTML congelado, com SHA-256
`3861d7e5d7698e394583f3b5454ac974eb39ac9cc91705a1431657faec849a2f`.
Só HTML e PDF são servidos; JSON privados e tentativas de acesso a diretórios
irmãos retornaram 404. Essa conferência não acessou respostas ou armazenamento
do navegador. A revisão independente reproduziu a seleção, as 71 páginas,
as 78 manifestações e os 28 locators; testou o JavaScript da exportação em VM
com dados sintéticos, sem gerar referências reais.

A coordenação também confirmou a projeção descrita no diagnóstico de identidade:
54.561 registros reproduzem exatamente as 46.391 obras tituladas e todos os
20.964 candidatos, com os mesmos 1.536 hashes de fonte. Os nove registros
restantes são disjuntos da subfila e continuam no pai. O recibo dessa conferência
é `identity-projection-recheck.json`; ele não persiste uma nova fila canônica.

As revisões independentes são registradas em
[metadados e método](review-metadata-methods.md),
[identidade e calibração](review-identity-calibration.md),
[texto completo](review-fulltext.md) e
[limite da CLI](review-calibration-input-limit.md).

## Integração da transição de identidade

A revisão `1b4b1ae7716b656762dcce3023940b29707ef83e` acrescenta a transição
vinculada de identidade e inclui a correção anterior da CLI. Outra execução de
`UV=/Users/davi/.local/bin/uv just quality`, em checkout separado e limpo antes
e depois, passou integralmente: **3.527 testes do workbench e 34 do estudo**,
estrutura, Ruff, mypy, construção, instalação e smoke tests das duas wheels.
O comando começou em 14/09 às 01:23:05 UTC e terminou às 01:36:26 UTC,
com código zero. Os testes do workbench levaram 790,97 s.

O recibo `quality-1b4b1ae.json` registra o SHA completo e as saídas vazias de
`git status --porcelain`; o log é `quality-1b4b1ae.log`. Essa segunda execução
foi necessária pela nova implementação de persistência e replay, posterior à
primeira integração.

A [revisão independente](review-identity-transition.md) executou os 25 testes
novos e dois probes adicionais. Os 27 passaram, incluindo rejeição de um
runtime de outro corpus e preservação das nove ausências de título e dez
conflitos depois de a subfila sintética terminar. Nenhuma decisão sobre o corpus
real foi produzida por esses testes.

A [aplicação real](identity-transition.md) terminou com código zero e replay
nativo exato, sem escrita durante a reprodução. Foram criados seis objetos CAS;
os 11.821 arquivos anteriores permaneceram intactos. A coordenação recontou e
recalculou os hashes de todos eles separadamente, incluindo as 1.536 fontes,
e confirmou seus metadados antes e depois da leitura. O recibo dessa conferência
é `identity-source-preservation-recheck.json`, hash
`9f291392680850f070400b93e5086230e9d865f10ffa7d2bd995dc2876b7841b`.

O recibo real da transição é
`f01e6185740e71849e8f72211891e38cd1f97f5d3c6b050ea3b5c95186ab088b`.
A fila inicial aguarda ação do responsável e o agregado permanece incompleto;
nenhuma decisão humana, inferência de modelo ou resolução de metadados foi
produzida. A revisão independente dos bytes reais consta como adendo em
[revisão da transição](review-identity-transition.md).

## Verificação da publicação

Depois das alterações de documentação, os nove testes de contrato de
`test_repository_systematic_review_agent_specs.py` passaram em 0,25 s.
O check de estrutura inicialmente identificou três destinos com sufixo de
linha em links privados. Os sete links locais desse relatório foram convertidos
em caminhos literais, conservando coordenadas e conteúdo, para que os links
publicados também funcionem sem o estado privado deste computador. A versão
anterior e o recibo da alteração ficam em `publication-source-docs/`, fora do Git.
Após a correção, `just structure` passou nas sete verificações e
`git diff --check` passou. Não houve mudança de código após a matriz completa
da revisão `1b4b1ae`.
