# Importação das referências de calibração

O conversor privado está pronto para receber a exportação completa do
[formulário v3](http://127.0.0.1:8768/): 50 referências de título/resumo e uma
extração com seis campos. Ele produz um sucessor do scaffold com 101 tarefas,
preservando exatamente as respostas fornecidas. Nenhuma exportação humana foi
lida ou convertida durante esta preparação.

O pacote local fica em
`~/.local/state/research-workbench/corpus-preparation-20260913/calibration-import/`.
`import_owner_references.py` é o conversor; `calibration-import.md`, nesse
diretório privado, contém os comandos completos para copiar a exportação e
executar a importação. As cópias de respostas ficam fora do Git e das pastas
dos formulários. O download original é preservado.

| Artefato final | SHA-256 |
| --- | --- |
| Conversor | `b2e9a83cc02edc373321e1c53c7e416abca86665d95c7718e0374c9404079eee` |
| Testes sintéticos | `1c5c5cf29d28292ec05c6c8b6a5af078c2748975b46ce2d0b674b6841c54a8de` |
| Instruções privadas | `c0ab7579f8cf8dfaf2aae3bba54d51d5ab582f7d4b6f278b46d603745d655b3d` |

## Caminho de uso

Depois do preenchimento, Davi exporta `minhas-decisoes-calibracao-v3.json` e
fornece esse arquivo. A cópia para importação é criada com modo 0600 em um
novo diretório 0700. O conversor exige uma declaração explícita do histórico
de ajuste. Não há valor padrão: `no_prior_tuning` só pode ser usado após essa
declaração real; `declared_in_suite` recusa o scaffold atual e exige um sucessor
com as partições necessárias. Esse histórico ainda não foi informado.

O conversor confere os hashes do pacote, protocolo, scaffold e mapa dos casos,
exige os 50 trabalhos distintos e seus pares A/B e copia a referência de cada
trabalho para as duas tarefas correspondentes. Os critérios escolhidos são
preservados no recibo, sem criar novas assertions para os modelos. As seis
respostas de extração precisam estar explicitamente preenchidas ou marcadas
como não resolvidas, conforme o contrato.

Antes de criar saída, ele valida `ReviewCalibrationSuite` e reproduz fontes e
locators pela API nativa. Uma importação válida grava `suite.json`, os bytes
originais de `owner-export.json` e `receipt.json` em um destino novo e privado.
Esses arquivos ainda não são uma calibração executada: faltam inferência,
replay, métricas e auditoria humana previstas no protocolo.

## Revisão e correções

A [revisão independente](review-calibration-import.md) encontrou um destino
que permitia publicar respostas na pasta HTTP. A primeira correção bloqueou
os caminhos declarados; o reteste encontrou um alias de caixa do macOS para
o mesmo diretório. O conversor final compara também dispositivo/inode dos
diretórios protegidos com os ancestrais do destino. As duas versões anteriores
ficam preservadas em `candidates/` e não devem ser usadas para importar.

O reteste final passou em **36 verificações**, sem skips: 32 testes do
sucessor e quatro conferências independentes. Os caminhos HTTP normal e com
alias foram recusados antes da leitura de respostas, sem criação de saída;
o GET retornou 404. O caminho privado JavaScript → conversor → CLI nativa
continuou válido, com 101 tarefas, seis campos e cópia exata. Todos esses dados
eram sintéticos; nenhum resultado científico ou julgamento humano foi criado.
