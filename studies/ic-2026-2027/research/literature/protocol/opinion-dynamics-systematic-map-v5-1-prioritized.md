# Esclarecimento de escopo v5.1 — mapa amplo priorizado

Em 25/09/2026, o item 25 do log privado de decisões vinculou uma única
recalibração após a falha dos dois modelos de A na primeira coorte. Este é um
[sucessor ligado ao protocolo v5](opinion-dynamics-systematic-map-v5-prioritized.md),
cujo texto dos critérios permanece intacto. O [JSON v5.1](opinion-dynamics-systematic-map-v5-1-prioritized.json)
mantém literalmente os `statement` dos critérios v5 e acrescenta o esclarecimento
aos `edge_cases` dos critérios de inclusão e domínio humano. Seu digest canônico
`ReviewProtocol` é `0e7de8e2b517cc76d521eed2971a5bc8538c41e19ba6c0a922ec5f8b40a95115`.

Modelos canônicos de dinâmica de opiniões — voter, Sznajd, majority rule,
q-voter, Deffuant, Hegselmann–Krause/Krause, DeGroot, Friedkin–Johnsen,
Axelrod e variantes de consenso ou confiança limitada — pertencem ao domínio
de opinião humana, salvo quando o registro aplica explicitamente o modelo a um
sistema não humano, como robôs, animais, sensores ou controle de engenharia.
Sem resumo em todas as observações, a regra anterior de `uncertain` continua
valendo na etapa de título/resumo.

Decisão metodológica: Codex (GPT-6), agente delegado; autoridade: delegação de
Davi em 25/09/2026, itens 20–21, e recalibração pré-declarada no item 25.
Estado: adopted under delegation, pending ratification. O envelope nativo
`OwnerDecision` está em
`/Users/davi/.local/state/research-workbench/owner-decisions-20260925/broad-map-v5-1/decision.json`,
SHA-256 `05bd016ff71b7ea82349578c4fa714d6ce39c20a697d84c0f49c74ced5fc4bf2`.
Os juízos do papel Owner foram feitos por agentes sob delegação, sem verificação
humana. A nova coorte ainda não tem referências adotadas nem gate aprovado.

## Emenda operacional de 27/09/2026 — cadência do ranqueador

O item 29 do log privado registra a decisão do papel Owner, exercido pelo
agente sob delegação, de permitir `prepare-batch k --provisional` quando as
saídas A e B do lote k−1 cobrem todas as tarefas, mesmo antes da adoção desse
lote. O ranqueador usa as decisões já adotadas e, do lote pendente, somente os
acordos A/B de inclusão ou exclusão. Incertezas e discordâncias não fornecem
rótulos. Pode haver no máximo um lote anterior sem adoção; os demais precisam
estar adotados e com extração e acordo completos. A seleção do lote k é fixada
com os hashes das saídas e tarefas usadas e não é recalculada quando k−1 for
adotado.

A mudança reduz a espera entre lotes durante a adjudicação. Quando a triagem
para por saturação, o ranqueador também determina quais obras serão triadas;
seu efeito sobre cobertura deve ser avaliado pela amostra do restante. O lote
provisório em curso é concluído antes de congelar o restante. Os critérios e decisões de
elegibilidade, a adjudicação, a auditoria independente, a saturação por índice
de lote e a verificação de recuperação na amostra do restante seguem as regras
vigentes. Sem `--provisional`, a preparação continua usando somente decisões
adotadas. Esta emenda altera a cadência operacional de treinamento, sem mudar
o JSON v5.1 nem seu digest canônico. Ela excepciona o texto de
`opinion-dynamics-systematic-map-v5-prioritized.md:44–46` (centroides só após
decisões finalizadas e adotadas) e `:108–109` (extração antes de avançar),
somente para preparar o próximo lote. Artefatos afetados: `selection.json`,
`ranker-state.json`, tarefas `batch-NNNN-screener-tasks-{a,b}.jsonl` do lote
seguinte, saídas `screener-{a,b}.jsonl` do predecessor usadas provisoriamente,
`remainder/selection.json` e registros de saturação. Nenhuma obra precisa ser
retriada por essa mudança; as seleções já congeladas não são recalculadas.

## Emenda de escopo de 27/09/2026 — quadro de produção e coortes

O item 31b do log privado corrige a interpretação de
`opinion-dynamics-systematic-map-v5-prioritized.md:60–64`: as exposições
inventariadas, inclusive os 4.041 membros de pares ambíguos, foram reservadas
somente da coorte de calibração. Não eram exclusões do quadro de produção.
As 12.381 obras do inventário voltam ao conjunto elegível do ranqueador e ao
restante a partir do próximo lote preparado; `batch-0001/selection.json` fica
congelado. As 400 obras das duas coortes entram como fase triada
`calibration-cohorts`, com julgamento e hash da referência adotada de cada
rodada. A identidade dos pares ambíguos continua tardia e sujeita à política
de versões; nenhuma fusão é presumida.

Justificativa: excluir 12.781 propostas sem triagem nem amostragem distorcia a
cobertura e impedia reconciliar as 43.906 propostas deduplicadas. Artefatos
afetados: seleções e estados do ranqueador dos próximos lotes, importação
`calibration-cohorts/adopted.jsonl` e `provenance.json`, quadro do restante,
relatórios de fluxo e evidências de saturação. Não há retriagem das coortes nem
do lote 1; a correção preserva seus bytes e inclui todas as obras no fluxo.
Decisão: agente delegado (Codex, GPT-6), sob delegação de Davi de 25/09/2026
(itens 20–21); adotada sob delegação, pendente de ratificação e sem verificação
humana das referências. O `OwnerDecision` nativo e seus hashes de entrada
estão no estado privado em `production-v5-1/scope-amendment/decision.json`,
SHA-256 `f42146d6324adda097bc7c66ee576615e9819a9f82a90ce1aa775b0add75774a`.
