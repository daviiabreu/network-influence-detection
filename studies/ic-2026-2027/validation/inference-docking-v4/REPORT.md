# Docking clean-room v4 — maquinaria de inferência e calibração

## Abstract (English)

We report a second clean-room docking study of the v4 detection-boundary
protocol (project commit 37513841). It covers the inference and calibration
machinery left out of the first study. An independent numpy implementation was
written from the specification documents alone (Phase 1, commit `de3457ce`).
It covers the profile solver, the acceptance tolerance, independent
validation with its retry, mean-shift nuisance propagation, the cluster
bootstrap, the band, gap and gate rules, and the Jeffreys stop rule. We then
fed identical synthetic inputs, adversarial ones included, to both
implementations, under a pre-declared protocol (commit `7382bfa9`). The
tolerance, validation, retry, projection, finite differences, nuisance draws,
V_nuis, bootstrap SE, allowances and the shared-seed stop-rule probability
agree to 1e-12 or better, most of them bitwise. All remaining discrepancies
are spec ambiguities. The largest is how the logit SE is evaluated inside the
max-t draws: it changes the critical value by up to 2.1×, and the project
reproduces frozen v1 exactly. We found no probable project mismatch
(category c).

## Escopo e disciplina

- A Fase 1 leu apenas os sete documentos autorizados, sem abrir `src/`,
  `tests/` nem scripts de experimento. O commit da Fase 1 é **`de3457ce`**
  (`docking_v4.py` e `test_docking_v4.py`, com 32 testes de invariantes, todos
  aprovados). As ambiguidades A01–A21 estão em `AMBIGUITIES.md`.
- A comparação foi pré-declarada em `comparison-predeclared.json`, commit
  `7382bfa9`, antes de qualquer execução. O harness é `compare_v4.py`, e o
  resultado integral está em `comparison-results.json`.
- `explain_v4.py` e `explain-results.json` são análises **post hoc**, não
  pré-declaradas. Servem apenas para atribuir causas às discrepâncias da banda
  e registrar os caminhos do solver em S09 e S21.
- Nada foi executado de `run_gate.py`, `run_curve.py`, estágios de gate ou
  tiers. Não se usou nenhum namespace de sementes do D10. As sementes do
  harness derivam de `ic-detection-boundary-v4-inference-docking-*`. A exceção
  é a semente 250925006, codificada no projeto para a regra de parada e
  compartilhada por definição do stream.
- Nenhum arquivo existente foi modificado.

## Resultados por componente

**1. Solver de perfil (22 casos).** O status coincide em 17 dos 22 casos:
raiz interior linear, não linear e íngreme; face inferior; η além do limite;
canto; perfil decrescente; L2 plano (ill-conditioned); NaN; orçamento
esgotado; anchor-exact e âncora com média zero mas não bytewise; família de um
parâmetro interior e no endpoint; pisos e tetos de tolerância. Nos casos
aceitos, θ difere em no máximo 3,9e-5, abaixo do critério de 1e-3. Os dois
lados satisfazem a tolerância em cada momento ajustado.

As cinco divergências são todas de categoria (a):

- **S05, S06 e S17.** O projeto rotula como `no-L1-root` o que a docking
  rotula `family-limit-*`. No projeto, os limites de família vêm do pré-teste
  de viabilidade em `fit_cell` (A03b).
- **S10, degraus discretos.** `numerical-limit` contra `ill-conditioned`
  (A05b). Os dois estados são "de implementação" para o G0.
- **S09, perfil em corcova.** O projeto aceita uma raiz interior genuína em
  η≈0,00835 após amostrar apenas η ≤ 0,01. A docking avalia η=0,8 cedo e
  detecta a não monotonicidade. O projeto documenta que a verificação não é
  um teorema sobre pontos não amostrados (A06b).
- **S21, raiz a 0,999·tol do endpoint.** O projeto rotula `interior`, porque
  chega à raiz exata por um passo. A docking rotula `boundary`, porque aceita
  o endpoint primeiro. Ambos são estados aceitos (A24).

Há uma nota de harness em S03: o critério pré-declarado "todo momento
ajustado" ignorou que, na face, apenas L1 precisa ser satisfeito. Os dois
lados falham igualmente em L2, como esperado.

As contagens de avaliações foram reportadas, não comparadas. Elas ficaram
dentro do orçamento, por exemplo 34 contra 23 na raiz não linear e 50 contra
41 nos degraus.

**2. Tolerância `min(5e-5, max(1e-6, 0.25·SE))`.** SE, tolerância e decisão
de aceitação são idênticos em todos os ajustes do componente 1 e nas sondas
com SE ∈ {0; 1e-7; 4e-6; 1e-5; 2e-4; 1e-3}, incluindo as duas quinas da
fórmula.

**3. Validação independente.** Nos 28 casos, `passed`, a equivalência
`|res|+2.2414·SE_val` e sua decisão frente a 0,0003 são idênticos. Os casos
incluem o limiar de 4σ a ±1e-9 relativo, NaN, SE zero, L2 enorme com um
momento só e a borda da equivalência. O |z| coincide exceto em 0/0 e NaN: o
projeto reporta 0 e inf, a docking reporta NaN, e a decisão não muda (A28).

O protocolo de retry coincide nos três cenários: falha e depois aprovação, com
M=1024→4096; duas falhas; e lacuna do solver sem retry. Houve um bug de
harness (categoria b, só no harness): o stub produzia SE=0 e foi corrigido.
Antes da correção os dois lados já falhavam igualmente.

**4. Propagação local.** O Δθ projetado de `project_shift` coincide em
2.500/2.500 casos, com diferença máxima de 1,1e-16 e as flags de projeção
idênticas. Os casos incluem faces η=0 e η=0,8 e φ próximo de 0 e de 0,999. As
diferenças finitas também coincidem nos passos 0,01 e 0,005, com o sentido
para dentro junto às faces superiores.

Em `nuisance_draws`, os índices vieram do stream documentado, e a docking
recebeu o discriminador do projeto (A12). Nessas condições, as 200 AUCs, os
deslocamentos, V_nuis, o deslocamento médio e a fração projetada (0 e 0,74)
são **bitwise iguais**, no interior e na face. O MCSE difere apenas pela
fórmula, em cerca de 5e-6 relativo (A27). Na âncora, V_nuis=0 e Δθ≡0 nos dois
lados.

Com inclinação de Schur não positiva, o projeto levanta erro e a docking
resolve. A leitura do projeto é a mais fiel ao texto (A26).

**5. Bootstrap de clusters.** O ponto, o SE_scores e
SE_total=√(SE²+V_nuis) coincidem a ≤1e-12 nos cenários ICC 0,5, empates
inteiros, escores constantes, separação perfeita e rede única.

No tamanho de produção (2.000 redes, B=400, 40 repetições), o SE médio foi
0,007729 nos dois lados, contra um DP de Monte Carlo de 0,007906. Isso está
dentro da margem de 15%, que tem incerteza de cerca de 11%.

**6. Banda, lacunas e gate.** O piso de 2,7729 é respeitado nos dois lados, e
o caso degenerado dá exatamente 2,7729. Em 10 casos aleatórios, o crítico e a
banda **diferem**, com o crítico variando até 2,1×.

A análise post hoc mostra que a diferença se explica **integralmente**, com
igualdade bitwise nos 10 casos, por três leituras. A primeira é o SE logit
avaliado em cada draw, e não o plug-in em p̂. É o fator dominante: no caso 4,
o crítico é 7,15 com plug-in e 3,37 no projeto. A segunda é a centragem das
réplicas no ponto. A terceira é o quantil `higher`.

O projeto reproduz exatamente o v1 congelado (`detection_boundary.py:136-168`),
e o D6 declara a regra "frozen, unchanged". A classificação é, portanto, (a):
o texto do v1 ("SE plug-in total é transportado aos draws") admite as duas
leituras, e o código congelado resolve a ambiguidade (A22, A23, A15b). Como o
efeito na largura é material, recomenda-se que a emenda explicite a leitura.

As regras de inversão, lacunas, censura e gate a=0 coincidem em 9 dos 11
casos. Os casos iguais incluem a lacuna antes do cruzamento, a lacuna no topo,
a lacuna em a=0, a falha do gate, a ausência de cruzamento, o empate exato em
0,70 (inclusivo), a banda não monótona e o cruzamento em a=0 com gate válido.

As duas divergências, C03 e C10, são a fronteira sustentada vizinha a uma
lacuna. O projeto censura e a docking declara o primeiro ponto acima da
lacuna. A leitura do projeto é mais conservadora e preferível: um valor
declarado acima de uma lacuna é só um limite superior. É categoria (a), pela
A18 da docking.

**7. Regra de parada e cotas.** A probabilidade preditiva de Jeffreys foi
comparada com semente compartilhada, 200.000 simulações, 0 a 6 lacunas em 54
ajustes e 7 ou 6 células. Ela é **bitwise igual** à da docking, porque a ordem
dos sorteios é a mesma. Ela também concorda com a integral determinística
(quadratura) dentro de 4 MCSE; por exemplo, com 0 lacunas, 0,845035 contra o
valor exato de 0,844254. Com 1 lacuna a probabilidade já é 0,445, e a regra
de 0,80 para antes do G2.

A decisão de parada, os parâmetros posteriores e a cota agregada
ceil(0,02·pipelines) coincidem. As cotas do G2 (5/100 por célula e 14 ou 12
no agregado, com 6 células) e do G2c (3/100 e 2/40) coincidem em todos os
padrões de borda. A mediana de estabilidade FD em [0,8; 1,25] coincide, exceto
no caso 0/0, em que o projeto usa razão 1 (A25).

## Achados categoria (c)

**Nenhum.** Todas as discrepâncias são (a), exceto dois defeitos do próprio
harness (b): o critério de S03 e o stub de retry.

## O que permanece não verificado

- o matching sobre painéis reais (`PanelSource`), o pré-teste de viabilidade
  `feasible_lag1` e a Jacobiana média de L3–L5 estimada em realizações reais;
- o caminho dos controles com `inherited_eta` em `nuisance_draws`;
- o diagnóstico de amplificação e o diagnóstico de covariância do G2;
- os limiares calibrados do G2 (razão de dispersão, bootstrap de 399) e a
  razão G2c além da contagem de falhas;
- G1b e G1c, o projetor `g0_statuses` que alimenta a regra de parada, o
  runner de curva, o scheduler, o selamento, as sementes e a auditoria de
  colisões;
- a eficiência do solver em alvos reais, porque as contagens de avaliações
  não foram comparadas;
- a cobertura estatística das duas leituras da banda. A do projeto é a que o
  G1b testa.
