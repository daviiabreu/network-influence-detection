# Equivalência de host v4 — homelab

Medição em 2026-09-27T23:33:44.449167+00:00; replay G0-00000 a G0-00002 apenas para equivalência, não é evidência do gate. Checkout destacado `37513841`; freeze SHA-256 `99c4277235d4f2303b6f009d6ead8287a5d71372744dd6781e1e2d1847710837`; 82 hashes de código iguais ao freeze nos dois hosts. O `uv sync --frozen` concluiu no homelab com BLAS/OMP limitados a uma thread.

## Veredito pré-declarado

- Probe: **passou**; diferença absoluta máxima `6.66e-16`, `allclose(rtol=0, atol=1e-12)=true`.
- Campos discretos: **falhou**; 4448 divergências em `seed_material_sha256` nas fases (160, 2432, 1856 por tarefa). A primeira é `G0-00000/phases.jsonl[1056].seed_material_sha256`: Mac `29f202cba340b7e9a7e8ee329abfcff4aad5ba40cacc9f5c38f6c10eda14df50`, homelab `711adbe11da89f611c1fd4eb11849ac69081e637e3afd01cff230302494ebe93`. Estados, decisões, contagens e campos discretos do resultado coincidiram; os hashes de fase, que vinculam parâmetros numéricos, não.
- Campos contínuos: **passou**; 1331544 valores comparados, nenhuma violação de `1e-12 + 1e-9*|mac|`, diferença absoluta máxima `7.88e-12`. Os selos internos dos seis diretórios foram verificados.

**Equivalência geral: falhou.** Os únicos campos divergentes de `manifest(study)` são `environment.platform`, `environment.python`, `environment_sha256` e `host_sha256`; o JSON inclui ambos os manifestos completos.

## Tempo

| G0 | Mac (s) | Homelab, 3 processos (s) | Mac / homelab |
| --- | ---: | ---: | ---: |
| G0-00000 | 2525.5 | 1120.2 | 2.25× |
| G0-00001 | 2409.8 | 2652.4 | 0.91× |
| G0-00002 | 2459.6 | 2295.6 | 1.07× |

O lote paralelo levou 2652.5 s no homelab (4.07 tarefas/h com três processos). A soma dos tempos por tarefa foi 6068.2 s no homelab versus 7394.8 s no Mac (1.22×). Os tempos do Mac vieram dos registros selados em outra condição de carga; não houve amostra controlada de três ou oito processos no Mac. A amostra opcional de oito processos não foi iniciada após a falha de equivalência.

Recomendação: manter os oito shards no Mac e nenhum no homelab sob este critério. A Parte B não foi implementada; não há sucessor, importação, execução de gate/tier nem commit local. Pytest, ruff e mypy não foram executados porque não houve mudança de código após a falha do critério. O clone por SSH do GitHub falhou com `Permission denied (publickey)`; o clone HTTPS de leitura funcionou. Este registro não concede aceitação científica.

Registro JSON SHA-256: `d25b651a199df329a249b9380d739b43465ba1d9fd54996dba86a3a77b4884ef`.
