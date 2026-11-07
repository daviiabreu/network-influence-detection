# Dossiê de novidade e posicionamento — a*(r)

Data: 27/09/2026. Analista: Claude (sessão remota). Escopo: posicionar a
pergunta do pré-registro congelado v4 frente à literatura, para um artigo em
JCSS (alternativa: JASSS). Este dossiê não altera o protocolo, não executa
simulações e não afirma prioridade. As consultas da busca foram declaradas e
versionadas antes da execução (commit `987acded`, reconstrução local do
`9ae16947` do sandbox; seção "Consultas pré-declaradas" abaixo, mantida sem
alteração).

## Pergunta posicionada

Sob o protocolo v4 congelado
(`../../questions/exploration/2026-09-24-parallel/detection-boundary-preregistration-frozen.md`):
qual a menor força nominal de influência a*(r), numa grade fixa
G={0; 0,001; …; 0,90}, com que painéis sintéticos gerados com influência
(confiança limitada com repulsão, rede dirigida fixa, sem exposição
observada) atingem AUC ≥ 0,70 contra nulos sem influência — traço+AR (B,
confirmatório), AR (A), erro/heaping (C), persistência dependente do estado
(D) e mover–stayer (E) —, em função da confiabilidade de resposta
r ∈ {0,50; …; 0,90}? O painel tem 11 ondas no formato do SHP (10.626
pessoas simuladas, aproximação declarada das 10.627 de Gestefeld–Lorenz). O
discriminador é uma LDA fixa sobre as autocorrelações L3–L5, com L1/L2
pareados, e a unidade da AUC é o painel inteiro. O próprio protocolo declara
três limites. A AUC dessa LDA é limite inferior da AUC Bayes-ótima. Não
atingir o alvo não prova indistinguibilidade. E, sem rede observada, não se
identifica influência causal (Manski 1993).

## Como ler a matriz

- **verified-fulltext**: a citação foi conferida no texto bruto baixado nesta
  sessão (HTML ou PDF convertido), no localizador indicado. Quando o texto é
  preprint ou manuscrito do autor, isso está dito.
- **abstract-only**: só havia resumo, metadados Crossref ou material do
  autor diferente do artigo. A linha não sustenta afirmações além do
  resumo.
- Páginas de editora da SAGE e da Taylor & Francis devolveram HTTP 403
  nesta sessão, inclusive nos links de mineração de texto do Crossref.
  Quando há versão aberta do autor ou de repositório institucional, ela está
  identificada na linha.
- As diferenças em relação a a*(r) são leitura do analista, não afirmações
  dos autores.

## Resumo da matriz

| # | Antecedente | Influência entre pessoas | Erro/confiabilidade modelado | Nulo sem influência / persistência | Limiar ou fronteira estimado | Painel individual ≥ 3 ondas | Leitura |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | CoDiNG v3 (Nurek et al.) | sim (Naming Game) | não (limiar determinístico de verbalização) | sim: Keep, aleatórios, maioria | não | sim (6 surveys, NetSense) | verified-fulltext |
| 2 | Mulder 2023 | não (cross-lag intra-pessoa) | sim (confiabilidade do indicador, STARTS) | nulo = coeficiente zero | poder por N/ondas, não fronteira de força | sim (sintético) | abstract-only |
| 3 | Dang–Ma 2026 | não | sim (0,60/0,70/0,80) | coeficiente zero | poder por célula; sem força mínima | sim (3–5 ondas) | verified-fulltext (preprint) |
| 4 | Lersch 2023 | não | discutido; não é o fator variado no texto principal | estabilidade vs. mudança persistente | não (simulação sobre nº de ondas no suplemento) | sim (6 painéis, inclui SHP) | verified-fulltext (artigo); suplemento não relido |
| 5 | Moor-Smith–Carpentras 2026 | sim (Deffuant, HK, ED, Duggins) | ruído gaussiano no processo, não canal de resposta | sim: nulo "sem mudança" | sim, qualitativo: deriva mínima para superar o nulo; ruído a partir do qual falha | não (distribuições transversais ESS) | verified-fulltext (preprint) |
| 6 | Gestefeld–Lorenz 2023 | sim (modelo de Lorenz et al. 2021) | não (ponto médio discutido e negligenciado) | não; R² contra binomial | não | sim (transições SHP 1999–2009) | verified-fulltext |
| 7 | Gelastopoulos–Sage–van de Rijt 2025 | não (reforço intra-individual) | não | heterogeneidade (traço) vs. reforço | resultado de equivalência genérica, não limiar | teórico + PSID | verified-fulltext |
| 8 | Stadtfeld–Snijders–Steglich–van Duijn 2020 | sim (SAOM, rede observada) | não | coeficiente de influência zero | poder por N/ondas/efeito | sim (2–5 ondas) | verified-fulltext (versão depositada pelo autor) |
| 9 | Ureña-Carrion–Peixoto–Iñiguez 2026 | sim (contágio binário) | não; variantes "ruidosas" com componente independente | sim: modelo independente entre candidatos | sim: detectabilidade assintótica por região de parâmetros | séries completas de estados, rede conhecida | verified-fulltext (preprint) |
| 10 | Kiley–Vaisey 2020 | não | discutido (confundido com mudança não persistente) | disposições estáveis vs. atualização ativa | não | sim (3 ondas GSS) | verified-fulltext (manuscrito do autor) |
| 11 | Lucas 2023 | não | traço/estado/erro em simulação | CLPM vs. modelos com traço | não | sim | abstract-only |
| 12 | Carpentras–Quayle 2023 | sim (Deffuant, Duggins) | distorção monotônica de escala | não | não | não | verified-fulltext |
| 13 | Hill–Kriesi 2001 | não | modelo de erro de medida contrastado | mistura de grupos estáveis/instáveis/mudança | não | sim (4 ondas, painel suíço) | abstract-only |
| 14 | Borile et al. 2026 | sim (BCM) | não (interações assumidas observáveis) | não | identificabilidade de parâmetros | não (sequência de interações) | verified-fulltext (preprint) |
| 15 | Lenti–Monti–De Francisci Morales 2024 | sim (BCM) | proxies binários ruidosos | não | não (recuperação de parâmetros) | interações observadas | verified-fulltext (preprint) |
| 16 | Tang–Snijders–Flache 2025 | sim (SAOM, rede observada) | não | outros mecanismos no mesmo SAOM | não | 2 ondas, 46 turmas | verified-fulltext |
| 17 | Carpentras–Quayle 2022 (Physica A) | sim (Deffuant) | sim: ruído, binning, distorção | não | não (erro de previsão por nível de erro) | não | verified-fulltext (preprint) |
| 18 | Xu–Frank 2021 (Network Science) | sim (modelos de influência em rede observada) | sim, mas erro/viés na observação da rede, não na resposta | não | não (análise de sensibilidade de inferências) | não informado no resumo | abstract-only |
| 19 | Advani–Malde 2018 (J. Econ. Surveys) | sim (efeitos sociais lineares) | sim, dados faltantes/erro na medida da rede | não | não (revisão de identificação) | não se aplica (revisão) | abstract-only |

Contagem: 14 linhas com citação conferida em texto integral (5 delas em
preprint ou manuscrito do autor) e 5 somente em resumo (Mulder, Lucas,
Hill–Kriesi, Xu–Frank, Advani–Malde). As linhas 17–19 vieram da busca da
tarefa 2 (Semantic Scholar, Q01 e Q05). Das nove linhas pedidas nominalmente, 8 são verified-fulltext e
1 é abstract-only (Mulder).

## Matriz detalhada

### 1. CoDiNG v3 — Nurek, Kołaczek, Michalski, Szymański e Lizardo

arXiv:2406.19204v3 (página de resumo: v3; primeira versão 27/06/2024). Lido: HTML v3, §§1, 5.1–5.3, 6.1–6.2, 7.

- **Estimando**: desempenho preditivo de um modelo de opinião com estado
  latente contínuo e verbalização discreta. As métricas são F1 macro, F1 de
  mudança e JSD de distribuições e de trajetórias, nas surveys 5 e 6.
- **Dados/simulação**: dados empíricos do NetSense (2011–2013), com eventos
  de comunicação observados e surveys semestrais de estudantes, em seis
  temas. Ajuste nas surveys 1–4 e teste nas 5–6.
- **Erro de medida**: não há canal de erro de resposta com confiabilidade.
  A passagem do latente ao discreto é um limiar determinístico (§4.1). As
  respostas são recodificadas para três estados (§5.1).
- **Nulos**: "keeping the same opinion, changing to the majority opinion,
  random change with uniform probability, and random change with probability
  proportional to the initial opinion distribution" (§5.2).
- **Discriminador/teste**: Wilcoxon unilateral de postos sinalizados sobre
  métricas por corrida, com correção de Benjamini–Hochberg (§5.3).
- **Limiar/fronteira**: não estima.
- **Geometria**: seis surveys semestrais. A comunicação é observada.
- **Diferença para a*(r)**: CoDiNG compara um modelo com influência contra
  nulos triviais em dados individuais reais, mas não varia a confiabilidade,
  não tem nulos traço+AR nem mover–stayer calibrados a momentos e não estima
  uma força mínima. Os nulos "Keep" e "random-empirical" são precedentes
  diretos da lógica de comparar com persistência. O próprio texto já relata o
  achado de que modelos raramente vencem nulos triviais.
- Citações (verified-fulltext, §6.2): "Overall F1 can be maximized without reproducing any dynamics, therefore the Keep baseline reaches a high overall F1 with change F1 equal to zero."
- (verified-fulltext, §7 Conclusions): "Opinion dynamics models remain valuable for studying generative mechanisms such as consensus and polarization but on real world data they often fail to outperform trivial baselines."

### 2. Mulder 2023 — powRICLPM

DOI 10.1080/10705511.2022.2122467. SEM 30(4), 645–658 (online 21/11/2022), licença CC BY 4.0 segundo o Crossref. O texto integral não estava acessível: a Taylor & Francis e o repositório de Utrecht devolveram 403 e 500. Lidos em seu lugar: o resumo de apresentação do autor (Bielefeld, 15/03/2023) e o manual CRAN do powRICLPM 0.2.1.

- **Estimando**: poder, viés, EQM e cobertura para parâmetros do RI-CLPM e do
  STARTS.
- **Dados/simulação**: Monte Carlo com a população definida pelo usuário.
- **Erro de medida**: sim, via confiabilidade do indicador e erro de medida
  no STARTS.
- **Nulos**: o efeito cross-lag igual a zero, testado pela significância do
  coeficiente.
- **Discriminador/teste**: teste de Wald ou de significância do parâmetro
  estimado por SEM.
- **Limiar/fronteira**: dá o tamanho amostral e o número de ondas para um
  poder-alvo. Não dá força mínima de um gerador contra uma família de nulos.
- **Geometria**: variável, definida pelo usuário.
- **Diferença para a*(r)**: o estimando é um coeficiente defasado entre duas
  variáveis da mesma pessoa, não o acoplamento entre pessoas. O critério é a
  significância de um parâmetro, não a separabilidade de geradores por AUC.
  A dependência conjunta do poder em relação a confiabilidade, ICC, ondas e N
  é, no entanto, precedente direto do formato "curva em função de r".
- Citação (abstract-only; manual CRAN powRICLPM 0.2.1, "Description"): "Conditions are defined in terms of sample size, number of time points, proportion of between-unit variance (ICC), and indicator reliability."
- (abstract-only; resumo de apresentação do autor): "The presentation focuses on the (basic) bivariate RI-CLPM, as well as extensions to include various (stationarity) constraints over time, measurement error (leading to the stable trait autoregressive trait state model), and non-normal data"

### 3. Dang e Ma 2026 — RI-CLPM readiness

arXiv:2608.09951v1 (16/07/2026). Não há DOI de periódico na página do arXiv. Lido: PDF v1, pp. 2–11 (resumo, introdução, desenho e resultados da simulação).

- **Estimando**: poder para detectar um efeito cross-lag intra-pessoa no
  RI-CLPM ("diagnostic sensitivity"), mais uma revisão de 186 aplicações.
- **Dados/simulação**: Monte Carlo com powRICLPM: N de 500 a 10.000, 3 a 5
  ondas, confiabilidade 0,60/0,70/0,80, ICC de 0,10 a 0,90 e efeito
  0,03/0,07/0,12. São 1.000 réplicas por condição (pp. 9–10).
- **Erro de medida**: sim, como confiabilidade fixada por condição.
- **Nulos**: efeito cross-lag zero. AR fixado em 0,40 (p. 10).
- **Discriminador/teste**: significância a α=0,05 (p. 10).
- **Limiar/fronteira**: há curvas de poder por célula, mas nenhuma força
  mínima de influência entre pessoas é estimada.
- **Geometria**: 3–5 ondas, N até 10.000.
- **Diferença para a*(r)**: o formato "sensibilidade condicionada a r, ondas
  e N" é o mesmo. O gerador (SEM linear intra-pessoa), o nulo (coeficiente
  zero) e o critério (significância) diferem. Não há dinâmica de opinião,
  rede nem nulos de persistência alternativos. Um revisor pode ler a*(r)
  como "análise de poder"; o texto deve explicar por que não é só isso.
- Citação (verified-fulltext, p. 2, Abstract): "we show that power to detect within-person cross-lagged effects depends jointly on reliability, ICC, number of waves, sample size, and target effect size; high ICC, modest reliability, and few waves can substantially reduce power even in large samples."
- (verified-fulltext, p. 10, "Power Estimation"): "power was defined as the proportion of replications in which the target within-person cross-lagged path was statistically significant at α = .05."

### 4. Lersch 2023 — mudança da cultura pessoal ao longo da vida

DOI 10.1177/00031224231156456. ASR 88(2), 220–251, licença CC BY 4.0. Lido: versão publicada no repositório edoc da HU Berlin (PDF, pp. 220–251), na introdução e em "Data". O suplemento (Parte B) está na SAGE, que devolveu 403, e não foi relido nesta sessão. A leitura anterior do suplemento está em `decision17-reference-verification.md`: 3, 5 e 10 ondas.

- **Estimando**: decomposição da variância de itens de cultura pessoal em
  diferenças estáveis entre pessoas, tendências específicas da pessoa
  (mudança persistente) e flutuação aleatória, por modelos de efeitos mistos
  e meta-análise.
- **Dados/simulação**: BHPS, HILDA, PSID, SHP, SOEP e UKHLS, com 428 medidas.
  Há uma simulação (suplemento B) sobre a detectabilidade da mudança
  persistente conforme o número de ondas.
- **Erro de medida**: discutido como fonte de flutuação ("measurement error
  prevents observation of these opinions", p. 227). No texto principal, não
  é um fator com confiabilidade fixada externamente.
- **Nulos**: modelo de disposições estáveis contra adaptação ao longo da
  vida.
- **Discriminador/teste**: estimação por efeitos mistos.
- **Limiar/fronteira**: não estima força mínima. A simulação diz em que
  desenho a mudança persistente não é detectada com confiabilidade.
- **Geometria**: painéis longos, incluindo o SHP.
- **Diferença para a*(r)**: Lersch já estabelece que painéis curtos não
  bastam e que o SHP é adequado para tendências individuais. O que falta é a
  influência entre pessoas, a curva condicionada a r e os nulos pareados por
  momentos. O acréscimo de a*(r) não é "usar painel longo".
- Citação (verified-fulltext, p. 222): "Third, using simulated data, I show that data-generating processes compatible with persistent change cannot be reliably identified in the context of a three-wave panel such as the GSS."
- (verified-fulltext, p. 228, "Data"): "in a simulation, I show that in the context of a three-wave/four-year panel such as the GSS, data-generating processes compatible with persistent change cannot be reliably detected (see Part B of the online supplement)."

### 5. Moor-Smith e Carpentras 2026 — validade de múltiplos modelos

Capítulo: DOI 10.1007/978-3-032-31712-4_30, *Advances in Social Simulation* (Springer Proceedings in Complexity), pp. 400–414. Preprint: arXiv:2602.00876v1. Lido: HTML v1, §§2.1, 3.1, 3.3, 4.2 e 5. O capítulo editado não foi lido.

- **Estimando**: variância explicada normalizada pelo nulo "sem mudança", com
  distância de Wasserstein entre distribuições previstas e observadas.
- **Dados/simulação**: dados sintéticos gerados por Deffuant, HK, ED e
  Duggins, e seis séries do ESS (onze países, onze rodadas).
- **Erro de medida**: não há canal de resposta. O ruído gaussiano é somado à
  distribuição e realimenta o estado seguinte (§3.3).
- **Nulos**: persistência agregada ("no change").
- **Discriminador/teste**: variância explicada relativa ao nulo, sem teste
  de classificação.
- **Limiar/fronteira**: sim, em forma qualitativa. Estima a deriva mínima
  para superar o nulo (§3.1) e procura o ruído a partir do qual a
  reconstrução falha (§3.3). Não há grade pré-registrada nem alvo de AUC.
- **Geometria**: distribuições transversais agregadas, não trajetórias
  individuais (§2.1).
- **Diferença para a*(r)**: é o precursor conceitual mais próximo, pela ideia
  de sinal mínimo contra persistência e de ruído que empurra a seleção para o
  nulo. a*(r) difere em quatro pontos: trajetórias individuais, erro apenas
  no canal de resposta com r externo, nulos de persistência flexíveis e
  pareados em L1/L2, e AUC por painel com discriminador fixo.
- Citação (verified-fulltext, §3.1): "We observe that a minimum amount of opinion drift is required for the explained variance to exceed that of our naive null model baseline"
- (verified-fulltext, §3.3): "Our goal is to identify the threshold beyond which model reconstruction becomes infeasible."
- (verified-fulltext, §3.3): "This again suggests that the optimizer is learning to mimic the null model—and “freeze” in situations where the signal becomes unclear."
- (verified-fulltext, §2.1): "this assumption allows us to use the available cross-sectional data as a practical—albeit imperfect—proxy for longitudinal ground-truth"

### 6. Gestefeld e Lorenz 2023 — calibração a distribuições e transições

DOI 10.18564/jasss.5204. JASSS 26(4):9. Lido: HTML integral, ¶¶3.12, 5.16, 6.18, 7.7–7.9.

- **Estimando**: R² de ajuste de distribuições estacionárias (ESS) e de
  probabilidades de transição individuais (SHP).
- **Dados/simulação**: ESS (1.235 distribuições) e SHP, com transições anuais
  de 1999 a 2009.
- **Erro de medida**: não modelado. O uso do ponto médio como não resposta é
  reconhecido e deixado de fora ("we neglect this feature in our model", ¶7.7).
- **Nulos**: R² contra uma binomial com p=0,5 (¶5.16). Não há nulo de
  persistência.
- **Discriminador/teste**: ajuste por R², sem teste de separabilidade.
- **Limiar/fronteira**: não estima.
- **Geometria**: 50.008 transições de 10.627 indivíduos (¶3.12).
- **Diferença para a*(r)**: é a fonte da geometria SHP e do cenário de 24
  passos por ano. Não pergunta se a dinâmica se distingue de persistência
  sob erro, e os próprios autores apontam o limite de validação.
- Citação (verified-fulltext, ¶3.12): "From the data from 1999 to 2009, we extract the annual transition probabilities with a total of 50008 recorded opinion shifts from 10627 individuals."
- (verified-fulltext, ¶7.9): "The answer to this question is a bit beyond the scope of the paper and also beyond what can be achieved with this type of data because it does not include information about the communication of individuals."
- (verified-fulltext, ¶5.16): "\(H_0\) is our null hypothesis with a binomial distribution of \(p=0.5\)."

### 7. Gelastopoulos, Sage e van de Rijt 2025 — reforço sem heterogeneidade

DOI 10.1073/pnas.2408163122. PNAS 122(23):e2408163122. Lido: PMC12167982, resumo, introdução, "Case 2: Personal Culture" e Discussion.

- **Estimando**: equivalência observacional entre modelos de heterogeneidade
  (traço fixo) e de reforço.
- **Dados/simulação**: prova matemática com três casos: ciência da ciência,
  cultura pessoal (PSID) e redes sexuais.
- **Erro de medida**: não modelado.
- **Nulos**: heterogeneidade estacionária. O teste de permutabilidade verifica
  estacionariedade.
- **Discriminador/teste**: prova de existência de modelos gêmeos; teste de
  corridas por embaralhamento.
- **Limiar/fronteira**: não estima. O resultado é de confusão genérica.
- **Geometria**: itens PSID com três ou mais ondas no teste de
  permutabilidade.
- **Diferença para a*(r)**: o reforço é intra-individual, não influência
  entre pessoas. Ainda assim, o resultado é um alerta: por construção, as
  famílias traço+X podem imitar dinâmica. Isso sustenta a decisão do
  protocolo de ler não-atingimento como "compatível com persistência" e
  nunca como indistinguibilidade geral. O contraste de a*(r) é finito e de
  família fixa, e não contradiz a equivalência genérica.
- Citação (verified-fulltext, Abstract): "We show that any longitudinal data with systematic differences can also be produced by a reinforcement-driven data generating process."
- (verified-fulltext, Discussion): "Our mathematical results show generic confounding, in the sense that for any type of longitudinal data there is always a pure reinforcement model as well as a pure heterogeneity model that could have generated it."

### 8. Stadtfeld, Snijders, Steglich e van Duijn 2020 — poder em redes longitudinais

DOI 10.1177/0049124118769113. SMR 49(4), 1103–1132, licença CC BY-NC 4.0. A SAGE devolveu 403. Lido: versão publicada depositada por Snijders (stats.ox.ac.uk), no resumo e no segundo estudo de caso (pp. 1103, 1115). Existe também o preprint arXiv:1701.05177, que não foi lido.

- **Estimando**: poder para os efeitos de seleção (homofilia) e de influência
  em SAOM.
- **Dados/simulação**: redes simuladas com base em estudos típicos: 30 a 120
  atores, 2 a 5 ondas, dados faltantes e rotatividade.
- **Erro de medida**: não modelado (só dados faltantes e rotatividade).
- **Nulos**: parâmetro de influência igual a zero.
- **Discriminador/teste**: teste de Wald ou de escore dos parâmetros SAOM.
- **Limiar/fronteira**: dá poder por desenho, não força mínima em função da
  confiabilidade.
- **Geometria**: 30–120 atores, 2–5 ondas.
- **Diferença para a*(r)**: exige rede observada e estima o parâmetro de
  influência. a*(r) não observa exposição, não tem canal de erro nesse
  antecedente e compara geradores, não testa um coeficiente. O antecedente
  mostra que poder baixo para influência é esperado mesmo com rede.
- Citação (verified-fulltext, p. 1103, Abstract): "Two detailed case studies illustrate how statistical power is strongly affected by network size, number of data collection waves, effect sizes, missing data, and participant turnover."
- (verified-fulltext, p. 1115): "In the minimal design with two waves and 30 actors, the power of the influence effect is only 10 percent and also the power of the homophily effect is low (34.5 percent)."

### 9. Ureña-Carrion, Peixoto e Iñiguez 2026 — inferência de processos em redes

arXiv:2607.08672v1 (09/07/2026), licença CC BY 4.0. Lido: HTML v1, Abstract, Introduction, Results (primeiras subseções), Discussion e Materials and Methods.

- **Estimando**: detectabilidade (razão de log-verossimilhança assintótica,
  mínima entre alternativas) de seis mecanismos de espalhamento binário.
- **Dados/simulação**: redes sintéticas, aproximações AME e dados empíricos
  de vários domínios.
- **Erro de medida**: não há canal de resposta. Variantes "ruidosas" misturam
  um componente independente na probabilidade de transição (Results, dados
  empíricos).
- **Nulos**: o modelo "Independent" está entre os candidatos e é o
  selecionado na maioria dos dados empíricos.
- **Discriminador/teste**: seleção de modelos por verossimilhança; taxa de
  verdadeiros positivos.
- **Limiar/fronteira**: sim, detectabilidade por região de parâmetros, com a
  indicação de onde a seleção falha.
- **Geometria**: estados de todos os nós em todos os passos, rede conhecida.
- **Diferença para a*(r)**: estados binários, rede conhecida, observação
  completa e verossimilhança exata. a*(r) trata opiniões contínuas
  discretizadas, rede não observada, erro de resposta com r e discriminador
  resumido. A ideia de mapa de detectabilidade, porém, já está aqui para
  contágio.
- Citação (verified-fulltext, Introduction): "Here, instead, we assume the network structure is known and observations of a dynamical process are available, while the interaction rules remain hidden."
- (verified-fulltext, Abstract): "Our results show that statistical model selection can fail under common conditions and suggest new directions for overcoming these limitations."
- (verified-fulltext, Discussion): "to our knowledge, our work represents the first systematic effort to assess both detectability limits and the prevalence of paradigmatic mechanisms in networked spreading phenomena."

### Antecedentes adicionais sinalizados pelos documentos de entrada

#### 10. Kiley e Vaisey 2020

DOI 10.1177/0003122420921538. ASR 85(3), 477–506. A SAGE devolveu 403. Lido: manuscrito dos autores (cópia em scispace; o preprint SocArXiv é 8za35), pp. 1 e 21–22 do manuscrito. A paginação da ASR não foi conferida nesta sessão.

- Atualização ativa contra disposições estáveis em 183 itens do GSS, 3 ondas.
  O erro de medida se confunde com mudança não persistente. Não há
  influência entre pessoas nem limiar.
- **Diferença**: a ambiguidade entre atualização e erro alto já está
  formulada. a*(r) a transforma numa curva operacional contra nulos
  explícitos.
- Citação (verified-fulltext, manuscrito p. 21): "If the rate of active updating is so high that individuals make changes between each wave, then the model becomes indistinguishable from the settled dispositions model with high measurement error"

#### 11. Lucas 2023

DOI 10.1177/25152459231158378. AMPPS 6(1), CC BY-NC 4.0. Somente o resumo (Crossref).

- Traço estável omitido gera caminhos cross-lag espúrios. Isso fundamenta o
  nulo B (traço+AR).
- Citação (abstract-only): "I then show in simulated data that with realistic assumptions, the CLPM is very likely to find spurious cross-lagged effects when they do not exist and can sometimes underestimate these effects when they do exist."

#### 12. Carpentras e Quayle 2023

DOI 10.1080/13645579.2022.2137938. IJSRM 26(2), 215–231. Lido: versão publicada, PDF via arXiv:2312.05101, pp. 226–228.

- Distorções monotônicas da escala mudam previsões do Deffuant e do Duggins
  e podem fazer dados do Deffuant parecerem incompatíveis com o Deffuant.
  Não há nulo nem limiar.
- **Diferença**: o protocolo usa esse trabalho para rotular separações
  "dependentes do canal".
- Citação (verified-fulltext, p. 227): "This means that poor predictions are not necessarily evidence that a model is poor."

#### 13. Hill e Kriesi 2001

DOI 10.1017/S0003055401002209. APSR 95(2), 397–413. Somente o resumo (Crossref). O Crossref lista apenas Hill como autora; a coautoria de Kriesi foi conferida na página da editora em `decision17-reference-verification.md`.

- Mistura de estáveis, instáveis e mudança racional num painel suíço de
  quatro ocasiões. Inspira o nulo E.
- Citação (abstract-only): "The results also undermine the measurement-error model, which maintains that unstable responses are mainly attributable to deficient survey instruments, not individual opinion change."

#### 14. Borile, Lenti, Ghidini, Monti e De Francisci Morales 2026

DOI 10.1098/rsos.251253. RSOS 13(3):251253. Preprint: arXiv:2506.11751v1. Lido: HTML v1, resumo e §2.

- Viés e identificabilidade dos estimadores de máxima verossimilhança do
  BCM, com sorteios e interações assumidos observáveis.
- **Diferença**: trata a identificabilidade de parâmetros dentro de um
  modelo, não a distinguibilidade contra nulos sem influência sob erro de
  resposta.
- Citação (verified-fulltext, Abstract): "the joint parameter estimation is affected by identifiability issues for specific regions of the parameter space, as several local maxima are present in the likelihood function."

#### 15. Lenti, Monti e De Francisci Morales 2024

DOI 10.1145/3616855.3635785. WSDM 2024, pp. 350–359. Preprint: arXiv:2310.02766v2. Lido: HTML v2, §§1 e 3.

- Estimação por verossimilhança no BCM com opiniões observadas, interações
  parcialmente observadas e proxies ruidosos.
- **Diferença**: recupera ε dentro de um modelo. Não compara com nulos de
  persistência nem varia a confiabilidade.
- Citação (verified-fulltext, §1): "We do so on three realistic scenarios of increasing complexity depending on data availability: ( ) fully observed opinions and interactions, ( ) partially observed interactions, ( ) observed interactions with noisy proxies of the opinions."
  Os marcadores (i)–(iii) foram perdidos na conversão do HTML; os parênteses
  vazios são do texto extraído.

#### 16. Tang, Snijders e Flache 2025

DOI 10.18564/jasss.5566. JASSS 28(1):2. Lido: HTML integral, ¶¶3.11 e 5.1.

- SAOM multinível em 46 turmas, com 1.019 adolescentes e 2 ondas. Separa
  confiança limitada de influência negativa com rede observada.
- **Diferença**: a rede e a amizade são observadas. Não há canal de erro
  nem curva de detecção.
- Citação (verified-fulltext, ¶5.1): "the application of the SAOM helps us easily disentangle bounded confidence and negative influence from each other and from other mechanisms, such as the (assimilative) influences from friends."

### Antecedentes encontrados na busca da tarefa 2 (linhas 17–19)

#### 17. Carpentras e Quayle 2022 — propagação de erro de medida no Deffuant

DOI 10.1016/j.physa.2022.127993. Physica A 606:127993 (novembro de 2022), título e autores conferidos no Crossref. Lido: preprint arXiv:2106.04328v1 ("The sensitivity of the Deffuant model to measurement error", 07/06/2021), §5 Conclusion. O título do preprint difere do publicado. A correspondência foi inferida pelos mesmos autores e pelos mesmos resultados numéricos (40% e 80%) descritos no resumo publicado segundo `claude-novelty-review.md`, não confirmada por nota de publicação.

- **Estimando**: erro de previsão (coeficiente de Theil) do Deffuant quando os
  dados passam por ruído aleatório, binning e distorção de escala.
- **Dados/simulação**: simulação, mais escalas do Wellcome Global Monitor para
  calibrar níveis plausíveis de ruído e distorção.
- **Erro de medida**: sim, em três tipos, mas não como confiabilidade
  teste–reteste de um painel.
- **Nulos**: nenhum nulo sem influência.
- **Discriminador/teste**: não há. A medida é o erro de previsão.
- **Limiar/fronteira**: não estima força mínima. Relata saturação do erro
  (40% com ruído, acima de 80% com distorções).
- **Geometria**: distribuições de opinião simuladas antes e depois da
  dinâmica, sem painel de ondas.
- **Diferença para a*(r)**: mostra que o canal de medida degrada previsões
  de um modelo de influência. Não pergunta se a influência se distingue de
  persistência nem varia r num painel.
- Citação (verified-fulltext, preprint §5): "Random noise and distortions, contrary to binning, may have a massive effect on the model’s prediction."

#### 18. Xu e Frank 2021 — sensibilidade de inferências de influência a erros de observação da rede

DOI 10.1017/nws.2020.36. Network Science 9(1), 73–98 (online 19/10/2020), conferido no Crossref. A página da Cambridge devolveu 404 na URL tentada. Somente o resumo (Crossref).

- Análise de sensibilidade, por simulação, da robustez de estimativas de
  influência social a seis mecanismos de viés na rede observada, com
  soluções analíticas para três deles.
- O erro está na rede, não no canal de resposta da opinião. Não há nulo de
  persistência nem limiar de força.
- **Diferença para a*(r)**: pressupõe rede observada e pergunta pela
  robustez de um coeficiente. a*(r) não observa rede e pergunta pela
  separabilidade de geradores sob erro de resposta.
- Citação (abstract-only): "we proposed a simulation-based sensitivity analysis method that can evaluate the robustness of inferences made in social network analysis to six forms of selection mechanisms that can cause biases in network observations"

#### 19. Advani e Malde 2018 — identificação de efeitos sociais com formação de rede e erro de medida

DOI 10.1111/joes.12256. Journal of Economic Surveys 32(4), 1016–1044, CC BY 4.0 segundo o Crossref. A Wiley devolveu 403. Somente o resumo (Crossref).

- Revisão econométrica de modelos lineares de efeitos sociais sob rede
  endógena e dados de rede faltantes ou medidos com erro.
- **Diferença para a*(r)**: tratam a identificação de um parâmetro de pares
  com rede (parcialmente) observada. Não comparam com nulos de persistência
  nem tratam erro de resposta da variável de desfecho.
- Citação (abstract-only): "Early methods developed to identify thesesocial effectsassumed that networks had formed exogenously, and were perfectly observed, both of which are unlikely to hold in practice."
  A junção "thesesocial effectsassumed" está assim no resumo do Crossref,
  por perda de marcação de itálico.

# Busca documentada

## Consultas pré-declaradas (texto do commit 987acded, sem alteração)

Declaradas em 27/09/2026, antes da execução. Cada consulta é executada, sem
alteração do texto, no OpenAlex (`/works?search=`), no Semantic Scholar
(`/graph/v1/paper/search?query=`) e no arXiv (`search_query=`). Para o arXiv, a
forma booleana abaixo é a tradução fixa da mesma consulta (termos com `all:`,
unidos por `AND`); nenhuma outra reformulação será feita depois de ver os
resultados. Triagem: 20 primeiros títulos por API e consulta.

| ID | Texto (OpenAlex e Semantic Scholar) | Tradução arXiv |
| --- | --- | --- |
| Q01 | opinion dynamics panel data measurement error | `all:"opinion dynamics" AND all:panel AND all:"measurement error"` |
| Q02 | social influence longitudinal survey reliability distinguishability | `all:"social influence" AND all:longitudinal AND all:reliability` |
| Q03 | bounded confidence model panel survey identifiability | `all:"bounded confidence" AND all:identifiability` |
| Q04 | opinion dynamics null model persistence panel | `all:"opinion dynamics" AND all:"null model" AND all:persistence` |
| Q05 | social influence detectability measurement error simulation | `all:"social influence" AND all:detectability` |
| Q06 | opinion dynamics test-retest reliability agent-based model | `all:"opinion dynamics" AND all:"test-retest"` |
| Q07 | bounded confidence autoregressive null model distinguishable | `all:"bounded confidence" AND all:autoregressive` |
| Q08 | social influence panel data observational equivalence stable traits | `all:"social influence" AND all:"observational equivalence"` |
| Q09 | opinion dynamics model validation longitudinal survey response error | `all:"opinion dynamics" AND all:longitudinal AND all:survey` |
| Q10 | detection threshold social influence panel data simulation | `all:"social influence" AND all:panel AND all:threshold AND all:simulation` |

Regras de triagem declaradas antes da execução: "relevante" exige que o
trabalho trate, ao mesmo tempo, (i) influência social ou dinâmica de opinião
e (ii) pelo menos um entre erro de medida/confiabilidade, painel longitudinal
comparado a um nulo sem influência, ou distinguibilidade/identificabilidade
do mecanismo. Relevantes ainda não presentes na matriz são lidos como na
tarefa 1. Falhas de API (limite de taxa, erro HTTP) são registradas como tais,
com nova tentativa espaçada, sem substituir a consulta.

## Condições de execução

- **OpenAlex**: a primeira tentativa (27/09, 22:59 UTC) recebeu HTTP 429,
  com o orçamento diário esgotado para o IP de saída compartilhado. As 10
  consultas rodaram após o reset, em 28/09 entre 00:01 e 00:16 UTC. Não foi
  enviado `mailto`. A ordenação é por relevância do OpenAlex, que pondera
  citações; por isso os 20 primeiros são dominados por trabalhos muito
  citados de outras áreas.
- **Semantic Scholar**: o pool sem chave devolveu 429 com frequência. Foram
  três passadas, com até 8 tentativas espaçadas por consulta. Q04 e Q08
  nunca obtiveram resposta e ficam registradas como falha (HTTP 429, sem
  títulos). As outras 8 consultas foram triadas.
- **arXiv**: a API `export.arxiv.org/api/query` devolveu HTTP 406 para
  toda consulta não armazenada em cache neste ambiente; os 10 registros
  ficam no JSON com `api="arxiv"`. A mesma tradução booleana foi executada na
  busca do site (`arxiv.org/search`, `searchtype=all`, que busca em todos os
  campos de metadados e une os termos por AND), com `api="arxivweb"`. Não é
  a API pedida; é o substituto mais fiel disponível.
- Total: 40 execuções registradas (10 × 4 rotas), 399 títulos triados.
  Resultado da triagem: 391 não relevantes, 5 relevantes já na matriz
  (Gestefeld–Lorenz, Borile ×2, Lenti, CoDiNG) e 3 relevantes novos (linhas
  17–19).
- Buscas suplementares fora do protocolo, em motor web genérico, em
  27/09/2026: (i) "simulation study distinguish social influence opinion
  dynamics from autoregressive stability panel survey measurement error
  reliability AUC classifier"; (ii) "\"opinion dynamics\" \"panel data\"
  \"measurement error\" identifiability bounded confidence agent-based 2025
  OR 2026". Nenhum resultado novo e próximo. Apareceram Gestefeld–Lorenz,
  Borile et al. e Banisch–Shamon (JASSS 27(1):17, já no dossiê de 12/09).
  Também foram usadas buscas web para localizar cópias abertas de Lersch,
  Mulder, Stadtfeld et al. e Kiley–Vaisey.
- Leituras: cerca de 80 requisições no total (textos, PDFs, metadados
  Crossref, Europe PMC, páginas de resumo do arXiv e 6 buscas web), sem
  contar as tentativas repetidas das APIs de busca.

## Registro de execução

Esta seção e o arquivo `search-log.json` foram reconstruídos em 28/09/2026.
Os originais, gerados no sandbox da sessão
`session_01EaXAsmH2mBrCesTwUsiFMv`, não saíram do contêiner. Os arquivos
brutos das quatro rotas foram refeitos com as listas de resultados que a
sessão imprimiu na transcrição, e os scripts de triagem e de geração da
própria sessão rodaram de novo, com as edições posteriores e sem mudança de
decisão. O resultado reproduz os totais de "Condições de execução". Os
títulos seguem cortados onde a sessão os imprimiu cortados: 115 caracteres
no OpenAlex e 100 a 110 no Semantic Scholar. A data e a URL de cada execução
nunca foram impressas e ficaram nulas, daí o `None` na coluna de data. Sem
DOI impresso, a coluna de identificador mostra o ID do OpenAlex ou do arXiv.
Do ID do Semantic Scholar, a transcrição guarda só os 12 primeiros
caracteres; em Q05, Q09 e Q10 nem isso, e o campo traz o marcador
`not-printed:<consulta>:<posição>`.

### OpenAlex

| Consulta | Data (UTC) | HTTP | Contagem | Retornados |
| --- | --- | --- | --- | --- |
| Q01 | None | 200 | 108695 | 20 |
| Q02 | None | 200 | 9536 | 20 |
| Q03 | None | 200 | 15878 | 20 |
| Q04 | None | 200 | 9454 | 20 |
| Q05 | None | 200 | 141303 | 20 |
| Q06 | None | 200 | 4149 | 20 |
| Q07 | None | 200 | 560 | 20 |
| Q08 | None | 200 | 3609 | 20 |
| Q09 | None | 200 | 52139 | 20 |
| Q10 | None | 200 | 36103 | 20 |

<details><summary>Q01 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2009 | Introduction to stochastic actor-based models for network dynamics | W2099815494 | não relevante: introdução ao SAOM com rede observada; sem canal de erro nem nulo de persistência |
| 2 | 2007 | The German Socio-Economic Panel Study (SOEP) - Scope, Evolution and Enhancements | W2141697271 | não relevante: fora do tema (descrição do painel SOEP); não trata influência social/dinâmica de opinião |
| 3 | 2013 | How Elite Partisan Polarization Affects Public Opinion Formation | W2114986694 | não relevante: efeito de elites na opinião pública; sem regra de influência entre pares nem erro de resposta |
| 4 | 2017 | A theory of multineuronal dimensionality, dynamics and measurement | W2766284800 | não relevante: fora do tema (neurociência); não trata influência social/dinâmica de opinião |
| 5 | 2013 | Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts | W2095655043 | não relevante: fora do tema (análise de texto política); não trata influência social/dinâmica de opinião |
| 6 | 1980 | The Sensitivity of Consumption to Transitory Income: Estimates from Panel Data on Households | W2892084985 | não relevante: fora do tema (economia do consumo); não trata influência social/dinâmica de opinião |
| 7 | 2019 | Firm-Level Political Risk: Measurement and Effects* | W2770414254 | não relevante: fora do tema (finanças); não trata influência social/dinâmica de opinião |
| 8 | 2008 | Perfluorooctane sulfonate (PFOS), perfluorooctanoic acid (PFOA) and their salts Scientific Opinion of the Panel on  | W4211232623 | não relevante: fora do tema (toxicologia); não trata influência social/dinâmica de opinião |
| 9 | 2025 | DESI 2024 VI: cosmological constraints from the measurements of baryon acoustic oscillations | W4394029306 | não relevante: fora do tema (cosmologia); não trata influência social/dinâmica de opinião |
| 10 | 2014 | The FIELDS Instrument Suite on MMS: Scientific Objectives, Measurements, and Data Products | W2052947135 | não relevante: fora do tema (física espacial); não trata influência social/dinâmica de opinião |
| 11 | 2002 | Error Reduction and Performance Improvement in the Emergency Department through Formal Teamwork Training: Evaluatio | W2007598609 | não relevante: fora do tema (medicina); não trata influência social/dinâmica de opinião |
| 12 | 2015 | Computational Fluid Dynamics for urban physics: Importance, scales, possibilities, limitations and ten tips and tri | W2082154841 | não relevante: fora do tema (dinâmica de fluidos); não trata influência social/dinâmica de opinião |
| 13 | 2008 | Opinion of the Scientific Panel on Contaminants in the Food chain on perfluorooctane sulfonate (PFOS), perfluorooct | W2141591360 | não relevante: fora do tema (toxicologia); não trata influência social/dinâmica de opinião |
| 14 | 2002 | A Method for Modeling the Intrinsic Dynamics of Intraindividual Variability: Recovering the Parameters of Simulated | W2064187565 | não relevante: variabilidade intraindividual em psicometria; sem influência social |
| 15 | 2016 | End of Life Management: Solar Photovoltaic Panels | W2553421097 | não relevante: fora do tema (engenharia); não trata influência social/dinâmica de opinião |
| 16 | 2012 | The Panel Study of Income Dynamics: overview, recent innovations, and potential for life course research | W2147217762 | não relevante: fora do tema (descrição do painel PSID); não trata influência social/dinâmica de opinião |
| 17 | 2006 | A framework for dealing with uncertainty due to model structure error | W2089719636 | não relevante: fora do tema (hidrologia); não trata influência social/dinâmica de opinião |
| 18 | 1979 | Labor Market Dynamics and Unemployment: A Reconsideration | W2034146766 | não relevante: fora do tema (economia do trabalho); não trata influência social/dinâmica de opinião |
| 19 | 2020 | Affective polarization, local contexts and public opinion in America | W3109607089 | não relevante: polarização afetiva e contexto local; sem modelo de influência nem erro |
| 20 | 2009 | Does the Media Matter? A Field Experiment Measuring the Effect of Newspapers on Voting Behavior and Political Opini | W2150725398 | não relevante: experimento de mídia; sem painel com canal de erro |

</details>

<details><summary>Q02 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2004 | “Fundamental Causes” of Social Inequalities in Mortality: A Test of the Theory | W2061973537 | não relevante: fora do tema (epidemiologia social); não trata influência social/dinâmica de opinião |
| 2 | 2022 | Social capital I: measurement and associations with economic mobility | W4289222991 | não relevante: fora do tema (economia/capital social); não trata influência social/dinâmica de opinião |
| 3 | 2019 | Are loneliness and social isolation associated with cognitive decline? | W2961148372 | não relevante: fora do tema (saúde); não trata influência social/dinâmica de opinião |
| 4 | 2014 | Measuring Large-Scale Social Networks with High Resolution | W1987835826 | não relevante: medição de redes sociais; sem dinâmica de opinião nem nulo |
| 5 | 2019 | The Netherlands Twin Register: Longitudinal Research Based on Twin and Twin-Family Designs | W2983790886 | não relevante: fora do tema (genética comportamental); não trata influência social/dinâmica de opinião |
| 6 | 2004 | Validation Guidelines for IS Positivist Research | W116282327 | não relevante: fora do tema (sistemas de informação); não trata influência social/dinâmica de opinião |
| 7 | 2014 | Leadership as social identity management: Introducing the Identity Leadership Inventory (ILI) to assess and validat | W2008557696 | não relevante: fora do tema (psicologia organizacional); não trata influência social/dinâmica de opinião |
| 8 | 2017 | Social influence in the global diffusion of alternative fuel vehicles – A meta-analysis | W2730695225 | não relevante: meta-análise de difusão de veículos; influência social sem painel com erro |
| 9 | 2018 | Social and emotional skills for student success and well-being | W2803071139 | não relevante: fora do tema (educação); não trata influência social/dinâmica de opinião |
| 10 | 2018 | A brief measure of social media self-control failure | W2787273183 | não relevante: fora do tema (psicometria de mídia); não trata influência social/dinâmica de opinião |
| 11 | 2007 | Workforce Perceptions of Hospital Safety Culture: Development and Validation of the Patient Safety Climate in Healt | W1714083232 | não relevante: fora do tema (saúde); não trata influência social/dinâmica de opinião |
| 12 | 1997 | Social competence: An untapped dimension in evaluating head start's success | W1997668501 | não relevante: fora do tema (educação infantil); não trata influência social/dinâmica de opinião |
| 13 | 2011 | CALLING: THE DEVELOPMENT OF A SCALE MEASURE | W2016465515 | não relevante: fora do tema (psicometria organizacional); não trata influência social/dinâmica de opinião |
| 14 | 2010 | Proactivity, job characteristics, and engagement: a longitudinal study | W2159680808 | não relevante: fora do tema (psicologia organizacional); não trata influência social/dinâmica de opinião |
| 15 | 2017 | Is subjective social status a unique correlate of physical health? A meta-analysis. | W2737985520 | não relevante: fora do tema (saúde); não trata influência social/dinâmica de opinião |
| 16 | 2021 | Social isolation, social support and loneliness as predictors of cardiovascular disease incidence and mortality | W4200480463 | não relevante: fora do tema (saúde); não trata influência social/dinâmica de opinião |
| 17 | 1981 | Social Support Scales: A Methodological Note | W2117455049 | não relevante: fora do tema (psicometria); não trata influência social/dinâmica de opinião |
| 18 | 1998 | Learning styles: a cross‐sectional and longitudinal study in higher education | W2159084167 | não relevante: fora do tema (educação); não trata influência social/dinâmica de opinião |
| 19 | 2011 | LEARNING TO BE BAD: ADVERSE SOCIAL CONDITIONS, SOCIAL SCHEMAS, AND CRIME* | W1945806682 | não relevante: fora do tema (criminologia); não trata influência social/dinâmica de opinião |
| 20 | 2018 | Factors associated with residents’ contract behavior with family doctors in community health service centers: A lon | W2903495686 | não relevante: fora do tema (saúde pública); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q03 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2012 | Double Digest RADseq: An Inexpensive Method for De Novo SNP Discovery and Genotyping in Model and Non-Model Species | W2161184021 | não relevante: fora do tema (genômica); não trata influência social/dinâmica de opinião |
| 2 | 2015 | 2015 American Thyroid Association Management Guidelines for Adult Patients with Thyroid Nodules and Differentiated  | W2145150141 | não relevante: fora do tema (medicina); não trata influência social/dinâmica de opinião |
| 3 | 2010 | Selection Bias in Web Surveys | W2129332419 | não relevante: viés de seleção em surveys web; sem dinâmica de opinião |
| 4 | 2004 | Stable and Efficient Multiple Smoothing Parameter Estimation for Generalized Additive Models | W2009499611 | não relevante: fora do tema (estatística/GAM); não trata influência social/dinâmica de opinião |
| 5 | 2009 | On Modeling and Interpreting the Economics of Catastrophic Climate Change | W2097259059 | não relevante: fora do tema (economia do clima); não trata influência social/dinâmica de opinião |
| 6 | 2021 | Bayesian statistics and modelling | W3128782210 | não relevante: fora do tema (estatística bayesiana geral); não trata influência social/dinâmica de opinião |
| 7 | 2018 | Dark Energy Survey year 1 results: Cosmological constraints from galaxy clustering and weak lensing | W2744012041 | não relevante: fora do tema (cosmologia); não trata influência social/dinâmica de opinião |
| 8 | 2017 | Penalising Model Component Complexity: A Principled, Practical Approach to Constructing Priors | W1487139063 | não relevante: fora do tema (estatística/priors); não trata influência social/dinâmica de opinião |
| 9 | 2009 | Back to square one: Identification issues in DSGE models | W1494778797 | não relevante: identificação em DSGE (macroeconomia); sem influência social |
| 10 | 2010 | Understanding Bias in Nonlinear Panel Models: Some Recent Developments | W1544882719 | não relevante: viés em painéis não lineares (econometria); sem influência social |
| 11 | 2016 | A survey of the sorghum transcriptome using single-molecule long reads | W2337011385 | não relevante: fora do tema (genômica); não trata influência social/dinâmica de opinião |
| 12 | 2008 | The XMM-Newton serendipitous survey | W4292026935 | não relevante: fora do tema (astronomia); não trata influência social/dinâmica de opinião |
| 13 | 2009 | Superallowed 0+→0+ nuclear β decays: A new survey with precision tests of the conserved vector current hypothesis a | W1969401205 | não relevante: fora do tema (física nuclear); não trata influência social/dinâmica de opinião |
| 14 | 2013 | THE COS-HALOS SURVEY: RATIONALE, DESIGN, AND A CENSUS OF CIRCUMGALACTIC NEUTRAL HYDROGEN | W2006160097 | não relevante: fora do tema (astronomia); não trata influência social/dinâmica de opinião |
| 15 | 2002 | Setting confidence intervals for bounded parameters | W1541353174 | não relevante: fora do tema (estatística); não trata influência social/dinâmica de opinião |
| 16 | 2020 | The landscape of QCD axion models | W3008473238 | não relevante: fora do tema (física); não trata influência social/dinâmica de opinião |
| 17 | 2021 | Identifiability and predictability of integer- and fractional-order epidemiological models using physics-informed n | W3217086243 | não relevante: fora do tema (epidemiologia); não trata influência social/dinâmica de opinião |
| 18 | 1999 | Theoretical and empirical review of multinomial process tree modeling | W2078938818 | não relevante: fora do tema (psicologia cognitiva); não trata influência social/dinâmica de opinião |
| 19 | 2018 | How Are SNAP Benefits Spent? Evidence from a Retail Panel | W2585698078 | não relevante: fora do tema (economia); não trata influência social/dinâmica de opinião |
| 20 | 2018 | Benchmarks for models of short-term and working memory. | W2794687249 | não relevante: fora do tema (psicologia cognitiva); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q04 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2012 | Characterising performance of environmental models | W2130089609 | não relevante: fora do tema (modelagem ambiental); não trata influência social/dinâmica de opinião |
| 2 | 2010 | Persistence of Innovation in Dutch Manufacturing: Is It Spurious? | W3122095672 | não relevante: fora do tema (economia da inovação); não trata influência social/dinâmica de opinião |
| 3 | 2021 | A Search and Learning Model of Export Dynamics | W2286320298 | não relevante: fora do tema (economia); não trata influência social/dinâmica de opinião |
| 4 | 2004 | News Arrival, Jump Dynamics, and Volatility Components for Individual Stock Returns | W3121388661 | não relevante: fora do tema (finanças); não trata influência social/dinâmica de opinião |
| 5 | 2020 | Affective polarization, local contexts and public opinion in America | W3109607089 | não relevante: polarização afetiva; sem modelo de influência nem erro |
| 6 | 2012 | Public Opinion and Executive Compensation | W2120727421 | não relevante: fora do tema (economia política); não trata influência social/dinâmica de opinião |
| 7 | 2009 | Does the Media Matter? A Field Experiment Measuring the Effect of Newspapers on Voting Behavior and Political Opini | W2150725398 | não relevante: experimento de mídia; sem painel com canal de erro |
| 8 | 2018 | How Are SNAP Benefits Spent? Evidence from a Retail Panel | W2585698078 | não relevante: fora do tema (economia); não trata influência social/dinâmica de opinião |
| 9 |  | Editor's Choice Digesting Anomalies: An Investment Approach | W3125206904 | não relevante: fora do tema (finanças); não trata influência social/dinâmica de opinião |
| 10 | 2020 | Per- and Polyfluoroalkyl Substance Toxicity and Human Health Review: Current State of Knowledge and Strategies for  | W3091745167 | não relevante: fora do tema (toxicologia); não trata influência social/dinâmica de opinião |
| 11 | 2016 | International Investment Positions and Exchange Rate Dynamics: A Dynamic Panel Analysis | W2140867761 | não relevante: fora do tema (macroeconomia); não trata influência social/dinâmica de opinião |
| 12 | 2009 | The Econometrics of DSGE Models | W2890348142 | não relevante: fora do tema (macroeconomia); não trata influência social/dinâmica de opinião |
| 13 | 2015 | The Complexities of Agent-Based Modeling Output Analysis | W2204468525 | não relevante: análise de saída de ABM em geral; sem influência social nem erro de resposta |
| 14 | 2002 | PPP Strikes Back: Aggregation And the Real Exchange Rate | W2891641280 | não relevante: fora do tema (macroeconomia); não trata influência social/dinâmica de opinião |
| 15 | 2020 | Mental health before and during the COVID-19 pandemic: a longitudinal probability sample survey of the UK populatio | W3044137491 | não relevante: fora do tema (saúde mental); não trata influência social/dinâmica de opinião |
| 16 | 2022 | Developmental plasticity in thermal tolerance: Ontogenetic variation, persistence, and future directions | W4293104207 | não relevante: fora do tema (biologia); não trata influência social/dinâmica de opinião |
| 17 | 2020 | Financial access, governance and the persistence of inequality in Africa: Mechanisms and policy instruments | W3026414438 | não relevante: fora do tema (economia do desenvolvimento); não trata influência social/dinâmica de opinião |
| 18 | 2007 | Tipping and the Dynamics of Segregation | W2890132440 | não relevante: dinâmica de segregação (Schelling); sem painel nem erro de resposta |
| 19 | 2007 | Behavioral heterogeneity in stock prices | W3121754738 | não relevante: fora do tema (finanças); não trata influência social/dinâmica de opinião |
| 20 | 2010 | DSGE Models for Monetary Policy Analysis | W3122823987 | não relevante: fora do tema (macroeconomia); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q05 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2014 | A new criterion for assessing discriminant validity in variance-based structural equation modeling | W2105846236 | não relevante: fora do tema (PLS-SEM); não trata influência social/dinâmica de opinião |
| 2 | 2016 | Testing measurement invariance of composites using partial least squares | W2167344400 | não relevante: fora do tema (PLS-SEM); não trata influência social/dinâmica de opinião |
| 3 | 2003 | A survey of socially interactive robots | W2099019320 | não relevante: fora do tema (robótica); não trata influência social/dinâmica de opinião |
| 4 | 2012 | The Rediscovery of Bifactor Measurement Models | W2025929695 | não relevante: fora do tema (psicometria); não trata influência social/dinâmica de opinião |
| 5 | 2008 | Measurement Instruments for the Anthropomorphism, Animacy, Likeability, Perceived Intelligence, and Perceived Safet | W2032568497 | não relevante: fora do tema (robótica); não trata influência social/dinâmica de opinião |
| 6 | 2000 | Economic Analysis of Social Interactions | W2107295826 | não relevante: fora do tema (economia); não trata influência social/dinâmica de opinião |
| 7 | 2019 | Social Science Research: Principles, Methods and Practices | W1598829572 | não relevante: fora do tema (manual de métodos); não trata influência social/dinâmica de opinião |
| 8 | 2004 | Confidence Limits for the Indirect Effect: Distribution of the Product and Resampling Methods | W2113168655 | não relevante: fora do tema (mediação estatística); não trata influência social/dinâmica de opinião |
| 9 | 2010 | The Simulation of Smiles (SIMS) model: Embodied simulation and the meaning of facial expression | W2160234840 | não relevante: fora do tema (psicologia); não trata influência social/dinâmica de opinião |
| 10 | 2009 | Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses | W2072500831 | não relevante: fora do tema (software de poder estatístico); não trata influência social/dinâmica de opinião |
| 11 | 2009 | Puzzlingly High Correlations in fMRI Studies of Emotion, Personality, and Social Cognition | W2160453617 | não relevante: fora do tema (neuroimagem); não trata influência social/dinâmica de opinião |
| 12 | 2004 | Constructing an understanding of mind: The development of children's social understanding within social interaction | W2169370430 | não relevante: fora do tema (psicologia do desenvolvimento); não trata influência social/dinâmica de opinião |
| 13 | 2019 | Detecting Selection Bias in Meta-Analyses with Multiple Outcomes: A Simulation Study | W2932936731 | não relevante: fora do tema (meta-análise); não trata influência social/dinâmica de opinião |
| 14 | 2019 | Genome-wide meta-analysis identifies new loci and functional pathways influencing Alzheimer’s disease risk | W2908002252 | não relevante: fora do tema (genética); não trata influência social/dinâmica de opinião |
| 15 | 2010 | The Walking Behaviour of Pedestrian Social Groups and Its Impact on Crowd Dynamics | W2089584121 | não relevante: fora do tema (dinâmica de pedestres); não trata influência social/dinâmica de opinião |
| 16 | 2019 | The global soil community and its influence on biogeochemistry | W2969523923 | não relevante: fora do tema (ecologia); não trata influência social/dinâmica de opinião |
| 17 | 2015 | A Beginner's Guide to Structural Equation Modeling | W1836311887 | não relevante: fora do tema (manual de SEM); não trata influência social/dinâmica de opinião |
| 18 | 2020 | Detecting crosstalk errors in quantum information processors | W2970450884 | não relevante: fora do tema (computação quântica); não trata influência social/dinâmica de opinião |
| 19 | 2015 | Constructing, conducting and interpreting animal social network analysis | W1828958803 | não relevante: fora do tema (redes animais); não trata influência social/dinâmica de opinião |
| 20 | 2015 | A critique of the cross-lagged panel model. | W1971772643 | não relevante: crítica ao CLPM (traço estável vs. dinâmica intra-pessoa); fundamento de nulo traço+AR, sem influência entre pessoas |

</details>

<details><summary>Q06 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2008 | Technology Acceptance Model 3 and a Research Agenda on Interventions | W2112042732 | não relevante: fora do tema (sistemas de informação); não trata influência social/dinâmica de opinião |
| 2 | 2010 | Clinician’s Guide to Cardiopulmonary Exercise Testing in Adults | W2074602210 | não relevante: fora do tema (medicina); não trata influência social/dinâmica de opinião |
| 3 | 2000 | The Wheel of Wellness Counseling for Wellness: A Holistic Model for Treatment Planning | W1993824068 | não relevante: fora do tema (aconselhamento); não trata influência social/dinâmica de opinião |
| 4 | 2009 | A developmental, mentalization-based approach to the understanding and treatment of borderline personality disorder | W2098937677 | não relevante: fora do tema (psiquiatria); não trata influência social/dinâmica de opinião |
| 5 | 2005 | “Economic man” in cross-cultural perspective: Behavioral experiments in 15 small-scale societies | W2125976408 | não relevante: fora do tema (economia experimental); não trata influência social/dinâmica de opinião |
| 6 | 2015 | Early chronic kidney disease: diagnosis, management and models of care | W1755861215 | não relevante: fora do tema (medicina); não trata influência social/dinâmica de opinião |
| 7 | 2025 | Sample size matters when estimating test–retest reliability of behaviour | W4408734208 | não relevante: tamanho amostral e confiabilidade teste–reteste de comportamento; sem influência social |
| 8 | 1974 | Children at Risk: The Search for the Antecedents of Schizophrenia. Part I. Conceptual Models and Research Methods | W2009100694 | não relevante: fora do tema (psiquiatria); não trata influência social/dinâmica de opinião |
| 9 | 2012 | Management of Hyperglycemia in Hospitalized Patients in Non-Critical Care Setting: An Endocrine Society Clinical Pr | W2144913975 | não relevante: fora do tema (medicina); não trata influência social/dinâmica de opinião |
| 10 | 2019 | Questions and controversies in the study of time-varying functional connectivity in resting fMRI | W2995313551 | não relevante: fora do tema (neuroimagem); não trata influência social/dinâmica de opinião |
| 11 | 2013 | Function in the human connectome: Task-fMRI and individual differences in behavior | W2071608556 | não relevante: fora do tema (neuroimagem); não trata influência social/dinâmica de opinião |
| 12 | 2015 | Facebook as a research tool for the social sciences: Opportunities, challenges, ethical considerations, and practic | W1779879527 | não relevante: fora do tema (métodos de pesquisa em redes sociais online); não trata influência social/dinâmica de opinião |
| 13 | 2017 | Moving Forward: Challenges and Directions for Psychopathological Network Theory and Methodology | W2601774270 | não relevante: fora do tema (psicopatologia); não trata influência social/dinâmica de opinião |
| 14 | 2016 | The impact model of business intelligence on decision support and organizational benefits | W2255477244 | não relevante: fora do tema (sistemas de informação); não trata influência social/dinâmica de opinião |
| 15 | 2015 | Traumatic Brain Injury Detection Using Electrophysiological Methods | W2132029553 | não relevante: fora do tema (medicina); não trata influência social/dinâmica de opinião |
| 16 | 2019 | Philosophical Transactions of the Royal Society of London. Series A, Mathematical and Physical Sciences | W4242282425 | não relevante: fora do tema (periódico (registro)); não trata influência social/dinâmica de opinião |
| 17 | 2022 | Safety, tolerability and viral kinetics during SARS-CoV-2 human challenge in young adults | W4221135099 | não relevante: fora do tema (medicina); não trata influência social/dinâmica de opinião |
| 18 | 2011 | Therapeutic Alliance and Outcome of Psychotherapy: Historical Excursus, Measurements, and Prospects for Research | W2007748712 | não relevante: fora do tema (psicoterapia); não trata influência social/dinâmica de opinião |
| 19 | 2013 | A Posteriori Comparison of Natural and Surgical Destabilization Models of Canine Osteoarthritis | W2137567737 | não relevante: fora do tema (medicina veterinária); não trata influência social/dinâmica de opinião |
| 20 | 2020 | Trust in Robots: Challenges and Opportunities | W3083287224 | não relevante: fora do tema (robótica); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q07 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2021 | Parameter estimation and uncertainty analysis in hydrological modeling | W4200172698 | não relevante: fora do tema (hidrologia); não trata influência social/dinâmica de opinião |
| 2 | 1999 | A Conceptual Framework for Predictability Studies | W2111804884 | não relevante: fora do tema (climatologia); não trata influência social/dinâmica de opinião |
| 3 | 2019 | Statistical modeling methods: challenges and strategies | W2963352985 | não relevante: fora do tema (estatística geral); não trata influência social/dinâmica de opinião |
| 4 | 2017 | Resting-State fMRI Dynamics and Null Models: Perspectives, Sampling Variability, and Simulations | W2632689099 | não relevante: modelos nulos em fMRI; sem influência social |
| 5 | 2005 | Provenance of correlations in psychological data | W1999909108 | não relevante: fora do tema (psicometria); não trata influência social/dinâmica de opinião |
| 6 | 2018 | Dynamics-based regression models for the South Atlantic Convergence Zone | W2897114607 | não relevante: fora do tema (climatologia); não trata influência social/dinâmica de opinião |
| 7 | 2019 | An open challenge to advance probabilistic forecasting for dengue epidemics | W2988205563 | não relevante: fora do tema (epidemiologia); não trata influência social/dinâmica de opinião |
| 8 | 2015 | Do Jumps Matter for Volatility Forecasting? Evidence from Energy Markets | W2130774119 | não relevante: fora do tema (finanças); não trata influência social/dinâmica de opinião |
| 9 | 2022 | A Theory‐Based Analysis of Null Causality between HRM Practices and Outcomes: Evidence from Four‐Wave Longitudinal  | W4307562539 | não relevante: nulo de causalidade em painel de RH (4 ondas); sem influência entre pessoas |
| 10 | 2018 | Stochastic Modeling of Wind Derivatives in Energy Markets | W2803375681 | não relevante: fora do tema (finanças); não trata influência social/dinâmica de opinião |
| 11 | 2023 | Dynamic structural equation models with binary and ordinal outcomes in Mplus | W4367303348 | não relevante: DSEM para desfechos ordinais; método, sem influência social |
| 12 | 2007 | No-Arbitrage Semi-Martingale Restrictions for Continuous-Time Volatility Models subject to Leverage Effects, Jumps  | W1545499910 | não relevante: fora do tema (finanças); não trata influência social/dinâmica de opinião |
| 13 | 2022 | Generative aptamer discovery using RaptGen | W4281786804 | não relevante: fora do tema (bioinformática); não trata influência social/dinâmica de opinião |
| 14 | 2017 | Differentiating Wheat Genotypes by Bayesian Hierarchical Nonlinear Mixed Modeling of Wheat Root Density | W2597327681 | não relevante: fora do tema (agronomia); não trata influência social/dinâmica de opinião |
| 15 | 1985 | Rational Bubbles in Stock Prices? | W1526117138 | não relevante: fora do tema (finanças); não trata influência social/dinâmica de opinião |
| 16 | 2006 | Location-based estimation of the autoregressive coefficient in ARX(1) models | W2291308706 | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 17 | 2015 | Nonparametric directionality measures for time series and point process data | W2219596751 | não relevante: fora do tema (séries temporais); não trata influência social/dinâmica de opinião |
| 18 | 2023 | Stealing the Decoding Algorithms of Language Models | W4388858191 | não relevante: fora do tema (segurança de LLM); não trata influência social/dinâmica de opinião |
| 19 | 2018 | Uncertainty across volatility regimes | W2775047032 | não relevante: fora do tema (finanças); não trata influência social/dinâmica de opinião |
| 20 | 2024 | Systematic Review of Generative Modelling Tools and Utility Metrics for Fully Synthetic Tabular Data | W4404387843 | não relevante: fora do tema (dados sintéticos); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q08 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2015 | A critique of the cross-lagged panel model. | W1971772643 | não relevante: crítica ao CLPM; fundamento de nulo traço+AR, sem influência entre pessoas |
| 2 | 2011 | Personality Psychology and Economics | W3122622199 | não relevante: fora do tema (economia/personalidade); não trata influência social/dinâmica de opinião |
| 3 | 2017 | The future of Earth observation in hydrology | W2587446396 | não relevante: fora do tema (hidrologia); não trata influência social/dinâmica de opinião |
| 4 | 2019 | Challenges to capture the big five personality traits in non-WEIRD populations | W2956992498 | não relevante: fora do tema (personalidade); não trata influência social/dinâmica de opinião |
| 5 | 2015 | Trusting the State, Trusting Each Other? The Effect of Institutional Trust on Social Trust | W1833090007 | não relevante: confiança institucional e social; sem modelo de influência |
| 6 | 1999 | Bayesian model averaging: a tutorial (with comments by M. Clyde, David Draper and E. I. George, and a rejoinder by  | W1603903339 | não relevante: fora do tema (estatística bayesiana); não trata influência social/dinâmica de opinião |
| 7 | 2011 | Personality Psychology and Economics | W2132319517 | não relevante: fora do tema (economia/personalidade); não trata influência social/dinâmica de opinião |
| 8 | 2009 | Planetary Boundaries: Exploring the Safe Operating Space for Humanity | W2105414963 | não relevante: fora do tema (ciência do clima); não trata influência social/dinâmica de opinião |
| 9 | 2017 | An overview of structural equation modeling: its beginnings, historical development, usefulness and controversies i | W2570564972 | não relevante: fora do tema (SEM (revisão)); não trata influência social/dinâmica de opinião |
| 10 | 1998 | Evaluating patient-based outcome measures for use in clinical trials. | W3141544461 | não relevante: fora do tema (medicina); não trata influência social/dinâmica de opinião |
| 11 | 2018 | On Direct vs. Indirect Peer Influence in Large Social Networks | W2687523731 | não relevante: influência direta vs. indireta em grandes redes observadas; sem canal de erro nem nulo de persistência |
| 12 | 2020 | Descriptive, Predictive and Explanatory Personality Research: Different Goals, Different Approaches, but a Shared N | W3110670080 | não relevante: fora do tema (personalidade); não trata influência social/dinâmica de opinião |
| 13 | 2014 | Peer Influence in the Diffusion of iPhone 3G over a Large Social Network1 | W3121874823 | não relevante: influência de pares na difusão do iPhone com rede observada; sem erro de resposta |
| 14 | 2015 | A Large Scale Test of the Effect of Social Class on Prosocial Behavior | W1517495738 | não relevante: fora do tema (psicologia social experimental); não trata influência social/dinâmica de opinião |
| 15 | 2016 | Do social media foster or curtail adolescents’ empathy? A longitudinal study | W2407390883 | não relevante: fora do tema (mídia e empatia); não trata influência social/dinâmica de opinião |
| 16 | 2015 | ESM 2.0: State of the Art and Future Potential of Experience Sampling Methods in Organizational Research | W2106887764 | não relevante: fora do tema (métodos ESM); não trata influência social/dinâmica de opinião |
| 17 | 2015 | Influence of reward motivation on human declarative memory | W2202905384 | não relevante: fora do tema (neurociência); não trata influência social/dinâmica de opinião |
| 18 | 2018 | The dark core of personality. | W2854454445 | não relevante: fora do tema (personalidade); não trata influência social/dinâmica de opinião |
| 19 | 2020 | MTurk Research: Review and Recommendations | W3108819963 | não relevante: fora do tema (métodos online); não trata influência social/dinâmica de opinião |
| 20 | 2020 | Networks beyond pairwise interactions: Structure and dynamics | W3033513666 | não relevante: revisão de interações de ordem superior; sem painel nem erro |

</details>

<details><summary>Q09 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2008 | Technology Acceptance Model 3 and a Research Agenda on Interventions | W2112042732 | não relevante: fora do tema (sistemas de informação); não trata influência social/dinâmica de opinião |
| 2 | 2014 | Consumer Brand Engagement in Social Media: Conceptualization, Scale Development and Validation | W2061289966 | não relevante: fora do tema (marketing); não trata influência social/dinâmica de opinião |
| 3 | 2006 | Entrepreneurship and Dynamic Capabilities: A Review, Model and Research Agenda* | W1525360602 | não relevante: fora do tema (gestão); não trata influência social/dinâmica de opinião |
| 4 | 2012 | Dynamics of calling: A longitudinal study of musicians | W2099641586 | não relevante: fora do tema (psicologia vocacional); não trata influência social/dinâmica de opinião |
| 5 | 2022 | A Survey of Ensemble Learning: Concepts, Algorithms, Applications, and Prospects | W4296079469 | não relevante: fora do tema (aprendizado de máquina); não trata influência social/dinâmica de opinião |
| 6 | 2002 | Error Reduction and Performance Improvement in the Emergency Department through Formal Teamwork Training: Evaluatio | W2007598609 | não relevante: fora do tema (medicina); não trata influência social/dinâmica de opinião |
| 7 | 2014 | A survey on robotic devices for upper limb rehabilitation | W2054326469 | não relevante: fora do tema (robótica); não trata influência social/dinâmica de opinião |
| 8 | 2020 | Digital Twin: Values, Challenges and Enablers From a Modeling Perspective | W3003667836 | não relevante: fora do tema (gêmeos digitais); não trata influência social/dinâmica de opinião |
| 9 | 2013 | The validation of the turnover intention scale | W2003978304 | não relevante: fora do tema (psicometria organizacional); não trata influência social/dinâmica de opinião |
| 10 | 2011 | Improving national cultural indices using a longitudinal meta-analysis of Hofstede's dimensions | W2137689550 | não relevante: fora do tema (cultura nacional); não trata influência social/dinâmica de opinião |
| 11 | 1979 | Labor Market Dynamics and Unemployment: A Reconsideration | W2034146766 | não relevante: fora do tema (economia do trabalho); não trata influência social/dinâmica de opinião |
| 12 | 2002 | Structural equation modeling for travel behavior research | W2105828903 | não relevante: fora do tema (transportes); não trata influência social/dinâmica de opinião |
| 13 | 2011 | Prevalence, Persistence, and Sociodemographic Correlates of DSM-IV Disorders in the National Comorbidity Survey Rep | W2126948325 | não relevante: fora do tema (psiquiatria); não trata influência social/dinâmica de opinião |
| 14 | 2010 | Development and Distortion of Malaysian Public- Private Partnerships: Patronage, Privatised Profits and Pitfalls DO | W1797402740 | não relevante: fora do tema (economia política); não trata influência social/dinâmica de opinião |
| 15 | 2014 | A Survey of Modelling and Identification of Quadrotor Robot | W2087131289 | não relevante: fora do tema (robótica); não trata influência social/dinâmica de opinião |
| 16 | 2013 | The paths to social licence to operate: An integrative model explaining community acceptance of mining | W2070989922 | não relevante: fora do tema (aceitação social de mineração); não trata influência social/dinâmica de opinião |
| 17 | 2015 | Dynamics of Environmental and Financial Performance | W2286593088 | não relevante: fora do tema (gestão ambiental); não trata influência social/dinâmica de opinião |
| 18 | 2007 | Consumption over the Life Cycle: Facts from Consumer Expenditure Survey Data | W3122976614 | não relevante: fora do tema (economia do consumo); não trata influência social/dinâmica de opinião |
| 19 | 2013 | Robustness of the Theory of Planned Behavior in Predicting Entrepreneurial Intentions and Actions | W1994547427 | não relevante: fora do tema (empreendedorismo); não trata influência social/dinâmica de opinião |
| 20 | 2022 | Dealing with Careless Responding in Survey Data: Prevention, Identification, and Recommended Best Practices | W4293870301 | não relevante: respostas descuidadas em surveys; erro de resposta sem dinâmica de opinião |

</details>

<details><summary>Q10 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2021 | Large-scale association analyses identify host factors influencing human gut microbiome composition | W3121407008 | não relevante: fora do tema (genômica); não trata influência social/dinâmica de opinião |
| 2 | 2013 | Large Covariance Estimation by Thresholding Principal Orthogonal Complements | W2040373108 | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 3 | 2007 | Gaze cueing of attention: Visual attention, social cognition, and individual differences. | W2150839178 | não relevante: fora do tema (psicologia cognitiva); não trata influência social/dinâmica de opinião |
| 4 | 2023 | IPCC, 2023: Climate Change 2023: Synthesis Report. Contribution of Working Groups I, II and III to the Sixth Assess | W4385118605 | não relevante: fora do tema (clima); não trata influência social/dinâmica de opinião |
| 5 | 2019 | Genome-wide meta-analysis identifies new loci and functional pathways influencing Alzheimer’s disease risk | W2908002252 | não relevante: fora do tema (genética); não trata influência social/dinâmica de opinião |
| 6 | 2020 | Dementia prevention, intervention, and care: 2020 report of the Lancet Commission | W3046275966 | não relevante: fora do tema (medicina); não trata influência social/dinâmica de opinião |
| 7 | 2020 | Thresholds for ecological responses to global change do not emerge from empirical data | W3049046061 | não relevante: fora do tema (ecologia); não trata influência social/dinâmica de opinião |
| 8 | 2014 | Big Data: New Tricks for Econometrics | W2155419203 | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 9 | 2020 | A review of vibration-based damage detection in civil structures: From traditional methods to Machine Learning and  | W3016123475 | não relevante: fora do tema (engenharia); não trata influência social/dinâmica de opinião |
| 10 | 2018 | Social motivations of live-streaming viewer engagement on Twitch | W2794283760 | não relevante: fora do tema (mídia); não trata influência social/dinâmica de opinião |
| 11 | 2015 | Climate Change 2014 - Synthesis Report | W2513922847 | não relevante: fora do tema (clima); não trata influência social/dinâmica de opinião |
| 12 | 2015 | Computational Fluid Dynamics for urban physics: Importance, scales, possibilities, limitations and ten tips and tri | W2082154841 | não relevante: fora do tema (dinâmica de fluidos); não trata influência social/dinâmica de opinião |
| 13 | 2020 | Temporal signal and the phylodynamic threshold of SARS-CoV-2 | W3065795114 | não relevante: fora do tema (filodinâmica); não trata influência social/dinâmica de opinião |
| 14 | 2017 | Assessing the impacts of 1.5 °C global warming – simulation protocol of the Inter-Sectoral Impact Model Intercompar | W2537682884 | não relevante: fora do tema (clima); não trata influência social/dinâmica de opinião |
| 15 | 2010 | On making causal claims: A review and recommendations | W2098756964 | não relevante: recomendações sobre alegações causais; sem modelo de influência |
| 16 | 2012 | Years lived with disability (YLDs) for 1160 sequelae of 289 diseases and injuries 1990–2010: a systematic analysis  | W2108344016 | não relevante: fora do tema (epidemiologia); não trata influência social/dinâmica de opinião |
| 17 | 2017 | A tutorial on modeling and analysis of dynamic social networks. Part I | W3083024126 | não relevante: tutorial de modelos de redes sociais dinâmicas (dinâmica de opinião sem erro de resposta nem nulo de persistência) |
| 18 | 2021 | Review of deep learning: concepts, CNN architectures, challenges, applications, future directions | W3140854437 | não relevante: fora do tema (aprendizado profundo); não trata influência social/dinâmica de opinião |
| 19 | 2020 | Modelling the COVID-19 epidemic and implementation of population-wide interventions in Italy | W3018782651 | não relevante: fora do tema (epidemiologia); não trata influência social/dinâmica de opinião |
| 20 | 2016 | Detection and attribution of climate extremes in the observed record | W2278233808 | não relevante: fora do tema (clima); não trata influência social/dinâmica de opinião |

</details>

### Semantic Scholar

| Consulta | Data (UTC) | HTTP | Contagem | Retornados |
| --- | --- | --- | --- | --- |
| Q01 | None | 200 | 13623 | 20 |
| Q02 | None | 200 | 10725 | 20 |
| Q03 | None | 200 | 1437 | 20 |
| Q04 | None | 429 | — | 0 |
| Q05 | None | 200 | 21048 | 20 |
| Q06 | None | 200 | 391 | 20 |
| Q07 | None | 200 | 248 | 20 |
| Q08 | None | 429 | — | 0 |
| Q09 | None | 200 | 252 | 20 |
| Q10 | None | 200 | 1099 | 20 |

<details><summary>Q01 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2022 | Propagation of measurement error in opinion dynamics models: The case of the Deffuant model | 10.1016/j.physa.2022.127993 | relevante: dinâmica de opinião com erro de medida (ruído, binning, distorção) no Deffuant; lido e incluído como linha 17 |
| 2 | 2020 | The Impact of Measurement Error on Wage Decompositions: Evidence From the British Household Panel Survey and t | 10.1177/0049124117701476 | não relevante: fora do tema (economia/salários); não trata influência social/dinâmica de opinião |
| 3 | 2023 | Effects of mixing modes on nonresponse and measurement error in an economic panel survey | 10.1186/s12651-022-00328-1 | não relevante: modos de coleta e erro de medida em painel econômico; sem dinâmica de opinião |
| 4 | 2017 | Consistent Estimation of Linear Panel Data Models with Measurement Error | 10.1016/J.JECONOM.2017.06.003 | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 5 | 2023 | Calibrating an Opinion Dynamics Model to Empirical Opinion Distributions and Transitions | 10.18564/jasss.5204 | relevante (já na matriz): Gestefeld–Lorenz, linha 6 |
| 6 | 2024 | Learning Opinion Dynamics from Data | 10.1145/3616855.3635729 | não relevante: tese sobre estimação por verossimilhança de ABM de opinião; coberta por Lenti et al. (linha 15) |
| 7 | 2025 | Modeling public opinion dynamics in social networks using a GAN-SEIR framework | 10.1007/s13278-025-01426-x | não relevante: modelo GAN-SEIR de opinião pública; sem erro de resposta nem nulo de persistência |
| 8 | 2015 | Identification and estimation of nonparametric panel data regressions with measurement error | 10.1920/WP.CEM.2015.3415 | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 9 | 2025 | Does AI vibrancy reshape employment structures and unemployment? Short-run evidence from global panel data | 10.14254/1795-6889.2025.21-2.11 | não relevante: fora do tema (economia); não trata influência social/dinâmica de opinião |
| 10 | 2016 | Earnings Dynamics and Measurement Error in Matched Survey and Administrative Data | 10.1080/07350015.2018.1514308 | não relevante: fora do tema (economia do trabalho); não trata influência social/dinâmica de opinião |
| 11 | 2025 | The Concentration of AI Talent as an Industrial Strategy: A Cross-Country Panel Data Analysis Applied to Finan | 10.56294/dm20251144 | não relevante: fora do tema (economia); não trata influência social/dinâmica de opinião |
| 12 | 2018 | Comparing retrospective and panel data collection methods to assess labor market dynamics | 10.1186/S40176-018-0125-7 | não relevante: fora do tema (economia do trabalho); não trata influência social/dinâmica de opinião |
| 13 | 2023 | Opinion Instability and Measurement Errors: A G-Theory Analysis of College Students | arXiv:2306.17311 | não relevante: instabilidade de opinião vs. erro de medida (teoria G) sem influência social; tema coberto por Hill–Kriesi e Kiley–Vaisey |
| 14 | 2026 | OpenNOD: Modeling Event-Driven Opinion Dynamics in Open Social Networks | 10.1109/TBDATA.2025.3650059 | não relevante: dinâmica de opinião em redes abertas orientada a eventos; sem erro de resposta nem nulo |
| 15 | 2017 | Many IVs Estimation of Dynamic Panel Regression Models with Measurement Error | 10.1016/J.JECONOM.2017.06.009 | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 16 | 2019 | Bayesian Estimation of Panel Count Data Models: Dynamics, Latent Heterogeneity, Serial Error Correlation, and  | 10.1016/B978-0-12-814367-4.00006-X | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 17 | 2017 | An efficient algorithm for extracting the magnitude of the measurement error for fractional dynamics. | 10.1039/c7cp04464j | não relevante: fora do tema (física/química); não trata influência social/dinâmica de opinião |
| 18 | 2023 | How Does Persuasion Happen? A Novel Bounded Confidence Opinion Dynamics Model Based on Social Judgment Theory | 10.1109/JSYST.2022.3205724 | não relevante: modelo de confiança limitada (julgamento social); sem erro de resposta nem nulo |
| 19 | 2014 | Measurement Error in Panel Data | 10.1093/OXFORDHB/9780199940042.013.0011 | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 20 | 2013 | Measurement Error in the Linear Dynamic Panel Data Model | 10.1007/978-1-4614-6871-4_4 | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q02 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2025 | Mobile Banking Adoption: A Multi-Factorial Study on Social Influence, Compatibility, Digital Self-Efficacy, an | 10.3390/jtaer20030192 | não relevante: fora do tema (adoção de tecnologia); não trata influência social/dinâmica de opinião |
| 2 | 2026 | Influence of Social Relationship Disruption on the Depression of Chinese Older Adults: A Study Based on the Ch | 10.1080/01634372.2026.2642772 | não relevante: fora do tema (adoção de tecnologia); não trata influência social/dinâmica de opinião |
| 3 | 2022 | A longitudinal study of vaccine hesitancy attitudes and social influence as predictors of COVID-19 vaccine upt | 10.1080/21645515.2022.2043102 | não relevante: influência social percebida como preditor de vacinação; sem modelo dinâmico nem erro |
| 4 | 2025 | Does Social Health Insurance Influence Cognitive Impairments Among Older People? Evidence from Longitudinal Su | 10.1080/08959420.2025.2461943 | não relevante: fora do tema (saúde); não trata influência social/dinâmica de opinião |
| 5 | 2022 | Dynamics between perceived social support and study engagement among primary school students: A three-year lon | 10.1007/s11218-022-09734-2 | não relevante: fora do tema (educação); não trata influência social/dinâmica de opinião |
| 6 | 2026 | The Influence Of Perceived Ease Of Use, Perceived Security And Social Influence On Buying Behavior In Investme | 10.30989/ijess.v4i1.2059 | não relevante: fora do tema (finanças); não trata influência social/dinâmica de opinião |
| 7 | 2020 | Continuous participation in social activities as a protective factor against depressive symptoms among older a | 10.1080/13607863.2020.1822283 | não relevante: fora do tema (saúde); não trata influência social/dinâmica de opinião |
| 8 | 2020 | Life-History Factors Influence Teenagers’ Suicidal Ideation: A Model Selection Analysis of the Canadian Nation | 10.1177/1474704920939521 | não relevante: fora do tema (saúde); não trata influência social/dinâmica de opinião |
| 9 | 2017 | Are there differences in responses to social identity questions in face-to-face versus telephone interviews? R | 10.1080/13645579.2016.1165495 | não relevante: modo de entrevista e respostas; sem dinâmica de opinião |
| 10 | 2026 | Social influence on women’s contraceptive use: Population-based, sociocentric network study in rural Uganda | 10.1016/j.socscimed.2026.119145 | não relevante: rede sociocêntrica e contracepção; influência observada, sem painel com canal de erro |
| 11 | 2020 | The impact of COVID-19 on smoking patterns in Pakistan: findings from a longitudinal survey of smokers | 10.1093/ntr/ntaa207 | não relevante: fora do tema (saúde); não trata influência social/dinâmica de opinião |
| 12 | 2025 | The Influence of Service Quality on Customer Retention (A Survey on Customers of Keziaspot East Jakarta) | 10.59141/jrssem.v5i1.1001 | não relevante: fora do tema (marketing); não trata influência social/dinâmica de opinião |
| 13 | 2025 | Development and Evaluation of a Survey Instrument: Investigating the Influence of Social Media on Body Image P | 10.18178/ijssh.2025.15.2.1241 | não relevante: fora do tema (psicometria); não trata influência social/dinâmica de opinião |
| 14 | 2025 | Acceptance and Use of Technology on Digital Learning Resource Utilization and Digital Literacy Among Chinese E | 10.3390/bs15060728 | não relevante: fora do tema (educação); não trata influência social/dinâmica de opinião |
| 15 | 2021 | MANAGER’S SOCIAL INFLUENCE ON AGGRESSION MANAGEMENT AND ORGANISATIONAL COMMITMENT | 10.24191/smrj.v18i2.14885 | não relevante: fora do tema (gestão); não trata influência social/dinâmica de opinião |
| 16 | 2025 | THE INFLUENCE OF SOCIAL SUPPORT AND SPIRITUALITY WITH QUARTER LIFE CRISIS IN PRISONERS | 10.61796/icossh.v2i3.94 | não relevante: fora do tema (psicologia); não trata influência social/dinâmica de opinião |
| 17 | 2025 | The Influence of Right Speech (Samma Vaca) on the Communication Ethics of Buddhist Students on Social Media | 10.60046/jocrss.v3i1.217 | não relevante: fora do tema (comunicação); não trata influência social/dinâmica de opinião |
| 18 | 2025 | The Influence of Government Accounting Standards and Human Resource Competence on the Quality of Financial Sta | 10.47772/ijriss.2025.908000279 | não relevante: fora do tema (contabilidade); não trata influência social/dinâmica de opinião |
| 19 | 2025 | Influence of Social Media Platforms on the Purchase Decisions of Luxury Apparel | 10.34190/ecsm.12.1.3464 | não relevante: fora do tema (marketing); não trata influência social/dinâmica de opinião |
| 20 | 2017 | Likes - The key to my happiness: The moderating effect of social influence on travel experience | 10.1016/j.im.2017.04.003 | não relevante: fora do tema (turismo); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q03 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2025 | Bias and Identifiability in the Bounded Confidence Model | arXiv:2506.11751 | relevante (já na matriz): Borile et al., linha 14 |
| 2 | 2022 | A geospatial bounded confidence model including mega-influencers with an application to Covid-19 vaccine hesit | arXiv:2210.08012 | não relevante: BCM geoespacial com megainfluenciadores; sem erro de resposta nem nulo de persistência |
| 3 | 2025 | Increased risk of herpes zoster associated with stress and sleep deprivation: Evidence from korea health panel | 10.1016/j.jpsychires.2025.03.015 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 4 | 2025 | Speech-Language Therapists' Training, Confidence, and Barriers When Serving Bilingual Children: Development an | 10.1044/2025_AJSLP-24-00498 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 5 | 2023 | Sleep duration, sleep quality and the risk of being obese: Evidence from the Australian panel survey. | 10.1016/j.sleep.2023.06.012 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 6 | 2025 | From institutional trust to digital literacy: Socioeconomic and political determinants of COVID-19 vaccine hes | 10.1080/21645515.2025.2533639 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 7 | 2025 | Social ties, employment and mental health in people with disabilities in Korea: evidence from a 2016–2018 pane | 10.1093/inthealth/ihaf078 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 8 | 2025 | Economic Burden of Urinary Incontinence in Men with Prostate Cancer: Results from the Medical Expenditure Pane | 10.1016/j.urology.2025.09.014 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 9 | 2025 | Prognostic factors for early identification of asthma: Analysis of the Korean Health Panel Survey (2014–2018) | 10.1097/MD.0000000000045378 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 10 | 2026 | Patterns and determinants of formal healthcare utilisation among individuals with and without proxy-identified | 10.1371/journal.pmen.0000644 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 11 | 2022 | Factors Affecting Korean Medicine Health Care Use for Functional Dyspepsia: Analysis of the Korea Health Panel | 10.3390/healthcare10071192 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 12 | 2023 | Backward assessments or expectations: what determines the consumer confidence index more strongly? Panel model | 10.59139/ws.2023.02.1 | não relevante: fora do tema (economia (painel)); não trata influência social/dinâmica de opinião |
| 13 | 2025 | Association Between Informal Caregiving and Changes in Cardiovascular-related Health Behaviors Among Middle-ag | 10.2188/jea.JE20240197 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 14 | 2023 | Association between pain burden and presence of any limitation among older adults (≥50 years of age) with pain | 10.1097/MD.0000000000034863 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 15 | 2024 | Allopurinol Adherence in US Patients with Gout: Analysis of the Medical Expenditure Panel Survey, 2018–2021 | 10.1097/RHU.0000000000002177 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 16 | 2024 | Food Security and Mental Health in the United States: Evidence from the Medical Expenditure Panel Survey. | fedec046935d | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 17 | 2021 | Changes in child abuse experience associated to sleep quality: results of the Korean Children & Youth Panel Su | 10.1186/s12889-021-11309-3 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 18 | 2023 | Productivity Loss Among Opioid and Benzodiazepine Users in the United States: A Medical Expenditure Panel Surv | 10.1097/JOM.0000000000003029 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 19 | 2026 | Primary Care Utilization After Pregnancies Complicated by Hypertension and Diabetes: An Analysis of the Medica | 10.1016/j.whi.2026.05.001 | não relevante: fora do tema (saúde (painel)); não trata influência social/dinâmica de opinião |
| 20 | 2024 | Inconsistencies in self-reported diabetes in a large panel study: the Survey of Health, Ageing and Retirement  | 10.1186/s12874-023-02137-7 | não relevante: inconsistência de autorrelato em painel de saúde; erro de resposta sem dinâmica de opinião |

</details>

<details><summary>Q05 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2022 | The joint influence of estimation of sensitive variable under measurement error and non-response using OR | 10.1080/00949655.2022.2075362 | não relevante: fora do tema (amostragem de variáveis sensíveis); não trata influência social/dinâmica de opinião |
| 2 | 2023 | Local influence in linear mixed measurement error models with ridge estimation | 10.1080/03610918.2023.2205063 | não relevante: fora do tema (modelos de erro de medida mistos); não trata influência social/dinâmica de opinião |
| 3 | 2024 | Functional partially linear single index models with measurement error in both functional and real covari | 10.1080/03610918.2024.2407880 | não relevante: fora do tema (estatística funcional); não trata influência social/dinâmica de opinião |
| 4 | 2024 | LC dynamic signal modeling and analysis of resonant frequency measurement error under rapid eye movements | 10.1088/1361-6501/ad89eb | não relevante: fora do tema (sensores médicos); não trata influência social/dinâmica de opinião |
| 5 | 2026 | Robust and Machine Learning Augmented Estimation of Finite-Population Variance using Auxiliary Informatio | 10.71317/jgst.2.9.2026.547 | não relevante: fora do tema (amostragem); não trata influência social/dinâmica de opinião |
| 6 | 2022 | Using Randomized Response to Estimate the Population Mean of a Sensitive Variable under the Influence of  | 10.1007/s42519-022-00251-1 | não relevante: fora do tema (resposta aleatorizada); não trata influência social/dinâmica de opinião |
| 7 | 2025 | Examiner experience moderates reliability of human lower extremity muscle ultrasound measurement – a doub | 10.1186/s13089-025-00424-6 | não relevante: fora do tema (ultrassom); não trata influência social/dinâmica de opinião |
| 8 | 2022 | Social Influence Network Simulation Design Affects Behavior of Aggregated Entropy | 10.1109/tcss.2021.3092694 | não relevante: desenho de simulação de rede de influência e entropia agregada; sem erro de resposta nem nulo de persistência |
| 9 | 2025 | Analysis of random error influencing factors in the three-point method for center of mass measurement | 10.1088/1361-6501/addf67 | não relevante: fora do tema (metrologia); não trata influência social/dinâmica de opinião |
| 10 | 2025 | Simultaneous variable selection and parameters estimation for longitudinal data subject to missingness an | 10.1080/03610918.2024.2333355 | não relevante: fora do tema (dados longitudinais com faltantes (bioestatística)); não trata influência social/dinâmica de opinião |
| 11 | 2021 | Influence measures and outliers detection in linear mixed measurement error models with Ridge estimation | 10.1080/03610918.2021.1926502 | não relevante: fora do tema (diagnóstico de influência em regressão); não trata influência social/dinâmica de opinião |
| 12 | 2025 | Performance Study of the Six-Component Piezoelectric Helicopter Rotor Balance Vector Test System Consider | 10.1109/TIM.2025.3593559 | não relevante: fora do tema (engenharia); não trata influência social/dinâmica de opinião |
| 13 | 2025 | Measurement error compensation method for TDOA-based localization under non-line-of-sight conditions | 10.1088/1361-6501/adc760 | não relevante: fora do tema (localização por sensores); não trata influência social/dinâmica de opinião |
| 14 | 2024 | Performance evaluation of extended EWMA control chart in the presence of measurement error | 10.1080/03610918.2024.2408624 | não relevante: fora do tema (controle de qualidade); não trata influência social/dinâmica de opinião |
| 15 | 2022 | Sample size recommendations for studies on reliability and measurement error: an online application based | 10.1007/s10742-022-00293-9 | não relevante: tamanho amostral para estudos de confiabilidade (clínico); sem influência social |
| 16 | 2017 | Mean shift and influence measures in linear measurement error models with stochastic linear restrictions | 10.1080/03610918.2015.1122047 | não relevante: fora do tema (regressão com erro de medida); não trata influência social/dinâmica de opinião |
| 17 | 2022 | A 3D radius compensation method to reduce the influence of probe fluctuation error in blade space curve m | 10.1088/1361-6501/ac9db0 | não relevante: fora do tema (metrologia); não trata influência social/dinâmica de opinião |
| 18 | 2020 | Sensitivity analysis for network observations with applications to inferences of social influence effects | 10.1017/nws.2020.36 | relevante: erro/viés na rede observada em inferências de influência social; incluído como linha 18 (resumo) |
| 19 | 2018 | Credibly Identifying Social Effects: Accounting for Network Formation and Measurement Error | 10.1111/JOES.12256 | relevante: identificação de efeitos sociais com rede endógena e erro de medida da rede; incluído como linha 19 (resumo) |
| 20 | 2021 | Online Smart Meter Measurement Error Estimation Based on EKF and LMRLS Method | 10.1109/TSG.2021.3077693 | não relevante: fora do tema (redes elétricas); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q06 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2023 | Opinion Dynamics and Social Group Information Efficiency: an agent-based model | 10.18254/s207751800028247-0 | não relevante: ABM de opinião e eficiência informacional; sem erro de resposta nem nulo |
| 2 | 2026 | Selecting a Simulation Runtime for Opinion Dynamics: Evaluating Elixir for Agent-Based Models | 10.55056/ceur-ws.org/vol-4164/paper14.pdf | não relevante: fora do tema (software de simulação); não trata influência social/dinâmica de opinião |
| 3 | 2020 | An agent-based model of multi-dimensional opinion dynamics and opinion alignment | arXiv:2003.05929 | não relevante: ABM de opinião multidimensional; sem erro nem nulo |
| 4 | 2023 | Studying Narrative Economics by Adding Continuous-Time Opinion Dynamics to an Agent-Based Model of Co-Evolutio | 10.2139/ssrn.4316574 | não relevante: fora do tema (economia narrativa); não trata influência social/dinâmica de opinião |
| 5 | 2024 | Abstract TP25: Model-Free Dynamic Contrast-Enhanced MRI in Cerebral Small Vessel Disease: Test-Retest Reliabil | 10.1161/str.55.suppl_1.tp25 | não relevante: fora do tema (medicina); não trata influência social/dinâmica de opinião |
| 6 | 2025 | Short-term and long-term test-retest reliability of memory, complexity, and randomness of EEG microstates sequ | 10.1007/s11571-025-10391-2 | não relevante: fora do tema (neurociência); não trata influência social/dinâmica de opinião |
| 7 | 2024 | An Exploration of Drivers of Opinion Dynamics | 10.18564/jasss.5212 | não relevante: exploração de determinantes de dinâmica de opinião; sem erro de resposta nem nulo de persistência |
| 8 | 2026 | Opinion Dynamics in Repeated Interaction Experiments | 10.2139/ssrn.6576098 | não relevante: experimento de interação repetida com exposição observada; sem painel observacional nem erro de resposta |
| 9 | 2024 | 446 A stochastic, dynamic agent-based model of swine nutrient requirements for the growing finishing productio | 10.1093/jas/skae234.291 | não relevante: fora do tema (zootecnia); não trata influência social/dinâmica de opinião |
| 10 | 2016 | Quantitative Agent Based Model of Opinion Dynamics: Polish Elections of 2015 | 10.1371/journal.pone.0155098 | não relevante: ABM quantitativo de eleições; sem erro de resposta nem nulo |
| 11 | 2018 | Selecting Information in Financial Markets Herding and Opinion Swings in a Heterogeneous Mimetic Rational Agen | 10.1007/978-3-319-96661-8_12 | não relevante: fora do tema (finanças); não trata influência social/dinâmica de opinião |
| 12 | 2025 | Unveiling Agents’ Confidence in Opinion Dynamics Models via Graph Neural Networks | 10.1109/TCSS.2024.3508452 | não relevante: inferência de confiança de agentes por GNN; sem erro de resposta nem nulo |
| 13 | 2020 | A Mathematical Model to determine the Reliability Percentage of a Statement using the Bounded Confidence of Op | 10.1109/ICOSEC49089.2020.9215409 | não relevante: confiabilidade de afirmação via BCM; sem painel |
| 14 | 2021 | Natural-Language Multi-Agent Simulations of Argumentative Opinion Dynamics | arXiv:2104.06737 | não relevante: simulação multiagente com linguagem natural; sem erro nem nulo |
| 15 | 2026 | Towards Agentic Agent-based Models: Feasibility, Performance, and Statistical Model Checking | arXiv:2607.17948 | não relevante: fora do tema (ABM com LLM); não trata influência social/dinâmica de opinião |
| 16 | 2026 | A tube-restriction test: A candidate impulsivity-related assay based on nose-poke behavior dynamics. | 10.1016/j.jneumeth.2026.110912 | não relevante: fora do tema (neurociência); não trata influência social/dinâmica de opinião |
| 17 | 2026 | LLM-Agent-based Social Simulation for Attitude Diffusion | arXiv:2604.03898 | não relevante: simulação social com agentes LLM; sem erro de resposta nem nulo |
| 18 | 2026 | Toward Verifiable Audience Digital Twins: An Agent-Based Architecture Integrating COM-B and ELM | 10.5220/0015183700004094 | não relevante: fora do tema (ABM com LLM/marketing); não trata influência social/dinâmica de opinião |
| 19 | 2020 | Supporting Policy Design for the Diffusion of Cleaner Technologies: A Spatial Empirical Agent-Based Model | 10.3390/IJGI9100581 | não relevante: fora do tema (difusão tecnológica); não trata influência social/dinâmica de opinião |
| 20 | 2022 | Using agent-based modeling to compare corrective actions for Listeria contamination in produce packinghouses | 10.1371/journal.pone.0265251 | não relevante: fora do tema (segurança alimentar); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q07 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2025 | Modified Kumaraswamy seasonal autoregressive moving average models with exogenous regressors for double-bounde | 10.1371/journal.pone.0324721 | não relevante: fora do tema (séries temporais); não trata influência social/dinâmica de opinião |
| 2 | 2026 | SpecBound: Adaptive Bounded Self-Speculation with Layer-wise Confidence Calibration | arXiv:2604.12247 | não relevante: fora do tema (LLM); não trata influência social/dinâmica de opinião |
| 3 | 2017 | Bounded random walks as a null model for evaluating population trends | 10.1007/s10144-017-0574-5 | não relevante: passeio aleatório limitado como nulo de tendências populacionais (ecologia); sem influência social |
| 4 | 2026 | MDM-ASR: Bridging Accuracy and Efficiency in ASR with Diffusion-Based Non-Autoregressive Decoding | arXiv:2602.18952 | não relevante: fora do tema (reconhecimento de fala); não trata influência social/dinâmica de opinião |
| 5 | 2023 | The Impact of Economic Growth on Poverty Reduction in Kenya: Empirical Analysis Using Autoregressive Distribut | 10.47191/ijmei/v9i2.04 | não relevante: fora do tema (economia); não trata influência social/dinâmica de opinião |
| 6 | 2026 | Raw CVE/CWE Retrieval Does Not Improve LLM-Based Vulnerability Detection in Python: A Pre-Specified Null Resul | 10.3390/jcp6050163 | não relevante: fora do tema (segurança de LLM); não trata influência social/dinâmica de opinião |
| 7 | 2026 | Adaptive Confidence Intervals in Efron's Gaussian Two-Groups Model | arXiv:2604.26992 | não relevante: fora do tema (estatística); não trata influência social/dinâmica de opinião |
| 8 | 2019 | Adaptive consistent unit root tests based on autoregressive threshold model | 9cb3b97224fe | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 9 |  | Robust conﬁdence interval for random coeﬃcient autoregressive model with bootstrap method | 5fdb0f195069 | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 10 | 2026 | Consumer Confidence, Islamic Msme Financing, Inflation, Ramadan, And Real Sales: ARDL | 10.55606/sscj-amik.v4i2.6141 | não relevante: fora do tema (economia); não trata influência social/dinâmica de opinião |
| 11 | 2022 | Analysis of zero-and-one inflated bounded count time series with applications to climate and crime data | 10.1007/s11749-022-00825-y | não relevante: fora do tema (séries temporais); não trata influência social/dinâmica de opinião |
| 12 | 2022 | Fisher's disjunction as the principle vindicating p-values, confidence intervals, and their generalizations: A | 10.1016/j.ijar.2022.12.005 | não relevante: fora do tema (estatística); não trata influência social/dinâmica de opinião |
| 13 | 2026 | Minimax optimal submatrix detection: Sharp non-asymptotic rates | arXiv:2605.09569 | não relevante: fora do tema (estatística); não trata influência social/dinâmica de opinião |
| 14 | 2015 | Differentially Private Least Squares: Estimation, Confidence and Rejecting the Null Hypothesis | 05cfe249e88a | não relevante: fora do tema (privacidade diferencial); não trata influência social/dinâmica de opinião |
| 15 | 2015 | Differentially Private Ordinary Least Squares: $t$-Values, Confidence Intervals and Rejecting Null-Hypotheses | 45f6db8d8a1a | não relevante: fora do tema (privacidade diferencial); não trata influência social/dinâmica de opinião |
| 16 | 2022 | Autoregressive Uncertainty Modeling for 3D Bounding Box Prediction | arXiv:2210.07424 | não relevante: fora do tema (visão computacional); não trata influência social/dinâmica de opinião |
| 17 | 2020 | Forecasting based on an ensemble Autoregressive Moving Average - Adaptive neuro - Fuzzy inference system – Neu | 10.1016/j.energy.2020.117159 | não relevante: fora do tema (previsão energética); não trata influência social/dinâmica de opinião |
| 18 | 2012 | On Confidence Intervals for Autoregressive Roots and Predictive Regression | 10.2139/SSRN.2150172 | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 19 | 2026 | Certified Predictive Value-of-Advice Gating for Cost-Aware Language-Model Guidance in Reinforcement Learning | arXiv:2609.29548 | não relevante: fora do tema (aprendizado por reforço); não trata influência social/dinâmica de opinião |
| 20 | 2012 | Adjusted Confidence Intervals for a Bounded Parameter | 10.1007/s10519-012-9560-z | não relevante: fora do tema (genética); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q09 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2025 | Credibility study of vehicle dynamics model based on virtual-reality fusion test | 10.1088/1742-6596/3126/1/012051 | não relevante: fora do tema (engenharia automotiva); não trata influência social/dinâmica de opinião |
| 2 | 2026 | VALIDATION OF A 12-DOF TRACTOR-SEMITRAILER LONGITUDINAL MODEL USING EXPERIMENTAL DATA FOR LOAD TRANSFER A | 10.54554/jmet.2025.17.01.004 | não relevante: fora do tema (engenharia automotiva); não trata influência social/dinâmica de opinião |
| 3 | 2021 | Early predictions of response and survival from a tumor dynamics model in patients with recurrent, metast | 10.1002/psp4.12594 | não relevante: fora do tema (oncologia); não trata influência social/dinâmica de opinião |
| 4 | 2025 | Effects of Long-Term Air Pollution Exposure on Disease Outcomes and Hybrid Immune Responses in SARS-CoV-2 | 10.1289/EHP15660 | não relevante: fora do tema (epidemiologia); não trata influência social/dinâmica de opinião |
| 5 | 2026 | Digital Twins for Opinion Dynamics: A Generative LLM Framework for Social Networks | arXiv:2609.19913 | não relevante: gêmeos digitais de opinião com LLM; sem erro de resposta nem nulo de persistência |
| 6 | 2019 | Establishment and validation of a locomotive–track coupled spatial dynamics model considering dynamic eff | 10.1016/J.YMSSP.2018.09.032 | não relevante: fora do tema (engenharia ferroviária); não trata influência social/dinâmica de opinião |
| 7 | 2025 | An entropy-initiated coupled-trait ODE framework for modeling longitudinal cohort dynamics | arXiv:2506.20622 | não relevante: ODE para dados de coorte longitudinais; sem influência social |
| 8 | 2026 | Longitudinal monitoring of twenty homes reveals spatiotemporal dynamics which require new models of disco | 10.1038/s41598-025-32727-y | não relevante: fora do tema (energia); não trata influência social/dinâmica de opinião |
| 9 | 2026 | PSO-Based Optimal Tuning of P, PI, PD, and PID Controllers for Aircraft Longitudinal Dynamics: A Comparat | 10.38124/ijisrt/26may130 | não relevante: fora do tema (controle aeronáutico); não trata influência social/dinâmica de opinião |
| 10 | 2025 | Validation of a Small UAV Dynamic Model Using CFD and Flight Test Data | 10.3311/pptr.41190 | não relevante: fora do tema (aeronáutica); não trata influência social/dinâmica de opinião |
| 11 | 2024 | DYnamics of Contraception in Eswatini (DYCE): protocol for a high-frequency, longitudinal cell phone surv | 10.1136/bmjopen-2024-090686 | não relevante: fora do tema (saúde reprodutiva (protocolo)); não trata influência social/dinâmica de opinião |
| 12 | 2026 | Trim-Point Stability Assessment and Fault-Tolerant Control Validation of a FW-eVTOL Aircraft | 10.1109/RAST69551.2026.11672457 | não relevante: fora do tema (aeronáutica); não trata influência social/dinâmica de opinião |
| 13 | 2024 | Model Predictive Control with Powertrain Delay Consideration for Longitudinal Speed Tracking of Autonomou | 10.3390/wevj15100433 | não relevante: fora do tema (veículos autônomos); não trata influência social/dinâmica de opinião |
| 14 | 2021 | Data-driven vehicle modeling of longitudinal dynamics based on a multibody model and deep neural networks | 10.1016/J.MEASUREMENT.2021.109541 | não relevante: fora do tema (engenharia automotiva); não trata influência social/dinâmica de opinião |
| 15 | 1998 | LOGISTIC MODELLING OF LONGITUDINAL SURVEY DATA WITH MEASUREMENT ERROR | not-printed:Q09:15 | não relevante: regressão logística com erro de medida em survey longitudinal (1998); sem influência social |
| 16 | 2013 | Modelling Optimum Response in a Longitudinal Survey | not-printed:Q09:16 | não relevante: fora do tema (desenho de survey longitudinal); não trata influência social/dinâmica de opinião |
| 17 | 2016 | A General Social Agent-Based Model of Opinion Dynamics with Applications to STEM Education and Radicaliza | not-printed:Q09:17 | não relevante: ABM geral de opinião com aplicações; sem erro de resposta nem nulo de persistência |
| 18 | 2026 | Adaptive Control of Negative Emotion Propagation in Public Opinion: A Hybrid Approach Integrating Stochas | 10.1109/TNSE.2026.3703066 | não relevante: controle de propagação de emoções em opinião online; sem painel com erro |
| 19 | 2026 | Preliminary Validation of a Safety Culture Maturity Measurement Model and Conceptual Roadmap for Garment  | 10.56338/mppki.v9i9.10864 | não relevante: fora do tema (cultura de segurança); não trata influência social/dinâmica de opinião |
| 20 | 2021 | Hidden Markov models for longitudinal rating data with dynamic response styles | arXiv:2111.13370 | não relevante: HMM para avaliações longitudinais com estilos de resposta dinâmicos; erro de resposta sem influência social |

</details>

<details><summary>Q10 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2026 | A three-way dynamic panel threshold regression model for change point detection in bioimpedance data | 10.1007/s10260-026-00842-3 | não relevante: fora do tema (bioimpedância); não trata influência social/dinâmica de opinião |
| 2 | 2026 | Simulation Study on Peak Path of Tourism Carbon Emissions Introduced by System Dynamics and Panel Th | 10.7716/aem.v15i3.4039 | não relevante: fora do tema (emissões de turismo); não trata influência social/dinâmica de opinião |
| 3 | 2024 | Prediction of Social Influence in Social Networks | 10.1109/iThings-GreenCom-CPSCom-SmartData-Cybermatics62450.2024.00046 | não relevante: predição de influência em redes sociais online; sem painel com erro de resposta nem nulo de persistência |
| 4 | 2026 | Variance-aware penalized panel models for temporal risk detection from wearable sensor data. | 10.1186/s12967-026-08652-7 | não relevante: fora do tema (sensores vestíveis); não trata influência social/dinâmica de opinião |
| 5 | 2024 | Semantic Segmentation-Based Intelligent Threshold-Free Feeder Detection Method for Single-Phase Grou | 10.1109/TIM.2023.3335520 | não relevante: fora do tema (sistemas elétricos); não trata influência social/dinâmica de opinião |
| 6 | 2024 | Assessing the Influence of Sensor-Induced Noise on Machine-Learning-Based Changeover Detection in CN | 10.3390/s24020330 | não relevante: fora do tema (manufatura); não trata influência social/dinâmica de opinião |
| 7 | 2024 | The Improvement of wavelet threshold method and its application in geological radar detection | 10.1109/ICIPS64173.2024.10900317 | não relevante: fora do tema (geofísica); não trata influência social/dinâmica de opinião |
| 8 | 2025 | Estimation of common breaks in linear panel data models via screening and ranking algorithm | 10.1038/s41598-025-96322-x | não relevante: fora do tema (econometria de quebras); não trata influência social/dinâmica de opinião |
| 9 | 2017 | Social influence determination on big data streams in an online social network | 10.1007/s11042-017-4890-8 | não relevante: determinação de influência em fluxos de dados de rede online; sem painel com erro |
| 10 | 2026 | Dynamic identity management in online health communities: How illness stage moderates the effects of | 10.1177/20552076261460659 | não relevante: fora do tema (saúde online); não trata influência social/dinâmica de opinião |
| 11 | 2017 | Social influence determination on big data streams in an online social network | 10.1007/s11042-017-4890-8 | não relevante: duplicata do item 9 no retorno da API |
| 12 | 2026 | Towards efficient optimization of multi-agent social simulation via large language models | 10.1007/s13042-025-02816-5 | não relevante: otimização de simulação social com LLM; sem erro de resposta nem nulo |
| 13 | 2021 | How Does Income Inequality Influence Environmental Regulation in the Context of Corruption? A Panel  | 10.3390/ijerph18158050 | não relevante: fora do tema (economia ambiental); não trata influência social/dinâmica de opinião |
| 14 | 2026 | Factors that influence acute malnutrition detection and treatment by community health promoters in S | 10.1371/journal.pgph.0005689 | não relevante: fora do tema (saúde pública); não trata influência social/dinâmica de opinião |
| 15 | 2025 | Social Robots for Bed-Fall Detection in Hospitals | 10.1109/RO-MAN63969.2025.11217811 | não relevante: fora do tema (robótica); não trata influência social/dinâmica de opinião |
| 16 | 2024 | Exploring the nexus of globalization and natural resource scarcity in driving green technology innov | 10.1111/1477-8947.12463 | não relevante: fora do tema (economia ambiental); não trata influência social/dinâmica de opinião |
| 17 | 2024 | Quantile Regression and Homogeneity Identification of a Semiparametric Panel Data Model | 10.1080/10618600.2024.2433672 | não relevante: fora do tema (econometria); não trata influência social/dinâmica de opinião |
| 18 | 2022 | Joint Detection Threshold Optimization and Illumination Time Allocation Strategy for Cognitive Track | 10.1109/TSP.2022.3188205 | não relevante: fora do tema (radar); não trata influência social/dinâmica de opinião |
| 19 | 2024 | Detection and context reconstruction of sub-events that influence the course of a news event from mi | 10.1007/s42001-024-00279-2 | não relevante: fora do tema (detecção de eventos em notícias); não trata influência social/dinâmica de opinião |
| 20 | 2020 | Detection of units with pervasive effects in large panel data models | 10.1016/J.JECONOM.2020.05.001 | não relevante: detecção de unidades com efeitos difusos em painéis (econometria); sem dinâmica de opinião nem erro de resposta |

</details>

### arXiv (busca web; API devolveu 406)

| Consulta | Data (UTC) | HTTP | Contagem | Retornados |
| --- | --- | --- | --- | --- |
| Q01 | None | 200 | 0 | 0 |
| Q02 | None | 200 | 0 | 0 |
| Q03 | None | 200 | 16 | 16 |
| Q04 | None | 200 | 0 | 0 |
| Q05 | None | 200 | 32 | 20 |
| Q06 | None | 200 | 0 | 0 |
| Q07 | None | 200 | 2 | 2 |
| Q08 | None | 200 | 0 | 0 |
| Q09 | None | 200 | 1 | 1 |
| Q10 | None | 200 | 0 | 0 |

<details><summary>Q03 — 16 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2026 | Drift Behavior in a Bounded-Confidence Opinion Model with Media Influence | 2606.28318 | não relevante: deriva em BCM com mídia; sem painel nem erro de resposta |
| 2 | 2026 | Discovery of interaction and diffusion kernels in particle-to-mean-field multi-agent systems | 2603.15927 | não relevante: descoberta de núcleos de interação em campo médio; sem painel nem erro de resposta |
| 3 | 2025 | Bias and Identifiability in the Bounded Confidence Model | 2506.11751 | relevante (já na matriz): Borile et al., linha 14 |
| 4 | 2024 | How social reinforcement learning can lead to metastable polarisation and the voter model | 2406.07993 | não relevante: aprendizado por reforço social e polarização; sem painel nem erro |
| 5 | 2023 | A Unified View on Neural Message Passing with Opinion Dynamics for Social Networks | 2310.01272 | não relevante: fora do tema (redes neurais de grafos); não trata influência social/dinâmica de opinião |
| 6 | 2023 | Likelihood-Based Methods Improve Parameter Estimation in Opinion Dynamics Models | 2310.02766 | relevante (já na matriz): Lenti et al., linha 15 |
| 7 | 2021 | Predicting Users' Value Changes by the Friends' Influence from Social Media Usage | 2109.08021 | não relevante: previsão de valores por influência de amigos em mídia social; sem canal de erro nem nulo |
| 8 | 2021 | The critical behavior of Hegselmann-Krause opinion model with smart agents | 2102.02385 | não relevante: transição crítica no HK; sem dados |
| 9 | 2020 | When open mindedness hinders consensus | 2001.06877 | não relevante: mente aberta e consenso (teoria); sem dados |
| 10 | 2016 | Bounded Confidence under Preferential Flip: A Coupled Dynamics of Structural Balance and Opinions | 1610.02660 | não relevante: BCM com equilíbrio estrutural; sem dados |
| 11 | 2014 | Tricritical points in a Vicsek model of self-propelled particles with bounded confidence | 1406.6921 | não relevante: fora do tema (física de partículas autopropelidas); não trata influência social/dinâmica de opinião |
| 12 | 2012 | Non-conservative kinetic exchange model of opinion dynamics with randomness and bounded confidence | 1205.0211 | não relevante: modelo cinético de opinião; sem dados |
| 13 | 2011 | A bounded confidence approach to understanding user participation in peer production systems | 1107.5620 | não relevante: confiança limitada em produção entre pares; sem erro de resposta |
| 14 | 2010 | The Bounded Confidence Model Of Opinion Dynamics | 1006.3798 | não relevante: revisão do BCM; sem painel |
| 15 | 2010 | How opinion dynamics generates group hierarchies | 1003.3586 | não relevante: hierarquias de grupo; sem dados |
| 16 | 2004 | Modelling Group Opinion Shift to Extreme : the Smooth Bounded Confidence Model | cond-mat/0410199 | não relevante: BCM suave (2004); sem dados |

</details>

<details><summary>Q05 — 20 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2026 | Radicalization Kinetics under Algorithmic Exposure in a Stochastic Multiplex Model of Opinion Dynamics | 2608.10968 | não relevante: radicalização sob exposição algorítmica; sem painel com erro de resposta |
| 2 | 2026 | GraphPolaris: A System for Query, Analysis, and Visualization of Graph Databases | 2607.12845 | não relevante: fora do tema (visualização de grafos); não trata influência social/dinâmica de opinião |
| 3 | 2026 | IMPACTeen: Intentions, Manipulation, Persuasion, Annotations, and Consequences in Teen Communication Dataset | 2606.16910 | não relevante: fora do tema (dados de comunicação adolescente); não trata influência social/dinâmica de opinião |
| 4 | 2026 | Human, AI, and Hybrid Ensembles for Detection of Adaptive, RL-based Social Bots | 2603.23796 | não relevante: fora do tema (detecção de bots); não trata influência social/dinâmica de opinião |
| 5 | 2026 | Conformity Dynamics in LLM Multi-Agent Systems: The Roles of Topology and Self-Social Weighting | 2601.05606 | não relevante: conformidade em sistemas multiagente de LLM |
| 6 | 2025 | The Psychology of Falsehood: A Human-Centric Survey of Misinformation Detection | 2509.15896 | não relevante: fora do tema (desinformação); não trata influência social/dinâmica de opinião |
| 7 | 2025 | Unraveling SITT: Social Influence Technique Taxonomy and Detection with LLMs | 2506.00061 | não relevante: fora do tema (LLM); não trata influência social/dinâmica de opinião |
| 8 | 2025 | Survival Games: Human-LLM Strategic Showdowns under Severe Resource Scarcity | 2505.17937 | não relevante: fora do tema (jogos com LLM); não trata influência social/dinâmica de opinião |
| 9 | 2024 | How the cascade inference problem distorts information diffusion | 2410.21554 | não relevante: problema de inferência de cascatas; difusão, sem erro de resposta nem nulo de persistência |
| 10 | 2024 | A Deep Learning Framework for Evaluating Dynamic Network Generative Models and Anomaly Detection | 2406.11901 | não relevante: fora do tema (modelos generativos de redes); não trata influência social/dinâmica de opinião |
| 11 | 2024 | Social-LLM: Modeling User Behavior at Scale using Language Models and Social Network Data | 2401.00893 | não relevante: fora do tema (modelagem de usuários); não trata influência social/dinâmica de opinião |
| 12 | 2023 | Analyzing User Characteristics of Hate Speech Spreaders on Social Media | 2310.15772 | não relevante: fora do tema (discurso de ódio); não trata influência social/dinâmica de opinião |
| 13 | 2023 | Does society show differential attention to researchers based on gender and field? | 2308.11382 | não relevante: fora do tema (cientometria); não trata influência social/dinâmica de opinião |
| 14 | 2022 | Is Multi-Modal Necessarily Better? Robustness Evaluation of Multi-modal Fake News Detection | 2206.08788 | não relevante: fora do tema (fake news multimodal); não trata influência social/dinâmica de opinião |
| 15 | 2022 | Maximizing the Influence of Bichromatic Reverse k Nearest Neighbors in Geo-Social Networks | 2204.10203 | não relevante: fora do tema (consultas geossociais); não trata influência social/dinâmica de opinião |
| 16 | 2022 | Surf or sleep? Understanding the influence of bedtime patterns on campus | 2202.09283 | não relevante: fora do tema (padrões de sono); não trata influência social/dinâmica de opinião |
| 17 | 2021 | Scaling New Peaks: A Viewership-centric Approach to Automated Content Curation | 2108.04187 | não relevante: fora do tema (curadoria de conteúdo); não trata influência social/dinâmica de opinião |
| 18 | 2020 | Delay-induced periodic behavior in competitive populations | 2008.00257 | não relevante: fora do tema (populações competitivas); não trata influência social/dinâmica de opinião |
| 19 | 2019 | Quantifying Voter Biases in Online Platforms: An Instrumental Variable Approach | 1910.00757 | não relevante: vieses de voto em plataformas (variável instrumental); sem painel com erro |
| 20 | 2019 | The Mass, Fake News, and Cognition Security | 1907.07759 | não relevante: fora do tema (segurança cognitiva); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q07 — 2 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2026 | Krause Synchronization Transformers | 2602.11534 | não relevante: fora do tema (transformers); não trata influência social/dinâmica de opinião |
| 2 | 2026 | MDM-ASR: Bridging Accuracy and Efficiency in ASR with Diffusion-Based Non-Autoregressive Decoding | 2602.18952 | não relevante: fora do tema (reconhecimento de fala); não trata influência social/dinâmica de opinião |

</details>

<details><summary>Q09 — 1 títulos</summary>

| # | Ano | Título | ID | Triagem |
| --- | --- | --- | --- | --- |
| 1 | 2024 | CoDiNG -- Naming Game with Continuous Latent Opinions of Individual Agents | 2406.19204 | relevante (já na matriz): CoDiNG, linha 1 |

</details>

### arXiv API export

| Consulta | Data (UTC) | HTTP | Contagem | Retornados |
| --- | --- | --- | --- | --- |
| Q01 | None | 406 | — | 0 |
| Q02 | None | 406 | — | 0 |
| Q03 | None | 406 | — | 0 |
| Q04 | None | 406 | — | 0 |
| Q05 | None | 406 | — | 0 |
| Q06 | None | 406 | — | 0 |
| Q07 | None | 406 | — | 0 |
| Q08 | None | 406 | — | 0 |
| Q09 | None | 406 | — | 0 |
| Q10 | None | 406 | — | 0 |


## Síntese da busca

Nenhum dos 399 títulos triados estima uma fronteira de detecção de
influência social em função da confiabilidade da resposta, nem compara
trajetórias de painel com uma família de nulos de persistência pareados.
Os três relevantes novos tratam erro de medida em dinâmica de opinião
(Carpentras–Quayle 2022) ou erro na rede observada em inferências de
influência (Xu–Frank; Advani–Malde). Nenhum dos três ocupa a pergunta.

Limites de cobertura:

- As ordenações por relevância do OpenAlex e do Semantic Scholar trouxeram
  pouco material pertinente nos 20 primeiros. Uma parte da literatura
  próxima só apareceu por citação nos documentos de entrada (Moor-Smith–
  Carpentras, Dang–Ma, Ureña-Carrion et al., Gelastopoulos et al., Lersch).
  A busca por palavras-chave, sozinha, seria insuficiente.
- Duas consultas do Semantic Scholar falharam.
- A API do arXiv foi substituída pela busca do site.

A ausência de antecedente nesta busca não prova ausência na literatura.



## Veredito

**Categoria: (b) sobreposição parcial.** Não encontramos, na busca
documentada abaixo e nas leituras da matriz, trabalho que estime a menor
força de influência social com que trajetórias individuais de painel se
distinguem de uma família de nulos de persistência sem influência, em função
da confiabilidade da resposta. Isso não é prova de ausência. A cobertura foi
limitada a três APIs (uma delas parcialmente indisponível, ver registro),
ao inglês e a preprints indexados até 27/09/2026. Não há, portanto, evidência
de preempção total (a). A classificação (c) exigiria que nenhum componente
estivesse ocupado, o que é falso.

Componentes já ocupados e por quem:

1. **Sinal mínimo contra um nulo de persistência e ruído que empurra a
   seleção para o nulo.** Moor-Smith–Carpentras (§§3.1, 3.3), em
   distribuições agregadas e com ruído no processo. CoDiNG (§§6.2, 7) mostra
   que modelos de influência raramente vencem nulos triviais em dados
   individuais.
2. **Sensibilidade conjunta a confiabilidade, ondas e N.** Mulder
   (powRICLPM) e Dang–Ma (pp. 2, 9–11), para um coeficiente cross-lag
   intra-pessoa com critério de significância.
3. **Poder para detectar influência em painel.** Stadtfeld et al., com rede
   observada e sem erro de medida.
4. **Mapa de detectabilidade de mecanismos por região de parâmetros.**
   Ureña-Carrion et al., para contágio binário com rede conhecida e
   observação completa.
5. **Ambiguidade entre atualização e disposições estáveis sob erro; limites
   de painéis curtos.** Kiley–Vaisey (manuscrito, p. 21) e Lersch (pp. 222,
   228).
6. **Equivalência genérica entre traço e dinâmica.** Gelastopoulos et al.
7. **Geometria SHP e calibração de modelo de opinião a transições.**
   Gestefeld–Lorenz.
8. **Canal de medida que altera o julgamento de modelos.** Carpentras–Quayle
   (2022 e 2023).
9. **Erro de medida na inferência de influência social.** Xu–Frank e
   Advani–Malde, com erro na rede observada, não na resposta; lidos só em
   resumo.

Componente sem antecedente encontrado: a conjunção de todos os pontos
abaixo. Nenhum item isolado é novo.

- gerador de influência entre pessoas sem rede observada;
- erro de resposta separado do processo, com r fixado externamente numa
  grade;
- família de nulos de persistência (traço+AR, AR, heaping, dependente do
  estado, mover–stayer) pareada aos mesmos momentos L1/L2 observados;
- discriminador fixo pré-registrado com AUC por painel;
- força mínima numa grade fixa, relatada como curva a*(r) com censura.

### Afirmações que o artigo pode fazer com segurança

- "Numa busca documentada (OpenAlex, Semantic Scholar e arXiv, 27/09/2026;
  consultas e triagem no material suplementar), não identificamos estudo que
  estime uma fronteira de detecção da força de influência em função da
  confiabilidade da resposta contra nulos de persistência pareados."
  A frase deve vir acompanhada das limitações de cobertura.
- Sensibilidade dependente de confiabilidade, ondas e N é conhecida em
  modelos de painel (Mulder; Dang–Ma). A contribuição é levar essa lógica a
  geradores de dinâmica de opinião contra uma família de nulos sem
  influência.
- Trabalhos de validação de dinâmica de opinião já mostram que ajustes
  convergem para persistência sob ruído ou sinal fraco (Moor-Smith–Carpentras;
  CoDiNG). O estudo quantifica, para um par gerador/nulo e um discriminador
  fixos, quanto sinal é preciso para escapar disso, por nível de r.
- a*(r) é um limiar operacional para a LDA declarada. É limite superior do
  limiar ótimo, e seu não-atingimento não prova indistinguibilidade.
- Separação só no canal observado é dependente do canal (Carpentras–Quayle).

### Afirmações a evitar

- "Primeiro estudo a…", "inédito" ou "nenhum trabalho" sem a qualificação
  da busca.
- Que o estudo detecta ou identifica influência social causal. Sem
  exposição observada isso não é possível (Manski; e o próprio protocolo).
- Que não-atingimento demonstra indistinguibilidade ou equivalência
  observacional. Isso seria confundir com Gelastopoulos et al., que provam
  equivalência genérica por outra via.
- Que a grade r corresponde à confiabilidade do item do SHP. As âncoras não
  são transportáveis (ver `decision17-reference-verification.md`).
- Que "mais ondas ou mais confiabilidade aumentam a detectabilidade" é um
  achado. É esperado e já demonstrado (Lersch; Dang–Ma; Stadtfeld et al.).
- Atribuir a Dang–Ma ou a Mulder resultados além do lido. Mulder foi lido
  apenas em resumo e manual; o suplemento B de Lersch não foi relido nesta
  sessão.
- Chamar a de parcela empírica da variância de mudança. É uma âncora
  interna do simulador.
- Apresentar a*(r) como fronteira minimax ou assintótica.

### Antecedentes perigosos para a alegação de novidade

- **Moor-Smith–Carpentras 2026**: mais próximo em espírito, com deriva
  mínima contra o nulo sem mudança e limiar de ruído. Um revisor pode ver
  a*(r) como a versão em painel desse resultado. A resposta é que a
  diferença está em trajetórias individuais, erro de resposta com r, nulos
  flexíveis pareados e AUC.
- **Dang–Ma 2026 e Mulder 2023**: o formato "curva de sensibilidade × r ×
  ondas × N" já existe. O risco é o artigo ser lido como análise de poder
  aplicada. É preciso explicitar a diferença entre geradores, nulos e
  critério.
- **Gelastopoulos et al. 2025**: se o traço+AR puder imitar qualquer
  dinâmica, um revisor pode questionar o sentido de a*(r). A resposta é que
  a família é fixa, o pareamento é só em L1/L2 e o sinal fica em L3–L5, mas
  a relação deve ser discutida explicitamente.
- **Ureña-Carrion et al. 2026**: reivindica o "first systematic effort" em
  limites de detectabilidade de mecanismos em redes. Deve ser citado e
  delimitado: contágio binário e rede conhecida.

## Limites deste dossiê

- Mulder, Lucas, Hill–Kriesi, Xu–Frank e Advani–Malde estão só em resumo. O suplemento de Lersch, o
  capítulo editado de Moor-Smith–Carpentras e as versões publicadas de Borile
  e Lenti não foram relidos.
- Kiley–Vaisey foi lido no manuscrito dos autores; a paginação da ASR não
  foi conferida.
- A busca foi feita em inglês, com três APIs e 10 consultas. Teses,
  literatura não inglesa e metodologia de survey não foram varridas.
- As citações de HTML convertido podem ter perdido símbolos matemáticos. A
  linha 15 registra um caso.
