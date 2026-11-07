# Evidência exploratória da proposta A

25/09/2026. Não adotada; nenhuma execução confirmatória. A
[proposta](../../../research/questions/exploration/2026-09-24-parallel/amendment-proposal-a.md)
contém interpretação, limitações, exposição e gate futuro. O
[sumário](summary.json) contém resultados, prefixos sem seleção por sucesso e
hashes dos outputs privados. A [projeção](compute-projection.json) é uma conta
de capacidade, não um benchmark da matriz inteira.

## Proveniência e execução

Diretório bruto:
`/Users/davi/.local/state/research-workbench/amendment-a-20260925/`.
Namespace exclusivo `ic-detection-boundary-amendment-a-20260925-calibration`.
Geometria N=10.626, onze ondas, retenção 0,89, r=0,70, dois eventos/rede em
treino e referência. Python 3.12.13, NumPy 2.5.3, macOS 27.0 arm64.
`OPENBLAS_NUM_THREADS=1`, `VECLIB_MAXIMUM_THREADS=1`,
`UV_CACHE_DIR=/private/tmp/uv-cache-cov2`.

O sweep estrito foi iniciado em `719a83c` (protótipo científico em `3bc4765`).
Seu driver antigo gravou HEAD ao final da etapa, `505e37f`; esse campo isolado
não é a revisão de início. A nota no sumário preserva e explica a discrepância.
Mapa e refits usam as funções de `be62f39`, com driver/fila de `d722690`.
As adições posteriores não alteram os caminhos científicos congelados.

Planos cronológicos preservados: [inicial](plan.json),
[reinício e tolerância](refit-plan-successor.json),
[alocação por custo](budget-plan-successor.json) e
[derivada independente](matching-map-plan.json). Nenhuma revisão selecionou
força/r/alvo por AUC. O probe adicional a=0,03, bloco 9003, foi feito depois
dos primeiros AUCs para medir o custo da segunda célula já prevista; essa
exposição está declarada na proposta.

Receitas de reprodução, sempre em **diretório novo**; não executar todas estas
etapas sem um supervisor de tempo. O uso de arquivos exclusivos (`open("x")`)
protege os outputs existentes. Comandos a partir da raiz do repositório:

```sh
export UV_CACHE_DIR=/private/tmp/uv-cache-cov2
export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
uv run --project studies/ic-2026-2027 --locked python \
  studies/ic-2026-2027/experiments/exploratory/amendment-a-calibration/run.py \
  --output /private/tmp/amendment-a-new-run --stage matching
```

Depois, executar `matching_map.py --output ...` e as etapas `reference`, `zero`
e `refits` do mesmo driver, nessa ordem; o mapa pode ser preparado junto das
duas referências sociais (seis + dois workers ativos). Executar
`diagnostics.py --output ... --mode zero` após `zero`; o modo `mechanics` não
depende dos painéis. O modo `refits` inclui stencils opcionais depois dos 40
refits primários; `local_probe.py --aggregate-only` só funciona se todos os
stencils e baselines exigidos estiverem completos. Não estão completos nesta
entrega. O probe adicional chamou `refit_job(0.03, 9003, output)` do driver.

O supervisor local executou processos em grupos próprios e interrompeu o grupo
de refits no prazo absoluto de 3.550 s desde o início do sweep. Resultado:
40 refits completos em a=0,10, um probe separado em a=0,03, teste nulo grande,
teste da banda e 48 ajustes do sweep; a fila regular de a=0,03 e os stencils
opcionais foram interrompidos. Não completar prefixos com sucessos selecionados
nem registrar os trabalhos interrompidos como falhas de matching.

Em a=0,10, bloco 1 também forneceu o ponto inicial do mapa. O sumário mostra
prefixos brutos 10/20/40 como descrições e prefixos independentes condicionais
ao mapa a partir do bloco 2. Logo, há 39 refits independentes desse
**desenvolvimento**, não 40. A Jacobiana usa outro bloco, 9001.

Para regenerar somente a projeção dos resultados, sem novas simulações:

```sh
uv run --project studies/ic-2026-2027 --locked python \
  studies/ic-2026-2027/experiments/exploratory/amendment-a-calibration/summarize.py \
  --raw /Users/davi/.local/state/research-workbench/amendment-a-20260925 \
  --output /private/tmp/amendment-a-summary-replayed.json
```

## Verificação

TDD nos comportamentos novos: igualdade pathwise, transporte otimizado com
N completo, sementes/fases, matching constrangido, reinício, refit por mapa,
EP agrupado com empates, banda/endpoints e propagação de nuisance. Os testes de
N=10.626 comparam painéis e perfis com o código congelado.

- Estudo: 188 testes passaram, incluindo 14 novos; Ruff e mypy passaram.
- Workbench: estrutura/lint/tipos passaram no `just quality`; o conjunto de
  testes foi interrompido após 1.210 passarem, em
  `tests/recovery/test_focused_attempts_backup.py`, 38 min 37 s. A matriz completa
  não passou; não houve modificação de implementação do workbench.
- Builds e wheel smokes dos dois projetos passaram, executados separadamente.
- `scripts/check_repository.py`: sete checks passaram, usando
  `UV_CACHE_DIR=/private/tmp/uv-cache-cov2`.
- Auditoria: 1.673.642 materiais de sementes de calibração, zero colisões.
- Pré-registro congelado: SHA-256
  `fb6b4dcf43161a52c725e565bf2a4d2697423bec7d138ad1d30388547cfcd706`, inalterado.
- Fora do módulo novo, `git diff 1d3c674 -- studies/ic-2026-2027/src` está vazio.
  As únicas mudanças em testes antigos são tipagem e assinatura de fixtures;
  não se removeram testes ou asserções.

Nenhum desses checks é aprovação científica, nem valida o bootstrap local
no regime novo de matching mais estrito. A proposta registra expressamente que
o orçamento de 72 h para todo o escopo congelado não foi demonstrado.

Outputs brutos: diretório 0700, arquivos 0600. Manifesto `manifest.sha256`
verificado integralmente; SHA-256 do manifesto:
`4a0c6ac2ad97569c1a598d751a5f5b4b7643de0d1f1a5bdb64f929140324b9bf`.
O sumário versionado contém os hashes de todos os 121 arquivos, incluindo
proveniência e cópia do supervisor executado.
