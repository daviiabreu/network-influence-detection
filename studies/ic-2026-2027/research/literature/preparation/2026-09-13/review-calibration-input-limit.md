# Revisão independente do limite de entrada da calibração

Data local: 13/09/2026, America/Sao_Paulo. Revisão do diff de trabalho contra `HEAD` `b1f8bea6574137ce176ddfd5aecab5d158e93c1f`, restrita aos quatro candidatos abaixo. Nenhum achado acionável nos eixos de requisitos e convenções. Não foram editados os candidatos nem executados modelos ou uma calibração científica.

| Candidato revisado | SHA-256 |
| --- | --- |
| `workbench/src/research_workbench/cli.py` | `a53f26014a8517bf89c0e485488a5d46eba56f46a1e87b233f1cb97e068914c6` |
| `workbench/tests/workflow/test_calibration_scaffold.py` | `5b21fb940423a3731d8189cd7507a01742066c50b9f856fb36c181b8e12de8d3` |
| `workbench/tests/workflow/test_calibration_bibliographic_v2.py` | `66b7c98f622b5c17feaa7662bcedd9fb179543034722dc3ad5ad3ea9221fa99a` |
| `docs/process/systematic-review-calibration.md` | `c1425c18ba31def44aa8d4c9c9266ec9410e0ca933fbf4fee4568d9dbcc569d1` |

O diff desses quatro caminhos, obtido por `git diff HEAD -- <caminhos>` na ordem da tabela, tem 6855 bytes e SHA-256 `74381528922ff6f146893b727393993dcbae6e6d0025b1935f9ccc003665c0b1`. Alterações em `READINESS.md` e outros arquivos do pacote de preparação não integram esta revisão.

## Requisitos e comportamento

Em `cli.py:184`, `_MAX_CALIBRATION_INPUT_BYTES` vale 20.000.000. Há somente duas utilizações: `scaffold-calibration --corpus`, linha 1689, e `validate-calibration-suite --suite`, linha 1768. `_MAX_INPUT_BYTES` continua em 10.000.000 e permanece aplicado ao protocolo e aos role bindings; o diff não altera credenciais, comandos de execução, tarefas ou critérios científicos. A nova constante específica evita ampliar o limite genérico, sem introduzir dependência ou camada de abstração.

Os dois argumentos continuam usando `_read_regular_bytes(..., private=True)`. O helper, inalterado, verifica caminho fora do Git e sem symlinks, arquivo regular estável, proprietário atual, modo 0600 e ausência de hardlinks; confere identidade e metadados antes e depois da leitura. Lê no máximo `max_bytes + 1` e rejeita excesso antes de retornar ao decodificador. No scaffold, a leitura ocorre antes da construção e da criação do diretório de saída; na validação, precede até a procura por TODOs.

A reprodução temporária confirmou que o helper aceita exatamente 20.000.000 bytes. Nos dois comandos, 20.000.001 bytes retornaram código 2 por tamanho, sem stdout nem criação de saída. Nessa reprodução, o decodificador de JSON e a procura de TODOs foram substituídos por funções que falhariam se chamadas; nenhum deles foi alcançado. Fixtures temporárias também confirmaram rejeição de modo 0644, symlink, hardlink, FIFO e caminho sob um marcador `.git`. Essas verificações complementam a inspeção do helper; não simulam todas as possíveis corridas concorrentes de filesystem.

Os limites dos outros caminhos foram conferidos no código existente. `systematic_review_evaluation.py:102` conserva `_MAX_ARTIFACT_BYTES = 25_000_000`; `load_executed_review_suite`, linha 391, lê pelo helper `_read`, e `replay_review_evaluation`, linha 728, usa o mesmo helper para `suite.json`. A CLI encaminha execução de calibração e execução por subscription a esse loader. Já o replay por subscription reabre o binding com `self._store.read(bound)` em `subscription_calibration.py:340`; a CLI instancia esse store com limite de 50.000.000 em `cli.py:1446`. A leitura CAS verifica tamanho, hash e limite antes de entregar os bytes ao contrato. Esses módulos não foram alterados pelo candidato.

O aumento não modifica o schema ou o teste de sentinelas: TODOs continuam sendo recusados antes de `ReviewCalibrationSuite.model_validate_json`, e a resposta de validação continua sem autorizar promoção. Os argumentos do scaffold continuam sem executor, credenciais ou modelo. Os limites por tarefa e a validação de referências, fontes, tuning e autoria permanecem nos caminhos existentes, incluindo o orçamento por papel verificado no preflight de subscription.

## Caso real e verificação executada

Foram conferidos apenas os metadados dos arquivos privados de `broad-research-20260911/calibration-preparation-v3-extraction-20260913`:

| Entrada real | Bytes | SHA-256 |
| --- | ---: | --- |
| `corpus-selection.json` | 12416114 | `316b118739cb6e6eebd3b7cebe748d805124bda4523a7fb9e404a7c5278b62e7` |
| `calibration-scaffold.json` | 14256404 | `8c00d9c368a0049c1dd2bdb2e28301b5e61deb323778ca7d6adc258484731902` |

Ambos excedem 10.000.000 e cabem em 20.000.000 bytes. Uma chamada somente de leitura a `validate-calibration-suite` sobre a suíte real retornou código 2 pela presença de TODOs de autoria, com stdout vazio. Assim, o limite deixou de impedir a leitura e o bloqueio científico permaneceu. Não foi recriado o scaffold real nem alterado o CAS.

Foi executado nesta revisão `python -m pytest -q -p no:cacheprovider workbench/tests/workflow/test_calibration_scaffold.py workbench/tests/workflow/test_calibration_bibliographic_v2.py`, pelo Python da venv do workbench: **45 testes passaram em 10,64 s**. Os casos alterados cobrem entradas acima do antigo limite, rejeição acima do novo teto, preservação de TODOs e validação de uma fixture autoral sintética. O scaffold v2 mantém saída 0600 em diretório 0700 e não se torna executável enquanto não autorado. Os testes de parâmetros recusam opções de modelo, autenticação e executor no scaffold.

Ruff passou nos três arquivos Python; mypy também passou nos mesmos três arquivos, com cache desabilitado. Não foi executada a suíte completa. A [documentação candidata](../../../../../../docs/process/systematic-review-calibration.md) descreve corretamente o limite específico e distingue tamanho de arquivo, orçamento de tarefa e validação científica. O escopo não altera contratos, ownership ou gates científicos. Os hashes dos candidatos e das duas entradas reais foram reconferidos ao encerrar; esta revisão não autoriza promoção, triagem ou execução científica.
