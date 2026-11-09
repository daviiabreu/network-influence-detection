# Verificação pontual do sucessor

Executada em 30/09/2026 no worktree `docs/map-v5-1-successor-20260930`, HEAD `8c3f667d2c972126a4d8d943f8a3b615880eafc4`, com `workbench/.venv/bin/python` (3.12.13). Todos os processos foram sequenciais, com `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `VECLIB_MAXIMUM_THREADS=1` e bytecode desabilitado. Não houve chamadas de modelos, triagem, extração, recuperação, simulações, suítes, instalação, commit ou push.

| Checagem | Resultado observado |
| --- | --- |
| Reconciliação pelo estado autorizado | 8.817 triadas = 4.724 incluídas + 1.820 excluídas + 2.273 incertas; 557 reduções; 4.167 inclusões distintas |
| Série histórica | Os 14 denominadores e todas as contagens por categoria reproduzidos antes do filtro |
| Filtro de secundários | 70 obras retiradas; 3.986 remanescentes; código de parada aplicado às transições da série rebaseada |
| Comparação independente dos agregados | 49 parcelas e 14 snapshots conferidos; reduções entre 0 e 70 por categoria; nenhuma contagem acima do denominador |
| Código gráfico histórico | Hashes dos três módulos no commit do manifesto conferem |
| Preservação dos originais | 13 artefatos, incluindo o run-record, conferidos por SHA-256 e contra HEAD; README original recebe exatamente um ponteiro |
| Proveniência do recálculo | Hashes do script, módulos integrados, entradas privadas e sete saídas agregadas registrados |
| Divulgação | Novos JSON/CSV sem identificadores de obras, evidência, texto de fontes ou juízos individuais; documentação sem caminhos privados absolutos |
| Ruff no único arquivo Python novo | `ruff check --config workbench/pyproject.toml`: aprovado |
| Formatação no único arquivo Python novo | `ruff format --check --config workbench/pyproject.toml`: um arquivo já formatado |
| mypy no único arquivo Python novo | `mypy --strict --follow-imports=skip`: sem problemas em um arquivo; imports não ampliam a checagem às dependências |
| Estrutura | `scripts/check_repository.py`, executado pelo Python do workbench via `runpy`: sete checagens aprovadas |
| Diff | `git diff --check`: aprovado; única mudança em artefato preexistente é o ponteiro no README |

A execução do verificador de estrutura usou uma barreira de auditoria que bloqueia `open`, `scandir` e `listdir` em qualquer caminho proibido antes de seu acesso. As sete checagens concluíram sem acionar a barreira. As figuras não foram regeneradas: o ambiente indicado não contém Matplotlib ou NumPy e o ambiente histórico completo não está identificado. A verificação de agregados não é validação da elegibilidade pendente nem conclusão científica da revisão.
