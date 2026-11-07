# Reprodução dos resultados do piloto

Executar a partir de `studies/ic-2026-2027/`, usando o Python do lock:

```sh
uv run --locked python -m ic_study.analysis.fragmentation_pilot \
  --spec experiments/exploratory/fragmentation-pilot-v1/spec.json \
  --phase pilot --max-attempts 100000 \
  --output /tmp/fragmentation-pilot-regeneration.jsonl
```

A saída deve ser nova; o executor recusa sobrescrita. As outras fases são
`benchmark` com limite 50000, `control` com 100000 e `sensitivity` com 100000.
Novas execuções terão tempos, datas e hashes próprios. Comparar os inputs e
campos científicos das linhas `trial`, preservando seus índices e fase.
O código da execução original é o commit
`a394f28e66868b0c5d2c9f6d032b5394bb354073`; os hashes no cabeçalho identificam
os arquivos científicos exatos. Mudanças posteriores somente em documentação
não alteram esses arquivos.

O exemplo abaixo confere o hash do artefato principal, recalcula seu resumo e
regenera todos os campos científicos do caso 35. Ele chama o modelo e os
observadores implementados no pacote; não executa o código externo do artigo.
O manifesto usa caminhos do armazenamento local desta entrega. Em outra
máquina, localizar os mesmos bytes pelo SHA-256 e ajustar somente o local.

```python
import hashlib
import json
from pathlib import Path

from ic_study.analysis.fragmentation_pilot import summarize
from ic_study.models.deffuant import Parameters, State
from ic_study.simulation.fragmentation import effective_partition, simulate

directory = Path("experiments/exploratory/fragmentation-pilot-v1")
manifest = json.loads((directory / "run-manifest.json").read_text())
meta = manifest["phases"]["pilot"]
data = Path(meta["artifact_path"]).read_bytes()
assert hashlib.sha256(data).hexdigest() == meta["sha256"]
records = [json.loads(line) for line in data.splitlines()]
header, rows, footer = records[0], records[1:-1], records[-1]
assert footer["record"] == "completed" and len(rows) == 112
assert summarize(rows) == footer["summary"]
for name, digest in header["source_sha256"].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest

case = rows[35]
params = Parameters(
    confidence=case["confidence"],
    **header["spec"]["models"][case["model"]],
)
state = State(
    case["initial_opinions"], [tuple(edge) for edge in case["base_edges"]], params
)
result = simulate(
    state,
    event_seed=case["event_seed"],
    max_attempts=header["max_attempts"],
    tolerance=header["spec"]["phases"]["pilot"]["tolerance"],
    margin=header["spec"]["certificate_margin"],
)
assert json.loads(json.dumps(result.to_dict())) == case["result"]
stop = case["result"]["cached_stop"]
snapshot_state = State(stop["opinions"], state.edges, params)
assert len(stop["partition"]) == 13
assert len(effective_partition(snapshot_state)) == 12
assert len(result.endpoint_partition) == 12
print("Resumo e caso 35 reproduzidos")
```

O registro de análise inclui uma segunda regeneração do caso de sensibilidade
de índice 3, com os mesmos inputs e tolerância 0,001. Ambas coincidiram em
todos os campos retornados pelos observadores. Essas regenerações não são
novas réplicas estatísticas.
