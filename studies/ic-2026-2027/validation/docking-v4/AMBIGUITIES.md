# Registro de ambiguidades da especificação — docking v4 (Fase 1)

Escrito **antes** de abrir qualquer arquivo em `src/`, `tests/` ou
`experiments/*/*.py`. Fontes lidas (todas em `studies/ic-2026-2027/`):

- `research/questions/exploration/2026-09-24-parallel/detection-boundary-preregistration-frozen.md` (v1)
- `.../detection-boundary-amendment-v4.md` (v4.3)
- `.../amendment-v4-decision-spec.md` (D1–D11)
- `.../amendment-v4-1-revision.md` (R1–R8)
- `.../v4-review-decisions.md`, `.../v4-delta-review-decisions.md`
- `experiments/exploratory/detection-boundary-v4/README.md`
- `experiments/exploratory/detection-boundary-v1/README.md`, `.../validation.md`

Cada item: trecho da especificação, leituras possíveis, escolha adotada (marcada
`[Qn]` no código de `dockv4/`).

| # | Tema | Texto da spec | Leituras possíveis | Escolha do docking |
| --- | --- | --- | --- | --- |
| Q0 | Papel de A/C/D/E | v1 «Família nula e matching»: A, B, C, D, E são nulos sem interação | O pedido de docking chama A/C/D/E de «alternativas» | Seguir a spec: A–E são **nulos**; a única alternativa é o braço social com força a. |
| Q1 | N e coortes | «N=10.626 … 7.084 entradas em t=0, 3.542 em t=5 … arredondar N para divisibilidade por seis» | N=1.000 (pedido) não é divisível por 6 | Docking usa **N=1.002** (2/3 em t=0, 1/3 em t=5, domicílios de 2). Domicílios tardios = último terço por índice (pessoas trocáveis). O estado latente existe para todas as N pessoas desde t=0, inclusive antes da entrada e após a saída; a máscara só afeta a observação. |
| Q2 | Atrito | «retenção domiciliar anual 0,89, saída definitiva independente da opinião» | (i) sobrevivência Bernoulli 0,89 a cada onda após a entrada; (ii) retenção relativa à coorte inicial; não-resposta individual? | (i), por domicílio (as duas pessoas compartilham máscara), sem não-resposta individual, sem reentrada. Mesma regra para a coorte tardia. |
| Q3 | Transporte R_N | «R_N preserva postos e atribui quantis normais de variância 1» | (a) Φ⁻¹((j+0,5)/N) cru (variância ≈0,998 em N=1.002); (b) esses quantis reescalados para média 0 e variância 1 exatas; (c) outras posições (Blom) | **(b)**, com DP populacional (ddof=0), sobre toda a população N (não só respondentes). |
| Q4 | Onda 0 e passos | «Inicialização normal por postos, sem burn-in»; «uma etapa síncrona por onda» | Há passo antes da onda 0? | z₀=R_N(ε₀) é observado em t=0; 10 passos entre as 11 ondas (1 por onda, ou 24 na sensibilidade, observando só o fim). |
| Q5 | Direção da rede | «Oito permutações … oito entradas/saídas … cada pessoa recebe oito termos» | i ouve perm_k(i) ou perm_k⁻¹(i) | i ouve perm_k(i). Com permutações uniformes as duas leis são idênticas. Autoarestas mantidas (contribuem f(0)=0 à média de 8). |
| Q6 | Padronização de D | «Centralizar D e dividir pelo seu DP transversal» | DP com ddof 0 ou 1 | ddof=0 (fator √(N/(N−1)) de diferença). DP(D)=0 com a>0 levanta erro. |
| Q7 | Ordem dos sorteios | D2: «X_φ … mesmas sementes … coincidem pathwise» | Ordem dos normais no stream `state` | ε₀ e depois uma inovação N-vetorial por passo, idêntica entre social e X_φ. A rede usa o stream `network` e não é sorteada em a=0 (irrelevante para a lei). |
| Q8 | Discretização | «transportar postos dos respondentes para 0…10 equiprováveis com quantis (j+0,5)/n_t … usa a onda inteira» | «onda inteira» = todos os respondentes da onda vs toda a população | Respondentes da onda t; categoria = ⌊11·(j+0,5)/n_t⌋, j = posto base 0 entre respondentes. |
| Q9 | Família C | «erro maior no centro … 10% de heaping w=0 antes de discretizar; desempate independente. Ambos os braços da comparação C recebem marginal-alvo com 0,1 extra em 5» | (i) heaping por resposta observada vs por pessoa; (ii) o braço social na comparação C recebe erro heteroscedástico/heaping? | Heaping Bernoulli(0,10) independente por (pessoa, onda) no stream `heap`, aplicado a w depois do erro; desempate uniforme independente para todos os respondentes. Braço social na comparação C: canal principal homoscedástico, **sem** heaping, discretizado na marginal C (p₅=0,1+0,9/11; demais 0,9/11) pelo mesmo mapa de quantis. |
| Q10 | Normalização s(z) | «s(z)=1+2exp(−z²/2), normalizado por E[s²]=1» | Esperança sob N(0,1) analítica vs empírica por onda | Analítica: divide por √(1+4/√2+4/√3)=√6,1378; w=√r z+√(1−r) s̃(z) e. |
| Q11 | Momento L_k | «Lk é Pearson reunindo todos os pares válidos separados por k ondas dentro de cada painel» | (a) Pearson único dos pares empilhados (médias globais); (b) média de Pearsons por par de ondas; (c) centragem por onda | **(a)**, sobre o ordinal observado 0…10. |
| Q12 | LDA | «padronização no treino, covariância 0,8S+0,2I, entradas L3,L4,L5 … Escores maiores significam reorganização» | S = covariância intra-classe agrupada ou total; padronização com média/DP agrupados das duas classes; ddof | Média e DP (ddof=1) das duas classes de treino juntas; S = covariância intra-classe agrupada (ddof n−2) das variáveis padronizadas; w=(0,8S+0,2I)⁻¹(μ_social−μ_nulo). |
| Q13 | AUC | «AUC usa todos os pares de escores, meio crédito para empate» | — | Mann–Whitney com postos médios. Critério de detecção: AUC ≥ 0,70. |
| Q14 | Gerador | «SHA-256, primeiros oito bytes big-endian» — não diz qual RNG | PCG64, MT19937, Philox… | `numpy.random.default_rng(seed)` (PCG64). Streams por papel: `state` (ε, inovações, ε de D), `null-state` (T de B, s de E), `network`, `mask`, `error` (e, u/v de c), `heap` (heaping e desempate). Namespace `ic-detection-boundary-v4-docking-*`; namespaces confirmatórios recusados. |
| Q15 | Índices de treino/teste | «índice 2i+classe, rede floor(indice/(2×eventos_por_rede))» | Qual classe é 1 | Classe 1 = social, 0 = nulo. Fases `train` e `check`. |
| Q16 | B em t=0 | D2: «z_t = R_N(√λT+√(1−λ)x_t)» | Aplicar em t=0 ou z₀=x₀ | Aplicar em todas as ondas, inclusive t=0. Idem E (em t=0, z₀=x₀ trivialmente). |
| Q17 | D | «ρ(z)=ρ0+γ(1−ρ0)[1−exp(−z²/2)]; atualização R_N(ρ(z)z+√(1−ρ(z)²)ε)» | z antes ou depois do passo | ρ avaliado no z corrente (pré-passo), z₀=R_N(ε₀). |
| Q18 | Estilo persistente c | «e_it=√c u_i+√(1−c)v_it» | — | u por pessoa fixo nas ondas, no stream `error`. (Não usado na grade de comparação.) |
| Q19 | Matching | D4/R1/R2/item 11: solver de perfil, Illinois, 96 avaliações, validação 2.048 pares, retry | — | **Fora do escopo do docking estrito.** Implementei um perfil simples (Illinois interno em φ, externo em λ, tolerância R2, pares CRN com índice 2i+1 e rede própria) só para obter um θ comum aos dois códigos. Sem validação R1, retry, orçamento, estados de face além de boundary/limite superior. Supõe L2 crescente em λ para B. |
| Q20 | Médias/variâncias por onda | Pedido de docking | No ordinal observado são fixadas pelo transporte (≈5 e ≈10) | Relatadas assim mesmo; esperam-se diferenças nulas por construção. O teste informativo é n_t (geometria). |
| Q21 | Ambiente | `.python-version` = 3.12.13 | Não disponível no container | Python 3.12.3 do sistema com `uv sync --frozen --python /usr/bin/python3.12`; numpy 2.5.3 do lock. scipy não está no lock: a implementação usa só numpy + `statistics.NormalDist`; os testes estatísticos da Fase 2 usam um venv separado com scipy. |

Não implementado (fora do escopo pedido): D5 (nuisance), bootstrap/bandas, controles
latente/ordinal r=1/latent_rank, mobilidade, δ, ancoragem ω.
