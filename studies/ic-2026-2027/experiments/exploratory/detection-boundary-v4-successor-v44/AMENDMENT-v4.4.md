# Emenda v4.4: lacuna por propagação mal condicionada

Sucessor operacional vinculado à emenda v4.3 e ao freeze `freeze-v4.json` (commit `37513841`). Estado: aprovada pelo Owner quando o registro `freeze-v44.json` tiver `status: frozen`; até lá, proposta.

## Motivo

Em 01/10/2026, às 04:18 UTC, o worker do shard 5 encerrou durante o tier 2. Os outros sete shards concluíram suas unidades do tier 2 e ficaram presos na barreira do tier 3, à espera das duas unidades restantes do shard 5. O relançamento com o código congelado, às 04:21 UTC, falhou da mesma forma em cerca de 40 segundos.

O diagnóstico foi feito numa cópia da unidade, com autorização do Owner. Ele reproduziu a falha na célula a=0,003 da unidade `t2-u03-r2`: `ValueError("ill-conditioned local profile")`, lançado por `project_shift` (`src/ic_study/analysis/detection_boundary_v4.py`) durante a propagação do nuisance, quando a jacobiana local do perfil é degenerada. O runner congelado não trata essa exceção, então o shard termina, e repetir a execução reproduz a falha. Pela regra do protocolo, uma falha pede um sucessor documentado, e não uma reexecução até passar.

## Exposição antes desta emenda

Nenhum resultado de curva do tier 2 ou de tiers posteriores foi lido. O coordenador conhece apenas:

- contagens de arquivos, existência de `curve.json` e horários de modificação dos diretórios das unidades do shard 5;
- a mensagem de erro e a pilha de chamadas da célula afetada, obtidas na cópia.

O tier 1, que contém a curva principal, já estava completo e não é afetado.

## Regra

1. Uma célula cuja execução pelo `execute_cell` congelado termina exatamente com `ValueError("ill-conditioned local profile")`, lançado por `project_shift` em `detection_boundary_v4.py`, é registrada como lacuna do tipo `propagation`. O registro `result` traz `success: false`, `attempts: []`, `dependency_gap: false` e `successor_gap` com `amendment`, `kind`, `error`, `function` e `successor_sha256`, e a célula é selada.
2. Não há retentativa. Ajuste, sementes, painéis e as demais células não mudam, e nenhuma outra regra do protocolo é alterada.
3. Qualquer outra exceção, inclusive a mesma mensagem lançada por outra função, continua encerrando o shard como no runner congelado.
4. A lacuna segue as regras existentes. Em força positiva, censura fronteiras e não invalida a unidade. Em a=0, a unidade perde o gate nulo, como qualquer outra lacuna nessa força.
5. A regra vale para toda célula ainda não concluída, em todos os shards, a partir do relançamento. Células concluídas não são reexecutadas.

## Implementação

`v44_run_curve.py` fica fora do fechamento congelado. Ele carrega o `run_curve.py` congelado ao lado do `--freeze` informado e executa, sem mudança, o preflight e o laço desse runner, com uma única substituição: o agendador congelado (`schedule`, que aceita o worker como parâmetro) recebe um worker que difere de `execute_cell` só no caso da regra 1. Por estar fora do checkout congelado, o arquivo não altera os hashes de código que o preflight e a retomada dos shards conferem. O nome contém `run_curve.py`, para que a liberação continue reconhecendo um worker de curva em execução. Os testes estão em `tests/unit/test_v44_successor_runner.py`. A validação na cópia da célula real gravou e selou a lacuna esperada.

## Execução

Os oito shards são relançados com o sucessor, com os mesmos argumentos, ambiente, logs e prioridade do driver congelado (`v4-tier-driver.sh`). O registro de cada lacuna carrega o hash do sucessor que a gravou.

## Relatório e manuscrito

O relatório e o exportador passam a reconhecer o tipo `propagation`: coluna própria na tabela de inventário e explicação na legenda. Nenhum outro tipo de lacuna, contagem ou regra muda. Methods registra a emenda, o incidente e o seu alcance.

## Ratificação

A aprovação do Owner autoriza o relançamento. A ratificação científica, com revisão do orientador, permanece pendente, como nas demais decisões delegadas.
