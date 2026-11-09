# Correção de resumo OpenAlex com índice esparso

Data: 2026-09-09 (America/Sao_Paulo).

Estado: correção preparada e verificada em worktree isolado do commit
`25a84f597dc52eacdb9aa96b3c5b95a8ce2b3603` e integrada ao checkout principal. O resumo
opcional passa a ser indisponível quando o índice contém posições válidas, mas
faltantes. Não há compactação de palavras, preenchimento de lacunas ou alteração
de schema. Estruturas inválidas, posições duplicadas, negativas ou de tipo
incorreto continuam sendo rejeitadas.

## Falha observada e limite de proveniência

A [aquisição primária v2](2026-09-09-primary-acquisition-v2.md) foi interrompida
com `bibliographic provider response is invalid`. A operação
`search.bbce4748bd9d17924db5a0ec7c8187bfc6571d2fa818ba86e28b996c8e875733.try.1`
tem somente `request_dispatched`, sem `response_recorded`. Sua requisição é
`search.openalex.q01`, `page_index = 2`, `page_size = 100`; o hash da requisição
é `bbce4748bd9d17924db5a0ec7c8187bfc6571d2fa818ba86e28b996c8e875733` e o evento
tem hash `65ed40bddf67a5cfd72ad8e33b19549c1e6c9f7cb616cf11c97054194e43faed`.

Um artefato CAS de 578.078 bytes, escrito logo após o dispatch, contém uma página
OpenAlex com 100 resultados. Seu SHA-256 é
`06938ca347d74f83093af996e1c70c4cf06720253fc3d28fb08fa046f8e15940`.
A proximidade temporal e a reprodução da mesma falha sustentam o diagnóstico
operacional, mas não estabelecem o vínculo canônico entre esses bytes e a
requisição: falta o recibo de resposta. A correção não cria esse vínculo, não
atribui horário de aquisição aos bytes e não reconcilia a operação pendente.

Nesse artefato, apenas o registro OpenAlex `W2118356608`, posição 22 da página,
falha na normalização. O campo `/results/21/abstract_inverted_index` contém 62
posições distintas entre 0 e 65, todas inteiras e não negativas, mas faltam
14, 26, 43 e 57. Não há posições duplicadas. Seu hash canônico é
`e3b73c802a0e65054187afdb0e55c9872006a645fe2d78a6110ec5e9a1090e4b`;
o registro tem hash canônico
`910275ee501e025d7c780239edd807f8fb0cd6fec58962013654a1c0f1b3d772`.
Nenhum texto do resumo foi copiado para este relatório ou para os testes Git.

## Alteração e verificação

Em `_openalex_abstract`, no
[normalizador bibliográfico](../../../../../workbench/src/research_workbench/workflows/systematic_review/bibliographic_search.py),
a única alteração de comportamento troca o `TypeError` do gate de contiguidade
por `None`. A validação de estrutura, tipos, negatividade e unicidade ocorre
antes desse gate e permanece intacta. Índices densos continuam produzindo a
mesma sequência textual; índices esparsos não autorizam reconstrução parcial.
Os bytes originais continuam preservados no CAS, e os demais campos do registro
e a paginação não dependem da disponibilidade desse resumo.

Os testes versionados usam somente metadados sintéticos. As duas regressões de
lacuna inicial ou interna falharam contra o comportamento anterior e passaram
após a correção. Elas comparam todos os demais campos com uma página de
referência cujo resumo é nulo, preservam o segundo resumo denso, os ranks e o
cursor e verificam a retenção dos bytes originais. Casos de estruturas inválidas,
tipos incorretos, duplicatas e posições negativas continuam falhando.

A verificação privada com os bytes reais produziu 100 registros. Os outros 99
preservaram exatamente seus bytes canônicos; o resultado completo corresponde
ao normalizador anterior recebendo somente o resumo afetado como indisponível.
O cursor permaneceu igual. As duas páginas OpenAlex já registradas, com 200
registros, reproduziram exatamente os resultados históricos sob ambas as
versões. Para o CAS sem recibo, a comparação pura utilizou um horário fixo de
diagnóstico, sem declará-lo como horário observado de aquisição.

Validação no worktree isolado: 177 testes passaram em
`test_systematic_review_bibliographic_search.py`; Ruff e `ruff format --check`
passaram nos dois arquivos Python alterados; mypy não encontrou problemas no
módulo alterado. O gate integrado do checkout principal é responsabilidade da
integração e não foi repetido por este diagnóstico.

Na integração, 134 testes adicionais de host, aquisição, corpus, armazenamento
e configuração passaram. Ruff e mypy aprovaram módulo e testes alterados; uma
anotação explícita do dicionário sintético resolveu o erro de tipo do teste.
As 75 páginas registradas do prefixo primário também reproduziram exatamente,
com o mesmo hash do relatório de verificação. O gate completo anterior passou
em `25a84f597dc52eacdb9aa96b3c5b95a8ce2b3603`: 3.023 testes do workbench,
seis do estudo, estrutura, lint, tipos e os dois wheel smokes. Esta correção
local posterior foi verificada pelos checks afetados, conforme a política
de validação proporcional; o resultado completo não é atribuído a outra revisão.

O relatório privado, contendo hashes, paths e a comprovação da ausência do
binding de resposta, está em
`/Users/davi/.local/state/research-workbench/publish-20260909/openalex-abstract-diagnostic/report.json`,
SHA-256 `d8d49c3d6a818937b6bb89dd6aa6fe40c442fdf286338b6cb05894058df5809d`.
Nenhuma requisição de rede, acesso a credencial ou gravação no journal de
aquisição foi executada para implementar e verificar a correção.

Resumo indisponível não significa exclusão científica. Esta alteração não
conclui a aquisição, não autoriza screening, não aceita um corpus e não resolve
o [diagnóstico de categorias na deduplicação v1](2026-09-09-deduplication-v1-category-diagnostic.md).
