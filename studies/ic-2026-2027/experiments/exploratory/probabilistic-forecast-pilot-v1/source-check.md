# Checagem de fontes do piloto de previsão probabilística

Data: 12/09/2026. Corte bibliográfico: 11/09/2026. Status: nota exploratória
de fontes para o piloto B; não é revisão sistemática, extração aceita,
protocolo registrado ou demonstração de novidade. Complementa o
[memo de evidência empírica](../../../research/questions/exploration/2026-09-12/empirical-evidence.md).
Foram consultados textos primários públicos; nenhum dado de pesquisa foi
adquirido e nenhum código externo foi executado.

## Benchmark: um passo e erro médio entre realizações

Moor-Smith e Carpentras definem o operador como previsão da próxima onda
a partir da distribuição observada na onda anterior. A Eq. (1) soma
distâncias Wasserstein, e os §§3.1.1 e 3.2 reiteram que cada previsão recebe
o estado verdadeiro correspondente. Portanto, a validação reinicia em cada
observação; não é uma trajetória livre alimentada pelas previsões anteriores.
No §2.3, o ajuste repete cada configuração e usa a média dos erros:
“use the average error as the loss for that trial”.
[Fonte primária: preprint v1, §§2.1–2.3, 3.1.1 e 3.2](https://arxiv.org/html/2602.00876v1).

Escrevendo explicitamente a aleatoriedade, a perda descrita corresponde a

\[
\widehat L(M,D)=\frac1R\sum_{r=1}^{R}\sum_{t=2}^{T}
\Delta\!\left(O_t,M^{(r)}(O_{t-1})\right).
\]

O artigo identifica Wasserstein e SciPy, mas não informa ali versão ou
nome da função. A função unidimensional `scipy.stats.wasserstein_distance`
calcula W1; essa é a interpretação adotada no piloto, sem alegar auditoria
da implementação original. Para histogramas, os suportes devem ser as
categorias e os pesos suas frequências, não as frequências tratadas como
valores amostrais.
[Documentação oficial do SciPy: definição, parâmetros e notas](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wasserstein_distance.html).

Os próprios autores reconhecem, no §5, que o procedimento favorece saídas
reproduzíveis e pedem uma metodologia para “multiple outcomes with different
probabilities”. Isso já antecipa a motivação do piloto; a extensão não pode
ser apresentada como descoberta dessa limitação.
[Fonte primária: discussão](https://arxiv.org/html/2602.00876v1).

## Energy score e estimador finito

Gneiting e Raftery definem o energy score para previsões de vetores em
\(\mathbb R^m\), norma euclidiana e expoente \(\beta\in(0,2)\), com momento
de ordem \(\beta\) finito. A Eq. (22) usa orientação de recompensa;
invertendo o sinal e fixando \(\beta=1\), o piloto minimiza

\[
ES(P,y)=\mathbb E_P\|X-y\|_2-
\frac12\mathbb E_P\|X-X'\|_2,
\qquad X,X'\stackrel{iid}{\sim}P.
\]

A regra é estritamente própria nessa classe. Histogramas de proporções
em onze categorias são vetores num simplex limitado, logo satisfazem a
condição de momento. Usar norma ao quadrado corresponderia ao limite
\(\beta=2\), que depende somente da média e perde a propriedade estrita.
A afirmação euclidiana também não autoriza substituir a norma por W1 sem
uma justificativa matemática específica.
[Gneiting–Raftery, 2007, §4.3, Eqs. (22)–(23), e §5.1; PDF dos autores, pp. 367–369](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf).

Ferro distingue uma previsão que é a própria distribuição empírica do
ensemble de um ensemble interpretado como amostra da distribuição preditiva.
Na Definição 1, a avaliação é *fair* quando a esperança sobre membros e
observação favorece a distribuição geradora correta; é *strictly fair*
se o ótimo é único. A garantia para amostras independentes não se transfere
automaticamente para membros dependentes.
[Ferro, 2014, §§2.1, 2.3 e 3; PDF do autor](https://empslocal.ex.ac.uk/people/staff/ferro/Publications/ferro2013.pdf),
[registro editorial, DOI 10.1002/qj.2270](https://rmets.onlinelibrary.wiley.com/doi/abs/10.1002/qj.2270).

Fricker, Ferro e Stephenson apresentam a correção do CRPS univariado na
Eq. (4), com pares distintos, e explicam que sua esperança deve igualar a
do score da distribuição geradora. A Eq. (4) subtrai do CRPS empírico
\(\sum_{i\ne j}|X_i-X_j|/[2m^2(m-1)]\); combinada ao termo de dispersão
original, isso produz o denominador \(2m(m-1)\). Essa fonte trata diretamente
o caso escalar, não demonstra uma nova fórmula para histogramas.
[Fricker–Ferro–Stephenson, 2013, §4, pp. 250–251; PDF dos autores](https://empslocal.ex.ac.uk/people/staff/dbs202/publications/2013/fricker2013.pdf).

Derivação para o piloto: condicionados à informação disponível e aos
parâmetros fixos, sejam \(X_1,\ldots,X_R\) histogramas simulados iid,
independentes da observação de verificação, com \(R\ge2\). Então

\[
\widehat{ES}_{fair}=
\frac1R\sum_r\|X_r-y\|_2-
\frac{1}{2R(R-1)}\sum_{r\ne s}\|X_r-X_s\|_2.
\]

Cada termo da primeira média estima \(\mathbb E\|X-y\|_2\); cada par
distinto estima \(\mathbb E\|X-X'\|_2\). Pela linearidade da esperança,
\(\mathbb E[\widehat{ES}_{fair}\mid y]=ES(P,y)\). Assim, o estimador
é não viesado para esse score e estritamente fair sob as hipóteses dadas.
O denominador \(R^2\), mesmo com diagonal nula, deixaria viés positivo
\(\mathbb E\|X-X'\|_2/(2R)\) em relação à distribuição geradora.
Esse outro denominador é correto quando o alvo é a distribuição empírica
finita dos membros. A escolha depende do alvo declarado.

## Antecedentes encontrados na busca dirigida

| Trabalho e fonte primária inspecionada | Comparação que já existe e limite para este piloto |
| --- | --- |
| Lenti, Monti e De Francisci Morales, WSDM 2024: [preprint v2, §§4–5](https://arxiv.org/html/2310.02766v2); [versão WSDM disponibilizada pelo autor](https://gdfm.me/assets/media/2024/01/likelihood-based-methods-improve-parameter-estimation-in-opinion-dynamics-models.pdf) | Já compara máxima verossimilhança com método de momentos simulados em BCM probabilístico. O baseline usa MSE entre estatísticas das séries de interações; há observação completa, parcial e proxies ruidosos. Isso ocupa a comparação genérica entre ajuste probabilístico e discrepância de simulação. Não é a comparação de scores da lei de histogramas futuros sob uma camada de survey comum. |
| Kolic et al., 2025, [preprint v1, §§2.2 e 4.5.2, apêndice A.2, Fig. SI8](https://arxiv.org/html/2509.17625v1) | Além de comparar inferência por verossimilhança e assimilação, avalia previsão de interações por MAE e apresenta resultados com **Brier score**. A Eq. (14) compara probabilidades previstas com indicadores de interação, e as Eqs. (15)–(16) agregam probabilidades. Portanto, não é seguro afirmar que avaliações probabilísticas e de erro só aparecem separadas nessa literatura. O alvo são interações após inferência de opiniões latentes, não histogramas de survey. A legenda SI8 afirma que valores maiores são melhores; o HTML não explicita a transformação usada. Não reinterpretei sua orientação nem reproduzi seus números. |
| Douven, Kriegeskorte e Stinson, 2026, [artigo editorial, Dynamic aggregation, Data and method e Results](https://journals.sagepub.com/doi/full/10.1177/26339137261435121) | Compara agregadores, incluindo HK modificado, por Brier e acurácia de classificações. Ajusta simultaneamente os dois objetivos no treino e avalia em holdout. São 376 participantes e 1.200 afirmações com verdade conhecida. É contraexemplo a uma novidade genérica de comparar objetivos probabilísticos e decisões pontuais em modelos de opinião; não testa a previsão temporal da distribuição de opiniões de uma população. |
| Gonzalez-Hernandez et al., 2024, [JASSS, resumo e Prediction accuracy, Eqs. (2)–(5)](https://jasss.soc.surrey.ac.uk/27/4/3.html) | Emprega score logarítmico em uma simulação de especialistas que ajustam crenças sob incentivos e consenso. Seu objeto é o algoritmo de recompensas e a qualidade de previsões binárias, não comparar a lei preditiva de histogramas de um modelo com suas realizações individuais. É antecedente relacionado, sem exclusão formal do corpus. |

A nota de Kolic complementa o memo anterior: sua descrição por MAE era
insuficiente para avaliar novidade, pois o apêndice também relata Brier.
Esse achado deve entrar no cruzamento com o corpus e na formulação final
da candidata, preservando o memo anterior como histórico.

## Alcance efetivo da busca

As consultas abaixo foram executadas no mecanismo de busca web em
12/09/2026, sem filtro temporal da API. Inspecionaram-se os textos primários
listados acima; resultados de agregadores serviram apenas como pistas.
As fontes de scoring foram localizadas por título/autores e termos
`energy score`, `fair`, `finite ensemble` e `off diagonal`, seguidos de
consulta às seções e equações indicadas.

```text
"opinion dynamics" "energy score"
"opinion dynamics" "proper scoring"
"opinion dynamics" "probabilistic" "forecast" "Wasserstein"
"opinion dynamics" "likelihood" "simulated moments"
"opinion dynamics" "scoring rules" forecast evaluation
"opinion dynamics" "probabilistic forecast" evaluation
"opinion dynamics" "energy score" histogram
"2602.00876" "score"
"2602.00876" probabilistic
"2509.17625" "Brier"
"Three and a half stages of crowd wisdom" "Brier" "accuracy"
```

As consultas por `energy score` e pelo identificador do benchmark não
localizaram, entre os resultados inspecionados, uma execução do contraste
exato proposto. Isso não é evidência de ausência: não houve busca em bases
bibliográficas com paginação exaurida, rastreio completo de citações,
screening duplo, adjudicação ou cobertura independente de ACM/IEEE.
A página Sage sem `/full/` falhou por timeout, mas a versão editorial
`/full/` foi acessada. A URL alternativa do PDF Gneiting–Raftery resolveu
a falha de leitura de trechos da primeira URL. Não houve reprodução de
pacotes, comparação integral entre preprints e versões publicadas nem
checagem de licença para reutilização de dados.

## Implicação para a contribuição e a execução

A contribuição candidata é testar em que condições a preferência pelo
baseline sem mudança depende do alvo de avaliação **na lei de histogramas
observados**, sob a mesma informação e camada de observação. A busca sustenta
esse recorte como hipótese de trabalho, sem certificar novidade. Usar um
score conhecido, redescobrir o congelamento ou mostrar que a métrica muda
uma ordenação isolada não basta.

No piloto, separar a avaliação de previsões fixas do ajuste com perdas
diferentes; manter sementes de avaliação independentes das de treino;
comparar diferenças pareadas dentro de cada score; e aplicar a mesma
amostragem futura aos baselines. A média de W1 por realização, W1 do
histograma médio e ES avaliam objetos distintos. ES com norma euclidiana
não utiliza a distância ordinal entre categorias: uma divergência entre
W1 e ES também pode refletir essa escolha geométrica. O piloto isolado
não deve atribuir toda divergência à propriedade probabilística; essa
limitação precisa constar da interpretação.

Um gerador conhecido só funciona como oracle do alvo quando sua previsão
implementa a mesma lei condicional de observação usada para produzir os
dados avaliados. Propriedade estrita é uma afirmação de risco esperado,
não garantia de vitória em cada realização, identificação de parâmetros,
calibração de survey real ou validação empírica do mecanismo.
