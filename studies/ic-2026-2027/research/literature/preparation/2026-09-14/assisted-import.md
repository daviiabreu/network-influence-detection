# Importação das referências assistidas

A [emenda aprovada](../../../decisions/2026-09-14-assisted-calibration-references.md)
foi incorporada ao protocolo v4. A importação nativa passa a criar uma suíte
`calibration-3`, conservando as fontes v3 e registrando separadamente a proposta
IA e sua adoção pelo responsável. O
[vínculo congelado](assisted-calibration-import-binding-v1.json) identifica o
scaffold, o pacote de conferência, os dois protocolos e as três configurações
de agentes. As novas configurações apenas apontam para o protocolo e o contexto
v4; instruções, ferramentas, contratos de entrada/saída e orçamentos permanecem
iguais aos dos predecessores.

Não existe exportação real completa importada. Aprovar a emenda não marcou os
50 casos e os seis campos como conferidos, não declarou histórico de ajuste nem
produziu auditoria posterior. O formulário já traz as propostas; Davi pode
conferir cada item, corrigir o necessário, declarar o histórico e exportar.
Exportações parciais servem para retomar a conferência, sem perda das respostas.

O formulário sucessor está em `http://127.0.0.1:8773/`, na pasta local
`~/.local/state/research-workbench/assisted-reference-implementation-20260914/review-form-v2/public/`.
Ele informa que o método foi aprovado e mantém os mesmos bytes do pacote de
fontes e do JavaScript anterior. Portanto aceita retomar exportações do
formulário anterior. Apenas o HTML de apresentação mudou, com SHA-256
`e9d6764789e25e698f11764d6fbd83d92459c7641e41056be13e4a017aa4939a`.
A inspeção no navegador confirmou os 50 casos e seis campos, todos inicialmente
sem marcação, e histórico desconhecido. Nenhuma resposta foi marcada pelo agente.

O primeiro importador aceita adoção integral das propostas sem alterações e
ausência de ajuste anterior declarada pelo responsável. Uma correção permanece
no arquivo de revisão e exige validar nova proposta/evidência antes da
importação. Não se reaproveitam justificativas, critérios ou trechos antigos
para uma resposta diferente. Se houve ajuste, deve ser preparado outro desenho
com casos separados para verificação. O histórico desconhecido continua
pendente.

A operação é `research-workbench systematic-review import-assisted-calibration`.
Seus argumentos e limites estão no
[processo de calibração](../../../../../../docs/process/systematic-review-calibration.md#scaffold-reference-adoption-and-validation).
O agente responsável pela continuidade deve usar os caminhos absolutos dos
arquivos locais, uma pasta privada nova fora do Git e declarar todas as raízes
servidas por HTTP. O export humano deve ser copiado para uma pasta privada com
modo `0700`, arquivo `0600`, preservando seus bytes. A operação retorna recibo
de validação e preservação de proveniência, sem executar revisores.

O passo seguinte à importação é validar a configuração comprometida no Git e
executar os revisores com entradas cegas. Depois, a auditoria do responsável
deve referenciar as saídas reais. As métricas descrevem concordância com as
referências assistidas adotadas. A aprovação automática permanece pendente
dessa auditoria; a revisão sistemática ainda tem filas de identidade, metadados,
triagem, extração e síntese por concluir.

O comparador nativo continua exigindo igualdade exata de `values` e
`unresolved_fields`, inclusive os localizadores, na extração. Uma paráfrase ou
um trecho diferente podem produzir falha mesmo quando a interpretação é
compatível. Esta emenda não altera esse avaliador nem permite que uma auditoria
posterior dispense falhas automáticas. Uma avaliação semântica precisaria de
regra e validação próprias antes de substituir o comparador atual.

## Verificação da implementação

A revisão independente identificou e levou à correção de exposição de respostas
em mensagens de erro e saídas parciais após falhas de gravação. Testes sintéticos
exercitaram importação, execução, dois replays idênticos, corrupção de fontes,
separação das entradas dos revisores e recuperação após falha, sem criar
declarações humanas para o material real.

A primeira rodada de `just quality` registrou 3.656 testes aprovados e sete
falhas no workbench. Quatro exigiram completar o catálogo, os contextos e as
tarefas sintéticas v4; os dez testes do contrato passaram após a correção.
As outras três ocorreram porque o comando havia sido iniciado com `umask 077`,
alterando as permissões esperadas pelos fixtures; os 45 testes afetados e de
seu módulo passaram com `umask 022`, sem alterar as proteções do produto.
Os 34 testes do estudo passaram. `just check` passou nos dois projetos, assim
como a construção e o smoke dos dois pacotes; o pacote workbench foi novamente
construído após acrescentar as tarefas v4. As correções tiveram revalidação
direcionada, sem apresentar a primeira rodada integral como aprovada.

Os logs locais estão em
`~/.local/state/research-workbench/assisted-reference-implementation-20260914/`.
Esses resultados verificam a implementação e não representam execução ou
aprovação científica da calibração.
