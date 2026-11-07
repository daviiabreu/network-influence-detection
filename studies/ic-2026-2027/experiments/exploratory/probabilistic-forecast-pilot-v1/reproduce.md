# Reprodução do piloto

A implementação e especificação foram congeladas antes dos benchmarks no
commit `333938e`; os lotes analíticos usaram
`71ae80cf313b6c467abad5eeedfa6a266e5daaa0`, que acrescenta apenas a decisão
de custo. O [manifesto](run-manifest.json) identifica cada execução e seus
hashes. O pacote usa Python 3.12 e biblioteca padrão, com lock independente.

## Regenerar os lotes

Use uma cópia limpa da revisão de execução. Dentro de `studies/ic-2026-2027`,
sincronize `uv sync --locked --group dev`. Neste host, `uv` está em
`/Users/davi/.local/bin/uv`. Escolha um diretório novo para as saídas:

```sh
pilot_output_dir=$(mktemp -d)
/Users/davi/.local/bin/uv run --locked python -m ic_study.analysis.forecast_pilot \
  --spec experiments/exploratory/probabilistic-forecast-pilot-v1/spec.json \
  --phase primary --members 32 --output "$pilot_output_dir/primary.jsonl"
/Users/davi/.local/bin/uv run --locked python -m ic_study.analysis.forecast_pilot \
  --spec experiments/exploratory/probabilistic-forecast-pilot-v1/spec.json \
  --phase precision --members 128 --output "$pilot_output_dir/precision.jsonl"
/Users/davi/.local/bin/uv run --locked python -m ic_study.analysis.forecast_pilot \
  --spec experiments/exploratory/probabilistic-forecast-pilot-v1/spec.json \
  --phase confirmation --members 128 --output "$pilot_output_dir/confirmation.jsonl"
```

Para os benchmarks, usar `--phase benchmark` com R=32 e R=64 e dois novos
arquivos. Não sobrescrever resultados concluídos. A reprodução recebe nova
identidade: timestamps, tempo e eventualmente ambiente mudam, logo o hash do
arquivo inteiro não precisa coincidir. As linhas científicas devem coincidir
na mesma implementação, especificação e ambiente. Ausência do rodapé
`completed` impede chamar um lote de concluído.

## Conferir os dados preservados e os resumos

A receita abaixo roda no diretório do estudo, neste host, com `uv run --locked
python`. Ela verifica todos os objetos, a identidade das fontes, os resumos
e dois casos completos de regeneração. Em outra máquina, regenere os arquivos
e adapte somente os caminhos locais do manifesto em uma cópia de trabalho.

```python
import hashlib
import json
from pathlib import Path

from ic_study.analysis.forecast_pilot import summarize, trajectory

pilot = Path("experiments/exploratory/probabilistic-forecast-pilot-v1")
manifest = json.loads((pilot / "run-manifest.json").read_text())
for run in manifest["runs"]:
    data = Path(run["location"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == run["sha256"]
    records = [json.loads(line) for line in data.splitlines()]
    header, rows, footer = records[0], records[1:-1], records[-1]
    assert footer["record"] == "completed"
    assert footer["trajectories"] == len(rows)
    for path, digest in header["source_sha256"].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest
    assert summarize(rows, header["spec"]) == footer["summary"]
    if run["phase"] == "confirmation":
        for row in (rows[120], rows[270]):
            regenerated = trajectory(
                header["spec"], row["cell"], row["replicate"],
                header["phase"], header["members"],
            )
            assert json.loads(json.dumps(regenerated)) == row
print("All files and summaries verified; two trajectories regenerated")
```

`score_ensemble` em `ic_study.metrics.histogram_scores` permite recalcular
as cinco perdas a partir de cada ensemble guardado. Ele recebe uma lista
de tuplas de contagens e a tupla de contagens observadas. Não é necessário
invocar um modelo para esse recálculo.

## Reconstruir os contrastes adicionais

`analysis-input.json` contém os resumos do rodapé sem alteração. Para cada
score/célula dinâmica, `oracle_contrasts` copia a diferença do candidato
gerador contra `constant`; os valores relativos dividem a diferença e os
limites do intervalo pela média de perda de `constant` naquele score.
`primary_criterion_cells_by_phase` exige limite inferior relativo de
mean-W1 maior que 0,01 e superior relativo de ES menor que -0,01.
A interseção das células aprovadas nas três fases dá o critério replicado.

Para os controles e a sensibilidade, usar as linhas completas e a função
`interval` da implementação congelada. Com `row` representando uma trajetória:

```python
import statistics
from ic_study.analysis.forecast_pilot import interval

def heldout(row, model, score):
    return statistics.mean(
        w["forecasts"][model]["scores"][score]
        for w in row["waves"] if w["split"] == "test"
    )

# group: as 30 trajetórias de uma célula e fase; oracle: cell["truth"].
# model: "dw", "pulsed_dw" ou o candidato escolhido só no treino.
values = [
    heldout(row, model, "energy") - heldout(row, oracle, "energy")
    for row in group
]
control_difference = interval(values, 2.04523)
```

Para o selecionado, `model` é `row['selected_on_train']['energy']` em cada
linha. Para a sensibilidade, emparelhar principal e precisão pelo ID da
célula e índice de réplica, conferir igualdade de `observed`, `outcome` e
`data_seed` em todas as ondas, calcular a diferença oracle–constant em cada
fase e aplicar `interval` a precisão menos principal. A confirmação tem
outro grupo de dados e não entra nessa comparação pareada.

As frequências de seleção contam `selected_on_train` por célula e score;
DW e DW episódico são as escolhas de dinâmica. Para a lei verdadeira
do controle de drift, usar `drift_plus`, não `constant`. Nenhuma dessas
contagens transforma escolha de modelo em teste de influência causal.
