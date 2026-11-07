# Exposição adaptativa e fragmentação: candidato exploratório

Data da consulta: 12 de setembro de 2026. Corte bibliográfico pretendido: 11 de setembro de 2026. Este memo propõe um teste exploratório, sem selecionar a pergunta da IC, aceitar síntese, decidir inclusão/exclusão ou alterar o protocolo. A leitura dirigida complementa a navegação do [mapa de área](../../../literature/search-design/2026-09-12-area-map/README.md); não estima cobertura da revisão sistemática. Foram respeitados o charter, o lifecycle, `research-questions.md` e o protocolo v3, cujo plano não autoriza afirmar novidade a partir da busca.

A recomendação nesta linha é um piloto de **certificação de fragmentação em redes esparsas**. A pergunta é se um resultado recente sobre a velocidade de convergência sob exposição adaptativa permanece quando a parada exige evidência de que os grupos não voltarão a interagir. Há um contraexemplo matemático pequeno para o critério aproximado; ainda falta saber se o problema tem frequência e consequência científica suficientes para sustentar um artigo. Apenas adicionar viés, rewiring, confiança adaptativa, outras topologias ou uma análise de precisão não seria uma contribuição suficientemente distinta.

## O que os originais já cobrem

As oito entradas abaixo foram verificadas em material primário aberto. “Lido” significa as partes explicitadas, não revisão integral das provas, execução do código ou validação independente dos resultados. Preprints e artigos publicados são manifestações distintas; o texto de um não foi presumido idêntico ao outro.

| Trabalho e identificador | Evidência relevante e limite da leitura |
| --- | --- |
| Sîrbu, Pedreschi, Giannotti e Kertész, 2019. [Algorithmic bias amplifies opinion fragmentation and polarization: A bounded confidence model](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0213246). DOI `10.1371/journal.pone.0213246`. | Lidos modelo, resultados, explicação de convergência, efeitos de tamanho e condições iniciais. A seleção favorece opiniões próximas; a regra usa piso de distância `0.0001` e parada por pequenas mudanças durante 1.000 iterações. O artigo já compara contatos totais, contatos com diferença não nula e contatos ativos na Fig. 4. Portanto, apresentar a separação desses relógios como nova seria incorreto. Há distinção explícita entre fragmentação e consenso muito lento. Não reproduzi as figuras. |
| Neuhäuser, Mellor e Lambiotte, PRE 2020. [Multi-body Interactions and Non-Linear Consensus Dynamics on Networked Systems, preprint v1](https://arxiv.org/html/1910.09226v1). DOI `10.1103/PhysRevE.101.032310`; arXiv `1910.09226`. | Lidas formulação, seções III–IV selecionadas e conclusão. A redução do caso linear a uma rede com pesos reescalados e o deslocamento da média sob interação não linear já estão desenvolvidos. “Comparar pares e trios” só seria informativo com uma hipótese adicional e controles de intensidade, composição e não linearidade. Não reconstruí todas as derivações nem verifiquei identidade com o texto publicado. |
| Pansanella, Rossetti e Milli, 2022. [From mean-field to complex topologies: network effects on the algorithmic bias model](https://arxiv.org/html/2205.08412v1). DOI `10.1007/978-3-030-93413-2_28`; arXiv `2205.08412`. | Lidos resumo, partes do modelo e discussão de topologias no preprint. Já leva o modelo de viés algorítmico para estruturas de rede. Contradiz a ideia de que sair do grafo completo, por si, preenche uma lacuna. Não reproduzi a implementação nem verifiquei todas as figuras. |
| Kan, Feng e Porter, JCN 2023. [An Adaptive Bounded-Confidence Model of Opinion Dynamics on Networks, preprint v3](https://arxiv.org/html/2112.05856v3). DOI `10.1093/comnet/cnac055`; arXiv `2112.05856`. | Lidas regras, partes dos resultados e seção sobre tamanho finito. Arestas discordantes são desfeitas e refeitas por homofilia; os autores já estudam pseudoconsenso e tempos longos. A comparação entre 1.000 e 5.000 nós mantém `p=0.01`, alterando o grau médio, e também muda os números de rewiring e atualizações; o próprio texto reconhece limitações. Isso motiva controles de tamanho e densidade, sem estabelecer que os resultados estejam errados. |
| Hegselmann, JASSS 2023. [Bounded Confidence Revisited: What We Overlooked, Underestimated, and Got Wrong](https://www.jasss.org/26/4/11.html). DOI `10.18564/jasss.5257`. | Lidos introdução, seção 3 e trechos sobre estabilidade, identificação de clusters e aritmética; não todo o artigo nem seus apêndices. Já documenta forte sensibilidade numérica e transições não monotônicas no HK. “Testar floating point e robustez” é uma pauta anterior. O contraexemplo deste memo usa frações exatas e uma ponte numa rede esparsa, evitando confundir erro de representação com insuficiência lógica da parada. |
| Li, Luo e Porter, SIADS 2025. [Bounded-Confidence Models of Opinion Dynamics with Adaptive Confidence Bounds, preprint v3](https://arxiv.org/html/2303.07563v3). [Registro publicado](https://doi.org/10.1137/23M1558951); arXiv `2303.07563`. | Lidas definição, enunciados selecionados, seção 4.2, conclusão e discussão de bailouts no apêndice D. Já adapta confiança em HK e DW e distingue grafo efetivo de opiniões finais. O preprint usa tolerância `0.02` no DW por custo computacional e reconhece que grupos finais aproximados podem diferir dos grupos no limite. Não auditei todas as provas nem a manifestação SIADS integral. |
| Thompsky, Wu, Porter e Luo, preprint 2026. [A Bounded-Confidence Model of Opinion Dynamics with Adaptive Interaction Probabilities, v2 de 22/05/2026](https://arxiv.org/html/2605.20418v2). arXiv `2605.20418`; sem DOI editorial verificado. | Lidas seções II–III, enunciados e partes das provas IV, especificação V.2, resultados e conclusão selecionados. Pesos de arestas controlam exposição e são reforçados/reduzidos após interações. O estudo relata efeitos opostos sobre tempo de convergência em redes chamadas densas e esparsas. Usa diâmetro por componente efetivo com tolerância `0.01`; o Teorema 4 garante a identificação dos grupos para grafos completos. Fora deles, a classificação é aproximada. Não reproduzi o levantamento numérico. É o concorrente central do candidato. |
| Gezha e Kozitsin, Entropy 2026. [Control over Recommendation Algorithms in Heterogeneous Modular Systems with Dynamic Opinions](https://pmc.ncbi.nlm.nih.gov/articles/PMC13025129/). DOI `10.3390/e28030333`. | Lidos resumo, enquadramento, formulação do controle e trechos de resultados/disponibilidade. Já considera heterogeneidade, modularidade e ajuste dinâmico do algoritmo para objetivos macroscópicos, incluindo despolarização. Impede vender “controlar recomendações para reduzir polarização” como lacuna genérica. Não auditei as provas de controle ótimo, a aproximação de campo médio nem executei o suplemento. |

Três concorrentes particularmente próximos e recentes são Kan et al. (2023), Li et al. (2025) e Thompsky et al. (2026). Hegselmann (2023) é também um contraexemplo direto a reivindicações amplas de novidade metodológica.

Uma pista adicional foi consultada: [Bounded-Confidence Models of Opinion Dynamics with Neighborhood Effects](https://arxiv.org/abs/2402.05368), com leitura de resumo, definição e trechos de parada/tamanho no HTML. Não entrou na comparação principal porque introduz influência de vizinhança e rewiring além do mecanismo mínimo proposto. A [Survey on Algorithmic Interventions in Opinion Dynamics](https://arxiv.org/html/2603.10756) foi aberta como ponte de descoberta, sem tratá-la como estudo primário nem extrair dela uma alegação de ausência. Outras pistas não inspecionadas integralmente permanecem fora das conclusões.

## Pergunta, hipótese e contribuição possível

Pergunta provisória: **em DW com probabilidades adaptativas de interação, a diferença entre redes esparsas e densas no tempo até consenso/fragmentação permanece quando a parada certifica que componentes de opinião não poderão se reconectar?**

A hipótese operacional para o piloto é que, perto do limiar de confiança, a parada por pequeno diâmetro aceita uma fração relevante de partições temporárias em redes esparsas; continuar essas mesmas trajetórias muda o número de grupos ou a interpretação do efeito dos pesos adaptativos. A hipótese rival é que esses casos são possíveis, porém raros nos ensembles utilizados, e os contrastes permanecem. Uma mudança de sinal não é presumida.

A contribuição só seria defensável se ligasse um resultado analítico simples a uma consequência substantiva: delimitar onde a classificação de fragmentação é confiável e onde uma conclusão sobre o mecanismo muda. Um certificado conservador sem aplicação relevante, um caso artificial isolado ou apenas uma tolerância menor não bastam como justificativa de novidade. A revisão ainda pode encontrar esse certificado ou a mesma comparação; não foi demonstrada prioridade.

### Contraexemplo analítico verificado neste memo

Considere quatro nós, arestas não direcionadas `{(0,1),(2,3),(0,3)}`, confiança `c=0.1`, compromisso simétrico `mu=0.5` e opiniões `(0, 0.009, 0.096, 0.105)`. Pesos iniciais `z0=0.5`, reforço `gamma=0.5` e redução `delta=0.5` são uma escolha admissível no modelo recente. A única ponte `(0,3)` está inicialmente fora da confiança. Os componentes do grafo efetivo são `{0,1}` e `{2,3}`, ambos com diâmetro `0.009 < tol=0.01`. A regra que verifica somente esses diâmetros aceitaria dois grupos.

Atualizar uma vez cada aresta interna leva a `(0.0045, 0.0045, 0.1005, 0.1005)`. A diferença da ponte passa a `0.096 < c`: ela volta a permitir influência. Todos os nós agora estão num intervalo de largura menor que `c`; sob amostragem recorrente das arestas, a rede conectada chega ao consenso. Esse caminho tem probabilidade positiva quando os pesos iniciais e as probabilidades relevantes são positivos.

A conta foi executada com `fractions.Fraction` em Python, com assertivas para os dois testes de distância. Isso verifica a aritmética e a insuficiência do critério como garantia geral em grafos esparsos. **Não** é reprodução das simulações do artigo, estimativa da prevalência do problema nem demonstração de que seus contrastes empíricos mudam. O Teorema 4 do preprint restringe-se explicitamente ao caso completo, portanto o exemplo não o refuta.

O [código público inspecionado, linhas 259–322](https://github.com/Yolandayx929/adaptive-edge-BCM/blob/5e33664982bda6b7576074ff47772791459ea22c/EdgeWeightedDW.py#L259) constrói componentes efetivos e testa diâmetros; não encontrei ali a condição de separação de intervalos descrita a seguir. Sua função tem tolerância padrão diferente da usada no artigo, de modo que uma reprodução precisará fixar os argumentos do experimento. Não executei o código externo nesta investigação.

### Certificado proposto e suas condições

Para cada componente efetivo `C`, formar seu intervalo atual `I_C=[min(x_C), max(x_C)]`. Uma condição suficiente candidata exige:

1. `diam(I_C) < tol < c` em cada componente;
2. para cada aresta da rede-base que liga componentes distintos `C,D`, a distância entre os intervalos `I_C,I_D` ser pelo menos `c`.

A justificativa é por invariância convexa: sem interação externa, médias internas permanecem nos intervalos atuais. A segunda condição impede que a primeira interação externa ocorra. A primeira mantém as arestas internas receptivas; com recorrência de amostragem, cada componente conectado converge internamente. A [revisão independente](independent-review.md) verificou o argumento de separação e a aritmética do microcaso; isso não constitui aceite científico ou verificação empírica da IC.

O certificado refere-se a confiança fixa, rede-base fixa e atualização simétrica por médias. Rewiring, confiança crescente, influência repulsiva, ruído ou novas exposições fora da rede podem romper o argumento. Exige controle numérico das comparações; frações exatas servem para os microcasos, enquanto cálculos grandes precisam registrar margem e tolerância. A condição é suficiente, não necessária, e não garante tempo de parada finito em todos os casos. Componentes socialmente desconectados podem ainda ter a mesma opinião limite: grupo dinâmico e cluster definido apenas pelo valor da opinião devem ser registrados separadamente.

## Desenho mínimo e viabilidade

Começar apenas com DW em rede fixa e pesos adaptativos do preprint de 2026. Manter opinião escalar, confiança comum, compromisso simétrico, distribuição inicial e regra de amostragem de arestas. Os braços necessários são DW uniforme e DW com reforço/decaimento de pesos; cada trajetória é observada com o critério publicado e continuada para o certificado, sem reiniciar opiniões ou sorteios. Sîrbu fornece contexto e um controle no grafo completo, não precisa ser um terceiro modelo no primeiro piloto. Kan e Li justificam a relevância de uma extensão posterior, mas suas regras não estão cobertas pelo certificado acima.

Usar inicialmente um grafo completo, uma família esparsa com grau médio fixado e uma estrutura modular com poucas pontes. Separar dois eixos: aumentar `N` a grau médio constante e aumentar o grau com `N` constante. Um aumento de `N` com `p` fixo não isola tamanho. Registrar conectividade inicial, não confundir componentes da rede-base com fragmentação produzida pelas opiniões e não ajustar os grafos retrospectivamente para maximizar o efeito.

Observáveis primários: proporção de partições declaradas finais que mudam após continuação; diferença pareada no número/participação dos grupos; tempo até certificado com censura explícita. Secundários: média global conservada, dispersão, distribuição de tamanhos, arestas reativadas, tentativas e atualizações efetivas por nó. Censura por orçamento não conta como fragmentação nem entra silenciosamente como tempo de convergência. Contatos ativos e tentativas são descrições complementares já usadas na literatura, não a alegação nova. Variação por semente, grafo e condição inicial deve permanecer separada; intervalos por reamostragem precisam respeitar essa hierarquia.

O coordenador verificou nesta sessão um Apple M5 com dez CPUs lógicas e 16 GiB de RAM. Não houve benchmark do modelo: CPU e semanas são uma estimativa de viabilidade. Grafos esparsos com `N=100,200,400`, sem armazenar cada estado, cabem confortavelmente em memória; o risco principal é o número de eventos até uma ponte rara ocorrer. Evitar reconstruir matrizes densas e séries completas a cada evento. A eventual implementação científica deve ficar em `src/ic_study/`, com parâmetros e sementes fora do código, conforme as instruções do estudo.

Plano indicativo: dois dias para revisão do argumento e microcasos; três a cinco dias para reprodução limitada e piloto; uma a duas semanas adicionais somente se o piloto justificar expansão. A reprodução precisa fixar versão, ambiente, tolerância efetiva, parâmetros, agenda de checagem, semente e hash dos inputs. Nenhum experimento amplo ou protocolo foi registrado por este memo.

## Piloto e decisão de continuar

O primeiro piloto deve conter o microcaso acima, controles completos e aproximadamente 60–120 trajetórias pareadas, escolhidas em poucas configurações antecipadas perto e longe da região de fragmentação do estudo de 2026. O orçamento por trajetória será definido após medir dez execuções curtas; esse benchmark deve preceder qualquer promessa de completar `10^8` eventos. Reservar novas sementes e grafos para confirmação posterior.

Continuar apenas se: o argumento resistir à revisão; a implementação reproduzir qualitativamente um controle publicado; casos de partição incorreta aparecerem além do exemplo construído; e a continuação alterar um contraste interpretável ou permitir delimitar uma região de confiabilidade com utilidade concreta. Um limiar operacional proposto para discussão é uma diferença de pelo menos cinco pontos percentuais na classificação em uma região pré-definida, ou mudança replicada do sinal do contraste entre os dois modelos. Esses valores são critérios de decisão propostos, não resultados nem um cálculo de poder já feito.

Descartar como tema principal se o problema desaparecer em tolerâncias justificáveis, se o limite superior de incerteza ficar abaixo da relevância previamente escolhida, se a mesma solução já existir, se só houver exemplos artificialmente afinados ou se o custo impedir avaliar as trajetórias censuradas. Nesse caso, preservar a nota e os testes como contribuição de reprodução. Não transformar um piloto negativo em “o artigo está correto em geral”: a conclusão fica limitada ao domínio testado. Se a contribuição permanecer apenas técnica, comparar sua relevância com as outras candidatas da IC antes de investir semanas.

Não proponho uma segunda direção de ordem superior neste memo: a distinção linear/não linear já está estabelecida por Neuhäuser et al., e a busca não produziu uma pergunta adicional mais forte que justifique dividir esforço.

## Acesso, código e licenças

Foram usadas páginas primárias abertas, arXiv, PMC e repositórios públicos. Não houve aquisição agentiva em ACM DL/IEEE Xplore, acesso autenticado, incorporação de texto restrito ou cópia de artigos para o repositório. Projeções temporárias de HTML aberto foram usadas apenas para leitura. Disponibilidade pública e licença de reutilização foram tratadas separadamente.

| Recurso | Verificação em 12/09/2026 |
| --- | --- |
| Sîrbu 2019 | Artigo declara CC BY 4.0 e aponta implementação em NDlib. [NDlib](https://github.com/GiulioRossetti/ndlib) tem [BSD-2-Clause](https://github.com/GiulioRossetti/ndlib/blob/5c659ccf5724bc4863a1aa17ad42ba94ae69baa8/LICENSE), verificada na árvore `5c659ccf5724bc4863a1aa17ad42ba94ae69baa8`. Isso não garante reprodução numérica da versão de 2019. |
| Thompsky et al. 2026 | [Repositório original](https://github.com/Yolandayx929/adaptive-edge-BCM/tree/5e33664982bda6b7576074ff47772791459ea22c), commit `5e33664982bda6b7576074ff47772791459ea22c`: fonte Python, figuras e [licença MIT](https://github.com/Yolandayx929/adaptive-edge-BCM/blob/5e33664982bda6b7576074ff47772791459ea22c/LICENSE) verificados. Inspecionados seleção, atualização e parada; não executado. Código usa NumPy/SciPy/pandas/igraph e bibliotecas gráficas. Para o piloto sintético não é necessário adquirir Facebook100. |
| Li et al. 2025 | [GitLab indicado pelos autores](https://gitlab.com/graceli1/Adaptive-Confidence-BCM): API pública confirmou `AdaptiveConfidenceBCM.py`, README e diretórios DW/HK. Não havia arquivo de licença na raiz consultada; licença explícita de código não confirmada. Não reutilizar trechos sob suposição de licença aberta. |
| Kan et al. 2023 | [GitLab indicado pelos autores](https://gitlab.com/unchitta/coevolving-bc): API pública confirmou `model.py`, `node.py`, `requirements.txt` e testes. Nenhuma licença identificada na árvore consultada. Não executei nem copiei esse código. |
| Neuhäuser 2020 e Pansanella 2022 | HTML/arXiv acessíveis. Código original específico não confirmado. A página arXiv de Pansanella declara CC BY 4.0; Neuhäuser usa a licença não exclusiva de distribuição do arXiv. |
| Hegselmann 2023 | Artigo aberto em JASSS; não confirmei um pacote de código/licença de software nesta leitura. |
| Gezha e Kozitsin 2026 | Artigo em PMC declara CC BY 4.0 e disponibiliza [suplemento ZIP](https://pmc.ncbi.nlm.nih.gov/articles/instance/13025129/bin/entropy-28-00333-s001.zip). O artigo diz que contém código para reprodução; não baixei nem inspecionei o ZIP, portanto não confirmei conteúdo executável ou licença específica do software. |

As páginas arXiv de Kan, Li e Thompsky exibiam a licença não exclusiva de distribuição do arXiv, não uma licença permissiva geral do manuscrito. Foram feitas paráfrases breves com atribuição; a licença MIT do código de Thompsky é uma verificação independente.

A revisão independente identificou uma inconsistência de sinal nas equações 1 e 3 do HTML e no texto extraído do PDF v2 de Thompsky et al.: a segunda atualização aparece como `xj + mu*(xj-xi)`. O código fixado usa `xj + mu*(xi-xj)`, a atualização simétrica convexa. O microcaso e o certificado deste memo adotam explicitamente a regra do código, com as duas opiniões anteriores ao evento; a futura reprodução precisa preservar essa escolha. O achado não demonstra impacto nos experimentos publicados.

## Registro da busca dirigida e limitações

Consultas literais enviadas à busca web em 12/09/2026, nesta ordem aproximada. Resultados comerciais, agregadores e resumos automáticos serviram somente para localizar originais. Algumas consultas muito específicas retornaram material irrelevante; isso não foi interpretado como ausência de literatura.

```text
"algorithmic bias" "bounded confidence" 2023 2024 2025 opinion
"opinion dynamics" "adaptive networks" 2024 2025 bounded confidence
"A Bounded-Confidence Model of Opinion Dynamics with Adaptive Interaction Probabilities"
"Interplay between algorithmic bias and external information" opinion
"algorithmic bias" "opinion" 2024 2025 2026 cutoff convergence
"Multi-body Interactions" "Non-Linear Consensus" code
"opinion" "Interplay between algorithmic bias and external information"
"algorithmic bias model" 2024 2025 2026
"bounded confidence" "convergence" "stopping" algorithmic bias
"Bounded-Confidence Models of Opinion Dynamics with Adaptive Confidence Bounds"
"Pansanella" "external information"
"algorithmic" "opinion dynamics" "2025" "bias" Pansanella
opinion dynamics temporal correlations null model adaptive exposure 2023 2024 2025 2026
"opinion dynamics" "accepted interactions" convergence
"opinion dynamics" "stopping criterion" "sparse" 2026
"Control over Recommendation Algorithms in Heterogeneous Modular Systems with Dynamic Opinions"
"bounded confidence" "stopping criterion" "convex"
"bounded-confidence" "stopping" "certificate"
"Deffuant" "premature" convergence
"bounded-confidence" "false" "convergence"
```

Além da busca, seguiram-se os links de código e identificadores dos originais. Uma tentativa inicial de HTML para `2402.05368v3` falhou; a página de resumo e o HTML sem sufixo depois abriram. O DOI da Physical Review Research sobre atividade heterogênea foi localizado, mas sua aquisição por HTTP retornou 403 e ele não foi contado entre as oito leituras principais. A verificação final por HEAD dos 19 links externos deste memo retornou 200 para 18 e 403 no DOI SIADS; o preprint de Li et al. permaneceu acessível e a ausência de leitura da manifestação editorial está declarada. Não foram contornados bloqueios. O artigo MDPI abriu pela manifestação PMC. A navegação bibliográfica dirigida não executou o procedimento completo de snowballing e não alterou a aquisição v3.

A única verificação numérica nova foi a conta racional de quatro nós. O [cruzamento por identificadores](corpus-crosswalk.json) encontrou correspondência para as oito fontes centrais deste memo nas propostas bibliográficas; isso não resolve identidades, versões ou elegibilidade. A leitura integral, a avaliação de qualidade, a busca de antecedentes do certificado e a aceitação da síntese continuam pendentes. A evidência atual sustenta um **piloto barato com chance de descarte**, não uma alegação de novidade, um resultado sobre plataformas reais ou a seleção final da pergunta.
