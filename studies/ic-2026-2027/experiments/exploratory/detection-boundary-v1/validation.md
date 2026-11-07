# Validação da emenda 14

Trabalho iniciado em 24/09 e consolidado em 25/09/2026, na branch
`research/question-consolidation`. Sem edição de `workbench/`, push ou merge.

TDD: os módulos novos começaram com falhas de importação nos testes científicos;
seguiram-se implementações e ciclos verdes. O update pré-transporte teve seu
próprio teste vermelho antes da extração da função. A falha real de serialização
do relatório foi reproduzida por um teste vermelho `json.dumps(disclosure(...))`;
a correção converte apenas o escalar NumPy para `bool` nativo. A geometria, as
sementes, o matching e o discriminador não mudaram entre tentativa e replay.

Checagens do estudo, com `UV_CACHE_DIR=/private/tmp/uv-cache-codex7`:

- `uv run --directory studies/ic-2026-2027 pytest -q`: **153 passaram**, 4,42 s,
  após a correção; 16 testes novos. A rodada anterior à correção tinha 152 verdes,
  mas não cobria a serialização do bit.
- `ruff check .`, `ruff format --check .`, executados no estudo: verdes.
- `mypy src tests`, com configuração estrita do estudo: 37 arquivos, verde.
- `scripts/build_and_smoke.sh studies/ic-2026-2027 ic_study uv`: wheel e smoke
  verdes novamente após a correção de serialização; teste dedicado e replay
  também passaram.
- `scripts/check_repository.py`: sete checagens verdes antes de cada commit.
- Seis links locais do rascunho sucessor resolvidos.

A matriz global `just quality` já estava em execução desde a rodada anterior;
a parte de testes de recuperação do workbench continuava pendente durante esta
entrega. Não se iniciou uma cópia concorrente. Os checks do estudo acima
correspondem ao código novo; não se declara a matriz global verde. Os módulos
do workbench não foram alterados. Log operacional:
`/private/tmp/ic-redesign-quality.log` (fora do Git).

A evidência científica é somente calibração em r=0,70. Não há resultado
confirmatório, curva de AUC publicada, estimativa numérica de a*, cobertura
bootstrap demonstrada ou confiabilidade de P$$P04 estimada. A arquitetura de
bootstrap aceita um callback que deve refazer matching/treino; ainda requer
integração científica e validação de cobertura antes do congelamento, como
explicitado no pré-registro. Não usar o teste unitário de orquestração como
substituto dessa validação.
