# Pistas de mecanismos e generalização — 24/09/2026

Leitura dirigida: duas candidatas refutáveis para **exame**, sem síntese aceita,
prioridade bibliográfica, novidade ou tema selecionado. A pergunta canônica
continua vazia em [`research-questions.md`](../../research-questions.md).
“Verdade” é o estado conhecido **no gerador sintético**, sem atribuir verdade
objetiva a posições políticas observadas.

O [piloto de fragmentação](../../exploratory-claim-map.md) achou uma diferença
estreita; sua expansão terminou. O de previsão não passou seu critério central.
Nenhuma proposta prolonga suas amostras ou toma parada e clusters como desfecho.
O [`mechanism-evidence.md`](../2026-09-12/mechanism-evidence.md) já exclui como
novidade simples acréscimos de topologias, pesos adaptativos ou trios.

## Antecedentes capazes de retirar a contribuição

“Texto” indica que li formulação/resultados pertinentes no HTML aberto, não
auditoria integral de provas ou reprodução. “Resumo” indica leitura limitada
à manifestação bibliográfica e sua descrição. Os seis itens são uma busca
dirigida, **não** uma lista de inclusão da revisão formal.

| Trabalho primário, leitura | Resultado já coberto e consequência |
| --- | --- |
| [Baumann et al., *Physical Review X* 2021](https://journals.aps.org/prx/abstract/10.1103/PhysRevX.11.011012), **resumo editorial** | Homofilia e base não ortogonal de temas já geram alinhamento ideológico entre questões inicialmente distintas. “Exposição seletiva cria correlação entre temas” isoladamente não é lacuna. |
| [Abedinzadeh e Akyol, arXiv:2603.21081v1](https://arxiv.org/html/2603.21081), **texto**: modelo, contribuições, simulação/conclusão | Estado vetorial, transferência entre temas, pares em rede fixa e influência assimétrica de fontes com viés de confirmação; já há condições de contração, cálculo/limites do ponto fixo e comparação de desenho de fontes. Uma nova fonte externa ou o efeito qualitativo do acoplamento não bastam. Os pares permanecem estáticos nesse modelo. |
| [Thompsky et al., arXiv:2605.20418v2](https://arxiv.org/html/2605.20418v2), **texto**: regra e resultados; [código público fixado](https://github.com/Yolandayx929/adaptive-edge-BCM/tree/5e33664982bda6b7576074ff47772791459ea22c), **reexecutado depois no [memo de reprodução](mechanism-reproduction-and-controls.md)** | Probabilidades de interação se adaptam por peso de aresta em DW escalar; já há contraste entre redes e tempos. O [piloto local](../../exploratory-claim-map.md) limita a linha da parada. Para outra pergunta, é antecedente e baseline de exposição, não prova de efeito multidimensional ou de aprendizado factual. |
| [Neuhäuser, Mellor e Lambiotte, arXiv:1910.09226v1](https://arxiv.org/html/1910.09226v1), **texto**: seções II–IV e conclusão | Interação de grupo linear reduz-se a pares reponderados; efeito genuinamente coletivo requer não linearidade. Também mostram deslocamento da média por reforço em trios. “Trios diferem de pares” sem controle da projeção e da não linearidade está ocupado. |
| [Dong, Liang e Zhang, *Chaos* 36(9):093111, 01/09/2026, DOI 10.1063/5.0337453](https://pubmed.ncbi.nlm.nih.gov/42684114/), **resumo bibliográfico**; [depósito dos autores](https://zenodo.org/records/21820152), **código inspecionado e executado depois no [memo de reprodução](mechanism-reproduction-and-controls.md)** | Modelo multidimensional com arestas e hiperarestas, expoente de conformidade de grupo, limiar/bifurcação e acoplamento entre temas; analisa 27 subreddits. Já derrota “hiperarestas amplificam alinhamento entre temas” como contribuição genérica. O registro Zenodo informa `cc-by-4.0`; a intervenção com nós congelados em 0 mede polarização relativa a 0, não erro para verdade externa. |
| [Sobkowicz, *JASSS* 21(4):8, 2018](https://www.jasss.org/21/4/8.html), **texto**: modelo, fontes/viés e resultados selecionados | Agentes com distribuições de crença recebem fonte aproximadamente verdadeira sob filtros cognitivos; o estudo já contrapõe aprendizado e persistência do erro. “Viés impede aprender a verdade” ou apenas acrescentar uma fonte confiável não é novo. |

Outros riscos próximos, aqui lidos no nível indicado: [Bartel, Burger e
Wolfram, arXiv:2601.04074v4](https://arxiv.org/html/2601.04074), **texto**,
já usam pesos individuais de importância e semelhança em todos os temas para
modular encontros binários; declaram ausência de fonte exógena no modelo.
[Xu e Zhang, arXiv:2310.05689](https://arxiv.org/abs/2310.05689), **resumo**,
estendem FJ a hiperarestas lineares e as decodificam como pares efetivos.
[Peralta et al., arXiv:2105.07703](https://arxiv.org/abs/2105.07703),
**resumo**, já cruzam viés algorítmico, modularidade e contatos por pares ou
grupos em estados binários. Essas leituras não estabelecem ausência de um
antecedente ainda mais próximo; exigem contrarrevisão de novidade.

## Candidata 1 — transferência factual entre temas sob exposição de pares adaptativa

**Pergunta exata.** Em dois temas com acoplamento positivo, uma fonte confiável
que informa apenas o tema 1 melhora o erro no tema 2 da mesma forma quando a
exposição a pares é adaptada à posição no tema 1 e quando a exposição é fixa,
sob o mesmo número de oportunidades de contato e a mesma dose de sinal?

**Hipótese refutável.** Num gerador previamente fixado com grupos inicialmente
discordantes no tema 1, crenças independentes no tema 2 e verdades concordantes,
o grupo inicialmente errado no tema 1 retém **maior erro quadrático no tema 2**
sob exposição homofílica adaptativa que sob mistura fixa, após a mesma dose de
sinal confiável no tema 1. O controle sem acoplamento deve eliminar a diferença
atribuível à transferência entre temas. A alternativa é equivalência dentro de
uma margem de relevância predefinida ou efeito explicável apenas por número de
contatos/sinais recebidos. A direção é uma conjectura, não resultado.

**Resultado mais próximo / resto incerto.** [Abedinzadeh e Akyol](https://arxiv.org/html/2603.21081)
já combinam fonte com viés e tópicos correlacionados, mas fixam o canal dos
pares; [Thompsky et al.](https://arxiv.org/html/2605.20418v2) adaptam o canal
dos pares em uma variável escalar. A questão residual é a interação **causal
controlada** entre adaptação do canal e transferência de informação entre
temas, com erro para uma verdade sintética. Pode ser mero resultado previsível
da combinação dos dois modelos, ou estar resolvida em outro trabalho.

**Comparação mínima.** Um único modelo vetorial de atualização convexa com a
mesma fonte para todos os braços. O **efeito total** compara adaptação por
semelhança no tema 1 com pesos fixos escolhidos *antes* das trajetórias. O
contraste **principal para contribuição de feedback temporal** compara a mesma
adaptação com uma matriz estática definida pela exposição *esperada* numa
calibração separada, sem usar resultados ou matrizes realizadas das réplicas
avaliadas. Cruzar com acoplamento (0, positivo) e fonte sem/com viés de
confirmação. Reutilizar rede inicial, vetores, oportunidades de contato, ruído
da fonte, dose de sinal e sementes por réplica. Fixar oportunidades, não
condicionar o efeito total à quantidade de contatos realizados: esta é parte
possível do efeito e deve ser relatada. Unidade independente: realização de
rede + condições iniciais + sinais; agentes da mesma réplica são dependentes.

**Invariantes e observáveis.** Fixar duas dimensões, distribuição inicial,
verdades, precisão e dose da fonte, força de atualização, orçamento e horizonte;
registrar matriz de exposição realizada, quantidade de sinais, MSE por tema e
grupo, além da transferência contrafactual entre tema 1 e 2. Não chamar
correlação de temas de aprendizado: exigir redução de erro no tema não
informado. O modelo deve reproduzir a redução escalar de exposição quando o
acoplamento é zero e o caso de pares fixos quando a adaptação é zero.

**Baseline/custo.** As equações e exemplos de
[Abedinzadeh e Akyol](https://arxiv.org/html/2603.21081) são base conceitual;
não identifiquei código de autores ali nesta consulta. Há o
[repositório de Thompsky et al.](https://github.com/Yolandayx929/adaptive-edge-BCM/tree/5e33664982bda6b7576074ff47772791459ea22c),
com regra escalar e licença MIT verificada no memo de 12/09; ele exigiria uma
extensão, nunca cópia assumida correta. **Hipótese de computação não medida:**
duas dimensões e grafos esparsos pequenos caberiam numa comparação local; custo
em eventos e número de réplicas são desconhecidos até medição específica.

**Abandono barato.** Primeiro, derivar dois casos pequenos com acoplamento zero
e positivo e verificar se o contraste não é algebraicamente idêntico a mudar
uma matriz fixa. Depois, apenas se houver diferença interpretável, propor
piloto com matriz esperada obtida em calibração independente, margem de
relevância e orçamento fixados antes da avaliação. Se o efeito total persistir,
mas o contraste principal com essa matriz esperada desaparecer, a hipótese de
feedback temporal cai; o efeito total permanece relato separado, sem sustentar
por si a contribuição proposta. Descartar também se a contrarrevisão localizar
a mesma comparação. A matriz **realizada após intervenção** é diagnóstico de
mediação, nunca controle para descartar o efeito total. Nada foi executado aqui.

## Candidata 2 — influência coletiva versus aprendizado por evidência externa

**Pergunta exata.** Com sinal externo de confiabilidade conhecida e maioria de
agentes inicialmente errada, reforço **não linear** em encontros de três pessoas
altera o erro de crença em relação a pares reponderados com a mesma incidência,
exposição à fonte e força local de influência?

**Hipótese refutável.** No domínio predefinido em que a maioria inicial erra e
uma minoria recebe sinais corretivos, o mecanismo coletivo não linear mantém
erro médio maior que seu par projetado, mesmo quando ambos têm exposição e
intensidade local comparáveis; pode simultaneamente reduzir dispersão. A
hipótese rival é que a diferença desaparece após projetar os trios em arestas
ponderadas ou igualar intensidade, de modo que a hiperaresta não acrescenta
explicação para o erro. Esse enunciado é sobre acurácia do gerador, não sobre
clusters ou velocidade de convergência.

**Resultado mais próximo / resto incerto.** A redução do caso linear e o
deslocamento da média sob reforço já são de
[Neuhäuser et al.](https://arxiv.org/html/1910.09226v1).
[Dong et al.](https://pubmed.ncbi.nlm.nih.gov/42684114/) já combinam grupos
não lineares, múltiplos temas e dados observacionais; seu texto integral não foi
lido nesta sessão. [Sobkowicz](https://www.jasss.org/21/4/8.html) já estuda
fonte aproximadamente verdadeira sob viés. Resta incerto se um contraste
**quantificado de acurácia**, com projeção linear e sinais externos controlados,
é novo, útil ou apenas consequência direta dessas regras.

**Comparação mínima.** Em topologia de trios fixa, cruzar regra coletiva linear
e não linear com fonte ausente/presente; para cada uma construir projeção em
pares por incidência. **Antes de observar desfechos**, especificar e congelar
a função de reforço não linear, seus parâmetros, e um estado de referência
com dispersão não nula e simétrico sob inversão de verdade/erro para normalizar
a força local entre regras. A igualdade local valerá nesse estado declarado,
não automaticamente em todos os estados; registrar como a força diverge fora
dele. Fixar mesmo sinal, destinatários e calendário nos braços; separar média,
dispersão e MSE relativo à verdade. A regra linear de hiperarestas deve
coincidir com sua projeção pareada em microcaso no domínio da teoria. Aplicar
o mesmo desenho à maioria inicialmente errada e correta. Unidade independente:
hiperrede + crenças iniciais + sinais, não cada encontro.

**Baseline/custo.** Fórmulas em
[Neuhäuser et al.](https://arxiv.org/html/1910.09226v1) e
[Xu e Zhang](https://arxiv.org/abs/2310.05689) delimitam o par projetado;
[Sobkowicz disponibiliza fonte e dados no OSF](https://osf.io/7xasr/),
segundo o próprio artigo, sem inspeção do depósito nesta sessão.
O [Zenodo dos autores de Dong](https://zenodo.org/records/21820152) anuncia
`Code_Public.zip` para simulações e validação, sem dados Reddit no depósito.
Na leitura inicial, consultei somente a página. O
[memo posterior](mechanism-reproduction-and-controls.md) documenta o conteúdo,
a execução reduzida e a licença `cc-by-4.0` do registro.
**Hipótese de computação não medida:** pequenos trios sintéticos podem ser
enumerados sem nova dependência; tempo para regiões de parâmetro e incerteza
entre hiperredes não foi estimado.

**Abandono barato.** Antes de qualquer campanha, procurar no texto integral de
Dong e em trabalhos que o citam o mesmo contraste com fonte verdadeira;
depois provar/checar a equivalência do controle linear em microcaso. Se o
contraste de erro não sobreviver à projeção, à dose e à normalização declarada,
ou for uma reformulação de resultado existente, abandonar. Congelar antes do
piloto uma região de condições iniciais e sinal, uma margem de MSE relevante
e o critério de continuação em ambas as maiorias; só sobreviver em exemplos
escolhidos depois de ver resultados não justifica tema. Nenhuma função ou valor
de parâmetro foi escolhido nesta nota.

## Decisões científicas pendentes

Escolher se a IC quer explicar transferência entre temas, erro diante de
evidência, ou outro fenômeno mostrado pela síntese; decidir a semântica e
plausibilidade de “verdade” e do sinal; revisar trabalhos próximos de 2024–26
em texto integral, sobretudo Dong; definir margem de relevância, unidade,
incerteza, custo e caminho de validação. A escolha de um modelo por conveniência
de código não substitui essas decisões. Esta leitura não alterou corpus,
triagem, extração, revisão aceita, execução ou memória.
