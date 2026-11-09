# Proposta de referências assistidas com conferência do responsável

Status: proposta de 14/09/2026, ainda não aplicada. O protocolo v3 e o processo
de calibração vigente permanecem inalterados. O [formulário de revisão
preenchido](http://127.0.0.1:8771/) torna a proposta examinável.

## Decisão proposta

Permitir que a IA redija as referências e que Davi as confira, corrija ou adote
explicitamente. A autoria inicial continuará registrada como IA; a conferência
de Davi será um ato separado. Isso atende ao pedido de preencher o formulário
sem exigir que ele redigite respostas já fundamentadas.

O [processo atual](../../../../../../docs/process/systematic-review-calibration.md)
exige que referências sejam trabalho autoral próprio do Research Owner e que
ferramentas não as completem. O texto substituto proposto para essa regra é:

> Referências podem ser redigidas pelo Research Owner ou propostas por IA.
> Referências assistidas exigem conferência e adoção explícita pelo Research
> Owner, preservando proposta, correções, fontes, autoria inicial e declaração
> de revisão. A adoção não será registrada como autoria humana independente.
> Confirmações anteriores à execução não substituem a auditoria posterior.

Essa é uma mudança metodológica, não apenas uma alteração de interface. A
aprovação da proposta autoriza sua implementação; não confirma automaticamente
as respostas nem declara leitura ou histórico de ajuste em nome de Davi.

## Material e interpretação

As 50 referências de título/resumo partem do [primeiro rascunho](README.md):
16 propostas de inclusão, 21 de exclusão e 13 incertas, fundamentadas nos
campos originais. O resultado de 19/29/2 da [consulta posterior](followup.md)
usa material adicional. Seus 17 casos aparecem em painéis separados e não
preenchem automaticamente as referências das tarefas originais. Essa
separação de entrada não apaga a exposição prévia às conclusões posteriores.

Os seis campos de extração pertencem a um artigo, V3-29, e usam o PDF fixo
arXiv 2508.17711v3 e os trechos já validados. A consulta externa ao GitHub não
vira evidência do que o PDF declarou. Correções de decisão, texto ou fonte
precisarão de nova conferência dos critérios e localizadores antes da
importação; um checkbox não valida a correção científica.

Os limiares atuais de 50 obras por etapa, recall mínimo de 0,95 e zero falsas
exclusões seriam preservados, mas relatados como comparação com a referência
assistida e adotada. O resultado mede concordância operacional com essa
referência; não estima acurácia independente nem cobertura da área. A autoria
IA pode introduzir erros correlacionados e ancorar a revisão humana. Mesmo uma
concordância perfeita não elimina esses riscos.

O [PRISMA 2020, itens 8 e 9](https://www.prisma-statement.org/s/PRISMA_2020_expanded_checklist-yc78.pdf)
pede relatar revisores, independência, automação e validação; não certifica
este desenho nem impõe o limite de 50 casos. A distinção entre seleção por
título/resumo e exame posterior do texto completo segue a orientação de
triagem inclusiva do [Cochrane Handbook, seção 4.6.3](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04).
Ambas as fontes foram consultadas em 14/09/2026. Sua utilização aqui é
metodológica; não importa critérios clínicos para o estudo matemático.

## Histórico e execução posterior

A criação das propostas, sua exposição e a consulta adicional já são fatos
registrados. Eles não demonstram, por si, que os prompts ou a configuração dos
executores foram ajustados com esses casos; tampouco demonstram ausência de
ajuste. O formulário começa com histórico desconhecido. Uma declaração real
será necessária para escolher a partição de verificação.

Se houve ajuste, obras e páginas usadas nesse ajuste precisam ficar separadas
da verificação conforme o contrato. Se o histórico não puder ser reconstruído,
este conjunto continuará como material de desenvolvimento e será necessária
outra seleção para a verificação. Não se inventará `no_prior_tuning` nem uma
partição historicamente independente.

Após eventual aprovação da mudança, a implementação deverá vincular o
registro assistido à suíte, validar suas fontes e partições e compatibilizar
os contratos e o protocolo. O envelope novo não será entregue ao importador
de respostas humanas como se tivesse a mesma autoria. Nenhuma execução pode
usar o envelope diretamente como suíte nativa.

O resultado automático continuará exigindo auditoria posterior: 20% das obras
de triagem executadas e todos os casos de extração. Para a preparação atual,
isso corresponde a dez obras e ao único caso de extração, se a composição
executada permanecer essa. Não haverá aprovação implícita de texto completo,
identidades, exclusões definitivas ou síntese.

## Vínculos e reavaliação

Esta proposta afeta a regra de autoria em
`docs/process/systematic-review-calibration.md`, a interpretação de referências
reais em `/supplementary_search_policy/stopping_rule` do protocolo v3 e a
proveniência da futura importação. A implementação deverá registrar o sucessor
compatível e sua aprovação antes de executar; o arquivo v3 não foi editado.

| Artefato afetado | SHA-256 |
| --- | --- |
| Protocolo v3, JSON canônico | `fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f` |
| Protocolo v3, bytes do arquivo | `107a43ef3eea63e4bb6294f80f3060ab84f2b9c81faec61dca37ccb454526943` |
| Scaffold de 101 tarefas | `8c00d9c368a0049c1dd2bdb2e28301b5e61deb323778ca7d6adc258484731902` |
| Primeiro rascunho IA | `ed1a884f33ba2255508c4c03802a7de97490db2e5f8773621e3c5126159f04ff` |
| Consulta adicional IA | `7110fbb314a58479cb93f189b9a0fe5cb23204b536c4d55d653e9fc9cfd2d826` |
| Pacote de conferência, 50 obras e seis campos | `b90d7945e7ed80967a9a10697bc364f54aa333c95c2668566791257e07bc19c8` |

Não há calibração ou triagem canônica concluída a refazer nesta parcela. A
configuração correspondente ao método que vier a ser aprovado deverá passar
por nova execução e auditoria, sem herdar um resultado de aprovação. A
aquisição e as filas anteriores permanecem como evidência histórica; seus
vínculos não serão reetiquetados silenciosamente para outro protocolo.
