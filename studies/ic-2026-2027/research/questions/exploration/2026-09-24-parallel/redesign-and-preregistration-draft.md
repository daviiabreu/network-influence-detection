# Redesenho e rascunho de pré-registro

> Sucedido, antes do congelamento, pela [emenda da decisão 14: fronteira de detecção](detection-boundary-preregistration-draft.md). Este texto e seus pilotos ficam como histórico; seus gates não definem a nova análise. O [resultado de estimabilidade e a auditoria da decisão 14](../../../../experiments/exploratory/detection-boundary-v1/README.md) estão registrados separadamente para preservar a especificação anterior ao piloto.

24/09/2026. Direção recebida nesta sessão: P1+P2 sintética ancorada em
metadados e confiabilidade externa, sem ancoragem individual no braço principal;
P4 com dose crítica como alternativa. A rodada inicial autorizou desenho,
implementação, testes e pilotos exploratórios com teto conjunto de 20 minutos.
A emenda da decisão 13 autoriza até dez minutos adicionais para a correção
externa de confiabilidade. Nenhuma rodada autoriza experimento confirmatório. Este documento é rascunho para revisão,
não protocolo registrado nem alegação de novidade. A pergunta canônica e o
mapa amplo não foram alterados.

O [memo](decision-memo.md) é sucedido aqui nos dois desenhos. A
[crítica reproduzida](claude-memo-critique.md) demonstrou separação trivial das
marginais de P1 e travamento universal de P4. Foram lidos também os pareceres
de [novidade](claude-novelty-review.md) e [desenho](claude-design-review.md), os
[dados e metadados](empirical-data-access-and-reproduction.md), os
[controles de mecanismo](mechanism-reproduction-and-controls.md), as saídas
`review-memo-evidence/` e os scripts da crítica. Os resultados anteriores
continuam preservados e não contam como observações deste redesenho.

## Emenda da decisão 13, anterior ao congelamento

A [decisão 13 e sua proveniência](decision-13-amendment.md) atualizam a versão
`418be2d`, com base no [dossiê de confiabilidade e antecedentes](reliability-and-prior-art.md),
copiado sem alteração e com hash conferido. O coordenador manteve P1+P2 após
avaliar a condição de parada de 48 h, sob delegação e com ratificação posterior
conforme o log. Isso autoriza continuar o desenho, não alegar novidade ou
aprovação de um pré-registro final.

A confiabilidade primária muda de 0,65 para 0,70 por determinação externa.
0,65 era uma escolha provisória anterior ao piloto, não uma estimativa obtida
nele. A correção ocorre antes do congelamento e não depende do contraste
primário, cujo valor não foi aberto. O piloto a 0,65 fica preservado como
histórico e não é apresentado como checagem executada a 0,70.

## Primária: reorganização dinâmica versus persistência, com marginais iguais

A pergunta é se respostas ordinais anuais de um mesmo item em onze ondas
permitem distinguir padrões de reorganização semelhantes aos de influência
(*influence-like*) de persistência latente com erro de resposta, depois de
retirar a informação fácil das marginais e do lag 1. O alvo é desempenho de
um estimador declarado em uma família sintética; os rótulos indicam os geradores.

O estudo NÃO detecta influência social. Não há dados de exposição/comunicação
no painel usado como referência. Um processo individual que reproduza o mesmo
núcleo observável pode gerar os mesmos padrões. A limitação é coerente com
[Manski (1993)](https://doi.org/10.2307/2298123) e
[Shalizi e Thomas (2011)](https://doi.org/10.1177/0049124111404820), conforme a
leitura de resumos declarada no dossiê: grupos de referência e a confusão entre
homofilia, contágio e covariáveis não são resolvidos pela geometria longitudinal.
Acerto não identifica influência causal; desempenho ao acaso não prova
impossibilidade para todo estimador.

### População, dinâmica e matching

São 10.626 pessoas em domicílios de duas pessoas. Há 7.084 entradas em 1999 e
3.542 em 2004. Cada domicílio ativo permanece com probabilidade 0,89 por ano,
independentemente dos estados; não há retorno após perda. A renovação entra
antes da observação de 2004. Os não observados continuam no processo latente.
São onze ondas anuais, t=0,...,10, e onze categorias 0,...,10 do mesmo item.

A referência é o item SHP `P$$P04` em 1999–2009, com 10.627 pessoas e
50.008 transições relatadas pelo antecedente, conforme a
[auditoria documental](empirical-data-access-and-reproduction.md). Os tamanhos
e perdas aqui são aproximações explícitas: não são contagens anuais válidas
extraídas do SHP. O desenho inclui renovação e perda por domicílio, mas não
pesos, ausências intermitentes, modos ou seleção dependente de opinião.
CRONOS-2 oferece pares de confiança nas ondas 1/4; seus três itens não
constituem três ondas de um único item e não ancoram este painel de onze anos.

Em cada realização, cada pessoa escolhe oito parceiros distintos, sem
escolher a si mesma, uniformemente entre os demais. Essa rede dirigida é
fixa durante as onze ondas e independente da opinião inicial. A população é
fechada para a dinâmica, embora a máscara de observação tenha renovação.
Não se apresenta essa rede como rede social reconstruída do SHP.

Seja R_N(v) a transformação que atribui, segundo os postos de v, os quantis
normais `(j+0,5)/N`, padronizados para variância populacional um. Inicialmente
z=R_N(ruído normal independente). Uma atualização social síncrona anual é

```text
g_ij = z_j - z_i
K(g) = g se |g| <= 1; -b*g caso contrário
u_i = 0,85*z_i + a*mean_j K(g_ij) + sqrt(1-0,85²)*eta_i
z(t+1) = R_N(u)
```

No primário b=0 e não existe termo em z_i(0): `0,85*z_i` usa z_i(t), a
opinião corrente, não a inicial. A inspeção de `latent_panel` confirmou isso;
R_N preserva os postos correntes, sem restaurar os postos de t=0. O braço
principal já satisfazia a decisão 13, portanto seu kernel não foi alterado.
O controle de persistência usa
`u_i=rho*z_i+sqrt(1-rho²)*eta_i`, seguido da mesma R_N. É persistência
estocástica AR, não opinião constante. Persistência estrita rho=1 será controle
secundário positivo de facilidade. A alternativa com b=0,05 testa repulsão
somente como robustez, sem substituir o mecanismo principal.

Braço secundário ancorado, a implementar antes de qualquer execução desse
braço: seja u_i(t) a proposta social acima. Usar
`z(t+1)=R_N((1-omega)*u(t)+omega*z(0))`, com
omega em {0;0,25;0,50;0,75;1}. omega=0 coincide exatamente com o primário;
omega=1 preserva exatamente a opinião inicial. Os intermediários mostram o
contínuo entre reorganização e ancoragem, mantendo a mesma marginal. Trata-se
de uma variante estilizada com atração convexa à âncora, não reprodução do
mecanismo de resets discretos de Gestefeld–Lorenz.

O [dossiê](reliability-and-prior-art.md) calcula, a partir de theta=0,1 e 24
passos anuais do melhor ajuste de Gestefeld–Lorenz, `1-0,9^24≈0,92`: probabilidade
de ao menos UM retorno à opinião inicial no ano. Não significa que 92% estejam
exatamente na âncora na observação anual, nem que omega=0,92 reproduza o artigo.
Esse retorno frequente aproxima o mecanismo de persistência com desvios
transitórios; por isso ele não define o braço principal.

Para cada omega secundário, comparar com AR de rho ajustado somente ao seu
lag 1 latente em 16+16 novas realizações de calibração, antes dos respectivos
confirmatórios; r permanece externo. Treino, avaliação e grade de r seguem
os tamanhos abaixo por omega, pareando rede/estado/erro entre variantes. Não
usar o desempenho secundário para substituir o primário ou escolher omega.
A variante requer testes de redução omega=0/1 e uma auditoria própria de
sementes antes da implementação/execução; não foi simulada nesta emenda.

A transformação de postos faz parte de ambos os geradores. Impõe a mesma
marginal latente em todas as ondas e remove a informação marginal por
construção. Não é DW puro, nem ajuste empírico de Gestefeld–Lorenz: o estimando
fica condicionado a esses núcleos normalizados. O matching de lag 1 usa só
16 realizações sociais de calibração: rho recebe a correlação média latente
adjacente; outras 16 verificam o controle. Exige-se diferença absoluta <=0,01.
Não há otimização de rho em painéis de treino ou avaliação. Aqui rho é
persistência DINÂMICA do controle; r, definido a seguir, é confiabilidade do
canal de medida. Ajustar rho para matching latente não estima nem ajusta r. Marginais
observadas são iguais em lei, com diferenças finitas monitoradas por variação
total; o lag 1 ordinal é diagnóstico adicional, não feature do discriminante.

### Canal, estimando e inferência

Para r, observar `w=sqrt(r)*z+sqrt(1-r)*e`, com e normal padrão independente
por pessoa e onda. Aplicar dez limiares normais fixos, quantis j/11, resulta
em onze categorias; ausências são -1 e nunca entram como categoria.
Equivalentemente, erro pré-padronização tem variância `(1-r)/r`.
A confiabilidade r é a fração de variância latente no canal contínuo antes da
discretização; não é correlação anual e não se presume igual à confiabilidade
ordinal. Sua tradução para uma estimativa teste–reteste/quase-simplex humana
precisa de justificativa específica.

A decisão 13 fixa EXTERNAMENTE a faixa principal r=0,65–0,80, com centro e
célula primária r=0,70. A grade principal é {0,65;0,70;0,75;0,80}; a grade
complementar de sensibilidade é {0,50;0,55;0,60;0,85;0,90}. Juntas, cobrem
0,50–0,90 em passos de 0,05. Não ajustar r às transições, à correlação anual,
aos lags do painel ou ao desempenho do discriminante; não selecionar um r
favorável depois dos resultados. O baseline de calibração permanece r=0,80.
Ambos os mecanismos recebem o mesmo canal em cada ponto.

As fontes e os limites de transporte constam do [dossiê](reliability-and-prior-art.md):
[Alwin e Tufiș (2023)](https://alwin-reliability.com/assets/img/Question%20Content%20and%20Reliability%20of%20Measurement.pdf)
reportam confiabilidade quase-simplex de atitudes GSS de 0,66–0,68;
[Hout e Hastings (2016)](https://doi.org/10.15195/v3.a43) reportam, entre outros
resultados, 0,68 para confiança no executivo em um painel, com instabilidade
em outros períodos. [Poses et al. (2021), ESS MTMM](https://doi.org/10.18148/srm/2021.v15i3.7816)
reportam qualidade q² de 0,72–0,78 para parlamento em experimentos distintos;
[Turper e Aarts (2017)](https://doi.org/10.1007/s11205-015-1182-4) citam
confiabilidades MTMM de 0,82–0,85 para itens de confiança.

A faixa é uma decisão externa informada por essas fontes, não uma estimativa
publicada direta para `P$$P04`, nem um intervalo de confiança comum aos estudos.
Qualidade MTMM q² inclui validade e não é intercambiável com confiabilidade r²;
MTMM e quase-simplex também tratam estados transitórios de formas diferentes.
Os valores MTMM servem como referência superior de planejamento, não limite
matemático para a confiabilidade anual. O centro 0,70 e a grade não serão
refitados, mesmo se os diagnósticos SHP não concordarem. Essa discordância
limitaria a interpretação e exigiria emenda externa anterior ao registro.
O canal contínuo padronizado é uma hipótese de transporte adicional; os desvios
em pontos da escala SHP calculados no dossiê não são injetados diretamente no
z padronizado deste simulador.

As quatro features são correlações ordinais de Pearson nos lags 2, 3, 4 e 5,
calculadas sobre todos os pares observados elegíveis, com centragem empírica.
Pares não são réplicas independentes. O discriminante linear padroniza usando
somente treino, estima médias por classe e covariância residual comum, e usa
`0,8*cov+0,2*I`; priors são iguais, corte zero, empate vale meio acerto.
A fórmula e a dimensão estão fixadas antes do piloto. Não há busca de features,
penalização, redes ou hiperparâmetros pelo resultado principal.

Estimando primário: BA, a média da probabilidade de acerto de cada mecanismo
em um painel novo a r=0,70, condicional ao treino congelado e ao ponto de
operação selecionado pela regra abaixo. O contraste é BA−0,5. Hipótese de
utilidade: BA>0,55; relevância planejada: estimativa >=0,65 e limite inferior
de IC95% acima de 0,55. BA próxima de 0,5 é um nulo informativo para este
estimador. IC90% inteiro em [0,45;0,55] caracteriza equivalência ao acaso;
intervalo que não satisfaz nenhuma regra é inconclusivo. Um resultado abaixo
de 0,45 indica inversão ou falha de generalização, não autorização para trocar
os rótulos depois do teste.

### Ponto de operação anterior ao primário

O [protocolo exploratório](../../../../experiments/exploratory/redesign-calibration-v1/protocol.md)
foi escrito e commitado antes de executar simulações. A regra examina a grade
ordenada a={0,025;0,05;0,1;0,2;0,4;0,8}. Em cada a, ajusta rho por lag 1 e
usa 48 painéis/classe para treinar e 48/classe distintos para medir BA somente
no baseline r=0,8. Seleciona o primeiro a com BA em [0,68;0,82] e matching de
lag 1 <=0,01. Se não existir, encerra v1 sem avaliar o primário.

Esta regra consulta a discriminação do baseline; portanto não é uma calibração
sem rótulos. Foi cega à BA da célula então provisória r=0,65 e continua cega
à BA da nova primária r=0,70, às diferenças entre canais
e a todos os confirmatórios. A inferência futura será condicional à seleção;
não será apresentada como desempenho de um par de mecanismos escolhido sem
calibração. No piloto original, depois da seleção, houve 96 painéis/classe de
treino e 96/classe de checagem a r=0,65. O único resultado de discriminação exportado é o gate
`0,55 < BA < 0,95`. Não se exportam BA, escores, contagens de acertos ou efeitos.
Um gate negativo não permite escolher o próximo a.

A correção externa para r=0,70 não altera a regra de seleção, que consulta só
r=0,80. Preservar a=0,4 e rho=0,838961863215152; não repetir a busca nem alterar
o matching para obter um novo acerto. A [checagem sucessora](../../../../experiments/exploratory/reliability-correction-v1/protocol.md)
usa 96 painéis/classe de treino e 96/classe de checagem novos, exclusivamente
de desenvolvimento, com o mesmo gate grosseiro e teto de 600 segundos.
Não compara numericamente 0,70 com 0,65, não abre BA e não roda P4.

### Tamanho e análise confirmatória propostos, não executados

Treino: 2.000 painéis por classe, cada um com nova rede. Validação: 400 por
classe, para auditoria de implementação e curva de aprendizado, sem mudar o
estimador pelo teste. Teste: 500 redes independentes, duas sementes de estado,
inovação e observação por rede e por mecanismo (1.000 painéis/classe).
Parear redes e máscaras entre mecanismos e confiabilidades; manter as duas
réplicas de uma rede no mesmo conjunto. O controle AR não usa a rede, mas
permanece no bloco pareado. Nenhuma rede de treino reaparece no teste.

Rede é efeito aleatório de nível superior; sementes de trajetória são efeitos
aleatórios aninhados. Estimar BA pela média dos escores de acerto dos blocos,
com bootstrap de 2.000 reamostragens de redes, levando juntas todas as sementes,
classes e canais do bloco. O tamanho efetivo conservador é 500, não o número
de agentes, ondas ou transições. Um escore médio de bloco em [0,1] tem variância
<=1/4: meia largura normal de IC95% <=1,96/(2*sqrt(500))=0,044. Isso justifica
precisão capaz de separar BA=0,65 de 0,55 sob o limite conservador; não é poder
estimado do piloto nem garantia de utilidade. O IC inclui variabilidade de
rede/estado/erro, mas condiciona no treino e no matching; incerteza de transporte
da âncora não desaparece com mais simulações.

Um único teste primário em r=0,70, sem ancoragem inicial. Reportar BA e sua
incerteza em TODOS os nove valores da grade, com o mesmo conjunto latente e
fluxos de erro pareados, e classificador treinado separadamente em cada r.
Treinar o classificador não autoriza estimar r. Para a curva de nove pontos,
usar banda simultânea de 95%: em cada reamostragem de redes, calcular o máximo
absoluto dos nove desvios de BA em relação às estimativas originais; o quantil
0,95 desses máximos define a meia largura comum, truncada em [0,1]. Não
interpretar como confirmação uma célula secundária favorável.

Curva de aprendizado com prefixos 500/1.000/2.000 do mesmo treino; o contínuo
ancorado, b=0,05, metade da amostra e atrito dependente do estado são secundários,
descritos integralmente sem escolher a célula vencedora. A implementação dos
braços secundários, das bandas e das demais sensibilidades permanece requisito
anterior ao registro/execução deles; não foram rodados nesta emenda. O caso de dois geradores
iguais testa ausência de sinal; a identidade de influência zero já está testada.

A decisão 13 registra a avaliação da condição de parada de 48 h e a
continuidade com âncora externa e sobreposições parciais explicitadas abaixo;
não reiniciar essa contagem nem manter a fonte como inexistente. Persistem
riscos de transporte da faixa e de anterioridade. Encerrar a aposta se matching
falhar, se o novo gate primário for negativo, se apenas persistência estrita
for separável, ou se a revisão focada mostrar que o contraste já está coberto. Resultado nulo confirmatório será relatado sem
mudar a célula. Não aumentar N, força ou treino depois de abrir o teste.

### Sobreposições parciais mais próximas

Esta comparação usa a profundidade de leitura declarada no
[dossiê](reliability-and-prior-art.md); não pressupõe nova leitura integral
nesta emenda. A contribuição proposta é quantitativa e condicional, não a
ideia genérica de separar mudança de erro de resposta.

| Antecedente | O que já cobre | Incremento específico proposto e seu limite |
| --- | --- | --- |
| [Kiley e Vaisey (2020), ASR, p. 487](https://doi.org/10.1177/0003122420921538) | Atualização frequente pode tornar-se indistinguível de disposições estáveis com erro alto. A ambiguidade entre mudança e persistência já está formulada. | Quantificar o desempenho e a região de falha de um discriminante fixo para um núcleo de interação sem âncora contra AR, com marginais iguais, lag 1 aproximado, r externo e onze ondas. Não reivindicar a indistinguibilidade qualitativa como descoberta. |
| [Lersch (2023), ASR](https://doi.org/10.1177/00031224231156456) | Compara disposição, atualização e adaptação em painéis longos; inclui SHP e `P$$P04`. As simulações descritas no dossiê já variam o número de ondas com processos gaussianos lineares. | Usar um núcleo não linear de reorganização, retirando a separação por marginais e controlando r externamente, para medir erros de discriminação nessa geometria. Usar SHP, onze ondas ou persistência versus mudança, isoladamente, não é o incremento. |
| [Moor-Smith e Carpentras (2026)](https://doi.org/10.1007/978-3-032-31712-4_30) | Ruído leva o otimizador a imitar o nulo; no ESS, o nulo repete a distribuição anterior. O estado perturbado alimenta a geração seguinte, com cortes transversais como proxy longitudinal. | Separar erro emitido na observação de mudança latente, conservar identidades e comparar com persistência individual sob r externo. Não reivindicar como novo que ruído favorece um nulo de pouca mudança. |

O código atual usa correlações nos lags 2–5, não um diagnóstico por matriz
completa de transição. As marginais são impostas por R_N, não distribuições
estacionárias emergentes endogenamente. Essas duas limitações impedem atribuir
ao desenho todos os incrementos sugeridos pelo dossiê. O capítulo de
Carpentras–Quayle de 2026 permanece sem leitura integral; a revisão focada pode
restringir ou eliminar o incremento proposto. Não se afirma novidade.

## Alternativa: dose crítica em grupos sobrepostos

Pergunta: apagar o agrupamento dos vizinhos em trios muda a dose externa
necessária para Pr(lock-in no horizonte)=0,5? O estimando é
`Delta=d50(HN)-d50(PN)`, com H/P indicando hiperarestas/projeção e N agregação
não linear. Delta positivo significa que a representação em trios exige maior
dose para reduzir o travamento até metade. O teste é bilateral: um deslocamento
negativo também responde à pergunta, sem seleção posterior de direção.

### Operadores, fonte e desfecho

N=198. Duas partições aleatórias em trios geram 132 grupos, grau de incidência
exatamente dois. Rejeitam-se trios duplicados e redes desconectadas, antes dos
estados. Essa família de duas partições não é uniforme entre todos os
hipergrafos regulares possíveis. A projeção pesa cada vizinho pela multiplicidade
de incidência. Inicialmente, 139 pessoas perto de 0,2 e 59 perto de 0,8,
com ruído normal DP=0,05 e truncamento em [0,1]. Verdade sintética igual a 1.

Em H, para cada trio incidente a i, multiplicar a atração à média dos dois
parceiros por `s(|x_j-x_k|)`, s(d)=exp(lambda*d), e depois tirar a média entre
trios. Em P, tirar a média dos vizinhos ponderada por incidência e multiplicar
a atração por s aplicado à distância média entre pares de vizinhos distintos,
ponderada pelo produto de suas multiplicidades. P não consulta quais parceiros
estavam no mesmo trio. Atualizar todos os nós simultaneamente com ganho 0,1.
Lambda=-1 no primário; lambda=0 é o controle linear.

Após cada passo, os mesmos 20 destinatários fixos sorteados recebem
`x <- x+d*(1-x)`. A dose d é o ganho por sinal, não a confiabilidade: a fonte
é sempre correta, há 100 sinais por destinatário no horizonte H=100 e não há
nós congelados. Essa frequência e a atualização síncrona substituem explicitamente
a versão de dez sinais e tentativas focais do memo anterior. Dose acumulada
nominal é 100*d por destinatário; a alteração realizada depende do estado.
Não a igualar depois dos resultados, pois é variável pós-tratamento.

Lock-in finito significa pelo menos metade dos nós abaixo de 0,5 em todos
os últimos vinte passos. Resolvido significa pelo menos 90% acima de 0,75
em toda essa janela. Os demais são não resolvidos. Para estimar Pr(lock), tanto
resolvidos quanto não resolvidos contam como zero, mas suas frequências serão
reportadas separadamente no confirmatório. d50 não significa que metade
aprendeu a verdade. Não se infere travamento assintótico nem biestabilidade.

O fatorial 2x2 H/P x linear/não linear compartilha rede, estado, destinatários
e dose. Linear H=P é identidade, portanto a diferença de diferenças dos limiares
reduz-se a Delta quando os limiares lineares existem. Com trios disjuntos,
H=P mesmo para lambda não nulo: ambos os controles têm testes analíticos e
numéricos. Sobreposição não é inferida comparando médias entre redes com graus
diferentes. Fonte ausente, maioria invertida, H=50/200, lambda=-2/+1 e
normalização s(0,25)=1 delimitam a interpretação e serão secundários.

### Calibração e estimador

Apenas PN é consultado na calibração, com 48 realizações e doses
{0;0,01;0,02;0,04;0,08;0,16;0,32;0,64;1}. Exigir taxa >=0,9 no primeiro
ponto e <=0,1 no último. Refinar cinco vezes por bisseção ao redor de 0,5,
reutilizando as mesmas sementes somente dentro da calibração. Rejeitar subida
local maior que 0,10. Conservar e publicar todos os pontos consultados.

Na grade final compartilhada, 48 novas realizações por braço HN/PN só verificam
se cada curva tem pelo menos uma célula estritamente entre 0,1 e 0,9 e se
ambas cruzam 0,5. Exportar somente esses dois booleanos; nenhum d50 de avaliação,
taxa por braço ou Delta. Os extremos da grade podem e devem estar no piso/teto;
o critério de não degeneração vale para a região de transição, não para doses
sem sinal ou saturadas. Não estender a grade pelo resultado de HN.

Estimar cada curva por regressão isotônica decrescente de pesos iguais (PAVA),
e interpolar linearmente o primeiro cruzamento de 0,5. Platô exatamente em
0,5 usa sua borda esquerda. Ausência de cruzamento é censura; nunca extrapolar,
substituir por 0/1 ou excluir silenciosamente a réplica bootstrap. O estimando
operacional é o cruzamento da curva interpolada na grade especificada; sua
aproximação a uma dose contínua depende da resolução local e monotonicidade.

### Pré-registro proposto

Usar 500 redes novas, duas sementes de estados e destinatários por rede, em
todos os braços e doses. A unidade de reamostragem é a rede completa, com todas
as sementes e curvas pareadas; bootstrap de 2.000 blocos dá IC95% de Delta.
Hipótese nula Delta=0. Sucesso: IC95% exclui zero e |Delta|>=0,02 na escala de
ganho d; equivalência prática: IC90% inteiro em [-0,02;0,02]. Censura, intervalo
largo ou cruzamento ausente são inconclusivos, não ausência de efeito.

O limite conservador da meia largura da taxa é 0,044 para 500 redes. Com
inclinação local s, a incerteza de uma dose é aproximadamente 0,044/s, além da
discretização. Para a diferença, usar conservadoramente 0,088/s mais a resolução
das duas curvas; não prometer precisão de dose a partir de n binomial sozinho.
Antes do registro, usar exclusivamente a inclinação PN de calibração para
verificar se esse orçamento pode atingir meia largura 0,02; se não, declarar
inviabilidade de precisão ou mudar o plano por emenda anterior ao teste.
Não estimar a variância de Delta nos pilotos. Cap fixo: 500 redes; nenhum
acréscimo pelo p-valor ou sinal observado.

Abandonar se o controle não delimitar d50, se os gates forem negativos, se
linear/disjunto falharem, se o deslocamento ficar na faixa de equivalência,
se só a normalização selecionada produzir efeito ou se o resultado for apenas
atraso eliminado em H=200. O último caso pode sustentar relato de tempo finito,
mas não confirmação de travamento persistente. Leitura integral de Dong e
confronto com Neuhäuser, Iacopini e modelos de massa crítica continuam pendentes
para qualquer alegação de contribuição.

## Separação de sementes, execução e estado do registro

Regra SHA256 sobre `ic-redesign-v1|fase|papel|índice`, primeiros oito bytes em
big-endian. Fases usadas: match, operating-train, operating-check, primary-train,
primary-check, dose-calibration e dose-check. Papéis do painel: state, network,
events, mask, error. Em treino/checagem, índice=2*i+classe; matching social
0–15 e controle 16–31. Papéis de P4: network, state, source, índices 0–47.
O reaproveitamento entre pontos da grade é intencional para números aleatórios
comuns de calibração, não reutilização na checagem principal.

Namespaces reservados, não executados: confirm-train, confirm-validation,
confirm-test, confirm-robustness e confirm-bootstrap. No teste proposto, papel
network usa índice de rede g=0,...,499; estado/evento/máscara/erro usam 2*g+k,
k=0,1. Acrescentar o nome da candidata ao papel para separar P1+P2 de P4.
Os prefixos literais são `panel/` e `dose/`. No treino/validação do painel,
índice=2*i+classe, i=0,...,1999 e i=0,...,399 respectivamente, inclusive para
network. No bootstrap, papel `panel/resampling` ou `dose/resampling`, índice
zero, inicializa o RNG que produz as 2.000 reamostragens.
Classes e braços compartilham esses fluxos quando pareados. A
[auditoria de sementes](../../../../experiments/exploratory/redesign-calibration-v1/seed-audit.json)
comparou 3.328 sementes distintas do piloto com 31.002 reservadas para esses
conjuntos confirmatórios e encontrou interseção zero, sem gerar trajetórias.
Robustez futura exige auditoria própria quando sua grade estiver especificada. O executor de piloto
recusa namespaces confirmatórios. A geração confirmatória e seu bootstrap ainda
não foram implementados: os tamanhos acima são um plano examinável, não código
que tenha produzido evidência.

Falhas numéricas ou menos de três pares válidos interrompem o lote, sem
substituição seletiva de sementes. Nenhuma parada por significância. O runner
recusa diretório existente, grava hashes das trajetórias e respostas do painel,
revisão de código, lock, especificação, protocolo, ambiente, regras de sementes,
contagens e tempos. Dados primários de discriminação e curvas HN/PN de checagem
não são persistidos; seus gates podem ser regenerados pelo código e sementes.
Saídas concluídas são imutáveis; correções exigem sucessor explícito.

NumPy foi acrescentado via uv somente ao estudo, que declarava
`dependencies = []`. Vetoriza painéis de dez mil pessoas, operações de trios e
álgebra linear do discriminante de quatro features; o lock foi atualizado.
Não houve edição de workbench, dependência em sklearn/SciPy ou infraestrutura
nova. Os testes seguem TDD com registros de falha por função ausente antes da
implementação; verificam invariantes científicos, não sucesso da hipótese.

## Resultados exploratórios e pendências

A [execução única](../../../../experiments/exploratory/redesign-calibration-v1/README.md)
no commit `0e2d8ee` levou 88,326 segundos para 3.520 simulações, abaixo do
limite de 20 minutos. No lote original não houve execução confirmatória,
repetição nem alteração de parâmetros após os gates; a correção externa
posterior de r está vinculada à decisão 13, em seção própria abaixo. O resumo preserva integralmente os pontos de
calibração; não contém valores numéricos dos contrastes primários.

| Desenho | Ponto de operação encontrado | Evidência grosseira em sementes novas |
| --- | --- | --- |
| P1+P2, piloto original | a=0,4; rho=0,8389618632; r provisório histórico=0,65. Baseline r=0,8: BA=0,75. | Gate `0,55 < BA < 0,95` passou; 96 painéis/classe de checagem. |
| P4 | PN: d50 de calibração=0,03671875, bracket local [0,03625;0,036875]. | Ambos os braços têm ao menos uma célula com `0,1 < Pr(lock) < 0,9` e cruzam 0,5; 48 realizações/ braço/dose. |

No matching de P1+P2, diferença absoluta de lag 1 latente=0,000126. Na
checagem principal, diferença absoluta de lag 1 ordinal=0,001836 e variação
total marginal agregada=0,000814. A geometria produziu média de 52.097 pares
anuais observados; não são transições humanas. Esses diagnósticos de matching
são permitidos pelo protocolo e não são o contraste principal.

Os números da linha P1+P2 acima são históricos, de r=0,65. O ponto de operação
latente se mantém, mas a célula primária corrente é r=0,70 conforme a decisão
13; sua checagem é registrada separadamente abaixo.

A grade final de P4 é {0;0,01;0,02;0,03;0,035;0,03625;0,036875;0,0375;
0,04;0,08;0,16;0,32;0,64;1}. No controle de calibração, entre 0,035 e 0,0375,
a inclinação secante em módulo é 125 por unidade de dose. A conta local
conservadora de precisão dá 0,088/125=0,000704 para a diferença, antes da
resolução de grade. Isso favorece viabilidade computacional, mas não garante
que a curva HN tenha essa inclinação ou esteja na mesma região refinada.
Intervalos largos entre doses fora do bracket central e censura no bootstrap
continuam riscos para estimar uma dose contínua. Registrar o estimando na grade
acima; uma grade contínua mais fina exigiria emenda baseada apenas no controle,
antes de qualquer confirmatório. Nenhuma foi rodada aqui.

Os gates são verificações empíricas pequenas de não degeneração, não intervalos
de confiança nem confirmação das hipóteses. A precisão e os efeitos dos
confirmatórios propostos permanecem desconhecidos. O rascunho está completo
para revisão, mas não congelado: a fonte externa foi incorporada; permanecem
transportabilidade da confiabilidade, revisão do núcleo normalizado por postos,
revisão focada de anterioridade,
avaliação da resolução da grade de dose e especificação executável das
sensibilidades. Não há alegação de novidade nem aprovação científica inferida
dos testes de software.

A [validação de engenharia](../../../../experiments/exploratory/redesign-calibration-v1/validation.md)
registra 137 testes do estudo, lint, tipos e wheel aprovados. O gate geral
`just quality` segue em execução no workbench no handoff; não está declarado
aprovado. Os arquivos desse projeto permaneceram intactos.

### Checagem da emenda de confiabilidade

A [checagem sucessora](../../../../experiments/exploratory/reliability-correction-v1/README.md)
no commit `7fc90af` concluiu 384 trajetórias em 20,366 segundos. O gate
`0,55 < BA < 0,95` passou em r=0,70, com 96 painéis/classe de treino e outros
96/classe de checagem. Não se divulgam BA, acertos, escores nem contraste com
r=0,65. Nenhuma hipótese foi confirmada e a grade futura não foi executada.

O ponto de operação permanece a=0,4, rho=0,838961863215152, agora com
confiabilidade primária externa r=0,70. A busca não foi repetida: seu baseline
r=0,80 não mudou. Na checagem nova, a diferença absoluta de lag 1 ordinal foi
0,002659 e a variação total marginal agregada 0,001192, diagnósticos de matching
permitidos pelo protocolo. Há 1.920 sementes novas, sem interseção com as
3.328 dos pilotos anteriores ou com as 31.002 reservadas para confirmação.
Nenhuma trajetória confirmatória foi gerada.

Ruff, mypy estrito do caller, oito testes focados do código científico reusado
e estrutura 7/7 passaram. Os hashes do dossiê copiado e das 27 entradas do lote
foram reconferidos; o ledger preserva 384 registros. Nenhum kernel, dependência,
arquivo do workbench ou saída anterior foi alterado. O gate geral da entrega
anterior continua sem resultado final verificado; esta emenda limitada não
relança a matriz. O rascunho segue sem congelamento, e o braço secundário
ancorado ainda requer implementação/testes próprios antes de ser executado.
