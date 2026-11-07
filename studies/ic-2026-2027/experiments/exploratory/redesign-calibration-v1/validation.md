# Validação da entrega

24/09/2026. Código científico executado: `0e2d8ee`. Piloto concluído e
imutável: `run-01`, commit de evidência `ed0c65f`. O rascunho de pré-registro
permanece em revisão; nenhum resultado confirmatório existe.

## Estudo e estrutura

- TDD em fatias: testes inicialmente falharam por ausência das interfaces de
  matching, dinâmica, observação, projeção, classificação da janela, estimador
  de dose, discriminante, sementes e gates. Implementação incremental levou
  os dez testes focados ao verde.
- Casos analíticos: marginais iguais e ordem preservada; influência zero reduz
  ao AR; canal não altera latente; perda por domicílio e renovação; equivalência
  linear e disjunta; janela com três estados; dose interpolada sem extrapolação;
  empates com meio acerto; sementes separadas, orçamento e saída não sobrescrita.
- Suíte completa do estudo: **137 passed in 39.04s**, sem falhas.
- Ruff: lint e format-check passaram nos 38 arquivos do estudo.
- Mypy estrito, executado a partir do estudo: passou nos 31 arquivos src/tests.
  A execução integrada inicial encontrou retorno NumPy inferido como Any;
  a correção está em `0e2d8ee`, antes do piloto, e o check estrito foi repetido.
- Build do sdist/wheel e instalação/importação em ambiente temporário independente:
  `wheel smoke: studies/ic-2026-2027 passed`.
- `check_repository.py`: 7/7, repetido antes de cada commit desta entrega com
  `UV_CACHE_DIR=/private/tmp/uv-cache-codex7`. Links, locks e imports entre
  projetos continuam válidos. `git diff --check` passou.
- Os 23 hashes de entrada do piloto foram reconferidos. O ledger tem 1.504
  painéis e namespaces disjuntos. A auditoria adicional de sementes reservadas
  está em [seed-audit.json](seed-audit.json), sem simulações confirmatórias.

Comandos do estudo, na raiz do repositório:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --locked \
  --project studies/ic-2026-2027 pytest studies/ic-2026-2027/tests -q
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --locked \
  --directory studies/ic-2026-2027 mypy src tests
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --locked \
  --project studies/ic-2026-2027 ruff check studies/ic-2026-2027
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --locked \
  --project studies/ic-2026-2027 ruff format --check studies/ic-2026-2027
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 \
  ./scripts/build_and_smoke.sh studies/ic-2026-2027 ic_study uv
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --locked \
  --project studies/ic-2026-2027 python scripts/check_repository.py
```

## Gate geral ainda em execução no handoff

`UV_CACHE_DIR=/private/tmp/uv-cache-codex7 just quality` foi iniciado. Estrutura,
linters e mypy dos DOIS projetos passaram. O pytest do workbench coletou 5.786
testes e ainda executava os casos de recuperação, após passar
`test_focused_attempts_backup.py`. Não houve falha observada até esse ponto.
O [snapshot do progresso](full-quality-progress.log) é parcial, não resultado
final nem dispensa do gate. O processo continua com log local em
`/private/tmp/ic-redesign-quality.log`; não se afirma `just quality` verde.
Os logs completos do estudo estão em `study-tests.log` e `study-build.log`.

Nenhum arquivo de workbench foi editado. Não houve push, merge, checkout de main,
aceite científico ou congelamento de pré-registro. A demora da suíte geral
não foi contabilizada como compute de piloto: as 3.520 simulações científicas
foram encerradas em 88,326 s, sem repetição posterior.
