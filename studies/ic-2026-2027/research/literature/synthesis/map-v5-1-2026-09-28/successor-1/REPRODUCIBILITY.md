# Reprodução histórica e do sucessor

## Revisões distintas

| Componente | Revisão fixada | Evidência |
| --- | --- | --- |
| Produção histórica | `bc55e6d88f1c6366230243b587e1a3db0bc2907b` | README e run-record de 28/09 |
| Entrada do código de produção na integração | `227b456886c6204c3f74e50c3bc41b71541fad2d`, merge `e7c3a67cc809dea8c79e1a797f75e9e9a66edafe` | Histórico Git; vínculo já descrito no README original |
| Depósito da série agregada | `5edc9d590a89062d0b6e5957df64b16cd6b40f44` | Último commit de `series.json`; digest abaixo |
| Gerador e estilo das figuras originais | `10ae2af51eb21fc07f903aa1300805ba69942c13` | [Manifesto histórico](../figures/manifest.json) |
| Código integrado usado no recálculo | `8c3f667d2c972126a4d8d943f8a3b615880eafc4` | Base deste worktree; hashes dos módulos em [provenance.json](provenance.json) |
| Script do sucessor | Arquivo ainda sem commit | SHA-256 em `provenance.json`; não atribuir o script novo ao commit-base |

A série histórica tem SHA-256 `bd17861913b43817ab0870d002942ad17d8049dc89c985e5b7825a95142ddb69`. Os três módulos gráficos registrados são `map_saturation_figures.py` (`5e6d306071d7a4ea733a0fad5f8fecd87d853b28bf0e5eaaedf12c0370959ced`), `v4_report_figures.py` (`17ed36be4d9c17494e978f5145886e9c343f52bcf11262ee0f7bd85eb5011ac0`) e `v4_report_tables.py` (`af4a7ece1f3faf71750b87b639dcb9c266930dec82ce82cde2845051435a1f5a`). Seus bytes na revisão histórica foram conferidos contra o manifesto nesta entrega.

## Ambiente e limites

O intérprete usado para as contagens e checagens deste sucessor é `workbench/.venv/bin/python`, Python 3.12.13. As versões consultadas foram Pydantic 2.13.5, Ruff 0.15.22 e mypy 1.20.2. As quatro variáveis de threads abaixo ficaram em 1; não houve processos de checagem em paralelo, instalação ou download de pacotes.

Esse ambiente não contém Matplotlib nem NumPy. O manifesto gráfico histórico não registra o ambiente completo, a instalação efetiva, a versão de Python nem a pilha de fontes e bibliotecas nativas. O `pyproject.toml` e o `uv.lock` do estudo na revisão histórica são a definição versionada disponível, mas não certificam qual ambiente efetivamente desenhou os originais. Fixar o código é necessário; ainda não é prova de equivalência gráfica byte a byte.

A reprodução numérica do sucessor foi executada. A revisão anterior relata igualdade de tabelas e diferença nos quatro PDF/PNG ao usar código posterior. Esta entrega conferiu os hashes depositados e o código histórico, mas não regenerou as figuras históricas. Não se declara essa reprodução aprovada ou reprovada.

## Recalcular somente agregados do sucessor

Executar da raiz deste worktree. `MAP_STATE_ROOT` deve apontar para a raiz autorizada do estado broad-map v5, e `MAP_COORDINATOR` para a pasta do coordenador. São parâmetros locais; o script abre dessa segunda pasta somente arquivos `v5r2-*` explicitamente nomeados. A saída deve ser uma pasta nova temporária. Não apontar a saída para um pacote concluído.

```sh
set -eu
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
map_repo="$PWD"
map_python="$map_repo/workbench/.venv/bin/python"
map_package="$map_repo/studies/ic-2026-2027/research/literature/synthesis/map-v5-1-2026-09-28"
map_successor="$map_package/successor-1"
map_replay=$(mktemp -d /private/tmp/map-successor-replay.XXXXXX)
: "${MAP_STATE_ROOT:?defina a raiz autorizada do estado broad-map v5}"
: "${MAP_COORDINATOR:?defina a pasta autorizada do coordenador}"
test "$(git rev-parse HEAD)" = 8c3f667d2c972126a4d8d943f8a3b615880eafc4
git diff --quiet HEAD -- scripts/v5_production.py scripts/v5_identity.py \
  workbench/src/research_workbench/workflows/systematic_review/v5_production.py \
  workbench/src/research_workbench/workflows/systematic_review/prioritized_stopping.py \
  workbench/src/research_workbench/workflows/systematic_review/prioritized_batches.py \
  workbench/src/research_workbench/workflows/systematic_review/v5_calibration_gate.py
"$map_python" "$map_successor/rebuild_aggregates.py" \
  --state-root "$MAP_STATE_ROOT" --coordinator "$MAP_COORDINATOR" \
  --output "$map_replay/aggregates"
MAP_SUCCESSOR="$map_successor" MAP_REPLAY="$map_replay/aggregates" \
  "$map_python" - <<'PY'
import hashlib, json, os
from pathlib import Path
source = Path(os.environ["MAP_SUCCESSOR"])
replay = Path(os.environ["MAP_REPLAY"])
manifest = json.loads((source / "provenance.json").read_bytes())
for name, expected in manifest["outputs_sha256"].items():
    assert hashlib.sha256((replay / name).read_bytes()).hexdigest() == expected, name
assert json.loads((replay / "provenance.json").read_bytes()) == manifest
print("7 agregados reproduzidos e proveniência igual")
PY
```

O script verifica a cobertura das seleções, valida a adoção das recuperações e a identidade pelo código integrado, reproduz as contagens históricas de todos os snapshots e calcula o filtro. Mantém identificadores e códigos por obra apenas em memória. Publica contagens e hashes; verifica que entradas e originais mantiveram seus bytes durante a operação. A auditoria histórica não é religada ao novo snapshot.

## Fixar o código histórico de produção

Para inspecionar a implementação histórica sem mudar o checkout atual, exportar apenas os caminhos necessários à reprodução para uma pasta temporária:

```sh
map_production_export=$(mktemp -d /private/tmp/map-historical-production.XXXXXX)
git archive bc55e6d88f1c6366230243b587e1a3db0bc2907b \
  scripts workbench/src workbench/pyproject.toml workbench/uv.lock \
  | tar -x -C "$map_production_export"
```

O subcomando histórico `report --output` não chama modelos, mas depende também da projeção de aquisição, preparação e das duas coortes, além de seus caminhos de runtime. Esses insumos não estão todos no acesso autorizado desta entrega. O comando completo não foi executado nem oferecido como reprodução integral aprovada. O recálculo acima usa apenas o estado autorizado e valida o resultado contra a série pública. Os demais subcomandos de produção não fazem parte desta reprodução.

## Reproduzir as figuras com o gerador fixado

O procedimento abaixo é para um ambiente já disponível que tenha as dependências gráficas compatíveis com o lock histórico do estudo. No ambiente do workbench utilizado nesta entrega, a verificação inicial interrompe a execução por ausência dessas dependências. Não instalar ou baixar pacotes para satisfazê-la nesta tarefa.

```sh
"$map_python" - <<'PY'
from importlib.util import find_spec
assert find_spec("matplotlib") and find_spec("numpy"), "dependências gráficas ausentes"
PY
map_figure_export=$(mktemp -d /private/tmp/map-historical-figures-code.XXXXXX)
map_figure_output=$(mktemp -d /private/tmp/map-historical-figures-output.XXXXXX)
git archive 10ae2af51eb21fc07f903aa1300805ba69942c13 \
  studies/ic-2026-2027/src studies/ic-2026-2027/pyproject.toml \
  studies/ic-2026-2027/uv.lock | tar -x -C "$map_figure_export"
MAP_PACKAGE="$map_package" MAP_FIGURE_EXPORT="$map_figure_export" \
MAP_FIGURE_OUTPUT="$map_figure_output" MPLBACKEND=Agg \
MPLCONFIGDIR="$map_figure_output/mpl-cache" \
PYTHONPATH="$map_figure_export/studies/ic-2026-2027/src" \
  "$map_python" - <<'PY'
import hashlib, json, os
from pathlib import Path
from ic_study.analysis import map_saturation_figures as figures
from ic_study.analysis.v4_report_tables import write_table
package = Path(os.environ["MAP_PACKAGE"])
export = Path(os.environ["MAP_FIGURE_EXPORT"])
output = Path(os.environ["MAP_FIGURE_OUTPUT"])
manifest = json.loads((package / "figures/manifest.json").read_bytes())
assert manifest["code"]["commit"] == "10ae2af51eb21fc07f903aa1300805ba69942c13"
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
modules = export / "studies/ic-2026-2027/src/ic_study/analysis"
assert Path(figures.__file__).resolve().parent == modules.resolve()
for name, expected in manifest["code"]["modules_sha256"].items():
    assert sha(modules / name) == expected, name
assert sha(package / "series.json") == manifest["inputs"]["series"]["sha256"]
series = figures.load_series(package / "series.json")
steps = figures.transitions(series)
figures.figure_trajectory(series, steps, output, dpi=300, synthetic=False)
figures.figure_shares(series, output, dpi=300, synthetic=False)
write_table(figures.transition_table(series, steps), output)
checks = {name: sha(output / name) == expected
          for name, expected in manifest["outputs"].items()}
(output / "reproduction-check.json").write_text(
    json.dumps({"generator_commit": manifest["code"]["commit"],
                "outputs_match_original": checks}, indent=2) + "\n")
print(json.dumps(checks))
PY
```

São chamadas somente as funções de desenho do mapa e de escrita da tabela, a partir de `series.json`. Não se executa outro gerador de resultados científicos. A coleta automática de revisão Git do comando gráfico não é usada, pois uma exportação temporária não é um checkout com aquele HEAD; a revisão é fixada pelo `git archive` e pelos hashes verificados. Os seis resultados e o registro de comparação ficam somente na saída temporária. Se os bytes diferirem, registrar as diferenças e o ambiente antes de atribuir uma causa; não substituir os originais.
