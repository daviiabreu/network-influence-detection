# Âncoras de confiabilidade e antecedentes para o estudo sintético com geometria SHP

Consulta em 24/09/2026. Este dossiê responde a duas perguntas para o estudo
sintético que compara um mecanismo de influência da família Gestefeld–Lorenz
(assimilação com confiança limitada e variantes repulsivas) a um modelo de
persistência latente individual com erro de medida, em painel anual de 11 ondas
com a geometria do item SHP `P$$P04` (1999–2009). A primeira pergunta é qual
faixa de confiabilidade publicada pode fixar o erro de medida. A segunda é se
algum trabalho já faz esse contraste. Nenhum microdado humano foi adquirido. Os
únicos cálculos próprios usam distribuições agregadas do depósito OSF de
Gestefeld e Lorenz (hash conferido) e o catálogo FORS, e estão marcados como
cálculos meus, não como estimativas publicadas. Cada fonte indica o que foi
efetivamente lido: texto integral, trecho ou só resumo e metadados.

## O item `P$$P04`

O catálogo oficial FORS da onda 19 ([variável `P17P04`](https://devisu.forscenter.ch/index.php/catalog/1086/variable/F1/V362?name=P17P04),
página lida integralmente) traz a pergunta literal: "How much confidence do you
have in ..., if 0 means 'no confidence' and 10 means 'full confidence'? The
Federal Government (in Bern)". A escala tem 11 pontos, com rótulos só nos
extremos. O catálogo registra 9.089 respostas válidas e códigos negativos para
"does not know" (−1), "no answer" (−2) e "inapplicable" (−3). Pela contagem do
catálogo, calculei média de 6,32 e desvio-padrão de 1,99 sem ponderação. O
mesmo enunciado aparece para a série 1999–2018 na Tabela 1 de
[Devine e Valgarðsson](https://doi.org/10.1111/1475-6765.12606) (lido no
[preprint integral](https://osf.io/zxjcn/download)), o que cobre a janela
1999–2009 com a ressalva de que essa é uma transcrição secundária, não o
questionário de cada onda. Gestefeld e Lorenz chamam o item de "Trust in
Government" e registram, na nota 4, que não há equivalente direto no ESS.

No CSV SHP depositado por Gestefeld e Lorenz (`SHPdataset+calibrated.csv`,
SHA-256 `5211247…123f`, conferido; mantido fora do Git), calculei média e
desvio-padrão das distribuições anuais. Em 1999–2009, a média variou de 5,28 a
5,95 e o desvio-padrão de 2,10 a 2,27 (média de 2,16). A categoria 5 concentra
21% a 26% das respostas. A linha de 2017 do depósito reproduz exatamente a
média 6,32 e o desvio 1,99 que obtive no catálogo FORS, o que confirma que o
depósito traz frequências não ponderadas.

Não encontrei estimativa publicada de confiabilidade para `P$$P04`. O que
existe é indireto. Devine e Valgarðsson (pp. 14–17 do preprint) mostram
estabilidade descritiva: a mudança absoluta média entre a primeira e a última
onda é 0,15 na escala 0–1, ou 1,5 ponto em 19 anos. Mudam no máximo uma
categoria 64% dos respondentes entre a primeira e a segunda ondas e 58% entre a
primeira e a última. Os modelos de crescimento latente indicam variação
intraindividual de cerca de um terço da variação entre pessoas. Não li o
apêndice com as correlações entre ondas. [Lersch (2023)](https://doi.org/10.1177/00031224231156456)
(texto integral) inclui `p$$p04` entre as medidas SHP de 1999–2009, 2011, 2014
e 2017. A inclusão aparece na linha 141 do [script `data_prep_shp.do`](https://osf.io/download/fdnt2/),
mas o artigo só reporta resultados agregados em meta-análise. A nota
[“Why use 11-point scales?”](https://forscenter.ch/wp-content/uploads/2018/10/varia_11pointscales.pdf)
de Scherpenzeel (texto integral) justifica a escala 0–10 do SHP pela literatura
MTMM, sem número para este item. Buscas indicam um working paper SHP 1/00 de
Scherpenzeel sobre avaliação MTMM de CATI e CAPI no piloto de 1999. Não o
localizei no site FORS: as URLs testadas deram 404. Portanto não sei se ele
inclui o item.

## Âncoras publicadas

A tabela reúne os números que efetivamente conferi. Há dois tipos de desenho.
Os modelos quase-simplex de Heise e de Wiley e Wiley, aplicados a três ou mais
ondas, medem uma confiabilidade entre ondas em que estados transitórios não
transmitidos contam como erro. O MTMM mede a qualidade dentro de uma mesma
entrevista (confiabilidade × validade), em que esses estados transitórios
contam como escore verdadeiro. Para um braço "persistência + erro" em escala
anual, a grandeza relevante é a primeira. Os valores MTMM funcionam como teto.

| Fonte e leitura                                                                                                                                                                                               | Desenho                                                                                | Item e escala                                                                                          | Valor                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Hout e Hastings 2016](https://doi.org/10.15195/v3.a43), texto integral; Tabela 2 (p. 980), pp. 973–974, 988–990, Fig. 6 e nota 6                                                                             | GSS, três painéis de 3 ondas com intervalo de 2 anos; Alwin–Heise (eq. 2) e multinível | 276 itens; "confidence in leadership" (14 itens, 3 categorias); executivo federal; POLVIEWS (7 pontos) | Mediana geral de 0,74 no Alwin–Heise e 0,68 no multinível. Itens não fixos: 0,71 e 0,65. Confiança: mediana 0,62, e 0,53 no multinível. Executivo: 0,68, só no painel 2010–2014. Nos painéis com troca de governo, a estimativa ficou inutilizável: 0,14 no painel 2008–2012 e valor impossível acima de 8 no de 2006–2010. POLVIEWS: 0,66. PARTYID: 0,84. |
| [Alwin e Tufiș 2023](https://alwin-reliability.com/assets/img/Question%20Content%20and%20Reliability%20of%20Measurement.pdf), texto integral; Tabelas 1, 2, 4 e Apêndice A, com dados adaptados de Alwin 2021 | Quase-simplex de 3 ondas em 10 painéis dos EUA (NES 1950/70/90, ACL, SAF, HRS, GSS)    | Não fatos contra fatos; confiança em instituições do GSS; liberal–conservador                          | Não fatos: 0,59–0,68 por painel. Fatos: 0,74–0,89. Atitudes no GSS: 0,66–0,68. Confiança em instituições do GSS: média 0,586, faixa 0,48–0,64 (Congresso 0,593; Suprema Corte 0,605). Liberal–conservador: 0,69 no GSS e 0,67–0,80 no NES.                                                                                                                 |
| [Alwin, Baumgartner e Beattie 2018](https://doi.org/10.1093/jssam/smx025), resumo                                                                                                                             | Quase-simplex no GSS, 496 perguntas                                                    | Número de categorias                                                                                   | A confiabilidade cai de forma monotônica com mais opções de resposta. Isso não favorece a escala de 11 pontos.                                                                                                                                                                                                                                             |
| [Poses et al. 2021](https://doi.org/10.18148/srm/2021.v15i3.7816), texto integral; p. 240 e Tabela 1 (pp. 241–244)                                                                                            | ESS, 28 experimentos MTMM nas rodadas 1–7 e até 41 grupos país–língua                  | Confiança política em 11 pontos, rotulada nos extremos                                                 | Qualidade q² para parlamento: 0,78 (R1), 0,76 (R2) e 0,72 (R4). Sistema legal: 0,73–0,81. Polícia: 0,79–0,88. Políticos: 0,77. Satisfação com o governo nacional: 0,69–0,72. Confiança social: 0,54–0,61. Média geral: q² de 0,65, confiabilidade de 0,74 e validade de 0,88.                                                                              |
| [Turper e Aarts 2017](https://doi.org/10.1007/s11205-015-1182-4), texto integral via Europe PMC; nota 3                                                                                                       | MTMM do ESS R2 via SQP                                                                 | Parlamento, sistema legal e políticos                                                                  | Confiabilidade r² de 0,82, 0,85 e 0,84.                                                                                                                                                                                                                                                                                                                    |
| [Kroh 2007](https://doi.org/10.1093/poq/nfm009), resumo                                                                                                                                                       | Comparação de formatos esquerda–direita                                                | 10, 11 e 101 pontos                                                                                    | Os três formatos têm confiabilidade parecida. A escala de 11 pontos tem a maior validade.                                                                                                                                                                                                                                                                  |
| [Devine e Valgarðsson 2024](https://doi.org/10.1111/1475-6765.12606), preprint integral; Tabela 1 e pp. 14–17                                                                                                 | SHP 1999–2018, estatística descritiva                                                  | `P$$P04`                                                                                               | Não é estimativa de confiabilidade. Os números descritivos estão na seção anterior.                                                                                                                                                                                                                                                                        |

Heise (1969, [doi:10.2307/2092790](https://doi.org/10.2307/2092790)) e
[Wiley e Wiley (1970)](https://doi.org/10.2307/2093858) foram conferidos pelos
metadados e pela exposição de Hout e Hastings (pp. 973–974). Não li os textos
originais. Também não li o livro de Alwin, [_Margins of Error_](https://doi.org/10.1002/9780470146316).
Os números atribuídos a ele vêm da nota de Alwin e Tufiș, que remete às
pp. 158–162 do livro. Para CRONOS-2, não achei relatório de confiabilidade nem
de MTMM dos itens de confiança. Os três itens repetidos das ondas 1 e 4,
documentados no dossiê de acesso, só permitem teste–reteste de duas ondas, que
não separa confiabilidade de estabilidade. O único MTMM que encontrei no CRONOS
original, na onda 6, trata de renda justa ([Michaud, Bosch e Sauger 2023](https://doi.org/10.1007/s11211-023-00410-0),
só metadados). Não rodei o SQP para `P$$P04`, porque ele exige conta. O
[artigo de Saris e Gallhofer (2007)](https://ojs.ub.uni-konstanz.de/srm/article/view/49)
sobre a base do SQP foi lido parcialmente e não fornece um número direto para
este item.

## Recomendação para o simulador

Recomendo uma faixa principal de confiabilidade anual ρ entre 0,65 e 0,80, com
0,70 como valor central. A análise de sensibilidade deve cobrir 0,50 a 0,90. O
limite inferior da faixa principal coincide com o topo das médias quase-simplex
de itens subjetivos nos EUA (0,59–0,68) e com a confiança no executivo do GSS
(0,68). O limite superior fica logo abaixo da confiabilidade MTMM dos itens de
confiança do ESS (0,82–0,85) e dentro da qualidade MTMM para parlamento e
sistema legal (0,72–0,81). Esses valores MTMM são teto porque não contam estados
transitórios como erro. Na sensibilidade, 0,50 aproxima a estimativa multinível
para confiança no GSS (0,52). Já 0,90 serve de teste de estresse, acima de
qualquer item atitudinal isolado nessas fontes.

Um cálculo meu restringe a faixa, com incerteza. Usei persistência pura com erro
gaussiano homocedástico, desvio marginal de 2,16 e arredondamento para 0–10,
em 400 mil pares simulados com semente 20260924. A proporção de pares anuais
que mudam no máximo uma categoria é 0,52 com ρ = 0,50, 0,56 com 0,60, 0,60 com
0,65, 0,63 com 0,70, 0,67 com 0,75, 0,73 com 0,80 e 0,87 com 0,90. Devine e
Valgarðsson relatam 64% entre a primeira e a segunda ondas do SHP. Mudança real
só acrescenta instabilidade. Logo, sob erro gaussiano, ρ abaixo de cerca de
0,65–0,70 faria o braço de persistência gerar mais instabilidade anual do que o
SHP mostra. Isso vale como ordem de grandeza. A amostra de Devine abrange
1999–2018 e usa a primeira onda de cada pessoa. O acúmulo de respostas no ponto
5 e erros não gaussianos podem deslocar o limite. O número precisa ser
recalculado com os pares 1999–2009 quando houver acesso aos microdados.

Com desvio marginal de 2,16, os valores de ρ correspondem a erros σ_e na escala
0–10 de 1,53 (ρ = 0,50), 1,28 (0,65), 1,18 (0,70), 1,08 (0,75), 0,97 (0,80) e
0,68 (0,90). Há uma consequência de desenho. Quando o braço de persistência
reproduz a marginal e a dispersão das transições anuais, σ_e deixa de ser livre
e fica praticamente determinado. A faixa publicada passa a servir de checagem
externa de plausibilidade. Ela não amplia o ajuste. Vale acrescentar uma
variante de erro que concentre respostas no ponto 5, já que Gestefeld e Lorenz
(¶7.7) observam uso do meio da escala como não resposta.

Uma estimativa própria para o SHP por Heise ou Wiley–Wiley seria útil, mas não
neutra. [Kiley e Vaisey (2020, p. 485)](https://doi.org/10.1177/0003122420921538)
observam que o estimador de Heise pressupõe o processo markoviano de
atualização, enquanto o modelo multinível de Hout e Hastings pressupõe
disposições fixas. Cada estimador embute uma das hipóteses em disputa. Por isso,
as âncoras externas acima devem fixar ρ, e o perfil de correlação por
defasagem, r(k) para k = 1…10, deve funcionar como estatística de teste, não
como estimativa de confiabilidade.

## Antecedentes: o contraste já foi feito?

Gestefeld e Lorenz (2023, [JASSS 26(4):9](https://www.jasss.org/26/4/9.html),
texto integral, ¶¶3.11–3.14, 4.11–4.12, 5.3, 5.10–5.11, 6.9–6.21, 7.1–7.13,
Tabela 3 e notas 4, 7 e 8) usam a mesma geometria: 50.008 transições anuais de
10.627 pessoas. Não comparam o modelo com uma alternativa de persistência mais
erro. O único nulo é binomial e vale para a marginal (nota 8). O ¶7.8 declara a
premissa de distribuições estacionárias com mudança individual contínua. O
¶7.9 recusa chamar o ajuste de validação, porque os dados não trazem informação
sobre a comunicação entre pessoas. O ¶7.12 reconhece alta imprecisão individual
em dados longitudinais de survey. O ¶3.13 interpreta as probabilidades de
transição como "long-term personality trait".

O ponto decisivo está no próprio modelo. A idiossincrasia θ devolve o agente à
sua opinião inicial a_i(0) (¶¶4.11–4.12, nota 7, que a aproxima da ancoragem de
Friedkin–Johnsen). Cada passo é uma interação ou um retorno por agente (¶5.3).
No melhor ajuste, θ = 0,1 e a contagem de passos por ano (TSC) é 24–25 (Tabela
3). Calculei que 1 − 0,9^24 ≈ 0,92: cerca de 92% dos agentes voltam à âncora ao
menos uma vez por ano simulado. Em resolução anual, o melhor ajuste publicado já
é uma persistência individual com desvios transitórios gerados por influência.
Isso é inferência minha a partir dos parâmetros publicados, não afirmação dos
autores. O veredito é sobreposição parcial nos dados e no modelo, sem
interrupção da linha. O contraste só deixa de ser quase degenerado se incluir
dois braços de influência: o ancorado de Gestefeld e Lorenz e um sem âncora. A
redistribuição aleatória original de [Lorenz et al. 2021](https://doi.org/10.1037/rev0000291),
mencionada no ¶4.12, serve para o segundo.

[Carpentras e Quayle (2023, IJSRM 26(2):215–231)](https://doi.org/10.1080/13645579.2022.2137938)
foram lidos em texto integral no [arXiv 2312.05101](https://arxiv.org/abs/2312.05101).
A seção "The falsifiability problem" mostra que uma distorção monotônica da
escala faz dados gerados pelo Deffuant parecerem incompatíveis com o próprio
Deffuant ("poor predictions are not necessarily evidence that a model is
poor"). Não há painel, persistência nem confiabilidade: a sobreposição é
parcial e conceitual. O capítulo de 2026, ["Every Opinion Dynamics Model Is a
Class of Equivalent Models"](https://doi.org/10.1007/978-3-032-31712-4_4) (pp.
51–64, anais SSC 2025), é fechado segundo OpenAlex, e a Springer redireciona
para autenticação. Li só metadados e o resumo do precursor
[arXiv 2010.04788](https://arxiv.org/abs/2010.04788), em que a troca de escala
pode "transform one model into another". Pelo título e pelo precursor, o tema
provável é equivalência sob transformação de escala, não persistência mais erro.
Isso continua sendo risco residual não verificado.

[Moor-Smith e Carpentras (2026)](https://doi.org/10.1007/978-3-032-31712-4_30)
foram lidos em texto integral no [preprint 2602.00876v1](https://arxiv.org/abs/2602.00876),
§§2.1–2.2, 3.3, 4 e conclusão. É o antecedente mais próximo em espírito. Com
ruído, o otimizador "learns to mimic the null model—and 'freeze'" (§3.3), e no
ESS "no model outperforms the null model consistently" (§4). O nulo, porém,
repete a distribuição anterior (eq. 2). O ruído entra na trajetória e alimenta a
geração seguinte. Os dados são cortes transversais, tomados como "proxy for
longitudinal ground-truth". Não há persistência individual, erro de medida
calibrado nem painel. O veredito é sobreposição parcial.

Kiley e Vaisey (2020, [ASR 85(3):477–506](https://doi.org/10.1177/0003122420921538),
texto integral, pp. 478–487), [Vaisey e Kiley (2021)](https://doi.org/10.15195/v8.a5)
(resumo) e Lersch (2023, [ASR 88(2):220–251](https://doi.org/10.1177/00031224231156456),
texto integral e [código OSF](https://osf.io/uey5h/)) formam o antecedente
estatístico mais forte. Os três comparam disposições estáveis com erro contra
atualização persistente em painéis. Kiley e Vaisey escrevem que, se as
mudanças ocorrem a cada onda, "the active updating model becomes
indistinguishable from the settled dispositions model with high measurement
error" (p. 487). Concluem a favor de mudança por substituição geracional, e não
por "contemporaneous persuasion and social influence" (p. 479). Lersch usa seis
painéis longos, incluindo SHP 1999–2019 com `p$$p04`. Numa comparação por BIC
de 415 modelos, a atualização vence em 27%, a adaptação ao curso de vida em
48% e a disposição estável em 22% (pp. 236–237). Ele também mostra por
simulação que painéis de 3 ondas em 4 anos não detectam mudança persistente
com segurança (p. 228, suplemento B não lido). O [script de simulação](https://osf.io/download/ghb9f/)
testa 3, 5 e 10 ondas com processos gaussianos lineares: persistência mais
ruído, AR(0,8), choque e tendências. A sobreposição é parcial e forte. Falta um
mecanismo de interação com distribuição estacionária endógena, marginais
igualadas, erro ancorado em confiabilidade publicada e diagnóstico por matriz
de transição.

Hill aqui é Jennifer L. Hill, com Hanspeter Kriesi: [_Political Analysis_
9(4):301–324](https://doi.org/10.1093/oxfordjournals.pan.a004872) e [_JEBS_
26(2):233–268](https://doi.org/10.3102/10769986026002233), ambos lidos só no
resumo, e [_APSR_ 95(2):397–413](https://doi.org/10.1017/S0003055401002209),
só metadados. Os modelos de mistura separam quem mantém a opinião, quem muda ao
acaso e os "durable changers", num painel suíço de quatro ondas em quase dois
anos sobre políticas de redução de poluição. Os autores concluem contra a tese
de erro de medida puro (Achen). A sobreposição é parcial: persistência, ruído e
mudança durável, sem mecanismo de influência e sem marginais igualadas. Na mesma
família entram Heise, Wiley–Wiley, Alwin, o modelo traço–estado–erro de
[Kenny e Zautra (1995)](https://doi.org/10.1037/0022-006X.63.1.52) e
[Cole, Martin e Steiger (2005)](https://doi.org/10.1037/1082-989X.10.1.3),
estes dois lidos no resumo. Cole et al. mostram soluções impróprias com poucas
ondas ou estabilidade extrema. O problema estatístico de separar traço, mudança
e erro em muitas ondas já é conhecido, mas sem mecanismo social.

[Lang e Lu (2023)](https://doi.org/10.3934/fods.2023007) (resumo do arXiv
2106.05565; o §1 foi lido na revisão anterior) caracterizam a
identificabilidade do núcleo de interação a partir de trajetórias e de
densidades de campo médio, sem ruído de medida nem alternativa de persistência.
Não há sobreposição com o critério de interrupção. [Kandler, Wilder e Fortunato
(2017)](https://doi.org/10.1098/rsos.170949) (resumo) mostram que "the temporal
dynamic of cultural change over time retains a stronger signature" e propõem
excluir processos em vez de identificar um. É apoio conceitual, sem painel com
erro.

A literatura sobre efeitos de pares não interrompe o estudo sintético, mas
limita a interpretação. [Manski (1993)](https://doi.org/10.2307/2298123)
(resumo) mostra que a inferência sobre efeito endógeno do grupo "is not
possible unless the researcher has prior information specifying the composition
of reference groups". [Shalizi e Thomas (2011)](https://doi.org/10.1177/0049124111404820)
(resumo) mostram que homofilia, contágio e efeitos de covariáveis individuais
são "generically confounded", e que imitação simples gera correlação entre
traços duradouros e escolhas. [Aral, Muchnik e Sundararajan (2009)](https://doi.org/10.1073/pnas.0908800106)
(resumo) atribuem à homofilia mais de 50% do contágio aparente. No campo médio
de Gestefeld e Lorenz, o grupo de referência é a população inteira e a
distribuição é estacionária. O termo social vira um funcional fixo, e um
processo individual não social com o mesmo núcleo de transição reproduz os
dados. Essa é uma inferência minha, coerente com Manski e com o ¶7.9. Mesmo um
resultado positivo discriminará assinaturas dinâmicas, isto é, âncora mais erro
contra mistura ergódica com deriva dependente do estado. Não discriminará
"influência social" enquanto tal.

Os trabalhos de validação com surveys não trazem o contraste, segundo o que li.
[Lorenz et al. 2021](https://doi.org/10.1037/rev0000291), [Duggins 2017](https://doi.org/10.18564/jasss.3316)
e [Banisch e Shamon 2024](https://doi.org/10.18564/jasss.5305) foram lidos no
resumo. Lorenz 2017, sobre esquerda–direita no ESS, só aparece citado no ¶1.7
de Gestefeld e Lorenz e não foi lido. [Kozitsin (2023)](https://doi.org/10.1080/0022250X.2021.1956917),
lido pelo trecho de busca, usa três retratos de usuários do VK com rede de
amizade, exatamente a informação de exposição que falta ao SHP. Nenhum deles
compara com persistência mais erro calibrado. Os 11 trabalhos que citam
Gestefeld e Lorenz no OpenAlex, lidos pelo título, também não fazem esse
contraste.

| Obra                                               | Contraste completo?                                                                        | Veredito                        | Diferença que resta                                                                            |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------- | ---------------------------------------------------------------------------------------------- |
| Gestefeld e Lorenz 2023                            | Não; falta baseline de persistência                                                        | Parcial                         | O melhor ajuste já é ancorado; é preciso separar os braços de influência ancorada e sem âncora |
| Carpentras e Quayle 2023                           | Não                                                                                        | Parcial, conceitual             | Canal de escala contra erro aleatório; sem painel                                              |
| Carpentras e Quayle 2026                           | Não verificado                                                                             | Risco residual                  | Capítulo fechado                                                                               |
| Moor-Smith e Carpentras 2026                       | Não; nulo macro e ruído de processo                                                        | Parcial                         | Persistência individual, erro de medida e painel                                               |
| Kiley e Vaisey 2020/2021; Lersch 2023              | Persistência com erro contra mudança, sim; influência explícita e marginais igualadas, não | Parcial forte                   | Mecanismo de interação, marginais igualadas, âncora de ρ e transições                          |
| Hill e Kriesi 2001; Heise, Wiley, Alwin, TSE       | Não                                                                                        | Parcial, estatístico            | Sem mecanismo social                                                                           |
| Lang e Lu 2023; Kandler et al. 2017                | Não                                                                                        | Sem sobreposição com o critério | Sem erro de medida                                                                             |
| Manski; Shalizi e Thomas; Aral et al.              | Não se aplica ao sintético                                                                 | Interrompe a afirmação causal   | Resultado vale como assinatura dinâmica                                                        |
| Lorenz et al., Duggins, Banisch e Shamon, Kozitsin | Não                                                                                        | Sem sobreposição                | —                                                                                              |

## Veredito

Não encontrei trabalho que já contenha o contraste completo: influência da
família Gestefeld–Lorenz contra persistência latente com erro, marginais
igualadas, erro dentro de confiabilidade publicada e geometria de 11 ondas. Não
há interrupção. Há duas sobreposições parciais fortes. Kiley–Vaisey e Lersch
já tratam persistência com erro contra mudança persistente em painéis longos,
inclusive no SHP com `P$$P04`, e já afirmam qualitativamente a
indistinguibilidade quando a atualização é frequente. Moor-Smith e Carpentras
já mostram que o ruído empurra a seleção para "sem mudança". A contribuição
defensável é quantitativa e específica ao mecanismo: em que ρ, com quais
estatísticas (perfil r(k), matriz de transição, assimetria dos desvios) e com
quantas ondas os braços se separam. Três ajustes tornam isso sustentável:
incluir o braço de influência sem âncora, porque o melhor ajuste publicado reancora
cerca de 92% dos agentes por ano; fixar ρ externamente na faixa de 0,65 a 0,80
em vez de ajustá-lo; e enunciar o resultado como distinção entre assinaturas
dinâmicas, não como identificação de influência social.

## Lacunas desta consulta

Não li o capítulo de Carpentras e Quayle (2026), o suplemento B de Lersch, os
apêndices de Devine e Valgarðsson, o livro de Alwin (2007), os textos integrais
de Hill e Kriesi, Kroh, Vaisey e Kiley (2021), Manski, Shalizi e Thomas, Aral
et al. e Kandler et al., nem o working paper SHP 1/00. O limite de ρ derivado do
SHP é cálculo meu, com erro gaussiano, sobre números de outra amostra. As buscas
foram feitas em inglês, com a ferramenta de busca web, OpenAlex, Crossref,
arXiv, OSF e os catálogos FORS e SWISSUbase.
