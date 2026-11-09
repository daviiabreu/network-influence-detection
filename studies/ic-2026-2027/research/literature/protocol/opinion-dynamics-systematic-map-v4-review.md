# Mapeamento v4: referências assistidas com adoção explícita

O [protocolo v4](opinion-dynamics-systematic-map-v4.json) implementa a
[emenda autorizada em 14/09/2026](../../decisions/2026-09-14-assisted-calibration-references.md).
A mudança permite que a referência seja proposta por IA, conferida, corrigida
quando necessário e adotada explicitamente por Davi. Sua autoria inicial
permanece identificada. A aprovação da emenda autoriza a implementação desse
método; não adota as respostas preparadas nem declara leitura humana, histórico
de ajuste ou auditoria de saídas.

O v4 conserva os campos científicos e de aquisição do
[v3](opinion-dynamics-systematic-map-v3.json), inclusive as 1.027 consultas,
o intervalo de publicação, as definições, os critérios de elegibilidade, a
deduplicação, os limiares de triagem, os campos de extração e a síntese. As
únicas diferenças são `protocol_id`, `protocol_version`, `created_on`,
`supersedes` e o novo `calibration_reference_policy`. A versão é `4.0.0`, a data
é `2026-09-14` e o predecessor é `opinion-dynamics-systematic-map-v3`.

| Vínculo | SHA-256 |
| --- | --- |
| Proposta aprovada, no commit `1f41791d1e3f441ac2d271895be7a7cf3b899602` | `dbcd3e271727aa6bf03d3836efb767c9b90a46259d1490497a1b4783791610c1` |
| Protocolo v3, JSON canônico | `fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f` |
| Protocolo v3, bytes do arquivo | `107a43ef3eea63e4bb6294f80f3060ab84f2b9c81faec61dca37ccb454526943` |
| Protocolo v4, JSON canônico | `ff8a14178e725983945c049e75181e8eeb1f3cee56a831e714cc78b09245d413` |
| Protocolo v4, bytes do arquivo | `390d2bc01520c3422ee37deb76e0302b8d0ce2dc229000c72ca729d56187ed74` |

O JSON canônico usa a serialização de `review_protocol_sha256`; o hash do
arquivo inclui a quebra de linha final. A aprovação histórica do v3 permanece
intacta. O TOML de aprovação do v4 deve vincular seu hash canônico e um commit
que contenha seus bytes; a decisão da emenda é o fundamento da autorização,
sem alegar que Davi inspecionou pessoalmente um JSON produzido depois dela.

## Contrato de referências e fontes

A nova política contém `reference_origin=ai_assisted_owner_adopted`,
`approved_proposal_sha256`, `source_protocol_sha256`,
`metric_scope=agreement_with_owner_adopted_ai_reference` e
`title_abstract_reference_source_policy=original_task_only`. O protocolo com
essa política exige `calibration-3`, `reference_provenance` e o
`source_protocol` completo. Uma nota documental isolada não permitiria ao
validador distinguir uma suíte assistida de uma suíte legada cuja proveniência
tivesse sido removida. Por isso a política faz parte do hash do protocolo
aprovado e não é apenas um campo opcional de um formulário externo.

A suíte de calibração herda explicitamente as fontes do v3. O validador deve
reproduzir o hash do protocolo de origem e verificar equivalência integral,
excetuando apenas os cinco campos da emenda. As identidades e versões do
sucessor devem ser novas, `supersedes` deve nomear o protocolo de origem e a
data não pode retroceder. A política de texto completo e todas as estratégias
de busca permanecem iguais. Essa comparação não é uma dispensa genérica de
incompatibilidades entre protocolos.

As requisições bibliográficas, páginas e registros de aquisição de texto
completo continuam com seus hashes e vínculos v3. As novas tarefas e seus
contextos de execução passam a vincular o v4. A validação continua a reconstruir
observações e trechos dos bytes originais, sem editar fontes ou reexecutar
consultas para trocar o protocolo declarado. Suítes legadas, scaffolds e
formulários humanos existentes conservam sua interpretação original.

Para título/resumo, uma referência só pode usar os campos fornecidos à tarefa
original. As consultas editoriais posteriores permanecem em material
suplementar identificado; não preenchem automaticamente o gabarito da entrada
anterior. Para extração, os localizadores devem reproduzir o texto completo
fixo do caso. A disponibilidade de um repositório externo não comprova que o
PDF declarou um campo nem autoriza substituir sua fonte.

## Medição, histórico e continuidade

Os limiares continuam em 50 obras por etapa avaliada, recall mínimo de 0,95 e
zero falsas exclusões. No v4, esses números descrevem concordância com a
referência IA adotada pelo responsável. Não estimam acurácia independente,
recall da busca, cobertura da área ou ausência de erros correlacionados. As
referências e sua proveniência ficam fora das entradas dos executores.

A exposição às propostas e às consultas adicionais será preservada. Ela não
prova presença nem ausência de ajuste dos prompts ou configurações. É
necessária uma declaração real de histórico antes de escolher verificação;
se houve ajuste, suas obras e páginas precisam ficar separadas da verificação.
Se o histórico não puder ser reconstruído, o conjunto permanece material de
desenvolvimento e será necessária outra seleção. Não se inventa
`no_prior_tuning` para tornar a suíte válida.

A adoção das referências ocorre antes da execução e não substitui a auditoria
posterior de 20% das obras de triagem executadas e de todos os casos de
extração. O resultado automático ainda chega a `awaiting_owner_review`; o
aceite exige a decisão vinculada à suíte e às saídas reais. Não há uma
calibração científica concluída cujo resultado possa ser herdado pelo v4.

Esta parcela implementa a emenda e os contratos de calibração. A transição
nativa do corpus v3 para uma execução de produção v4 ainda não está
implementada. Os compositores atuais exigem igualdade de protocolo entre
aquisição, corpus e triagem; não podem consumir recibos v3 como se fossem v4.
O corpus v3 continua incompleto, com filas de identidade e metadados
preservadas. Uma futura ponte deve criar sucessores vinculados aos pais e
validar a herança dos dados. A emenda não exige repetir as 1.027 consultas,
resolver identidades por inferência ou excluir registros para avançar.

A [aprovação v4](approvals/opinion-dynamics-systematic-map-v4-20260914.toml)
foi registrada e validada pelo carregador nativo contra o commit
`2bfeb201cd02d177f5ad368672af7c2325c173ce`, que contém os bytes do protocolo.
Nos comandos de aprovação, `expected_repository_revision` deve usar esse
commit explícito. O registro conserva a autorização das buscas inalteradas;
nenhuma aquisição ou calibração foi executada por essa validação.
