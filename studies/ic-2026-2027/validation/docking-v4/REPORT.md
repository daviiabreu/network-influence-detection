# Docking v4 — implementação independente vs implementação do projeto

27/09/2026. Evidência de **validação técnica** apenas. Não altera o plano de análise
congelado, não executa gate (G0–G2c), `run_gate.py`, `run_curve.py` nem tier
confirmatório e não usa namespaces reservados (D10). Revisão do projeto
auditada: `37513841` («Freeze v4 gate inputs»).

## Abstract (English, appendix)

We docked an independent ("clean-room") implementation of the v4 detection-boundary
simulation against the project code. The clean-room code was written only from the
frozen protocol, the v4 amendment, the D1–D11 specification, the R1–R8 revision and
the review decisions, and was committed (fe32097d) with a 22-item ambiguity log
before any project source was read. The comparison plan was also committed before
it ran (09819848). At the seed level, latent trajectories were bitwise identical
for the social arm (a = 0, 0.03, 0.30) and for null families A, B, D and E, and so
were the ordinal discretisers. At the law level (N = 1,002, 11 waves, 25 cells,
1,000 panels per implementation), all 150 TOST endpoints were equivalent within
0.20 SD, and none of 2,334 Holm-corrected difference tests rejected. LDA AUCs
agreed within 0.002 on average. The two LDA implementations differed by ≤ 9·10⁻⁵
on identical features. We found no code–specification mismatch. Matching, nuisance
propagation, bootstrap bands and gates were not docked.

## 1. Método

1. **Fase 1 (sala limpa).** Li apenas os nove documentos autorizados e escrevi
   `dockv4/` (numpy + `statistics.NormalDist`; scipy não está no lock do estudo):
   - geometria e máscara;
   - R_N;
   - braço social (bounded confidence com repulsão b=0,25, 8 permutações, ρ=0,85);
   - nulos A/B/C/D/E da lei v4 (D2);
   - canal w=√r z+√(1−r)e, transporte ordinal 0…10 e marginal/erro/heaping de C;
   - estilo c e 24 etapas;
   - L_k agrupado, LDA 0,8S+0,2I em L3–L5 e AUC com meio crédito;
   - um matcher de perfil simplificado.

   Há 16 testes de invariantes em `tests/`, entre eles:
   - a=0 ≡ A pathwise e AUC≈0,5;
   - Var(√r z)/Var(w)=r;
   - E[s̃²]=1;
   - geometria 7.084/3.542 e retenção 0,89;
   - AUC de distribuições iguais ≈0,5.

   **Commit da Fase 1: `fe32097d`**, que inclui `AMBIGUITIES.md`.
2. **Pré-declaração.** O arquivo `comparison-predeclared.json` fixa a grade, os
   resumos, os testes, a família Holm e as margens TOST antes de qualquer
   comparação (commit `09819848`).

   *Divulgação:* antes desse commit, uma sonda de tempo gerou 50 painéis do
   projeto em duas células e imprimiu médias L1–L5. Nenhuma margem ou célula foi
   escolhida a partir dela; as margens são genéricas.
3. **Fase 2.** O código do projeto foi dirigido por
   `compare/project_adapter.py`. Uma subclasse de `SeedPlan` usa o namespace
   `ic-detection-boundary-v4-docking-project`.

   Um «espelho» chama as funções públicas (`influence`, `null`, `panel_mask`,
   `measurement`, `ordinal_channel`) na mesma ordem que
   `PanelSource._profiles`. Ele reproduz os L1–L5 de produção **byte a byte**
   em 25/25 células (`results/partB-mirror-check.json`).

   As partes da comparação:
   - **A:** nível de semente.
   - **B:** nível de lei.
   - **C:** discriminador.

Parâmetros da comparação:

- N=1.002 (1.000 não é divisível por 6); 11 ondas.
- Parte B: 1.000 painéis por implementação e célula.
- Parte C: 50 réplicas por célula e implementação, com 100 redes × 2 eventos de
  treino e 250 × 2 de teste por classe (produção: 1.000/2.000 redes, N=10.626).
- O θ nulo das células C2/C3 foi ajustado uma vez pelo matcher do docking
  (M=256) e usado pelas duas implementações:
  - C2: φ=0,8436, λ=0,3392;
  - C3: φ=0,8566, λ=0,0507.

Ambiente:

- Python 3.12.3: o 3.12.13 fixado não está disponível no container.
- `uv sync --frozen`, numpy 2.5.3 e BLAS de uma thread.
- Os testes estatísticos usam scipy num venv separado.

Custo de parede das partes: A 1 s, B 112 s, C 440 s.

## 2. Registro de ambiguidades (resumo; completo em `AMBIGUITIES.md`)

| # | Ponto | Leitura adotada | Leitura do projeto (Fase 2) |
| --- | --- | --- | --- |
| Q0 | A/C/D/E | nulos, não alternativas | idem |
| Q1 | N, coortes | N=1.002; latente de todos desde t=0 | idem (`panel_mask`, `influence` em N) |
| Q2 | atrito | Bernoulli 0,89 por domicílio, saída definitiva | idem |
| Q3 | R_N | quantis (j+0,5)/N padronizados | idem (`grid /= grid.std()`) |
| Q5–Q7 | rede, DP(D), ordem dos sorteios | i ouve perm_k(i); ddof=0; ε₀ e depois inovações | idem (bitwise) |
| Q8 | discretização | ⌊11(j+0,5)/n_t⌋ entre respondentes | idem (bitwise) |
| Q9 | C | heaping por resposta; braço social só recebe a marginal C | idem |
| Q10 | s(z) | normalização analítica sob N(0,1) | **empírica no painel** (diferença relativa 1,6·10⁻⁴) |
| Q11 | L_k | Pearson dos pares empilhados | idem |
| Q12 | LDA | DP de padronização com ddof=1 | **ddof=0** |
| Q14 | RNG | PCG64 `default_rng` | idem |
| Q16–Q17 | B em t=0; ρ(z) de D | transformar em todas as ondas; z pré-passo | idem |
| Q19 | matching | perfil simplificado, sem validação R1 | não docado |

## 3. Resultados

### Parte A — nível de semente (`results/partA-seed-level.json`, `posthoc-channel.json`)

| Caso (20 sementes cada) | Latente bitwise igual | max \|Δz\| |
| --- | ---: | ---: |
| social a=0 / 0,03 / 0,30 | 20/20 cada | 0 |
| A (φ=0,85), B (0,80; 0,30), D (0,80; 0,50), E (0,80; 0,30) | 20/20 cada | 0 |

Outras verificações de nível de semente:

- **Função L_k** sobre painéis observados do projeto: máx. |Δ| = 2,8·10⁻¹⁵
  (critério ≤ 10⁻¹²).
- **Pós-hoc, não pré-declarada:** dado o mesmo w e a mesma máscara, os
  discretizadores são idênticos byte a byte em 20/20 casos, tanto na marginal
  equiprovável quanto na marginal C sem heaping. A primeira onda observada
  coincide com a geometria da spec em 20/20.

### Parte B — nível de lei (25 células × 1.000 painéis × 2 implementações)

Primário: TOST com margem de 0,20 DP por painel, α=0,05, interseção-união.
**150/150 endpoints equivalentes.**

| Endpoint | máx. \|d\| entre 25 células | d médio | maior p_TOST | margem absoluta mediana |
| --- | ---: | ---: | ---: | ---: |
| L1 | 0,095 | 0,012 | 0,0096 | 0,0024 |
| L2 | 0,112 | 0,020 | 0,025 | 0,0030 |
| L3 | 0,081 | 0,021 | 0,0040 | 0,0037 |
| L4 | 0,088 | 0,044 | 0,0060 | 0,0044 |
| L5 | 0,068 | 0,021 | 0,0016 | 0,0052 |
| Σ n_obs | 0,012 | 0,011 | 1,4·10⁻⁵ | ≈29 respondentes |

Secundário: 2.334 testes na mesma família Holm (inclui a Parte C).

- Tipos de teste:
  - Welch em 98 resumos por célula: n_t, média e variância por onda, L1–L10 e as
    55 correlações entre ondas;
  - KS em L1/L3/L5;
  - Brown–Forsythe em L1–L5.
- **Nenhuma rejeição após Holm.**
  - Menor p bruto: 0,0014 (Brown–Forsythe, L5, célula B r=0,9, razão de
    variâncias 0,80; p_Holm=1).
  - Máx. \|d\| em qualquer Welch: 0,13.
  - Estatística KS entre 0,020 e 0,065.
  - Razões de variância de L1–L5 entre 0,80 e 1,20.
- **Matriz de correlação entre ondas:** máx. \|Δ média\| por célula ≤ 0,0061;
  norma de Frobenius ≤ 0,024 (`partB-wave-corr.csv`).
- **Médias e variâncias por onda** do ordinal são fixadas pelo transporte (Q20) e
  não são informativas.

Nota de dependência: dentro de cada implementação, as células compartilham
sementes (CRN entre a, r e famílias). Por isso o sinal comum das diferenças
(social d≈+0,05…0,09; nulos d≈−0,03…0) é **um** sorteio, não 25 evidências.
Holm é válido sob essa dependência. Como a Parte A mostra identidade pathwise
do latente e do canal, uma diferença de lei só poderia vir da ordem de consumo
dos sorteios de máscara/erro, cuja lei é a mesma.

### Parte C — discriminador (50 réplicas por célula e implementação)

| Célula | Nulo | AUC média docking | AUC média projeto | DP (d / p) | Δ | p_TOST(0,02) | fração ≥0,70 (d / p) |
| --- | --- | ---: | ---: | --- | ---: | ---: | --- |
| C1 a=0, r=0,7 | A φ=0,85 | 0,4997 | 0,4978 | 0,019 / 0,018 | +0,0020 | 1,6·10⁻⁶ | 0 / 0 |
| C2 a=0,30, r=0,7 | B ajustado | 0,6771 | 0,6771 | 0,017 / 0,020 | +0,0001 | 3,8·10⁻⁷ | 0,10 / 0,10 |
| C3 a=0,03, r=0,5 | B ajustado | 0,5060 | 0,5072 | 0,020 / 0,019 | −0,0012 | 2,7·10⁻⁶ | 0 / 0 |

- Welch, KS e Brown–Forsythe sobre as AUCs não rejeitam após Holm.
- Com as **mesmas** matrizes de atributos, as duas LDA+AUC diferem no máximo
  8,8·10⁻⁵ (critério ≤ 10⁻³). A diferença vem do ddof da padronização (Q12).
- Os valores absolutos de AUC usam tamanhos reduzidos e **não** são estimativas
  do estimando do estudo, nem do a*(r).

## 4. Discrepâncias classificadas

| # | Discrepância | Classe | Detalhe |
| --- | --- | --- | --- |
| 1 | DP de padronização da LDA | (a) ambiguidade | Spec: «padronização no treino». Projeto: `features.std(axis=0)`, ddof=0 (`src/ic_study/analysis/redesign.py:73`). Docking: ddof=1. Efeito: \|ΔAUC\| ≤ 8,8·10⁻⁵ com atributos idênticos. As duas leituras são defensáveis; vale fixar uma no texto. |
| 2 | Normalização de s(z) em C | (a) ambiguidade | Spec: «normalizado por E[s²]=1». Projeto: média empírica de s² sobre todo o painel latente, incluindo não respondentes (`src/ic_study/models/detection_panel.py:110-111`). Docking: esperança analítica sob N(0,1). Diferença relativa −1,6·10⁻⁴ em N=1.002, determinística porque o latente é sempre a grade normal. Sem efeito detectável. |
| 3 | N=1.000 pedido | (a) | Incompatível com a geometria (divisibilidade por 6); usado N=1.002. |
| 4 | «Alternativas A, C, D, E» no pedido | (a) | Na spec, A–E são nulos. Docking e projeto concordam. |
| — | Bugs do docking | (b) | Nenhum encontrado pela comparação. Só houve correções de lint antes do commit da Fase 1. |
| — | Divergência código–spec | (c) | **Nenhuma** no escopo docado. |

**Achado de ambiente (fora das classes a–c).** Nesta máquina (Linux x86-64,
Python 3.12.3, numpy 2.5.3 do lock), 538 testes do estudo passam e 3 falham. As
mesmas 3 falhas se reproduzem num worktree limpo de `37513841`, portanto não
vêm deste docking:

- `tests/unit/test_detection_panel.py::test_zero_share_panel_keeps_frozen_calibration_bytes`
  (N=600 e N=10.626). O hash de bytes difere dos valores registrados na emenda
  (`4df30491…`, `0bd67064…`).
- `tests/unit/test_v42_solver.py::test_inner_updates_slope_when_trait_weight_attenuates_phi_derivative`.

Hipótese não verificada: os hashes foram gerados em macOS (caminhos
`/private/tmp`) e a aritmética de ponto flutuante difere entre plataformas.
Isso importa para o plano de shards «em outros hosts com equivalência
numérica» (D9/R8): a igualdade byte a byte não é portátil entre plataformas.
Sugere-se investigar antes de qualquer shard fora do host original. Não
corrigi nada.

Também li, sem docking estatístico, `validate_fit` e a tolerância do solver
(`src/ic_study/analysis/detection_boundary_v4.py:87,393-420`). Coincidem com o
texto de R1 (4·√(EP_fit²+EP_val²), 2.048 pares) e de R2
(min(5e-5, max(1e-6, 0,25 EP))). A leitura foi pontual, não uma auditoria do
solver.

## 5. O que o docking **não** cobre

- **Erro de modo comum.** A identidade bitwise mostra que as duas implementações
  fizeram as mesmas escolhas onde a spec é ambígua (Q3, Q5–Q9, Q11, Q14, Q16–Q17).
  Isso confirma que o código implementa a leitura natural do texto. Não protege
  contra um erro da própria especificação, nem contra uma leitura equivocada
  compartilhada por quem escreveu o código e por mim.
- **Fora do escopo:**
  - matching completo (D4/R1/R2/item 11: perfil com Illinois, orçamento 96,
    estados, validação com 2.048 pares, retry M=4.096);
  - propagação D5 e Jacobianas;
  - bootstrap de clusters, bandas logit, max-t e inversão;
  - gates G0–G2c, sementes e selamento;
  - controles latente/ordinal_one/latent_rank e mobilidade;
  - sensibilidades δ, ω, b=0 e 24 etapas (implementadas em parte, não
    comparadas);
  - regra de elegibilidade de L1;
  - N=10.626 e tamanhos de produção.
- **Resolução.**
  - No nível de lei, a comparação exclui diferenças ≥0,20 DP por painel
    (≈0,002–0,005 em unidades de L_k). Essa resolução é muito mais grossa que a
    tolerância de matching da spec (5·10⁻⁵).
  - Abaixo disso, a garantia vem só da identidade pathwise (latente,
    discretizador e L_k), que não cobre o heaping de C nem a máscara com as
    mesmas sementes: nesses dois, a ordem de consumo dos sorteios difere, e a
    concordância é só de lei.
- **Precisão da AUC.** A Parte C tem 50 réplicas com tamanhos reduzidos. A margem
  de 0,02 não diz nada sobre a precisão confirmatória.

## 6. Reprodução

A partir de `studies/ic-2026-2027`:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
.venv/bin/python -m pytest -q validation/docking-v4/tests
for p in A B C; do
  .venv/bin/python validation/docking-v4/compare/run_all.py --part $p \
    --raw RAW_DIR --out validation/docking-v4/results
done
.venv/bin/python validation/docking-v4/compare/posthoc_channel.py
PY_COM_SCIPY validation/docking-v4/compare/analyze.py \
  --raw RAW_DIR --out validation/docking-v4/results
```

Os arrays por painel ficam em `RAW_DIR`, fora do Git. Em `results/` ficam só
CSV/JSON pequenos (380 KB). O veredito agregado está em `results/verdict.json`.
