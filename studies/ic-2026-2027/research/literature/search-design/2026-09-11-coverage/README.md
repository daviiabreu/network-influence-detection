# Auditoria de cobertura e expansão da descoberta — 11 de setembro de 2026

A coleta v2 foi completa para suas 34 consultas, mas não demonstrava cobertura
suficiente do domínio. Este diagnóstico encontrou 24 candidatos sem
correspondência por DOI ou título normalizado em um desafio de 64 candidatos
selecionados antes de consultar o corpus. Há 38 correspondências por DOI e duas
somente por título. Os 64 têm metadados recuperados por DOI exato no Crossref e
nenhum DOI coincide com os 16 seeds de desenvolvimento. Isso é uma auditoria
exploratória, sem estimativa de recall populacional, holdout cego ou aceite.

A seleção intencional combina referências de uma revisão recente e buscas em
fontes de economia, controle, psicologia, sociologia matemática, computação e
física. Algumas fronteiras — convenções linguísticas, sociedades de LLMs e
otimização de exposição — podem terminar excluídas pelo critério de domínio ou
modelo. A ausência exata de 24 candidatos não significa 24 falsos negativos
confirmados. Nenhum caso foi retirado depois de conhecer o resultado.

O [desafio completo](baseline-challenge-64.json) registra DOI, título, fonte de
descoberta, família, correspondências e notas. A comparação leu as 22.404
observações lossless de v2, sem deduplicar ou alterar registros. O artefato de
origem tem SHA-256
`f1136eda2f2a3a181f71b1372669b7ec7db0c4b521ec22e98ee3be35b69e2860`.
A seleção foi congelada antes da consulta ao corpus, SHA-256
`fc461eafdf04bc28dca3fc844638ddb624eda4162833dbf933ed1f78179c820a`;
o horário UTC exato está no JSON. Metadados brutos e corpos de fontes ficam fora
do Git. A auditoria de variantes examinou títulos próximos, mas não inventou
equivalência entre versões.

## Lacunas e consultas

Há exemplos com relação direta ao escopo que motivam a expansão: regras de
atualização de crenças na
[aprendizagem social de Molavi e colaboradores](https://onlinelibrary.wiley.com/doi/10.3982/ECTA14613),
médias de opiniões na
[aprendizagem ingênua de Golub e Jackson](https://topcat.aeaweb.org/articles?id=10.1257%2Fmic.2.1.112)
e sistemas de crenças sujeitos a restrições lógicas no
[modelo de Friedkin e colaboradores](https://www.science.org/doi/10.1126/science.aag2624).
São candidatos relevantes para leitura, sem antecipar decisão de inclusão.

A [proposta de termos](query-expansion-proposal.json) acrescenta seis famílias:
crenças e atitudes, aprendizagem social, convenções e minorias, polarização além
da expressão literal “opinion dynamics”, interações de grupo e voto/ideologia.
Elas foram derivadas depois da comparação: recuperar estes mesmos casos com as
novas consultas será regressão de cobertura, e não novo teste independente.
A tradução precisa declarar os campos usados por cada índice. A família ampla
de polarização exige diagnóstico de volume e particionamento quando necessário;
atingir limite de páginas mantém a busca incompleta.

## Rastreamento de citações

O [manifesto de arestas](starnini-reference-edges.json) extrai 835 referências da
[manifestação arXiv de Starnini e colaboradores](https://arxiv.org/html/2507.11521v1),
submetida em julho de 2025. O artigo final tem DOI `10.1103/j1zg-ddqv`, mas a
manifestação anterior já existia antes do corte de v2. Foram preservados 720 links
DOI válidos: 690 alvos não-arXiv e 30 DOIs arXiv. Eles permitem recuperação por
identificador e triagem, sem converter a bibliografia inteira em estudos
primários. Existem 113 referências sem link DOI e
[dois links malformados](starnini-unresolved-reference-links.json).
O HTML original tem SHA-256
`b429006dd552984cccddb1e8080cca3c7c7fc985b2c9075bd03561c640b53da1`.

Para ampliar as tradições representadas, foram extraídas também as referências
de [Flache e colaboradores, JASSS](https://www.jasss.org/20/4/2.html) e do
[survey de Wang e colaboradores, Neurocomputing](https://doi.org/10.1016/j.neucom.2026.133705).
O [manifesto JASSS](flache-reference-edges.json) contém 174 referências, 126
arestas DOI e 48 referências sem DOI. O
[manifesto Neurocomputing](neurocomputing-reference-edges.json), obtido do
depósito de referências no Crossref, contém 185 referências, 161 arestas para
158 DOIs distintos e 24 referências sem DOI. A propriedade `doi_asserted_by`
preserva quem atribuiu cada vínculo no registro; recuperação de metadados ainda
precisa verificar a identidade do alvo. A página ScienceDirect retornou 403 na
abertura direta, e isso não foi apresentado como leitura de seu texto completo.

As três bibliografias somam 1.194 entradas de referência, com sobreposição,
1.007 arestas DOI e 950 alvos DOI distintos. Os dois manifestos adicionais
acrescentam 230 DOIs à união do RMP. Esses totais medem descoberta documental;
há livros, textos metodológicos, estudos de outro domínio e itens fora da janela
entre as referências, todos sujeitos a disposição explícita.

A [conferência de 16 de setembro](supplementary-evidence-inventory.md) encontrou
uma referência sem DOI omitida na extração Flache. O [sucessor separado](flache-reference-edges-v2.json)
preserva os originais e fecha seus 175 localizadores, com 126 arestas e 49
referências sem DOI. As três extrações passam a representar 1.195 entradas,
mantendo as 1.007 arestas e os 950 DOIs distintos. A correção não altera consultas,
aquisição, identidade ou elegibilidade.

Um [lead posterior ao congelamento](huang-zhang-2026-postfreeze-lead.json),
[Huang e Zhang](https://www.aup-online.com/content/journals/10.5117/CCR2026.2.9.HUAN),
foi conferido separadamente: já estava no baseline em duas observações OpenAlex,
Q01 e Q10. A editora e o Crossref registram 31 de julho de 2026. Ele não altera o
denominador de 64 nem é contado como descoberta ausente.

O rastreamento seguinte deve preservar seed, direção, localizador, identificador,
fonte, data e disposição de cada aresta. A partir dos estudos elegíveis, percorrer
referências e trabalhos citantes; revisões secundárias permanecem separadas dos
estudos primários. O vínculo observado “Starnini cita este trabalho” não prova
que todos os citantes foram recuperados. A regra registrada exige duas rodadas
consecutivas sem novo trabalho elegível após deduplicação. Nenhuma saturação é
declarada neste diagnóstico.

Quatro leads adicionais foram comparados depois do congelamento, em um
[registro separado](four-leads-postfreeze-reconciliation.json). Os artigos
ICWSM 2026 (DOI `10.1609/icwsm.v20i1.42655`), Findings NAACL 2025
(`10.18653/v1/2025.findings-naacl.101`) e Scientific Reports 2026
(`10.1038/s41598-026-44206-z`) já tinham observações com DOI no baseline.
O artigo [Unmasking conversational bias in AI multiagent systems](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0355458),
publicado em 18/08/2026, não apresentou correspondência por DOI ou título
normalizado. Seu preprint [arXiv:2501.14844](https://arxiv.org/abs/2501.14844)
também estava ausente por identificador. Ambos foram encaminhados à recuperação
exata no sucessor. A correspondência de título e autores entre manifestações
permanece candidata à adjudicação; não constitui fusão ou inclusão científica.
O desafio continua com 64 candidatos, incluindo o NAACL já registrado como
`llm-allocation`, sem acrescentá-lo novamente ao denominador.

## Candidatos e resultado no baseline

“DOI” indica correspondência do identificador; “título” é correspondência apenas
textual, ainda sujeita à identidade; “ausente” significa somente que os métodos
deste diagnóstico não localizaram DOI ou título equivalente. Todos aguardam
triagem. As famílias do JSON são eixos de desafio, não categorias finais.

| Candidato | Ano depositado | Título e identificador | Baseline |
| --- | ---: | --- | --- |
| rmp-ref-039 | 2025 | [Emergent social conventions and collective bias in LLM populations](https://doi.org/10.1126/sciadv.adu9368) | ausente |
| rmp-ref-053 | 2018 | [Opinion polarization by learning from social feedback](https://doi.org/10.1080/0022250X.2018.1517761) | DOI |
| rmp-ref-065 | 2006 | [Sharp transition towards shared vocabularies in multi-agent systems](https://doi.org/10.1088/1742-5468/2006/06/P06014) | ausente |
| rmp-ref-071 | 2024 | [Optimal Engagement-Diversity Tradeoffs in Social Media](https://doi.org/10.1145/3589334.3645713) | ausente |
| rmp-ref-072 | 2020 | [Modeling Echo Chambers and Polarization Dynamics in Social Networks](https://doi.org/10.1103/PhysRevLett.124.048301) | DOI |
| rmp-ref-078 | 2023 | [Effect of collaborative-filtering-based recommendation algorithms on opinion polarization](https://doi.org/10.1103/PhysRevE.108.054304) | ausente |
| rmp-ref-162 | 2022 | [The Effect of People Recommenders on Echo Chambers and Polarization](https://doi.org/10.1609/icwsm.v16i1.19275) | DOI |
| rmp-ref-193 | 2020 | [Emergence of polarization in a voter model with personalized information](https://doi.org/10.1103/PhysRevResearch.2.043117) | DOI |
| rmp-ref-245 | 2022 | [Modelling how social network algorithms can influence opinion polarization](https://doi.org/10.1016/j.ins.2021.12.069) | ausente |
| rmp-ref-250 | 2011 | [Small Worlds and Cultural Polarization](https://doi.org/10.1080/0022250X.2010.532261) | ausente |
| rmp-ref-266 | 2021 | [Cascades Across Networks Are Sufficient for the Formation of Echo Chambers: An Agent-Based Model](https://doi.org/10.18564/jasss.4566) | ausente |
| rmp-ref-269 | 2016 | [Opinion formation and bi-polarization with biased assimilation and homophily](https://doi.org/10.1016/j.physa.2015.10.006) | DOI |
| rmp-ref-275 | 1986 | [Majority rule, hierarchical structures, and democratic totalitarianism: A statistical approach](https://doi.org/10.1016/0022-2496(86)90019-2) | ausente |
| rmp-ref-279 | 2004 | [Contrarian deterministic effects on opinion dynamics: “the hung elections scenario”](https://doi.org/10.1016/j.physa.2003.10.041) | DOI |
| rmp-ref-365 | 2020 | [Adaptive voter model on simplicial complexes](https://doi.org/10.1103/PhysRevE.101.022305) | DOI |
| rmp-ref-372 | 2022 | [Group interactions modulate critical mass dynamics in social convention](https://doi.org/10.1038/s42005-022-00845-y) | ausente |
| rmp-ref-417 | 2025 | [Competition between group interactions and nonlinearity in voter dynamics on hypergraphs](https://doi.org/10.1103/PhysRevE.111.L052301) | ausente |
| rmp-ref-516 | 2008 | [Mobility and social network effects on extremist opinions](https://doi.org/10.1103/PhysRevE.78.036104) | ausente |
| rmp-ref-569 | 2013 | [Differentiation without Distancing. Explaining Bi-Polarization of Opinions without Negative Influence](https://doi.org/10.1371/journal.pone.0074516) | DOI |
| rmp-ref-576 | 2021 | [Consensus dynamics on temporal hypergraphs](https://doi.org/10.1103/PhysRevE.104.064305) | ausente |
| rmp-ref-577 | 2020 | [Multibody interactions and nonlinear consensus dynamics on networked systems](https://doi.org/10.1103/PhysRevE.101.032310) | ausente |
| rmp-ref-610 | 2022 | [Modeling algorithmic bias: simplicial complexes and evolving network topologies](https://doi.org/10.1007/s41109-022-00495-7) | DOI |
| rmp-ref-611 | 2023 | [Mass media impact on opinion evolution in biased digital environments: a bounded confidence model](https://doi.org/10.1038/s41598-023-39725-y) | DOI |
| rmp-ref-613 | 2023 | [Fragmentation from group interactions: A higher-order adaptive voter model](https://doi.org/10.1016/j.physa.2023.129257) | DOI |
| rmp-ref-614 | 2022 | [Consensus from group interactions: An adaptive voter model on hypergraphs](https://doi.org/10.1103/PhysRevE.105.054307) | DOI |
| rmp-ref-629 | 2021 | [Opinion formation on social networks with algorithmic bias: dynamics and bias imbalance](https://doi.org/10.1088/2632-072X/ac340f) | DOI |
| rmp-ref-633 | 2021 | [Effect of algorithmic bias and network structure on coexistence, consensus, and polarization of opinions](https://doi.org/10.1103/PhysRevE.104.044312) | DOI |
| rmp-ref-637 | 2019 | [Modelling opinion dynamics in the age of algorithmic personalisation](https://doi.org/10.1038/s41598-019-43830-2) | DOI |
| rmp-ref-673 | 2021 | [Modelling non-linear consensus dynamics on hypergraphs](https://doi.org/10.1088/2632-072X/abcea3) | ausente |
| rmp-ref-674 | 2020 | [A model for the competition between political mono-polarization and bi-polarization](https://doi.org/10.1063/5.0004996) | ausente |
| rmp-ref-676 | 2021 | [Link recommendation algorithms and dynamics of polarization in online social networks](https://doi.org/10.1073/pnas.2102141118) | ausente |
| rmp-ref-704 | 2010 | [Tipping diffusivity in information accumulation systems: more links, less consensus](https://doi.org/10.1088/1742-5468/2010/06/P06005) | DOI |
| rmp-ref-725 | 2023 | [Social identity bias and communication network clustering interact to shape patterns of opinion dynamics](https://doi.org/10.1098/rsif.2023.0372) | título |
| rmp-ref-737 | 2019 | [Algorithmic bias amplifies opinion fragmentation and polarization: A bounded confidence model](https://doi.org/10.1371/journal.pone.0213246) | DOI |
| rmp-ref-775 | 2020 | [Role of voting intention in public opinion polarization](https://doi.org/10.1103/PhysRevE.101.012101) | ausente |
| rmp-ref-812 | 2011 | [Social consensus through the influence of committed minorities](https://doi.org/10.1103/physreve.84.011130) | ausente |
| rmp-ref-824 | 2024 | [Modeling the Impact of Timeline Algorithms on Opinion Dynamics Using Low-rank Updates](https://doi.org/10.1145/3589334.3645714) | DOI |
| rmp-ref-832 | 2020 | [A two-layer model for coevolving opinion dynamics and collective decision-making in complex social systems](https://doi.org/10.1063/5.0004787) | DOI |
| social-learning-naive | 2010 | [Naïve Learning in Social Networks and the Wisdom of Crowds](https://doi.org/10.1257/mic.2.1.112) | ausente |
| social-learning-theory | 2018 | [A Theory of Non-Bayesian Social Learning](https://doi.org/10.3982/ECTA14613) | ausente |
| social-learning-nonbayesian | 2012 | [Non-Bayesian social learning](https://doi.org/10.1016/j.geb.2012.06.001) | DOI |
| nonlinear-tunable | 2023 | [Nonlinear Opinion Dynamics With Tunable Sensitivity](https://doi.org/10.1109/TAC.2022.3159527) | DOI |
| llm-allocation | 2025 | [Biases in Opinion Dynamics in Multi-Agent Systems of Large Language Models: A Case Study on Funding Allocation](https://doi.org/10.18653/v1/2025.findings-naacl.101) | DOI |
| recent-hyper-opinion | 2025 | [An opinion evolution model for online social networks considering higher-order interactions](https://doi.org/10.1371/journal.pone.0321718) | DOI |
| recent-multidimensional | 2025 | [Opinion diversity shaped by higher-order interactions on multi-dimensional issues](https://doi.org/10.1016/j.chaos.2025.116188) | DOI |
| evidence-dempster | 2024 | [Dynamic Opinion Formation in Networks: A Multi-Issue and Evidence-Based Approach](https://doi.org/10.3390/computers13080190) | DOI |
| grand-scale | 2025 | [Grand scale opinion dynamics](https://doi.org/10.1080/0022250X.2025.2529179) | DOI |
| social-power | 2016 | [A Theory of the Evolution of Social Power: Natural Trajectories of Interpersonal Influence Systems along Issue Sequences](https://doi.org/10.15195/v3.a20) | DOI |
| rmp-ref-073 | 2021 | [Emergence of Polarized Ideological Opinions in Multidimensional Topic Spaces](https://doi.org/10.1103/PhysRevX.11.011012) | ausente |
| rmp-ref-082 | 2024 | [Bounded confidence opinion dynamics: A survey](https://doi.org/10.1016/j.automatica.2023.111302) | DOI |
| rmp-ref-124 | 2016 | [The noisy voter model on complex networks](https://doi.org/10.1038/srep24775) | título |
| rmp-ref-303 | 2018 | [The triple‐filter bubble: Using agent‐based modelling to test a meta‐theoretical framework for the emergence of filter bubbles and echo chambers](https://doi.org/10.1111/bjso.12286) | ausente |
| rmp-ref-304 | 2023 | [Calibrating an Opinion Dynamics Model to Empirical Opinion Distributions and Transitions](https://doi.org/10.18564/jasss.5204) | DOI |
| rmp-ref-411 | 2024 | [Polarization on Social Media: Micro-Level Evidence and Macro-Level Implications](https://doi.org/10.18564/jasss.5298) | DOI |
| rmp-ref-444 | 2016 | [Robust Clustering in Generalized Bounded Confidence Models](https://doi.org/10.18564/jasss.3220) | DOI |
| rmp-ref-500 | 2021 | [Individual attitude change and societal dynamics: Computational experiments with psychological theories.](https://doi.org/10.1037/rev0000291) | ausente |
| rmp-ref-570 | 2010 | [Individualization as Driving Force of Clustering Phenomena in Humans](https://doi.org/10.1371/journal.pcbi.1000959) | DOI |
| rmp-ref-620 | 2017 | [Novel Multidimensional Models of Opinion Dynamics in Social Networks](https://doi.org/10.1109/TAC.2016.2613905) | DOI |
| rmp-ref-740 | 2016 | [Discrepancy and Disliking Do Not Induce Negative Opinion Shifts](https://doi.org/10.1371/journal.pone.0157948) | DOI |
| kinetic-toscani | 2006 | [Kinetic models of opinion formation](https://doi.org/10.4310/CMS.2006.v4.n3.a1) | DOI |
| kinetic-continuous | 2007 | [First‐Order Continuous Models of Opinion Formation](https://doi.org/10.1137/060658679) | DOI |
| kinetic-conviction | 2015 | [Kinetic models of opinion formation in the presence of personal conviction](https://doi.org/10.1103/PhysRevE.92.052818) | DOI |
| empirical-chacoma | 2015 | [Opinion Formation by Social Influence: From Experiments to Modeling](https://doi.org/10.1371/journal.pone.0140406) | DOI |
| belief-logic | 2016 | [Network science on belief system dynamics under logic constraints](https://doi.org/10.1126/science.aag2624) | ausente |
