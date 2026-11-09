# Subfila de identidade aplicada ao corpus v3

A transição foi implementada, revisada e aplicada aos dados reais. A fila
nativa conserva os 20.964 pares de identidade do pai e pode receber decisões
registradas. O corpus agregado continua `incomplete`: nenhuma identidade foi
decidida, nenhum metadado foi promovido e não houve liberação para triagem.

## Execução e linhagem

A execução usou o checkout limpo da revisão
`1b4b1ae7716b656762dcce3023940b29707ef83e`, após a
[matriz completa de qualidade](validation.md). Começou com contexto registrado
em 14/09/2026 às 01:50:53 UTC e terminou às 01:54:06 UTC, ainda em 13/09 no
fuso America/Sao_Paulo. O processo terminou com código zero. Seu identificador é
`opinion-dynamics-map-v3-broad-corpus-20260913-identity-transition-1`.

O protocolo permanece
`fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f`,
com a vinculação original da aprovação à revisão
`3b71a915252c7986f3dbf5310117eace4c8fa98f`. Essa vinculação não é a revisão do
código executado, registrada separadamente acima. O pai continua sendo o
recibo de metadados
`6b16e1cb9954ee505a592121d697fb58c56b444e3c430c8360301625ceb4dd82`.

| Resultado conferido | Quantidade |
| --- | ---: |
| Observações preservadas no agregado | 54.570 |
| Observações na subfila | 54.561 |
| Observações sem título conservadas fora da subfila | 9 |
| Obras tituladas, iguais às propostas do pai | 46.391 |
| Candidatos de identidade, iguais aos do pai | 20.964 |
| Pendências de metadados conservadas | 9 |
| Conflitos de prontidão conservados | 10 |
| Fontes originais vinculadas | 1.536 |

A partição dos registros é completa e disjunta. Apenas as nove observações
das propostas integralmente sem título ficam fora da entrada da subfila; elas
continuam no pai e no novo recibo. A observação sem título que possui uma
manifestação titulada no mesmo grupo permanece na subfila. Obras tituladas e
candidatos coincidem integralmente com os do pai, incluindo IDs e membros.

## Artefatos e preservação

| Artefato | Bytes | SHA-256 |
| --- | ---: | --- |
| Recibo da transição | 397.781 | `f01e6185740e71849e8f72211891e38cd1f97f5d3c6b050ea3b5c95186ab088b` |
| Fila nativa | 770.086 | `fcc36f8ea40020b7d9b7ce75d1916cf0a08216c76ac168b3c5b3522695be3054` |
| Registros da subfila | 116.448.380 | `d9e9289e18df4d2db4d9554ca707bc7385025950c20a437daae7d7d58c200c9e` |
| Deduplicação schema 2 | 29.383.919 | `52db5c30e794937c45478c8677c47ee85aebbded1789add8d963128c000adb39` |

Foram acrescentados seis objetos ao armazenamento por hash: os quatro acima e
o pedido e a resposta da operação. Nenhum arquivo anterior foi modificado.
Os novos objetos são somente de leitura. O replay nativo reproduziu o resultado
exato sem alterar o inventário de arquivos. A execução ficou sem acesso à rede
e não chamou modelos.

A coordenação fez uma conferência adicional sem importar o driver ou o runtime:
recalculou os hashes e comparou os metadados de todos os 11.821 arquivos
preexistentes, somando 1.123.492.062 bytes e incluindo as 1.536 fontes originais.
Todos coincidiram com o inventário anterior. O recibo dessa conferência tem hash
`9f291392680850f070400b93e5086230e9d865f10ffa7d2bd995dc2876b7841b`.
A [revisão independente](review-identity-transition.md) distingue testes de
código, execução nativa e inspeção direta dos artefatos reais.

Os recibos privados ficam em
`~/.local/state/research-workbench/corpus-preparation-20260913/identity-transition-v1/`.
`summary.json` tem hash
`b142684a62da2b281e40fed9dbde651d28d9fa751c4b01333269fbf20097d6a0`;
`new-cas-artifacts.json`,
`b382c98c431e869d9ab9c6b0f09614e189375dd1e8b2a034f7b545575ca471ab`.
O driver congelado tem hash
`1dd2e0840dca5c17e871fd6957e2d1a7338ce24f90818f5fdc5c176c591623ac`.
A revisão da coordenação antes de executar foi registrada separadamente em
`identity-transition-v1-coordinator-review.json`, hash
`6d815dac3938f929f7fbe72f54d4c397c4069a51c95145d3db0c4dcf00e066d8`.
Ela autoriza a operação técnica dentro da continuidade pedida por Davi;
não contém decisão científica ou referência humana.

## Estado que permanece aberto

O estado inicial da subfila é `awaiting_owner_action`. O recibo agregado
permanece `incomplete`, com `screening_ready=false` e
`scientific_eligibility_assessed=false`. Terminar a subfila futuramente não
resolverá por si só os nove casos de metadados e os dez conflitos. A operação
de correção canônica de metadados ainda precisa de uma transição própria,
vinculada às fontes e às disposições registradas.

O [diagnóstico anterior](identity-transition-plan.md) permanece como proposta
histórica, anterior à implementação. O módulo final separado,
`review_corpus_identity.py`, reutiliza a adjudicação nativa sem ampliar o
contrato de obra titulada nem mudar a política científica de identidade.

Referências humanas de calibração, histórico de ajuste, execução e auditoria
continuam pendentes. Esta aplicação prepara a revisão dos pares; não executa
triagem, exclusões, extração ou síntese da revisão sistemática.
