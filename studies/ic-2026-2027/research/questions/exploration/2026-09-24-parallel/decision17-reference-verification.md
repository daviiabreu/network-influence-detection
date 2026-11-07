# Verificação de referências para a decisão 17

Consulta: 25/09/2026. Nota bibliográfica de apoio ao pré-registro, sem execução de
simulações e sem alegação de novidade. O ponto de partida foi o parecer
`/Users/davi/.local/state/research-workbench/adversarial-novelty-20260925/adversarial-novelty-report.md`.
Os identificadores abaixo foram conferidos em páginas dos autores, editoras,
arXiv, textos primários depositados ou metadados Crossref. Metadados confirmados
não equivalem a leitura integral; os limites de leitura estão discriminados.

## Antecedentes próximos

| Referência verificada | Evidência consultada e relação com o desenho |
| --- | --- |
| Samuel Moor-Smith e Dino Carpentras (2026), *Testing the Validity of Multiple Opinion Dynamics Models*. DOI [10.1007/978-3-032-31712-4_30](https://doi.org/10.1007/978-3-032-31712-4_30); preprint [arXiv:2602.00876](https://arxiv.org/abs/2602.00876). | Texto do preprint lido em [§3.1](https://arxiv.org/html/2602.00876v1#S3.SS1) e [§3.3](https://arxiv.org/html/2602.00876v1#S3.SS3); título, autores e DOI do capítulo conferidos no Crossref. É o precursor agregado mais próximo: requer mudança mínima para superar o nulo de distribuição inalterada e examina ruído que inviabiliza reconstrução. O ruído alimenta o estado seguinte; a avaliação usa distribuições e distância de Wasserstein. O presente desenho usa trajetórias individuais, erro de resposta separado do processo, nulos de atualização e AUC por painel. O capítulo editado não foi relido integralmente. |
| Philipp M. Lersch (2023), *Change in Personal Culture over the Life Course*, ASR 88(2), 220–251. DOI [10.1177/00031224231156456](https://doi.org/10.1177/00031224231156456). | Artigo e [suplemento, Parte B, pp. 45–49](https://journals.sagepub.com/doi/suppl/10.1177/00031224231156456/suppl_file/sj-pdf-1-asr-10.1177_00031224231156456.pdf) consultados. Parte B compara 3, 5 e 10 ondas, com atualização AR, flutuação, ruptura e tendências; demonstra limites da discriminação entre disposições estáveis e atualização em painéis curtos. Inclui SHP no estudo empírico. O acréscimo proposto aqui é condicionar um limiar operacional à confiabilidade e ao matching observado de mecanismos não lineares e nulos, não descobrir que mais ondas ajudam. |
| Jeroen D. Mulder (2023; online em 2022), *Power Analysis for the Random Intercept Cross-Lagged Panel Model Using the powRICLPM R-Package*, SEM 30(4), 645–658. DOI [10.1080/10705511.2022.2122467](https://doi.org/10.1080/10705511.2022.2122467). | Metadados Crossref, [registro institucional do autor](https://research-portal.uu.nl/en/publications/power-analysis-for-the-random-intercept-cross-lagged-panel-model-/) e [documentação do autor](https://jeroendmulder.github.io/powRICLPM/reference/powRICLPM.html) consultados. Já trata poder em função de N, ondas, ICC e confiabilidade, inclusive STARTS. Aqui o alvo é separabilidade de geradores por AUC, não significância de um coeficiente cross-lag. Acoplamento entre pessoas e associação defasada entre variáveis de uma pessoa não são o mesmo estimando. |
| Junhua Dang e Zhihao Ma (2026), *Fitting RI-CLPM Is Not Enough: Diagnostic Sensitivity and Reporting Practices in Within-Person Longitudinal Research*. [arXiv:2608.09951v1](https://arxiv.org/abs/2608.09951), DOI [10.48550/arXiv.2608.09951](https://doi.org/10.48550/arXiv.2608.09951). | Resumo e metadados do depósito consultados; não consta DOI de periódico nessa página. Simulações com powRICLPM relacionam sensibilidade a confiabilidade, ICC, ondas, N e efeito. Antecede a lógica de sensibilidade conjunta; não estima o contraste de geradores aqui proposto. Não atribuir ao preprint resultados além do resumo sem leitura adicional. |
| Christoph Stadtfeld, Tom A. B. Snijders, Christian Steglich **e Marijtje van Duijn** (2020; online em 2018), *Statistical Power in Longitudinal Network Studies*, SMR 49(4). DOI [10.1177/0049124118769113](https://doi.org/10.1177/0049124118769113). | [Texto da editora](https://journals.sagepub.com/doi/10.1177/0049124118769113), procedimento e estudos de caso consultados. Já calcula poder para seleção e influência em SAOM variando tamanho, ondas, efeitos, faltantes e rotatividade. Tem redes observadas. O estudo atual não observa exposição e só discrimina padrões de painéis sintéticos. A referência abreviada de três autores omitia van Duijn. |
| Richard E. Lucas (2023), *Why the Cross-Lagged Panel Model Is Almost Never the Right Choice*. DOI [10.1177/25152459231158378](https://doi.org/10.1177/25152459231158378). | [Texto e simulações da editora](https://journals.sagepub.com/doi/10.1177/25152459231158378) consultados. Traços estáveis e variância de estado/erro podem gerar caminhos cross-lag espúrios quando o traço é omitido. Fundamenta um nulo traço + AR mais exigente; não valida causalmente o mecanismo de influência deste estudo. |
| Mateusz Nurek, Joanna Kołaczek, Radosław Michalski, Bolesław K. Szymański e Omar Lizardo, *CoDiNG — Naming Game with Continuous Latent Opinions of Individual Agents*. DOI [10.48550/arXiv.2406.19204](https://doi.org/10.48550/arXiv.2406.19204). | [v3 de 28/08/2026](https://arxiv.org/abs/2406.19204), [PDF](https://arxiv.org/pdf/2406.19204v3), Eq. 1, §5.2 e §6.1 verificados. A verbalização usa limiar determinístico; há baseline aleatório proporcional à distribuição inicial, que deve ser reconhecido. Esse baseline não é um canal de erro de resposta com confiabilidade fixada externamente. CoDiNG combina comunicação observada e surveys e distingue desempenho agregado e individual; a comparação atual usa geometria sintética sem exposição observada. |
| Kevin Kiley e Stephen Vaisey (2020), *Measuring Stability and Change in Personal Culture Using Panel Data*, ASR 85(3). DOI [10.1177/0003122420921538](https://doi.org/10.1177/0003122420921538). | [Resumo e metadados da editora](https://journals.sagepub.com/doi/10.1177/0003122420921538) reconferidos; a passagem da p. 487 foi documentada no [dossiê anterior](reliability-and-prior-art.md). A oposição atualização ativa/disposições estáveis e sua ambiguidade sob erro alto já estão formuladas. O desenho atual explicita uma curva de separabilidade contra essa família, em vez de apresentar essa ambiguidade como descoberta. |

## Confiabilidade, erros e nulos adicionais

Richard E. Lucas e M. Brent Donnellan (2012; online em 2011), *Estimating the
Reliability of Single-Item Life Satisfaction Measures: Results from Four
National Panel Studies*, DOI [10.1007/s11205-011-9783-z](https://doi.org/10.1007/s11205-011-9783-z),
foram verificados no [texto primário depositado](https://pmc.ncbi.nlm.nih.gov/articles/PMC3475500/),
incluindo Tabela 1. Para satisfação com a vida no SHP, a estimativa é 0,62 no
modelo univariado e 0,68 no bivariado. O texto descreve entrevistas por telefone.
Esses números não estimam a confiabilidade de `P$$P04`: mostram que separar
estado verdadeiro específico da ocasião de erro aleatório muda o estimando.
No protocolo, inovações e choques verdadeiros de atitude pertencem ao processo
latente; erro transitório de resposta pertence ao canal. Resultados simplex e
MTMM não podem ser tratados como medições intercambiáveis desse canal.

Julian Aichholzer (2013), *Intra-individual variation of extreme response style
in mixed-mode panel studies*, DOI [10.1016/j.ssresearch.2013.01.002](https://doi.org/10.1016/j.ssresearch.2013.01.002),
teve título, autoria e resumo conferidos no [registro do artigo](https://pubmed.ncbi.nlm.nih.gov/23522006/).
O estudo distingue estilos estáveis e voláteis em painel irlandês com entrevistas
presenciais e questionários postais. Justifica testar erro de resposta
correlacionado no tempo; não fornece um coeficiente universal de correlação
para confiança política no SHP.

Fabienne Kraemer, Peter Lugtig, Bella Struminskaya, Henning Silber, Bernd Weiß
e Michael Bosnjak (2025), *Monitoring Attitudes Over Time: Real Change or the
Result of Repeated Interviewing?*, DOI [10.1177/00491241251372503](https://doi.org/10.1177/00491241251372503),
foram verificados no [texto da editora](https://journals.sagepub.com/doi/10.1177/00491241251372503).
O experimento alemão de seis ondas encontra aumento tanto de confiabilidade
quanto de estabilidade latente após perguntas repetidas sobre aborto. A
sensibilidade de confiabilidade crescente por tempo no painel é pertinente,
mas não reproduz automaticamente o efeito completo de condicionamento.

Jennifer L. Hill e Hanspeter Kriesi (2001), *An Extension and Test of Converse's
“Black-and-White” Model of Response Stability*, APSR 95(2), 397–413, DOI
[10.1017/S0003055401002209](https://doi.org/10.1017/S0003055401002209),
foram verificados na [página da editora](https://www.cambridge.org/core/journals/american-political-science-review/article/abs/an-extension-and-test-of-converses-blackandwhite-model-of-response-stability/C8CE3C95740A1D05D3C23B2B0103A368).
A página/metadados listam incompletamente os autores, mas a própria afiliação
inclui ambos. O resumo descreve a extensão com mudança racional e painel suíço
de quatro ocasiões. Um nulo mover–stayer aqui é uma sensibilidade inspirada
nessa heterogeneidade, não reprodução de suas estimativas nem equivalência
literal ao modelo de três grupos.

C. W. J. Granger e M. J. Morris (1976), *Time Series Modelling and
Interpretation*, JRSS A 139(2), 246–257: DOI confirmado
[10.2307/2345178](https://doi.org/10.2307/2345178), metadados Crossref e
[registro editorial](https://academic.oup.com/jrsssa/article/139/2/246/7104929).
O resultado sobre somas de processos AR e ruído sustenta a representação ARMA;
a equivalência da assimilação linear em direção à média com AR deve ser
demonstrada sob as hipóteses do simulador, não atribuída como conclusão geral
de identificação causal desse artigo. DOI de Manski (1993):
[10.2307/2298123](https://doi.org/10.2307/2298123), já documentado no dossiê.

## Consequências para o texto congelado

Martin Gestefeld e Jan Lorenz (2023), *Calibrating an Opinion Dynamics Model
to Empirical Opinion Distributions and Transitions*, DOI
[10.18564/jasss.5204](https://doi.org/10.18564/jasss.5204), registram
[50.008 transições anuais de 10.627 indivíduos](https://www.jasss.org/26/4/9.html)
na janela 1999–2009; esses números foram reconferidos no artigo. Usar 10.626
pessoas no simulador para divisibilidade por seis é uma aproximação declarada
dessa geometria, não uma contagem do SHP. A máscara de entrada/atrito sintética
também não reproduz os microdados. O antecedente ajusta a quantidade de passos
por ano (melhor ajuste: 24), justificando fixar e variar explicitamente esse
parâmetro, sem transportar 24 como quantidade empiricamente identificada de
interações reais.

O [FORS](https://forscenter.ch/projects/swiss-household-panel/documentation/)
descreve o SHP como anual e principalmente telefônico (CATI). A janela anual
1999–2009 do item e sua fonte estão no [dossiê](reliability-and-prior-art.md).
As âncoras de [Poses et al. (2021)](https://doi.org/10.18148/srm/2021.v15i3.7816)
e [Hout e Hastings (2016)](https://doi.org/10.15195/v3.a43), já examinadas ali,
provêm de instrumentos, modos e objetos diferentes; ESS MTMM usa qualidade
que combina confiabilidade e validade. A transportabilidade não está
estabelecida. A curva em toda a grade 0,50–0,90 deve ser o resultado principal;
0,70 é destaque, não uma estimativa validada para `P$$P04`.

O teto de autocorrelação igual a r exige as hipóteses do canal independente:
na escala contínua padronizada, com erro independente entre ondas,
`corr(w_t,w_s) = sqrt(r_t r_s) corr(z_t,z_s)`. Com erro correlacionado, há o
termo adicional `sqrt((1-r_t)(1-r_s)) corr(e_t,e_s)`; portanto o teto iid não
deve ser reutilizado sem ajuste nessa sensibilidade. Transformação ordinal
não linear exige checar a região atingível do canal efetivamente implementado.
Essa ressalva é dedução do modelo, não estimativa da literatura.

A AUC de uma família fixa de discriminadores é um limite inferior da melhor
separabilidade por escores de Bayes sobre os mesmos dados; consequentemente,
o primeiro limiar atingido por essa família pode ser maior que o limiar ótimo.
Não inverter as duas direções. Não-atingimento não demonstra indistinguibilidade
para todo discriminador. O resultado permanece condicionado às estatísticas,
ao nulo, ao tamanho do painel e ao canal. A verificação desta lista fecha os
identificadores solicitados; não fecha a busca bibliográfica geral ou o
screening pendente registrado pelo parecer adversarial.
