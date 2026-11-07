# Checagem da confiabilidade externa r=0,70

24/09/2026. Executada uma vez no commit `7fc90af`, conforme o
[protocolo anterior ao lote](protocol.md) e a
[decisão 13](../../../research/questions/exploration/2026-09-24-parallel/decision-13-amendment.md).
O dossiê foi copiado byte a byte com SHA-256 conferido. Não houve novo ajuste
de confiabilidade, força ou persistência pelo resultado.

O baseline usado para escolher o ponto de operação continua r=0,80. Logo,
a=0,4 e rho=0,838961863215152 são mantidos sem repetir a busca. O lote testa
apenas se a correção externa do primário para r=0,70 preserva uma célula não
degenerada. São 96 painéis/classe para treino e 96/classe para checagem, com
sementes novas do namespace de desenvolvimento, índices 10000–10191.

Resultado: gate grosseiro `0,55 < BA < 0,95` passou. Não é intervalo de
confiança nem confirmação. Não se exportaram BA, acertos, escores ou diferenças
entre confiabilidades. Diferença absoluta de lag 1 ordinal=0,002659 e variação
total marginal agregada=0,001192; esses são diagnósticos de matching, não o
contraste primário. Média de 52.114,844 pares anuais sintéticos observados.

Custo total do lote: **20,366 s**, **384 trajetórias**, abaixo dos 600 segundos
autorizados. Uma única execução, nenhuma busca posterior. P4 e o braço secundário
ancorado não foram simulados. Os pilotos anteriores são preservados como
históricos, inclusive a checagem a r=0,65.

## Evidência

- [Manifesto](run-01/manifest.json): revisão, ambiente, comando, hashes e auditoria
  de sementes; 1.920 sementes novas, interseção zero com 3.328 anteriores e
  31.002 reservadas para confirmação. Derivar inteiros não executa confirmatórios.
- [Resumo](run-01/summary.json): tempo, contagem e gate; zero confirmatórios e
  nenhum contraste primário numérico exportado.
- [Ledger](run-01/panel-ledger.jsonl): 384 registros com parâmetros, sementes e
  hashes de trajetórias/respostas; sem escores de classificação.
- [Progresso](run-01/progress.jsonl): gate autorizado, sem estimativa de BA.

Todos os hashes de entrada foram reconferidos após a execução. O script é um
caller exploratório de `CalibrationRun`, `fit_discriminant` e `panel_gate`;
nenhuma lógica científica reutilizável foi duplicada fora de src. Ruff e mypy
estrito do caller passaram, assim como oito testes focados dos módulos reusados
(0,11 s) e a estrutura 7/7. Nenhum arquivo de workbench foi editado; a matriz
geral anterior continua sem resultado final verificado e não foi duplicada.

Comando executado da raiz:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache-codex7 uv run --project studies/ic-2026-2027 \
  python studies/ic-2026-2027/experiments/exploratory/reliability-correction-v1/check_reliability.py \
  --output studies/ic-2026-2027/experiments/exploratory/reliability-correction-v1/run-01
```

O diretório já existe e não pode ser sobrescrito. Uma reprodução deve indicar
outra saída e respeitar autorização/orçamento próprios; não é necessária para
adotar os gates já registrados. O [rascunho atualizado](../../../research/questions/exploration/2026-09-24-parallel/redesign-and-preregistration-draft.md)
continua anterior ao congelamento. A grade completa de r e o contínuo ancorado
são planos, não resultados executados neste lote.
