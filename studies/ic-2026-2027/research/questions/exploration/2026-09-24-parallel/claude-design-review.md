# Revisão independente: desenho, identificabilidade e inferência das quatro perguntas candidatas

24/09/2026. Revisor: Claude, de família de modelo diferente da dos autores. Eixo: desenho experimental, identificabilidade e inferência estatística. Não li a revisão de novidade feita por outro revisor. Não editei o repositório, não executei simulações novas e não adquiri dados.

## Entradas congeladas

O pacote em `scratchpad/q-review-package/` foi conferido contra `MANIFEST.txt`. Os dez arquivos coincidem com os SHA-256 listados nos commits `12b771048a64c4276cbfb30d45e1ab4695e79d83`, `ef9f50c11cd3082af1d20ef7a201bb78b4519890` e `03585e2d9a905fc3284092d7deaebd273d72d958`. Também li, só para leitura, o worktree `ic-parallel-scientific-preparation` no commit `12b7710`: `src/ic_study/` inteiro (exceto `literature/`), `pyproject.toml`, os README, `budget-decision.json`, `run-manifest.json` e `analysis-input.json` dos pilotos A e B. Os `analysis-input.json` e `run-manifest.json` batem com os hashes do mapa de afirmações (`7422ee1e…`, `376fec97…`, `14161a72…`, `0021bcc6…`). Abri o JSONL do lote principal de A no armazenamento externo depois de conferir o SHA-256 contra o manifesto (`8fd93519…a3bad3`), apenas para medir a vazão.

Numeração, igual à nota editorial: P1 é o Lead 1 (que observação distingue mecanismos), P2 é o Lead 2 (opinião latente ou resposta), P3 é a Candidata 1 (transferência entre temas sob exposição adaptativa) e P4 é a Candidata 2 (trios não lineares contra pares projetados).

## Síntese

A `design-review.md` concluiu que nenhuma das quatro pistas mostrava impossibilidade interna. Concordo que nenhuma é impossível. Mesmo assim, encontrei três defeitos demonstráveis que ela não apontou e que mudam o estimando. Em P1, a direção da hipótese é garantida por um teorema; do jeito que está escrita, a nula só pode ser verdadeira por limitação do estimador, e a "falsificação barata" proposta nunca falha. Em P3, o contraste principal não é específico de transferência entre temas, e o controle de "feedback" temporal perde sentido no limite determinístico, a menos que se defina em que nível ele opera. Em P4, comparar trios não lineares com pares projetados lineares mistura dois fatores, não linearidade e estrutura de grupo; em trios disjuntos, os dois modelos são idênticos por construção. P2 não tem defeito lógico, mas o passo analítico barato que propõe é um resultado clássico da psicometria de painel, e a pergunta só avança se houver pelo menos três ondas do mesmo item.

Nenhuma das quatro esbarra em custo de computação nesta máquina. O que decide o prazo é implementação, revisão e, em P2, acesso a dados. Recomendo investigar P3 com os ajustes da seção dela, reformular P1 e P4, e reformular P2 só depois de uma checagem de metadados que pode descartá-la.

## Base quantitativa comum

Vazão medida. No lote principal de A, as 112 trajetórias somam 2.106.855 tentativas em 24,24 s de tempo por trajetória, o que dá 86.934 tentativas/s no agregado. Por trajetória, o p5 é 25,9 mil/s e o p95 é 303 mil/s. Trata-se de DW escalar, N entre 100 e 200, com as checagens de parada incluídas. Para kernels novos (estado vetorial, fonte, hiperarestas) assumo entre 20 mil e 80 mil eventos/s. Essa faixa é hipótese e não foi medida. O host tem Apple M5, 10 CPUs lógicas e 16 GiB. Os pilotos rodaram em série, e o ganho real com paralelismo nunca foi medido.

Variabilidade local. Da confirmação de B (`all_cell_summaries/confirmation`), calculei o tamanho de efeito por trajetória, d = diferença média pareada contra o baseline dividida pelo desvio-padrão (DP = erro-padrão × √30). Nas células DW com 150 tentativas, d fica entre 0,65 e 0,90. Nas células de DW curto e episódico, em W1, fica entre 0,06 e 0,36. No controle sem atualização, o ES escolheu dinâmica em 40 de 120 trajetórias. Esses números vêm de outro desenho e servem de ordem de grandeza, não de premissa.

Fórmulas e premissas. Uso aproximação normal, α = 0,05 bilateral e poder de 0,8. Para diferença pareada, n = ((z₁₋α/₂ + z₁₋β)/d)². Quando há quatro contrastes primários, uso Holm no pior caso, k = 4. Os resultados que reaparecem adiante: d = 0,2 exige 197 unidades, d = 0,3 exige 88 e d = 0,5 exige 32 (45 com k = 4). Uma equivalência por TOST (Lakens 2017) com margem de 0,5 DP exige 35 unidades (50 com k = 4); com margem de 0,25 DP, 138. No teste de McNemar com 15% e 5% de pares discordantes, são 155. Para duas proporções, 0,30 contra 0,45 exige 163 por braço (231 com k = 4). Os cálculos estão em `scratchpad/power.py`.

Dependências. O pacote `ic-study` declara `dependencies = []`. Qualquer EM, classificador, ODE ou bootstrap pesado terá de ser escrito em Python puro ou justificar uma dependência nova, como numpy.

## Achados que valem para as quatro

A unidade independente é sempre a realização do gerador (rede ou hiperrede, condições iniciais, sinais e sementes). Agentes, encontros e ondas dentro de uma realização são dependentes; tratá-los como réplicas é a pseudorreplicação descrita por Hurlbert (1984). Números aleatórios comuns entre braços (Kleijnen 2015) reduzem variância, mas obrigam a análise pareada, e o pareamento só dura enquanto os braços consomem os fluxos aleatórios da mesma forma. Sementes de custo, de calibração ou ajuste e de avaliação devem ser disjuntas. A regra "benchmark só de custo" que o repositório já aplicou em `budget-decision.json` é boa prática e deve continuar.

Um desfecho em horizonte fixo é preferível a um desfecho "na convergência". A teve quatro censuras em redes modulares de 200 nós, e P3 e P4 criam justamente regimes de convergência lenta (homofilia adaptativa, biestabilidade). Se o desfecho for tomado na convergência, a censura se torna informativa.

O número de execuções deve vir de um piloto interno de variância, em sementes separadas, e não do resultado. Lee et al. (2015, JASSS 18(4):4, seção "Minimum Sample Size") descrevem a estabilização do coeficiente de variação e o cálculo por tamanho de efeito. Secchi e Seri (2017) mostram que a maior parte dos estudos com ABM publicados tem poder insuficiente. Cada pergunta deve ter um contraste primário declarado antes, com Holm sobre os primários; o resto vai como mapa descritivo. Escolher parâmetros, pares de mecanismos ou regiões depois de ver os desfechos é o jardim de caminhos bifurcados de Gelman e Loken (2014). Para JASSS, a descrição ODD (Grimm et al. 2020) e o código vinculado são expectativa editorial.

## P1 — Que observação distingue mecanismos?

### Unidade

No ensaio sintético, a unidade é a trajetória completa gerada por um mecanismo, uma realização de rede, condições iniciais e sementes de eventos e de observação. Os três níveis (histogramas, transições individuais e exposição identificada) são máscaras sobre a mesma trajetória. O contraste entre níveis é, portanto, dentro da mesma unidade e pareado. O desfecho ainda não está definido. Proponho a probabilidade de seleção correta entre os dois mecanismos em trajetórias de teste independentes das de treino, ou a diferença de log-score por trajetória. Em dados humanos, a transição pessoa–item–onda é unidade de medida e não de réplica, e pessoas agrupadas em domicílio ou escola são dependentes.

### Identificabilidade

A direção da hipótese está garantida. Os níveis são aninhados: o histograma é função das trajetórias individuais, que por sua vez são função das trajetórias com exposição. Pelo teorema de comparação de experimentos de Blackwell (1953, _Annals of Mathematical Statistics_ 24(2):265–272), um experimento que é transformação de outro nunca é mais informativo em nenhum problema de decisão. Para o discriminador ótimo, o risco não piora ao passar de L1 para L2 nem de L2 para L3. A nula do memo ("ganho fora da amostra zero ou menor que a variação entre réplicas") só pode ser verdadeira para um discriminador subótimo com orçamento finito. Um ganho nulo ou negativo mediria a limitação do estimador, isto é, a dimensão das estatísticas-resumo e o orçamento de simulação, e não ausência de informação. Esse é um defeito do enunciado, não um risco. A quantidade científica que sobra é a magnitude do ganho por unidade de custo de medição.

A falsificação barata proposta não pode falhar. Qualquer núcleo individual que preserve a distribuição marginal gera a mesma sequência de histogramas que a persistência. Exemplo mínimo: no mecanismo A ninguém muda; no mecanismo B, a cada passo, dois agentes sorteados trocam de opinião. As leis dos histogramas são idênticas em todas as ondas, e as transições individuais diferem desde a primeira. A etapa "procurar par com histogramas iguais e transições diferentes" sempre tem sucesso e não serve para abandonar nada.

O caso informativo é o inverso: dois mecanismos iguais no nível L2 como ele será analisado e distintos só em L3. Um cenário concreto: em grafo completo, compare o DW, em que o par (i, j) se move simultaneamente, com um mecanismo em que cada agente se move em direção a uma opinião sorteada da distribuição corrente, com o mesmo ε e o mesmo μ. No limite de campo médio, a lei de transição de uma pessoa isolada é a mesma nos dois. O que muda é a dependência conjunta entre as transições de quem interagiu. Se L2 for analisado como transições pessoa a pessoa independentes, que é o que o baseline Markov do memo faz, os dois mecanismos ficam indistinguíveis em L2, e todo o ganho aparece em L3. Num painel amostral, respondentes quase nunca interagem entre si. Na prática, então, L2 humano é exatamente essa marginal por pessoa.

L3 sem erro é degenerado. Com opiniões e pares observados sem ruído, a atualização do DW é determinística dado o par. Uma interação observada ou reproduz exatamente x + μ(y − x), ou não reproduz. Um único evento com |x − y| < ε separa o DW de quase qualquer alternativa. O ganho de L3 passa a ser função quase exclusiva do canal de erro escolhido pelo pesquisador. Por isso ele precisa de um canal ancorado (por exemplo, a confiabilidade teste–reteste publicada do item) ou deve ser reportado como curva em função da variância do erro, sem um número único.

### Dependência, vazamento e comparações desiguais

O pareamento entre níveis é correto e deve ser analisado como tal, com McNemar ou diferenças de log-score por trajetória. Há vazamento se estatísticas-resumo ou hiperparâmetros do discriminador forem ajustados nas mesmas trajetórias, ou nos mesmos pontos de parâmetro, usados no teste. Os parâmetros de teste devem ser sorteados de uma região pré-declarada, com sementes disjuntas.

"Mesmo orçamento" é uma comparação desigual disfarçada. Com o mesmo número de simulações de treino, o nível de maior dimensão fica subajustado: são 11 bins em L1, 121 células de transição em L2 e ainda mais em L3. Nessas condições, L1 pode vencer L2 só por variância do estimador. É preciso reportar curvas de aprendizado em três ou quatro orçamentos e o ganho no maior deles.

O par de mecanismos e a região de parâmetros determinam o resultado inteiro. Escolhê-los depois do piloto é seleção após o resultado. A multiplicidade é grande (níveis × redes × N × ondas × custo); convém declarar um contraste primário, L2 contra L1 ajustado por custo numa configuração, e tratar o resto como curva com bandas simultâneas.

### Comparação mínima e controles

Um par de mecanismos declarado antes, com predições diferentes na marginal por pessoa, para que o ganho de L2 não seja trivial nem nulo por construção. Persistência e Markov observado como baselines. Um único conjunto de simulações, com as máscaras L1 a L3 aplicadas a ele. Canal de erro ancorado. O mesmo discriminador em cada nível, com curva de aprendizado. Custo de medição declarado por nível, para converter o ganho em equivalência de amostra, por exemplo quantas pessoas-onda em L1 valem uma pessoa-trajetória em L2. O controle com o par trivial (persistência contra troca) serve só para verificar a implementação.

### Poder e custo

Premissas: o desfecho é binário (seleção correta por trajetória de teste) e o alvo é um ganho de 10 p.p. Com 15% dos pares em que só L2 acerta e 5% em que só L1 acerta, são necessárias 155 trajetórias de teste por mecanismo verdadeiro e por configuração. Para um ganho de 5 p.p. com 15% de discordância, são 469. B indica que o nível de histograma é fraco com séries curtas: 40 de 120 seleções erradas no controle nulo e d entre 0,06 e 0,90, conforme a célula.

Treino: supondo 10⁴ simulações por mecanismo, N = 200 pessoas, 4 ondas e 10 interações por pessoa por onda (8.000 eventos), com 0,1 a 0,4 s por trajetória já contando observação e extração de estatísticas, cada configuração custa de 33 a 133 minutos em série. Com 12 configurações (2 redes × 3 valores de N × 2 números de ondas), o total fica entre 7 e 27 horas em série. As máscaras reaproveitam as mesmas simulações, então os três níveis não triplicam o custo. A implementação (gerador de painel, canal de erro e discriminador sem numpy) deve levar de duas a três semanas; é estimativa, não medição.

### Critérios pré-registráveis

Sucesso: na configuração primária, com canal ancorado, o ganho de L2 sobre L1 ajustado por custo é de pelo menos 10 p.p., com limite inferior do IC95% acima de 5 p.p., e se mantém no maior orçamento da curva de aprendizado.

Abandono:

1. O TOST põe o ganho ajustado por custo dentro de ±5 p.p. em todas as configurações primárias.
2. O ganho de L2 só aparece com o par trivial e some no par com a mesma marginal por pessoa.
3. O ganho de L3 varia só com a variância do erro, sem depender do par de mecanismos.
4. A contrarrevisão encontra o mesmo contraste; Lenti et al. e Tang et al. são os antecedentes mais próximos declarados.

### Controle ou contraexemplo mais barato

Escrever o argumento de Blackwell e o par persistência/troca leva algumas horas e não exige código. Se o Research Owner aceitar que o sinal do ganho é garantido e ainda assim não considerar uma curva de custo e informação uma contribuição suficiente, a pergunta se encerra antes de qualquer implementação.

### Demonstrado e não medido

Demonstrado: a nula é vazia para o discriminador ótimo; a falsificação barata sempre tem sucesso; L3 sem erro é degenerado. Em B, a seleção com histogramas curtos foi frágil, com 40 de 120 erros no controle nulo. Não medido: o custo real do discriminador, a existência de dados com exposição medida (os dados de Tang exigem acesso e ética) e se a curva de custo e informação tem forma não trivial para algum par relevante.

Recomendação: reformular. A pergunta passa a ser a curva de ganho de discriminação por custo para um par de mecanismos declarado antes, com canal ancorado e curva de aprendizado, e deixa de ser um teste de sinal.

## P2 — Opinião latente ou resposta de questionário?

### Unidade

Em dados humanos, a unidade é a pessoa com respostas ao mesmo item em duas ou mais ondas. Pessoas do mesmo domicílio (o SHP é um painel domiciliar) e itens diferentes da mesma pessoa são dependentes. No sintético, a unidade é o painel gerado por núcleo latente, canal de resposta, atrito e sementes. O estado latente é variável do modelo, como o memo já diz.

### Identificabilidade

O contraexemplo analítico proposto é um resultado clássico. Com duas ondas, erro de medida e mudança real não se separam. Heise (1969, _American Sociological Review_ 34(1):93–101) separa confiabilidade e estabilidade com três ondas, supondo confiabilidade constante e dependência de primeira ordem. Wiley e Wiley (1970) trocam essa premissa por variância de erro constante. Para respostas categóricas, modelos de Markov latente com erro de classificação são identificados a partir de três ondas, sob restrições de homogeneidade (van de Pol e de Leeuw 1986, _Sociological Methods & Research_ 15:118–141). O debate entre Converse (1964) e Achen (1975, _APSR_ 69(4):1218–1231) é justamente a pergunta "instabilidade de resposta é mudança ou erro?". Para o desenho, a consequência é que o contraexemplo não pode ser o passo decisivo. O que decide é quantas ondas comparáveis do mesmo item existem e se as restrições do canal são defensáveis.

Cenário concreto de equivalência: persistência latente combinada com um erro de resposta que depende do estado e é maior no meio da escala. Em duas ondas, a matriz observada tem muita massa fora da diagonal nas categorias centrais e diagonal forte nos extremos. O DW com confiança limitada, em campo médio, produz o mesmo padrão qualitativo: moderados mudam e extremos quase não. Os dois são indistinguíveis em duas ondas. Com três ondas, erro independente entre ondas não se acumula: a associação entre as ondas 1 e 3 fica igual à associação entre 1 e 2 (com confiabilidade constante), enquanto mudança real faz a associação decair com a defasagem. Esse é o teste discriminante mais barato, e ele já faz parte do modelo quase-simplex.

Atrito não ignorável não é identificado sem informação externa. Amostras de renovação permitem testar e identificar classes de modelos de atrito (Hirano, Imbens, Ridder e Rubin 2001, _Econometrica_ 69(6):1645–1659). A checagem de metadados deve verificar se CRONOS-2 ou SHP têm renovação. Sem âncora, a entrega coerente é uma região de identificação parcial (Manski 2003), e é preciso declarar antes que largura de região ainda conta como informativa.

O "mecanismo" num painel amostral é um núcleo induzido. Como os respondentes quase nunca interagem, o DW entra apenas como o núcleo individual implicado pela distribuição da população (campo médio). A comparação real é entre famílias de núcleos de Markov latentes. O Markov latente irrestrito contém o núcleo do DW e sempre ajusta pelo menos tão bem dentro da amostra; fora da amostra, o DW só pode vencer por parcimônia. Declarar isso evita apresentar como evidência de mecanismo o que é vantagem de número de parâmetros.

### Dependência, vazamento e comparações

As fontes de dependência são domicílios, pesos amostrais, itens repetidos e mudanças de modo entre ondas. Os intervalos devem vir de bootstrap por domicílio, não por pessoa. Há vazamento se as âncoras do canal forem estimadas com os mesmos pares de ondas usados no ranking; o memo já pede âncoras independentes, e isso deve ser verificado na implementação. A validação temporal proposta (treinar em ondas anteriores, testar nas posteriores) é adequada. Com N grande, qualquer diferença mínima de log-score fica significativa, então a margem de relevância por pessoa tem de ser declarada antes. Na região de sensibilidade, o critério não pode ser "significativo em algum ponto da grade"; deve ser "o sinal do ranking é o mesmo em toda a região", o que também resolve a multiplicidade da grade.

### Comparação mínima e controles

Três modelos com o mesmo canal: persistência latente, núcleo DW de campo médio e Markov latente irrestrito, além do Markov observado já previsto. Pelo menos três ondas do mesmo item, com mesma redação e mesma escala. Restrições do canal declaradas antes. Uma região conjunta de erro dependente do estado e de atrito. Teste temporal. Uma reformulação mais afiada, que o eixo de novidade precisa avaliar: verificar se a evidência de transições individuais no SHP usada por Gestefeld e Lorenz (2023) sobrevive a uma correção por erro de medida com três ondas. Essa versão tem baseline publicado, unidade clara e desfecho decisivo.

### Poder e custo

Aqui o problema dominante é o viés dentro da região de sensibilidade, não a variância amostral. Premissas: DP da diferença de log-score por pessoa de 0,5 nat e efeito de desenho de 1,5 por domicílio. Com margem de 0,05 nat, bastam cerca de 1.180 pessoas; com margem de 0,01 nat, seriam cerca de 29.400, possivelmente mais que um painel nacional oferece por item. Não verifiquei o tamanho efetivo por item e onda.

O EM de um Markov latente com 3 a 5 estados, 3 ondas e 10⁴ pessoas deve levar de segundos a minutos por ajuste em Python puro; é estimativa. Uma grade de sensibilidade 20 × 20 com 200 réplicas de bootstrap somaria 80 mil ajustes, o que pode passar de um dia sem vetorização. Isso justificaria numpy ou uma grade menor. O prazo real depende do acesso aos microdados e da ética, e ambos são desconhecidos.

### Critérios pré-registráveis

Sucesso empírico: há pelo menos três ondas comparáveis do item, e as restrições do canal foram declaradas antes. Em toda a região conjunta declarada, a diferença de log-score fora da amostra entre o DW de campo médio e a persistência latente mantém o mesmo sinal e passa da margem de 0,05 nat por pessoa, com IC95% por bootstrap de domicílio. Um resultado de limite também conta: o sinal se inverte dentro da região, e a fronteira é reportada.

Abandono:

1. O item tem só duas ondas, sem âncora independente e sem renovação. O resultado se reduz a Heise (1969), sem contribuição empírica.
2. A região plausível é tão larga que o ranking fica indeterminado em toda ela, e nenhuma âncora disponível a estreita.
3. A contrarrevisão encontra Markov latente aplicado exatamente a esse ranking.

### Controle ou contraexemplo mais barato

Ler a documentação pública de CRONOS-2 e SHP para contar ondas por item, renovação, pesos e mudanças de modo, sem acesso a microdados. Leva de um a três dias. Se não houver três ondas comparáveis do mesmo item, descartar a linha empírica.

### Demonstrado e não medido

Demonstrado: o passo analítico barato já tem resposta na literatura clássica; num painel amostral, o mecanismo entra só como núcleo de campo médio, contido no Markov latente livre. Não medido: disponibilidade de ondas, itens e renovação; largura da região plausível de erro dependente do estado; tamanho efetivo por item; tempo de acesso e ética.

Recomendação: reformular, condicionada à checagem de metadados. Se a checagem falhar, descartar.

## P3 — Transferência factual entre temas sob exposição adaptativa

### Unidade

Rede inicial, vetores iniciais, sequência de sinais e sementes de contato formam uma realização; agentes da mesma realização são dependentes, como o memo reconhece. O grupo "inicialmente errado" é definido antes do tratamento, o que é correto. Proponho como estimando primário a interação exposição × acoplamento no MSE do tema 2 desse grupo, num horizonte fixo, com a decomposição em viés² e variância.

### Identificabilidade

O contraste principal não é específico de transferência. Com acoplamento zero, o tema 2 evolui apenas por média entre pares. As crenças iniciais do tema 2 são independentes, então o MSE do grupo é (média do grupo − T₂)² mais a variância dentro do grupo. A exposição homofílica pelo tema 1 fragmenta a mistura e mantém tanto a variância quanto a dispersão entre subgrupos no tema 2; a mistura fixa leva mais rápido à média global. Assim, "maior MSE no tema 2 sob adaptação" aparece mesmo sem nenhuma transferência. O memo prevê o controle sem acoplamento, mas a hipótese enunciada compara os braços só com acoplamento positivo. O estimando que isola transferência é a diferença-em-diferenças: (adaptação − controle) com acoplamento positivo, menos a mesma diferença com acoplamento zero. Como a aditividade não é garantida, os quatro braços devem ser reportados.

O controle de feedback depende do nível em que é definido. Se ele for a média temporal da exposição esperada, aplicada como matriz estática, fica homofílico desde t = 0, enquanto a adaptação começa uniforme (pesos iniciais iguais no código local) e só depois vira homofílica. Com sinal precoce, a matriz estática bloqueia a transferência mais cedo, e a diferença medida é de cronograma, não de feedback. O controle mais limpo é de malha aberta: a sequência esperada E[W(t)], estimada em sementes de calibração separadas e aplicada como cronograma que depende do tempo e não do estado.

Mesmo esse controle precisa de um nível declarado. Em blocos (grupo × grupo), o contraste mede o direcionamento da exposição conforme o estado individual mais as flutuações. Por aresta, com a expectativa tomada sobre sementes de eventos da mesma condição inicial, a malha aberta coincide com a adaptação no limite determinístico, porque ali a exposição esperada é a própria exposição realizada. Nesse nível, o contraste mede apenas efeitos de tamanho finito, que tendem a encolher com N. Sem essa escolha, "feedback temporal" é ambíguo, e o resultado pode se reduzir a uma flutuação de ordem 1/√N.

A direção decorre da construção. Com verdades concordantes e acoplamento positivo, levar o tema 1 à verdade puxa o tema 2 para a verdade por definição. Um controle com verdades discordantes (T₂ oposto, acoplamento positivo) é barato. Se o efeito da adaptação apenas espelhar o sinal, o que se mede é redução de mistura entre grupos, e não algo próprio de aprendizado factual.

### Dependência, vazamento e comparações

No código local, a adaptação muda a amostragem das arestas: `WeightedEdges.select(rng.random())` percorre uma árvore de somas, conferido em `models/deffuant.py`. O mesmo número aleatório leva a arestas diferentes quando os pesos diferem, então reutilizar sementes sincroniza condições iniciais e sinais, mas não a sequência de contatos depois da primeira divergência. "Mesmas oportunidades" precisa ser definido: ou o mesmo número de tentativas, ou uma adaptação por aceitação sobre amostragem uniforme, que preserva a sequência de tentativas entre braços. Fluxos separados por papel, como `seed_for` em `models/histogram_forecast.py`, permitem esse pareamento parcial.

A calibração de E[W(t)] deve usar sementes que não entram na avaliação, e o memo já exige isso. Horizonte, ε, dose e força de acoplamento devem ser fixados antes. A multiplicidade vem de 3 exposições × 2 acoplamentos × 2 vieses da fonte × 2 concordâncias × desfechos (MSE, viés, variância). Proponho como primárias as quatro interações (viés da fonte × concordância), com Holm.

### Comparação mínima e controles

Exposição em três níveis (adaptativa; fixa, declarada antes; malha aberta com E[W(t)] no nível declarado) × acoplamento {0, positivo} × fonte {sem viés, viés de confirmação} × verdades {concordantes, discordantes}. Mesmos sinais, mesmos destinatários e horizonte fixo. O memo já prevê verificar que acoplamento zero reproduz o caso escalar e que adaptação zero reproduz pesos fixos.

### Poder e custo

Premissa: o DP do contraste de interação por realização é o dobro da margem de relevância (d = 0,5). São então 32 realizações por braço, ou 45 com Holm k = 4. O TOST de abandono com a mesma margem exige 35, ou 50 com k = 4. Se o DP for quatro vezes a margem, o intervalo sobe para 126 a 177. Um piloto interno de variância em sementes próprias fixa n antes da avaliação.

Custo: N = 200, dois temas e horizonte de 100 tentativas por agente (20.000 tentativas). A 20 mil a 80 mil eventos/s, cada realização leva de 0,25 a 1 s. São 24 braços com 50 a 180 realizações cada, ou 1.200 a 4.320 execuções, o que dá de 5 minutos a 1,2 hora em série, mais 200 a 500 execuções de calibração. Kernel vetorial com fonte, testes de redução e revisão devem levar de uma a duas semanas; é estimativa. O `deffuant.py` atual é escalar, sem fonte e sem verdade.

### Critérios pré-registráveis

Sucesso: na célula primária (fonte sem viés, verdades concordantes), a interação entre (adaptação − malha aberta) e acoplamento no MSE do tema 2 do grupo inicialmente errado passa da margem declarada (por exemplo, 10% do MSE do braço fixo), com IC95% ajustado por Holm acima da margem, e o padrão com verdades discordantes não é o simples espelho.

Abandono:

1. O microcaso mostra identidade entre adaptação e malha aberta no nível declarado.
2. O TOST põe a interação dentro de ±margem.
3. O efeito com acoplamento zero tem a mesma ordem que com acoplamento positivo.
4. Só o contraste com a matriz fixa sobrevive. Isso é efeito total sem feedback, e o próprio memo o considera insuficiente.

### Controle ou contraexemplo mais barato

Um microcaso com dois grupos, dois temas e atualização linear, em que o peso entre grupos depende da distância no tema 1. Primeiro na versão determinística, onde a malha aberta por bloco coincide com a adaptação, o que confirma o argumento acima. Depois numa versão estocástica pequena com heterogeneidade dentro dos grupos, para medir se o direcionamento individual produz alguma diferença. São de dois a cinco dias. Se a diferença estocástica for desprezível em N moderado, a hipótese de feedback cai antes do kernel completo.

### Demonstrado e não medido

Demonstrado: o contraste com acoplamento positivo isolado não é específico de transferência; a matriz estática confunde feedback com cronograma; no limite determinístico, a malha aberta por aresta coincide com a adaptação; o amostrador local não mantém números aleatórios comuns nos contatos. Não medido: a magnitude do efeito de direcionamento em N realista, a vazão do kernel vetorial e a sensibilidade ao horizonte.

Recomendação: investigar, com os quatro ajustes (interação como estimando, malha aberta com nível declarado, verdades discordantes e horizonte fixo), começando pelo microcaso.

## P4 — Trios não lineares versus pares projetados

### Unidade

Hiperrede, crenças iniciais, sinais e sementes formam uma realização; a projeção em pares é derivada da mesma hiperrede, o que permite análise pareada. Encontros e agentes não são réplicas; o memo acerta nisso.

### Identificabilidade

Estrutura de grupo e não linearidade estão confundidas. Tome qualquer regra triádica g(xᵢ; xⱼ, xₖ). Numa hiperrede de trios disjuntos, a vizinhança de i no grafo projetado é exatamente {j, k}, e uma regra de nó h(xᵢ; vizinhos) = g reproduz a dinâmica de forma idêntica. Nesse caso, "coletivo" e "par com agregação não linear da vizinhança" são o mesmo modelo. O controle do memo, a projeção por incidência com pesos constantes, é linear, então o contraste entre trio não linear e projeção mistura não linearidade com estrutura de grupo.

A diferença própria de ordem superior só aparece com sobreposição, quando um nó pertence a vários trios com parceiros diferentes. Aí a não linearidade aplicada por trio e depois somada difere da não linearidade aplicada ao conjunto dos vizinhos. Neuhäuser, Mellor e Lambiotte (2020, _Phys. Rev. E_ 101:032310) mostram que ir além de pares reponderados exige não linearidade; isso não implica que o efeito não linear exija grupos. O desenho correto é um 2 × 2: estrutura {hiperaresta, projeção} × agregação {linear, não linear}, em que a projeção não linear agrega no nível do nó, com a sobreposição como fator. A afirmação "coletiva" é o termo de interação, e esse termo deve se anular com trios disjuntos (é uma checagem de implementação).

A direção é decidida pela forma de f. Um reforço conformista amplifica a maioria local, esteja ela certa ou errada. Com maioria errada, o erro aumenta; com maioria certa, diminui. Esse padrão antissimétrico é predição da própria regra, não achado. A quantidade informativa é o limiar de sinal (dose ou confiabilidade) necessário para reverter a maioria errada, em função do expoente, e saber se esse limiar muda entre hiperaresta e não linearidade de nó. Normalizar a força num único estado de referência é inevitavelmente arbitrário. O resultado deve ser enunciado sobre uma família declarada antes, por exemplo o expoente p entre 0,5 e 3 com p = 1 incluído, informando onde o sinal se inverte. Se a inversão ocorrer exatamente em p = 1 em todas as condições, o resultado é apenas conformidade convexa contra côncava.

Há risco de biestabilidade. O resumo de Dong et al. (2026) relata bifurcação subcrítica e região biestável sob conformidade não linear. Se isso se repetir aqui, o desfecho entre realizações será bimodal (aprisionamento na maioria errada ou não), e média de MSE com intervalo t é inadequada. O desfecho primário deve ser a probabilidade de aprisionamento no horizonte, com o MSE como secundário. Perto do limiar, a convergência fica lenta, o que reforça a necessidade de horizonte fixo e de uma categoria explícita de "não resolvido".

### Dependência, vazamento e comparações

Os braços do 2 × 2 compartilham hiperrede, crenças e sinais, e devem ser analisados de forma pareada. Congelar f, a faixa de p e o estado de normalização antes dos desfechos, como o memo já exige. A força total realizada em cada braço deve ser reportada como diagnóstico, nunca usada como controle. A multiplicidade vem do 2 × 2 × fonte × maioria × sobreposição × família de p; a interação com maioria errada, fonte presente e sobreposição é o contraste primário, com Holm se houver mais de um valor primário de p.

### Comparação mínima e controles

O 2 × 2 acima × fonte {ausente, presente} × maioria {errada, certa} × sobreposição {disjunta, sobreposta}. A equivalência linear em microcaso, prevista pelo memo, continua necessária; ela verifica o código, não a hipótese.

### Poder e custo

Premissa: o desfecho é binário (aprisionamento), e o alvo é distinguir 0,30 de 0,45. São 163 realizações por célula, ou 231 com k = 4; para 0,30 contra 0,40, 356. O pareamento pode reduzir isso, mas a correlação entre braços é desconhecida. São 32 células com 160 a 230 realizações, ou 5.100 a 7.400 execuções. Com N = 200, cerca de 400 trios, 20.000 ativações e três atualizações por ativação, a 0,25 a 1 s por execução, o total fica entre 21 minutos e 2 horas em série. Com uma família de cinco valores de p nos braços não lineares, sobe para 1 a 6 horas. A ODE de campo médio para a hiperrede 3-uniforme completa com sinal cabe num Euler ou RK4 da biblioteca padrão. O kernel de trios e a regra de nó são código novo, cerca de uma semana; é estimativa.

### Critérios pré-registráveis

Sucesso: com maioria errada, fonte presente e hiperrede sobreposta, a interação estrutura × agregação na probabilidade de aprisionamento é de pelo menos 10 p.p. no p primário, com IC95% (Holm) acima de 5 p.p. O sinal se preserva nos demais valores da família, exceto p = 1. A interação fica dentro de ±2 p.p. com trios disjuntos (checagem).

Abandono:

1. O TOST põe a interação dentro de ±5 p.p. no desenho primário; o efeito é de não linearidade, não de grupo.
2. O limiar de sinal para reverter a maioria errada coincide entre hiperaresta e não linearidade de nó.
3. O texto integral de Dong, ou a literatura de modelos q-voter e de contágio complexo, já contém o contraste.

### Controle ou contraexemplo mais barato

A identidade com trios disjuntos está demonstrada acima, sem código. O próximo passo é uma simulação pequena com sobreposição comparando hiperaresta não linear e regra de nó não linear, com a mesma f. Se a diferença for desprezível, encerrar. Leva cerca de uma semana, já contando o kernel.

### Demonstrado e não medido

Demonstrado: a identidade em trios disjuntos; a confusão entre não linearidade e estrutura no controle proposto; a direção fixada pela forma de f, com o padrão antissimétrico previsível. Com indicação forte, mas não medida neste modelo: biestabilidade e desfecho bimodal. Não medido: a magnitude da interação com sobreposição realista; o conteúdo do texto integral de Dong (a nota de 24/09 registra acesso pago e leitura apenas de resumo e código).

Recomendação: reformular, com o 2 × 2, a sobreposição como fator, a probabilidade de aprisionamento como desfecho e a família de f declarada antes.

## Quadro comparativo

| Pergunta | Identificabilidade                                                                                                                  | Custo estimado de computação                                                           | Primeiro resultado decisivo nesta máquina                                                                                                        | Ameaça principal                                                                              | Recomendação                                   |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| P1       | Fraca como enunciada: sinal garantido (Blackwell), L3 sem erro degenerado. Moderada como curva custo–informação com canal ancorado. | O maior dos quatro: 7 a 27 h em série (hipótese), mais discriminador sem dependências. | Horas (argumento de Blackwell e par persistência/troca) para decidir a reformulação; 2 a 3 semanas mais cerca de 1 dia de execução para a curva. | Resultado ditado pela escolha do par e do canal; antecedentes Lenti e Tang.                   | reformular                                     |
| P2       | Nula com duas ondas (Heise 1969); condicional a três ou mais ondas e a restrições do canal.                                         | Baixo (EM pequeno); bootstrap em Python puro pode passar de um dia.                    | 1 a 3 dias lendo metadados; acesso a microdados em prazo desconhecido.                                                                           | Dados (ondas, item, renovação, ética); núcleo de campo médio contido no Markov livre.         | reformular; descartar se os metadados falharem |
| P3       | Boa depois dos ajustes: interação com acoplamento, malha aberta com nível declarado, verdades discordantes.                         | Baixo: 5 min a 1,2 h em série.                                                         | 2 a 5 dias (microcaso determinístico e estocástico).                                                                                             | "Feedback" pode ser só flutuação de tamanho finito ou direcionamento; direção por construção. | investigar                                     |
| P4       | Confundida como enunciada (não linearidade × grupo); boa com 2 × 2 e sobreposição.                                                  | Baixo a médio: 21 min a 6 h em série.                                                  | Horas para a identidade (feita aqui); cerca de 1 semana para o contraste com sobreposição.                                                       | Dong (texto integral), q-voter e contágio complexo; biestabilidade.                           | reformular                                     |

Ordem sugerida, se o Research Owner quiser avançar: o microcaso de P3 e a checagem de metadados de P2 podem correr em paralelo, porque são baratos e cada um pode encerrar sua linha. P4 depende primeiro do acesso ao texto integral de Dong. P1 só vale implementação se a curva de custo e informação for aceita como contribuição.

## O que não pude verificar

- Não li o texto integral de Dong et al. (2026). Dependo da nota de coordenação, que registra acesso pago.
- Não reli Lenti et al., Tang et al., Gestefeld e Lorenz, Abedinzadeh e Akyol, Thompsky et al. nem Sobkowicz; uso as descrições dos memos.
- Não verifiquei se Neuhäuser et al. (2020) já comparam não linearidade de grupo com não linearidade de nó sobre o grafo projetado. Conferi só a referência bibliográfica e o resumo.
- Não consultei a documentação de CRONOS-2 nem do SHP: número de ondas por item, renovação, pesos, modo, tamanho por item e condições de acesso.
- A vazão de kernels vetoriais e de trios é hipótese. Os 86.934 tentativas/s vêm de DW escalar com checagens de parada. Não medi o ganho com paralelismo no M5.
- As estimativas de d tiradas de B vêm de outro desenho e de outro desfecho. Servem de ordem de grandeza, não de premissa de poder.
- Não reproduzi simulações dos pilotos. Recalculei vazão e desvios a partir de objetos com hash conferido, sem regenerar trajetórias.
- Os prazos de implementação são estimativas minhas, sem medição.
- Uma revisão de novidade separada pode tornar redundante alguma das reformulações sugeridas aqui, em especial a releitura do SHP em P2 e a interação de grupo em P4.

## Referências metodológicas citadas

- Achen, C. H. (1975). Mass political attitudes and the survey response. _American Political Science Review_, 69(4), 1218–1231.
- Blackwell, D. (1953). Equivalent comparisons of experiments. _Annals of Mathematical Statistics_, 24(2), 265–272. doi:10.1214/aoms/1177729032.
- Converse, P. E. (1964). The nature of belief systems in mass publics. In D. Apter (Ed.), _Ideology and Discontent_. Free Press.
- Gelman, A., & Loken, E. (2014). The statistical crisis in science. _American Scientist_, 102(6), 460–465.
- Grimm, V. et al. (2020). The ODD protocol for describing agent-based and other simulation models: a second update. _JASSS_, 23(2), 7.
- Heise, D. R. (1969). Separating reliability and stability in test-retest correlation. _American Sociological Review_, 34(1), 93–101.
- Hirano, K., Imbens, G. W., Ridder, G., & Rubin, D. B. (2001). Combining panel data sets with attrition and refreshment samples. _Econometrica_, 69(6), 1645–1659.
- Hurlbert, S. H. (1984). Pseudoreplication and the design of ecological field experiments. _Ecological Monographs_, 54(2), 187–211.
- Kleijnen, J. P. C. (2015). _Design and Analysis of Simulation Experiments_ (2nd ed.). Springer.
- Lakens, D. (2017). Equivalence tests: a practical primer for t tests, correlations, and meta-analyses. _Social Psychological and Personality Science_, 8(4), 355–362.
- Lee, J.-S. et al. (2015). The complexities of agent-based modeling output analysis. _JASSS_, 18(4), 4.
- Manski, C. F. (2003). _Partial Identification of Probability Distributions_. Springer.
- Neuhäuser, L., Mellor, A., & Lambiotte, R. (2020). Multibody interactions and nonlinear consensus dynamics on networked systems. _Physical Review E_, 101, 032310.
- Secchi, D., & Seri, R. (2017). Controlling for false negatives in agent-based models: a review of power analysis in organizational research. _Computational and Mathematical Organization Theory_, 23(1), 94–121.
- van de Pol, F., & de Leeuw, J. (1986). A latent Markov model to correct for measurement error. _Sociological Methods & Research_, 15(1–2), 118–141.
- Wiley, D. E., & Wiley, J. A. (1970). The estimation of measurement error in panel data. _American Sociological Review_, 35(1), 112–117.
