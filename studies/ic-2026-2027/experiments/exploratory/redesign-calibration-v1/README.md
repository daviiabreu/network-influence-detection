# Piloto de redesenho, 24/09/2026

Somente calibração e gates de não degeneração. Não há execução confirmatória.
O [protocolo](protocol.md) antecede todas as simulações; a
[especificação](spec.json) e o runner foram commitados antes da execução.

Execução única no commit `0e2d8ee`, sem diff rastreado: 88,326 segundos de
parede, 3.520 simulações, encerramento normal. Orçamento autorizado: 1.200 s;
limite preventivo do runner: 1.100 s. Não houve repetição nem busca adicional.
O gate geral do repositório rodou concomitantemente; o tempo é custo observado,
não benchmark exclusivo do processador. Testes unitários usam microcasos e não
foram empregados para selecionar parâmetros científicos.

P1+P2: 1.504 painéis, incluindo calibração e matching. Regra escolheu a=0,4,
rho=0,8389618632, com BA do baseline r=0,8 igual a 0,75. A checagem r=0,65
passou apenas o gate grosseiro `0,55 < BA < 0,95`. Não é intervalo de confiança.
Diferença absoluta de lag 1 latente de calibração: 0,000126; na checagem
primária, lag 1 ordinal: 0,001836, variação total marginal agregada: 0,000814.
Média de 52.097 pares anuais observados na checagem, na escala de referência
aproximada do SHP. O diagnóstico agregado não substitui ajuste de marginais
empíricas nem valida a máscara de perda contra microdados.

P4: 672 simulações do controle PN na calibração e 1.344 dos dois braços não
lineares em sementes novas. d50 do controle de calibração = 0,03671875, bracket
local [0,03625;0,036875]; grade final de 14 doses. Ambos os braços de checagem
têm célula interior e cruzam 0,5. Não se exportaram suas probabilidades,
limiares ou diferença. Os extremos da grade têm saturação deliberada; a região
de transição deixou de ser degenerada.

A [auditoria de sementes reservadas](seed-audit.json) também confirmou
interseção zero entre 3.328 sementes do piloto e 31.002 do plano confirmatório.
Apenas os inteiros foram derivados: nenhuma trajetória confirmatória foi gerada.

## Arquivos e reprodução

- [Manifesto](run-01/manifest.json): HEAD, Python, NumPy, plataforma, configuração,
  hashes de todos os módulos do estudo, lock, especificação e protocolo.
- [Resumo](run-01/summary.json): calibração consultada integral e gates primários.
- [Progresso](run-01/progress.jsonl): ordem efetiva dos pontos e gates.
- [Ledger do painel](run-01/panel-ledger.jsonl): 1.504 registros de parâmetros,
  sementes e hashes dos arrays latentes/observados. Não inclui features/escores.

Reprodução do piloto, somente se novamente autorizada com orçamento próprio,
na raiz desta revisão, exige diretório NOVO:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --locked \
  --project studies/ic-2026-2027 python -m ic_study.simulation.redesign_calibration \
  --spec studies/ic-2026-2027/experiments/exploratory/redesign-calibration-v1/spec.json \
  --output /private/tmp/ic-redesign-reproduction-new
```

Não sobrescrever `run-01`. O manifesto registra os papéis e intervalos das
sementes de P4; grupos, estados e fontes são funções determinísticas desses
valores. Todos os hashes de entrada e a separação entre fases do ledger foram
reconferidos após o lote. O ledger reutiliza sementes entre pontos de calibração
intencionalmente; nenhuma fase de calibração compartilha sementes com a checagem
primária. Arrays primários não foram conservados: reproduzir aqui significa
regenerar os mesmos gates, sem abrir os contrastes.

O [rascunho de pré-registro](../../../research/questions/exploration/2026-09-24-parallel/redesign-and-preregistration-draft.md)
explicita as hipóteses, limitações e condições antes de qualquer congelamento.
