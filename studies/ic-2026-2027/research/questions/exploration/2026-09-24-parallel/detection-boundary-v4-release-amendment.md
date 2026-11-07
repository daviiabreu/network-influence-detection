# Emenda de liberação da v4: liberar quando o inventário estiver completo

Registrada em 28/09/2026, às 23:28 UTC (commit `428ca7cd`), antes de qualquer tier confirmatório começar e antes de qualquer resultado confirmatório existir. Naquele momento o gate estava no estágio G2, com cerca de 200 de 700 tarefas. Os estágios anteriores foram lidos só pelos resumos de aprovação que o driver usa para seguir. Esta emenda é um sucessor ligado ao congelamento da v4 (`detection-boundary-freeze.json`, código em `37513841`, `freeze-v4.json` com SHA-256 `99c42772…`) e à emenda v4 ([`detection-boundary-amendment-v4.md`](detection-boundary-amendment-v4.md)). Ela não altera nenhum desses arquivos.

## Autoridade e motivo

A mudança segue a instrução de Davi, Research Owner, em 28/09/2026: "nao deixa travada pra 19/10, quanto antes melhor, mas COM QUALIDADE".

O fechamento fixo em 2026-10-19T02:59Z (`CLOSE_UTC` em `v4_plan.py`) tinha dois papéis. Delimitava a janela operacional e impedia que alguém olhasse resultados no meio do caminho e decidisse continuar, repetir ou interromper unidades conforme o que visse. O primeiro papel continua coberto pela regra (b) abaixo. O segundo também continua: a liberação antecipada é disparada mecanicamente pela conclusão do inventário inteiro, sem leitura de estimativa nem de status, e depois dela nenhuma unidade pode ser acrescentada, repetida ou interrompida. A antecipação dá mais tempo para análise, redação e revisão antes do intercâmbio de 22/10/2026.

## Regra

As estimativas confirmatórias são liberadas no primeiro destes momentos:

- **(a) Inventário completo.** As 414 unidades de `curve_units()` têm o registro de curva gravado no armazenamento selado, com status final "completo válido" ou "completo inválido", e nenhum processo `run_curve.py` está em execução. A condição é verificada só pela existência do arquivo de curva de cada unidade, sem abrir o conteúdo.
- **(b) Fechamento declarado.** Em 2026-10-19T02:59Z vale a regra original: unidades não concluídas viram "parcial por encerramento operacional".

Não existe liberação parcial nem por tier. Liberar é fechar o inventário, e a função congelada sela o armazenamento nesse momento.

## O que não muda

Continuam como estão:

- as definições: grade, confiabilidades, alvos, nulos, discriminador, bandas, censura e inversão;
- o gate e seus critérios;
- a execução: tiers e sua ordem, barreira global, oito shards, o Mac como único host (item 41 do log) e as sementes confirmatórias;
- o inventário e as regras de invalidação e de relato.

As análises exploratórias continuam proibidas de ler resultados confirmatórios antes da liberação.

## Implementação

O código congelado fixa o fechamento e recusa liberar antes dele (`_close_inventory` em `v4_curve.py`). O script sucessor `experiments/exploratory/detection-boundary-v4/release_on_completion.py` repete as checagens de pré-voo do `run_curve.py` congelado: congelamento, segunda vinculação e agregados de G0 a G2c. Depois ele confere a condição (a).

Se ela vale antes do fechamento, o script chama a função congelada `released_curves` com o argumento `now` igual ao fechamento declarado, porque a função compara o horário com essa constante. Por isso o inventário selado continua registrando `closed_utc` = 2026-10-19T02:59Z. O horário real, a condição que disparou a liberação e o SHA-256 da saída ficam num registro lateral (`release-record.json`), e o relatório cita os dois. Se o script rodar depois do fechamento, ele segue exatamente o caminho original.
