# Calibração empírica: identificabilidade e previsão probabilística

Data da investigação: 12/09/2026. Corte de publicação: 11/09/2026.
Status: memo exploratório para comparação de propostas; não é síntese aceita,
triagem do corpus completo, questão selecionada ou protocolo de experimento.

## Decisão provisória

A direção genérica de “calibrar modelos de opinião e validar fora da amostra”
já está ocupada. Também estão ocupadas a comparação entre inferência por
verossimilhança e simulações, a investigação de identificabilidade do BCM e a
comparação entre reconstrução individual e previsão agregada. A proposta que
merece um piloto curto é mais estreita: **a escolha do alvo probabilístico e da
regra de avaliação altera a preferência pelo modelo sem mudança, depois de
separar aleatoriedade da dinâmica e incerteza da pesquisa amostral?**

A contribuição possível seria estabelecer quando um teste de previsão consegue
discriminar distribuições geradoras e quando seus dados são insuficientes. Não
seria demonstrar que um mecanismo psicológico foi identificado. A novidade desta
combinação ainda é hipótese: o antecedente mais direto já aponta a dificuldade
com saídas estocásticas. A aceitação da síntese poderá eliminar esta proposta.

Este documento segue o [charter](../../../charter/study-charter.md), o
[protocolo v3](../../../literature/protocol/opinion-dynamics-systematic-map-v3.json)
e o [mapa exploratório da área](../../../literature/search-design/2026-09-12-area-map/README.md).
A [questão oficial](../../research-questions.md) permanece não selecionada.

## Oito trabalhos originais e os contraexemplos à novidade

As leituras abaixo foram feitas nas manifestações abertas indicadas. “Lido”
significa inspeção do texto e das seções descritas; não significa reprodução
computacional, revisão de todas as referências ou validação independente das
demonstrações. Preprint e versão publicada contam como uma obra.

| Obra e identificadores | Evidência diretamente inspecionada | Consequência para a proposta |
| --- | --- | --- |
| Chacoma e Zanette, 2015. `10.1371/journal.pone.0140406` | [PLOS, Methods, Results e Supporting Information](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0140406). Experimento com 85 estudantes e 20 questões quantitativas, duas respostas e confiança; parâmetros da influência são obtidos dessas observações. A resposta de referência foi gerada experimentalmente. | Já existe calibração de uma regra microscópica com dados humanos. Duas respostas em uma tarefa de estimativa não oferecem uma série histórica de opiniões políticas nem observação de propagação em rede. |
| Gestefeld e Lorenz, 2023. `10.18564/jasss.5204` | [JASSS, dados ESS/SHP, modelo, ajuste e conclusão](https://www.jasss.org/26/4/9.html). Calibração a 1.235 distribuições ESS e transições SHP; ajuste por R². Os autores distinguem capacidade geradora de validação e reconhecem a ausência de comunicação observada. | Reproduzir histogramas e transições já foi feito. Não permite atribuir mecanismos a pessoas somente a partir do ajuste. O arredondamento das opiniões contínuas para onze categorias pertence ao modelo de observação. |
| Banisch e Shamon, 2024. `10.18564/jasss.5305` | [JASSS, definição do modelo, análise sistemática, CoMMCal e discussão](https://www.jasss.org/27/1/17.html). Confrontam viés de processamento calibrado por mudanças individuais com distribuições macroscópicas. Usam divergência Jensen–Shannon, 500 agentes, 10.000 passos e 25 réplicas por ponto da grade. | Consistência micro–macro também é antecedente, não novidade. O modelo não observa a rede, a seleção de parceiros ou os processos de consumo de mídia da população. |
| Lenti, Monti e De Francisci Morales, WSDM 2024; preprint 2023. `10.1145/3616855.3635785`; `arxiv:2310.02766` | [Preprint v2, §§3–5](https://arxiv.org/html/2310.02766v2). Comparam máxima verossimilhança e método de momentos simulados no BCM estocástico: observação completa, somente interações positivas e proxies ruidosos de opiniões. Implementação por diferenciação automática. A identidade publicada foi conferida no [registro DBLP](https://dblp.uni-trier.de/rec/conf/wsdm/LentiMM24.html). | “Avaliar dados incompletos ou ruidosos” sozinho repete este estudo. As experiências controladas informam recuperação sob o gerador assumido; não demonstram validade humana do BCM. Não se acessou ACM DL. |
| Borile et al., preprint 2025; Royal Society Open Science 2026. `arxiv:2506.11751`; `10.1098/rsos.251253` | [Preprint v1, §§2–5 e apêndice B](https://arxiv.org/html/2506.11751v1). Analisa estimadores do limite de confiança e da convergência; relata viés persistente para convergência e problemas práticos na estimação conjunta. [Depósito Crossref exato](https://api.crossref.org/works/10.1098/rsos.251253) confirma título e publicação em 04/03/2026. | Identificabilidade já é tema central deste antecedente. Equações e limites aqui se referem ao preprint: a versão editorial retornou HTTP 403 e não foi comparada integralmente. |
| Kolic et al., PNAS Nexus 2026; preprint 2025. `10.1093/pnasnexus/pgag161`; `arxiv:2509.17625` | [Página editorial: resumo, data, disponibilidade](https://academic.oup.com/pnasnexus/article/5/5/pgag161/8687331); [preprint v1: Results, Methods e discussão](https://arxiv.org/html/2509.17625v1). Compara EnKF e inferência por verossimilhança, estima estados com 250 de 1.000 passos e prevê interações restantes. Há ruído nos estados e limite de confiança incorreto. | Já compara precisão individual/agregada e previsão sob especificação incorreta. A avaliação é sintética, com BCM síncrono determinístico e limite de confiança conhecido no caso principal. Não é calibração de parâmetros em surveys humanos. |
| Moor-Smith e Carpentras, 2026, apresentado como long paper no SSC 2025. `arxiv:2602.00876` | [Preprint v1, §§2–5](https://arxiv.org/html/2602.00876v1). Compara Deffuant, HK, ED e Duggins; calibra no passado e valida depois, incluindo seis séries ESS. A métrica e as ressalvas são detalhadas abaixo. | Elimina a novidade de um benchmark temporal genérico no ESS. É a base a reproduzir e estender, sem pressupor erro dos autores. |
| Tang, Snijders e Flache, 2025. `10.18564/jasss.5566` | [JASSS, métodos, especificação, resultados, discussão e apêndice](https://www.jasss.org/28/1/2.html). SAOM multinível em 46 turmas, preferências por vestuário rap/hip-hop e redes longitudinais. Estima efeitos de similaridade próxima/distante, controlando amizade e evolução da rede. Encontra suporte para influência negativa e assimilação entre amigos, pouco para confiança limitada. | A distinção empírica entre mecanismos concorrentes também já foi investigada. Resultado sobre um contexto e modelo não equivale a identificação causal universal; não é baseline intercambiável com histogramas transversais do ESS. |

Uma verificação adicional de novidade encontrou [Lenti et al., Variational
Inference of Parameters in Opinion Dynamics Models](https://arxiv.org/html/2403.05358),
`arxiv:2403.05358`: inspeção da descrição experimental e conclusão confirma
inferência de parâmetros microscópicos/macroscópicos em modelos sintéticos,
incluindo regras de interação, atualização e rede. Não constitui uma nona
extração aceita; reforça que propor um estimador genérico seria insuficiente.

## O teste próximo e o alvo que pode ser diferente

Moor-Smith e Carpentras definem, para histogramas de opiniões por onda,

\[
E(M,D)=\sum_{t=2}^{T}W_1(O_t,M(O_{t-1})),\qquad
M_0(O_t)=O_t,\qquad V=1-\frac{E(M,D)}{E(M_0,D)}.
\]

O TPE minimiza a média desse erro entre réplicas. Os autores já testam
gerador conhecido, recuperação por otimização, ruído gaussiano e séries ESS
selecionadas por drift; relatam desempenho baixo de Duggins mesmo sob seu
próprio gerador e explicitam a limitação para saídas estocásticas. Portanto,
nem adicionar ruído nem observar congelamento são contribuições novas.
[Fonte: §§2.1–2.3, 3 e 5](https://arxiv.org/html/2602.00876v1).

**Inferência metodológica deste memo:** avaliar a média de distâncias por
realização é um objetivo diferente de avaliar a distribuição preditiva das
realizações. Isso não torna a métrica inadequada para o alvo escolhido pelos
autores. Permite perguntar se as conclusões se mantêm para outro alvo,
explicitamente probabilístico, com a mesma informação disponível.

A distinção fundamental proposta é entre:

- a distribuição das opiniões de indivíduos numa população em uma onda;
- a distribuição preditiva de **histogramas observados** em uma onda futura,
  resultante das trajetórias possíveis da população e do processo de amostragem.

Para o segundo alvo, cada observação seria um vetor de proporções
\(y_t\in\mathbb R^{11}\). Um ensemble produziria
\(X_1,\ldots,X_R\), também histogramas observados simulados. O piloto pode usar
o energy score, com orientação de perda e norma euclidiana:

\[
\widehat{ES}=\frac1R\sum_{r=1}^R\|X_r-y_t\|_2
-\frac{1}{2R(R-1)}\sum_{r\ne s}\|X_r-X_s\|_2.
\]

Sua propriedade de avaliação probabilística deriva de
[Gneiting e Raftery, 2007, §4.3](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf),
`10.1198/016214506000001437`; trata-se de fundamento estatístico, não de técnica
nova. A estimativa acima usa pares independentes e exclui a diagonal. RPS para
uma resposta individual seria outro alvo, a registrar separadamente, e não
pode substituir este teste de histogramas. O score não resolve a escolha de
escala, observação ou informação disponível.

### Especificação comum para o contraste sintético

O alvo candidato é `Q_theta(H_(t+1) | H_t, n_t, n_(t+1), delta_t)`, a lei do
vetor de frequências observado na próxima onda, condicionado à mesma informação
disponível para todos os braços. As onze categorias ordenadas `0,...,10` têm
representantes `k/10`; cada opinião em `[0,1]` entra no bin do representante
mais próximo, com empate atribuído ao maior. Essa regra também define as
frequências usadas em W1. No piloto,
cada previsão de um passo reinicia no mesmo `H_t` observado, inclusive quando
`t` pertence ao trecho de validação. Isso não é previsão livre de várias ondas.

Uma inicialização comum proposta amostra `N` agentes das frequências de `H_t`,
aplica a dinâmica por `delta_t` e obtém a distribuição populacional simulada.
A observação futura é uma amostra multinomial de tamanho `n_(t+1)` dessa
distribuição. O baseline constante usa a mesma inicialização e observação, com
zero atualizações de opinião; o drift usa parâmetros estimados só no treino.
O oracle conhece parâmetros geradores, mas recebe o mesmo histograma observado,
sem acesso privilegiado a opiniões individuais latentes. Esse desenho simples
é um controle sintético, não uma representação já validada da amostragem ESS.

Para cada par onda/modelo, `R>=2` réplicas independentes definem a previsão; o
estimador acima usa norma euclidiana, expoente 1 e pares fora da diagonal.
Reportar erro Monte Carlo e usar observações/replicações externas independentes
para avaliar risco. A comparação W1 usa as mesmas categorias ordenadas e o mesmo
`H_(t+1)` observado; a previsão central é a média dos vetores do ensemble.
Comparar ordenações e diferenças pareadas dentro de cada score, nunca os valores
absolutos de scores com escalas distintas. Não substituir a norma euclidiana do
energy score por W1 e conservar uma alegação de propriedade estrita sem prova.
Essas definições resolvem a comparação conceitual; parâmetros, repetições e
partições finais serão congelados em uma especificação antes da execução.

Identificabilidade também deve permanecer separada de previsão. No BCM
estocástico do [preprint de Borile et al., §2](https://arxiv.org/html/2506.11751v1),
a probabilidade de interação é
\(\sigma_\rho(\epsilon-|x_i-x_j|)\), com aproximação das opiniões quando há
interação. A inferência depende de estados/eventos observáveis e de parâmetros
conhecidos; essas condições não são oferecidas por histogramas ESS. Um bom
score de histogramas não recupera automaticamente \(\epsilon\), a convergência,
a rede ou a causalidade da influência.

## Candidata falsificável e desenho do piloto

Pergunta candidata: **sob quais combinações de variabilidade da dinâmica,
intervalo entre observações e erro amostral a previsão probabilística de
histogramas distingue um modelo dinâmico do baseline sem mudança, e essa
distinção se transporta para ondas futuras do ESS?**

O piloto deve começar sintético, antes de escolher uma série que favoreça a
hipótese. Usar inicialmente Deffuant e uma versão estocástica explicitamente
definida; acrescentar Duggins apenas depois de reproduzir sua implementação e
entender a variabilidade. Isso mantém comparadores reconhecíveis sem abrir um
novo catálogo de modelos. Incluir geradores-controle sem mudança e com drift
exógeno, para que o procedimento possa concluir contra influência social.

Comparar três avaliações sobre as mesmas previsões: média de W1 por realização;
W1 de uma previsão central claramente definida; energy score do ensemble de
histogramas. A segunda separa efeitos de agregação das réplicas da propriedade
probabilística da terceira. Primeiro conservar o ajuste dos parâmetros e mudar
somente a avaliação. Depois, num experimento separado, ajustar com cada perda,
com o mesmo orçamento de busca, conjunto de candidatos e sementes de treino.
Essa separação evita confundir um otimizador melhor com um alvo diferente.

Em todos os braços, o baseline sem mudança deve receber a **mesma camada de
observação**: uma população constante ainda gera amostras distintas. Incluir
também um baseline de drift estimado somente no treino. Em simulações, variar
separadamente aleatoriedade das interações, espaçamento entre ondas e tamanho
da amostra; não chamar ruído gaussiano adicionado à dinâmica de erro de survey.
O oracle com parâmetros geradores conhecidos verifica a capacidade do teste;
o modelo ajustado verifica perda de informação e dificuldade de calibração.

Registrar recuperação de parâmetros como diagnóstico distinto: erros de
estimação, superfícies/perfis de perda e pares de parâmetros com previsões
indistinguíveis. Uma equivalência encontrada numericamente é evidência de
identificabilidade prática limitada naquele desenho, não prova de equivalência
estrutural de todos os mecanismos. Se o sistema não consegue separar o gerador
conhecido de controles, não inferir que dados empíricos rejeitam aquele mecanismo.

Para ESS, escolher variáveis, países e filtros somente com as ondas de treino;
congelar depois o holdout temporal. Preservar escala ordinal, pesos, desenho de
amostragem e mudanças no modo de coleta. A camada amostral simples multinomial
serve como controle sintético; não substitui automaticamente o desenho
complexo do ESS. Bootstraps devem respeitar a unidade de amostragem disponível,
e intervalos entre ondas não podem ser tratados como igualmente informativos
sem análise. Não usar cada entrevistado como réplica temporal independente.

Hipóteses e decisões propostas, a registrar antes das execuções:

| Evidência do piloto | Interpretação e decisão |
| --- | --- |
| Com gerador dinâmico conhecido e sinal suficiente, o score de histogramas favorece a distribuição geradora, enquanto a avaliação por realização favorece o congelamento | Justifica investigar dependência do alvo de avaliação. Não prova melhora empírica nem erro no benchmark anterior. |
| As avaliações concordam, ou a divergência desaparece com mais réplicas/observações | Não sustenta a contribuição pretendida. Abandonar ou reduzir a uma reprodução documentada. |
| O novo procedimento prefere dinâmica quando o gerador é sem mudança | Falha de controle: revisar calibração do teste, camada amostral, seleção ou vazamento antes de qualquer teste humano. |
| O oracle funciona, mas o modelo estimado falha | Evidência de dificuldade de calibração/informação, não de inexistência do mecanismo gerador. |
| Melhora sintética, mas sem vantagem sobre no-change e drift no holdout ESS | Resultado negativo informativo; não afirmar validade empírica ou identificar influência social. |
| Obra anterior já executou o mesmo contraste de alvos, controles e observação | Encerrar a alegação de novidade; só prosseguir se uma diferença científica substantiva for identificada. |

Como regra operacional inicial, limitar o piloto a dois regimes, duas escalas
de amostragem e pelo menos 30 trajetórias independentes por célula; estimar o
erro Monte Carlo antes de ampliar. O número definitivo de réplicas e o menor
efeito relevante dependem dessa estimativa, não de conseguir significância.
Usar sementes novas e um lote independente de confirmação; relatar também
taxa de escolhas erradas nos controles. Um limite de dois dias de trabalho
para acesso/reprodução e mais três para o contraste sintético evita consumir
o calendário numa dependência que não funciona. São limites de planejamento,
não medições de custo nem autorização de experimento registrado.

## Dados, código e viabilidade realmente verificados

| Recurso | Acesso/licença conferidos em 12/09/2026 | Viabilidade e limite |
| --- | --- | --- |
| Chacoma–Zanette, dados brutos | [S1 Table, DOI do suplemento](https://doi.org/10.1371/journal.pone.0140406.s002). Endpoint editorial retornou HTTP 200, PDF de 56.487 bytes e assinatura `%PDF-`. Artigo declara CC BY e dados no suplemento. | Dados existem, mas são PDF, não uma tabela já extraída/verificada. Permitem estudo de mudança individual entre duas respostas; não suprem o painel temporal necessário para a candidata. Não houve ingestão ou reprodução. |
| Gestefeld–Lorenz | [OSF fsbda](https://osf.io/fsbda/), apontado pelo artigo. Consulta pública sem credenciais retornou HTTP 401. | Licença e inventário não foram verificados. O link editorial contém acesso de visualização; nenhum token é reproduzido neste memo. Não baixar material que exija essa exceção de acesso. ESS e SHP têm condições próprias; não inferir licença dos dados a partir do artigo. |
| Banisch–Shamon | [OSF 5tz6g](https://osf.io/5tz6g/); [API pública do projeto](https://api.osf.io/v2/nodes/5tz6g/). Projeto público, `node_license=null`. No provedor `osfstorage`, a consulta retornou um README; lista de componentes retornou vazia. | README declara análises em MATLAB e componentes para dois artigos, mas os arquivos desses componentes não foram localizados nessa consulta. Não marcar o pacote como reproduzível nem assumir licença de reutilização. |
| Lenti et al., WSDM | O preprint aponta um [endereço anônimo de código](https://anonymous.4open.science/status/ABMcalibration-MLvsMSM-4837); consulta web falhou. | Artigo descreve código aberto; conteúdo e licença não foram confirmados. Verificação de reprodução pendente. |
| Lenti et al., inferência variacional, pista adicional | [GitHub dos autores](https://github.com/jaclenti/VI_opinion_dynamics). README, `src/`, notebooks e ambientes listados via API. API informou `license=null`; não apareceu LICENSE na raiz. | README instrui `inference_*.py` e GNU parallel para lotes. Há medidas `.pkl`, não todas as trajetórias. Não executar serializações ou presumir licença; não é baseline obrigatório da candidata. |
| Kolic et al., pacote de reprodução | O DOI citado pelo artigo, [17153274](https://zenodo.org/records/17153274), tem versão `empty-release`, ZIP de 446 bytes. O DOI conceitual resolve ao [sucessor 20067519](https://zenodo.org/records/20067519), criado em 07/05/2026: CC BY 4.0, ZIP de 113.365.239 bytes. | Foram inspecionados por HTTP Range o diretório ZIP (88 entradas), README e dois ambientes, sem executar código. O pacote usa Python/TensorFlow e Julia/EnKF; README descreve pipeline de geração, inferência e figuras. O [GitHub citado](https://github.com/corradomonti/comparison-lbi-da-abm) contém somente `README.txt` com `TBD`. O sucessor torna reprodução plausível, mas não comprova que funciona; registrar DOI e checksum antes do uso. |
| Moor-Smith–Carpentras | Texto aberto CC BY 4.0. Não foi identificado link de código no HTML v1 nem na busca literal por título/autores/código. | Ausência de link encontrado não prova ausência de implementação. Baseline completo depende de recuperar detalhes de parâmetros, orçamento, réplicas e implementações citadas; uma reimplementação deve ser declarada como tal. |
| Tang et al. | Artigo aberto e métodos RSiena/`sienaBayes` descritos. Nenhum link explícito para pacote de dados/código foi encontrado no HTML inspecionado. | TASS contém redes de adolescentes. Acesso, condições de uso e pacote específico não foram confirmados; não adquirir para esta candidata. Serve como antecedente científico, não como dependência do piloto. |
| ESS | [Condições oficiais](https://www.europeansocialsurvey.org/contact/disclaimer): dados CC BY-NC-SA 4.0; documentação CC BY-SA 4.0. O [portal](https://www.europeansocialsurvey.org/data-portal) retornou 502 nesta verificação; nenhum dataset foi obtido. | Fixar rodada, edição, variáveis, pesos e autorização aplicável antes da etapa empírica. A licença não prova acesso funcional. Não usar cópia de terceiro como substituta silenciosa. |

O pacote alternativo de Kolic oferece uma reprodução auxiliar, não resolve a
falta do código do benchmark ESS. Suas dependências declaradas incluem
Python 3.10.11/TensorFlow 2.11.1, além da parte em Julia; funcionamento nativo no
Apple M5 não foi verificado. A coordenação inspecionou uma máquina M5, 10 CPUs
lógicas e 16 GiB RAM; não há tempo/memória medidos para estes modelos nem
inventário de VPS. A candidata é plausível com experimentos pequenos de CPU e
sem novos modelos de linguagem, mas a viabilidade completa permanece
condicionada à reprodução e ao acesso ao ESS.

## Registro da busca e limites de cobertura

Todas as consultas abaixo foram executadas em 12/09/2026 pelo mecanismo de
busca web; fontes secundárias apareceram como pistas, mas afirmações de método
foram conferidas em editoras, arXiv, depósitos dos autores ou APIs oficiais.
Consultas não tinham filtro temporal da API: datas foram verificadas no
documento e o corte 11/09/2026 foi aplicado à decisão de considerar o trabalho.

```text
"opinion dynamics" "identifiability" 2024 2025
"opinion dynamics" "calibration" "validation" 2023 2024 2025 2026 data
"Bias and Identifiability in the Bounded Confidence Model"
"opinion" "models learned to" "freeze"
"opinion dynamics" "out-of-sample" 2025 2026
"opinion dynamics" "identifiability" 2023 2026
"Likelihood-Based Methods Improve Parameter Estimation in Opinion Dynamics Models"
"opinion dynamics" "freeze" "European Social Survey"
"Comparing data assimilation and likelihood-based inference" github arxiv
"Testing the validity of multiple opinion dynamics models" github
"Moor-Smith" "Carpentras" code opinion dynamics
"opinion dynamics" "proper scoring" 2024 2025 2026
"opinion dynamics" "probabilistic" "validation" "Wasserstein"
"opinion dynamics" "energy score"
"opinion dynamics" "proper scoring rules"
"10.18564/jasss.5566"
"10.1098/rsos.251253"
Gneiting Raftery 2007 strictly proper scoring rules energy score pdf washington
"European Social Survey" data license CC BY 4.0 download registration
site.europeansocialsurvey.org "register" "download" "data portal"
site.europeansocialsurvey.org "data portal" "register"
"empirical opinion distributions and transitions" "10.18564"
"Validating Argument-Based Opinion Dynamics" "10.18564"
```

O caminho de descoberta foi: sementes retidas → buscas temáticas de
identificabilidade/previsão → Lenti/Borile → Kolic e seus artefatos; busca de
“freeze” → resumo SSC 2025 → preprint completo de Moor-Smith–Carpentras.
Tang e a versão publicada de Borile vieram da checagem do corpus pela
coordenação e foram verificados nas fontes acima. Buscas por scores também
encontraram agregação de previsões humanas e incentivos de previsão, alvos
diferentes; não foram convertidos em exclusões científicas.

Não houve exaustão de provedores, duas rodadas sem novos elegíveis, triagem
dupla ou adjudicação humana. Não se acessou ACM DL/IEEE Xplore nem se fez busca
automatizada no Google Scholar. As falhas HTTP e licenças não verificadas
permanecem pendências, e não evidência de inexistência. O cruzamento exato dos
identificadores com o corpus é tarefa da coordenação e não foi inventado aqui.

Antes de selecionar a candidata, concluir esse cruzamento e procurar
ativamente extensões/citações de `arxiv:2602.00876`, `arxiv:2509.17625` e
`10.1098/rsos.251253` que já façam avaliação probabilística de histogramas com
erro amostral. A busca dirigida deste memo justifica uma opção para piloto;
não sustenta uma lacuna definitiva ou conclusão sobre toda a literatura.
