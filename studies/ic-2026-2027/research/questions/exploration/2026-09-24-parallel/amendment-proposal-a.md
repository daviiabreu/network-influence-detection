# Emenda sucessora — PROPOSTA A

25/09/2026. Proposta exploratória, não adotada. Não libera sementes nem execução
confirmatórias. Antecessor: [pré-registro congelado](detection-boundary-preregistration-frozen.md),
commit `fd65d2a`, SHA-256
`fb6b4dcf43161a52c725e565bf2a4d2697423bec7d138ad1d30388547cfcd706`.
Motivo: [falha operacional e numérica do gate](detection-boundary-coverage-check.md).
Esta proposta foi produzida somente a partir do brief, do antecessor, do relatório
de falha e do código pertinente. Nenhuma outra proposta foi procurada ou lida.

## Recomendação e limite de adoção

**Resultado: a identidade nula foi sustentada; reduzir refits para 10/20 não
foi sustentado; o orçamento do escopo completo continua não demonstrado.**

Substituir B por traço + AR com transporte compartilhado, usar matching
constrangido com derivada calibrada separadamente e validação independente dos
resíduos, e substituir a geração de dezenas de refits por célula por um
bootstrap local de matching/treino. Conservar refits completos como benchmark
de validação, não como uma pequena estimativa de variância tomada por exata.
Usar banda logit com correção fixa de Bonferroni nas nove forças, por r.

A mudança de banda é decisiva para o custo: o limite em a=0 deixa de depender de
simular as outras oito forças em cada repetição do gate. Não se está apresentando
um teste de uma célula como validação da banda max-t antiga. A validade fora dos
pontos examinados continua sendo uma extrapolação, a ser explicitada.

## Exposição e escolhas que permanecem congeladas

Houve quebra parcial do cegamento **antes desta proposta**: em sementes de
calibração, a=0,30 e r=0,70 produziram AUC 0,943912, EP de Monte Carlo 0,000724,
condicionada àquele matching/treino. O brief informa a implicação operacional
`a*(0,70)<0,30`; essa implicação não deve ser transportada automaticamente à
nova lei B. Conservam-se também as exposições anteriores registradas no
pré-registro. Não se alegará emenda inteiramente cega.

As sondas a=0,03 e 0,10, em r=0,70, foram escolhidas no plano antes de examinar
novas AUCs. São pontos próximos da possível fronteira na grade, não uma busca
nem uma prova de que a fronteira esteja entre eles. Os números de AUC que
necessariamente resultarem da medição de variância também constituem exposição
de calibração e deverão constar da evidência desta proposta.

Ficam congelados: os estimandos a* e a_s*, os alvos primário 0,70 e secundários
0,60/0,80; todas as nove forças e os nove r; N=10.626, onze ondas, entrada,
retenção, domicílios e canal; b=0,25 e a definição pré-transporte de a;
características L3/L4/L5 e LDA com 0,8S+0,2I; treino de 1.000 redes × dois
eventos/classe e teste de 2.000 redes × dois eventos/classe; unidades de cluster,
independência entre classes, controles, nulos secundários e sensibilidades.
Não há interpolação, seleção de r, escolha de sinais pelo teste, exclusão de
refit malsucedido ou promoção de análise secundária. Código e artefatos
congelados de simulação permanecem byte a byte intactos.

## Lei nula sucessora

Para B, gerar T_i normal fixo, independente do estado e das inovações; gerar
`x_0=R_N(epsilon_0)` e
`x_(t+1)=R_N(rho*x_t+sqrt(1-rho²)*epsilon_(t+1))`; observar o estado verdadeiro
`z_t=R_N(sqrt(lambda)*T+sqrt(1-lambda)*x_t)` pelo canal congelado.
Manter rho∈[0;0,999] e lambda∈[0;0,8]. O traço é durável, a atualização é
individual e não existe rede ou exposição social em B. Lambda passa a ser o
peso nominal da mistura antes do transporte final; a identidade gaussiana
`Cov(z_t,z_(t+k))=lambda+(1-lambda)*rho^k` **não** é mais alegada.

Em lambda=0, rho=0,85, R_N é idempotente no seu próprio grid. Inicialização,
inovações e cada atualização coincidem exatamente com a influência em a=0.
O transporte ordinal, a máscara e o erro comuns preservam a igualdade em lei.
Condicional a qualquer escore treinado independentemente, a AUC populacional é
exatamente 0,5, incluindo meio crédito aos empates. O teste usa classes
independentes; reutilizar os mesmos painéis nos dois rótulos não seria evidência.
Em a=0, fixar esse ponto conhecido, sem inventar incerteza de matching:
a variância populacional de nuisance é zero. Não fixar a AUC amostral em 0,5.

A igualdade vale para todo r e para o mesmo canal aplicado aos dois braços.
A extensão a 24 passos precisa aplicar os mesmos 24 transportes ao estado AR,
com teste de identidade próprio antes de uso. Não extrapolar automaticamente a
prova aos nulos A/C/E gaussianos ou à sensibilidade de ancoragem inicial.
As respectivas especificações substantivas não são alteradas por esta emenda.

## Matching e critérios de falha

1. Calibrar, por célula, um mapa local de dois momentos em sementes separadas:
   ponto inicial obtido sem discriminador e Jacobiana de L1/L2 observados por
   números aleatórios comuns. Diferenças finitas 0,01, verificadas também com
   0,005. Fixar o mapa antes das repetições de validação; não o atualizar com AUCs.
2. Para cada novo fit, usar M=1.024 painéis e momentos novos. Reutilizar somente
   a derivada. Resolver os dois parâmetros na caixa, incluindo os candidatos
   nas faces e reotimizando o parâmetro livre. Avaliar o gerador verdadeiro em
   cada passo, até 12 avaliações. Uma projeção componente a componente do passo
   Newton não é, sozinha, a solução do problema constrangido.
3. Em cada lag, usar o EP **pareado**
   `SE_k=sd(Lk_nulo-Lk_social)/sqrt(M)`. Separar otimização de aceitação:
   exigir pelo menos um passo constrangido antes de declarar convergência,
   exceto na identidade analítica a=0. Para raiz interior, exigir
   `|resíduo_k|≤min(0,00005; max(0,000001; 0,1*SE_k))`. Na borda, verificar
   estacionariedade constrangida com reavaliação local da derivada; não confundir
   passo projetado nulo com raiz de dois momentos. O probe de custo usou 2×SE,
   M=256 e permitia parar na primeira avaliação. Essa variante apresentou
   paradas no ponto inicial comum: não certifica a variância do sucessor mais
   estrito e seu custo é um piso, não uma medição do plano M=1.024.
4. Validar o ponto em 4.096 pares novos, fase independente do ajuste. Exigir
   `|resíduo_k|+2,2414*SE_k≤0,0003` em ambos os lags. Esta é uma verificação
   conjunta aproximada de equivalência dos dois momentos, não a declaração de
   que um erro grande virou aceitável porque seu EP também é grande.
5. Se a precisão, o mapa ou a convergência falhar, fazer uma única tentativa
   sucessora com M=4.096, mapa recalibrado e novo conjunto de validação do mesmo
   tamanho. Registrar ambas as tentativas. Falha final gera célula não resolvida;
   não treinar nem substituir por “AUC abaixo do alvo”. Uma falha do solver não
   prova impossibilidade matemática da família. Manter o gate de viabilidade
   anterior ao treino e a censura de fronteira por lacunas.

Os mesmos números aleatórios podem acoplar os braços **somente no matching**.
Treino, teste e referência mantêm classes independentes e fases separadas.
O mapa comum é uma escolha operacional condicionante: sua incerteza e eventual
viés de parada não desaparecem por reuso e devem aparecer no gate sucessor.

## Variância, refits e banda

Estimar a variância dos escores por placements da AUC e médias dos dois eventos
em cada rede. Somar `Var(placement_médio_social)/n_redes_social` e
`Var(placement_médio_nulo)/n_redes_nulo`. Não aplicar DeLong iid aos 4.000 eventos
como se fossem 4.000 redes. A justificativa de componentes estruturais é a de
[DeLong et al.](https://scholars.duke.edu/publication/712661), com extensão de
cluster discutida por [Obuchowski](https://pubmed.ncbi.nlm.nih.gov/9192452/).

Para nuisance, usar 2.000 reamostragens locais. Reamostrar os pares de momentos,
resolver o deslocamento dos parâmetros no mapa linear com as mesmas restrições,
transportar linearmente as características nulas de treino e de referência por
suas derivadas locais, reamostrar redes inteiras de treino nas duas classes,
reajustar a LDA e recalcular a AUC na referência fixa. A referência nula muda com
os parâmetros; manter seus valores inalterados perderia justamente parte da
variância que se quer medir. A classe social da referência pode ser reutilizada.
Esse procedimento é uma aproximação local, não 2.000 refits completos.

Usar `V_total=V_scores+V_nuisance`, **sem dividir V_nuisance por 2.000, 40 ou 20**.
Em a=0 usar V_nuisance=0 pela igualdade analítica, não pela variância dos AUCs
numa referência finita que pode variar artificialmente com a direção da LDA.
Antes de liberação, o bootstrap local deve ser comparado com 40 refits completos
no mesmo regime de matching/treino. Exigir estabilidade da variância ao reduzir
o passo 0,01 para 0,005: razão entre 0,8 e 1,25; comparar sua variância com o
intervalo de incerteza Monte Carlo do benchmark, sem escolher o passo que fique
mais perto do resultado desejado. Usar o maior dos dois componentes locais
quando ambos passarem; discrepância bloqueia o procedimento, não autoriza
inflar um fator até passar nos mesmos dados.

Dez ou vinte refits não tornam uma variância bem determinada. Sob aproximação
normal, o EP relativo de s² é `sqrt(2/(B-1))`: 47,1%, 32,4% e 22,6% para
B=10/20/40. Para ≤25% sob essa aproximação, são necessários pelo menos 33;
conservar 40 como piso de benchmark, não como garantia de precisão. Com 2.000 draws locais o erro puramente Monte Carlo seria 3,16%, mas
isso não inclui erro da aproximação. A referência para intervalos qui-quadrado
é o [NIST](https://www.itl.nist.gov/div898/handbook/eda/section3/eda358.htm);
a hipótese normal deve ser declarada, não presumida para refits truncados ou
selecionados por sucesso.

Manter logit, epsilon=1/(2×2.000), piso de EP e endpoints do congelado. Substituir
o crítico max-t adaptativo por `z_(1-0,05/18)=2,7729`, aplicado às nove forças,
separadamente por r. Bonferroni não exige independência entre forças e dispensa
estimar uma matriz 9×9 com dez ou vinte refits. Não cria simultaneidade entre os
nove r, nem corrige viés de matching, caudas mal aproximadas ou variância errada.

## Gate sucessor, antes de qualquer confirmatório

O gate terá três partes, em namespaces novos de calibração, disjuntos dos probes
expostos aqui. O novo texto, código, alocação, critérios e hashes serão fixados
antes dessas corridas. Não repetir até conseguir aprovação.

- **Pipeline em a=0:** R=200 repetições independentes em cada um dos nove r,
  com treino, teste e canal completos, ponto nulo conhecido e banda sucessora.
  Exigir inclusão de 0,5 em pelo menos 190/200 intervalos em cada r; falhas
  numéricas contam no denominador. Reportar também o IC pontual de 95% e sua
  cobertura, para que a largura da correção de nove forças não esconda erro do EP.
  Não é necessário gerar as oito forças não nulas para obter esse crítico fixo.
- **Incerteza fora do nulo:** R=100 pares de execuções independentes por
  célula em (a,r)=(0,03;0,70) e (0,10;0,70). Cada metade refaz matching,
  treino, teste e nuisance; as referências são comuns apenas aos refits
  internos de uma metade, nunca entre metades/repetições. A diferença de
  estimativas logit tem centro zero por replicação do mesmo procedimento.
  Exigir inclusão de zero em pelo menos 92/100 ICs pontuais de 95%, com
  `SE_delta²=V_1/[p_1(1-p_1)]²+V_2/[p_2(1-p_2)]²`, e razão entre variância
  empírica das diferenças e média de SE_delta² em [0,67;1,50]. AUCs 0/1
  usam a mesma regra epsilon; falhas contam no denominador. São 400 execuções
  não nulas no total. Este é um teste de consistência da incerteza por
  replicação, **não** cobertura absoluta de uma AUC não nula conhecida.
  Evita chamar a referência condicional 0,944 de verdade do procedimento
  inteiro ou gastar o orçamento fingindo que um centro Monte Carlo é exato.
  Viés comum às duas metades pode cancelar: o teste independente de matching
  permanece obrigatório e essa limitação deve constar do artigo.
- **Mecânica da banda:** R=2.000 repetições de um nulo exatamente igual nos
  dois rótulos em todas as nove coordenadas, com clusters de dois eventos,
  dependência entre forças e verdade vetorial (0,5,…,0,5). Exigir cobertura
  conjunta ≥1.880/2.000. Registrar separadamente esse teste e o pipeline ordinal;
  um surrogate de escores não valida o matching nem o gerador científico.

Para cobertura verdadeira 0,95, os EPs de Monte Carlo são 1,54 pp (R=200),
2,18 pp (R=100) e 0,49 pp (R=2.000). O limiar 92/100 aceita um procedimento
com cobertura 0,95 com probabilidade 93,69%, mas um de cobertura 0,85 com apenas
2,75%; pode aceitar cobertura 0,90 em 32,09% dos casos. Não prova cobertura
nominal exata. O limiar 190/200 em cobertura pontual 0,95 passa só em 58,31%;
a banda corrigida em uma coordenada costuma cobrir mais, mas isso não deve ser
vendido como poder para detectar toda subcobertura. Publicar Wilson/binomial,
falhas, além de passa/falha. Os pares são independentes entre repetições;
não tratar as duas metades de um par como duas repetições de cobertura.

Esse gate testa cobertura absoluta no nulo e consistência da incerteza fora
dele em dois pontos declarados. Não certifica cobertura absoluta fora do nulo
nem cobertura uniforme em 81 células, em outros nulos ou em todas as sensibilidades.
Nas demais células, continuam obrigatórios equivalência independente dos
momentos, estabilidade do stencil, diagnóstico de referência e registro de
invalidade. Uma falha não autoriza reduzir grade, canais ou controles.

## Medições desta proposta e orçamento

Medições em N=10.626, onze ondas, r=0,70, oito workers de painéis. Namespace
`ic-detection-boundary-amendment-a-20260925-calibration`; Python 3.12.13,
NumPy 2.5.3, macOS 27.0 arm64. O teto foi interpretado como tempo de parede:
**3.550,03 s = 59 min 10 s**, incluindo as etapas concorrentes dentro dessa
janela. Há pelo menos 4,22 CPU-h nos jobs que registraram CPU; referências e
alguns diagnósticos não registraram esse contador. Não são “60 CPU-minutos”.

Os [resultados e hashes](../../../../experiments/exploratory/amendment-a-calibration/summary.json)
e o [roteiro de reprodução](../../../../experiments/exploratory/amendment-a-calibration/README.md)
separam outputs brutos, planos sucessores operacionais, falhas e projeções.

### Matching: realizações, tolerância e Monte Carlo

O primeiro sweep usou oito blocos por combinação e solver numérico com alvo
estrito 0,00005. As colunas de tolerâncias mais largas abaixo são **reavaliações
dos resíduos finais desse mesmo sweep**, não oito novos ajustes para cada
coluna. `kSE` significa `min(0,0003; max(0,00005; k*SE_pareado))`.

| a | M | Sucesso a 0,00005 | A 0,0003 | A 1SE | A 2SE | EP pareado médio L1 / L2 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 256 | 8/8 | 8/8 | 8/8 | 8/8 | 0 / 0 |
| 0 | 1.024 | 8/8 | 8/8 | 8/8 | 8/8 | 0 / 0 |
| 0,03 | 256 | 7/8 | 7/8 | 7/8 | 7/8 | 0,0000878 / 0,0001159 |
| 0,03 | 1.024 | 7/8 | 7/8 | 7/8 | 7/8 | 0,0000443 / 0,0000575 |
| 0,10 | 256 | 5/8 | 7/8 | 6/8 | 7/8 | 0,0001314 / 0,0001745 |
| 0,10 | 1.024 | 7/8 | 7/8 | 7/8 | 7/8 | 0,0000664 / 0,0000872 |

O EP da média **social isolada** de L1 foi aproximadamente 0,000220 com 256 e
0,000112 com 1.024, inclusive em a=0. EP pareado zero em a=0 é a identidade
pathwise, não ausência de variação entre painéis. Quadruplicar M aproximadamente
reduziu os EPs à metade. Não resolveu sozinho os stalls: o bloco 7 de a=0,03,
M=1.024, terminou em lambda=0 com resíduo L1=0,000375 e EP=0,0000273.
É erro de alcance/solver muito maior que o ruído, não justificativa para aumentar
a tolerância. O sweep levou 1.630,70 s de parede. Oito repetições são uma sonda
pequena, não estimativa precisa de uma taxa universal de sucesso.

O mapa de resposta independente usou bloco 9001, M=1.024, passo 0,01; sua
preparação nas duas células levou 32,02 s, concorrente com a referência social.
Com esse mapa e aceitação 2SE, passaram 40/40 refits em a=0,10 e o probe
adicional em a=0,03. Isso mede sucesso operacional **no conjunto de ajuste**;
a equivalência em 4.096 pares independentes ainda não foi executada.

### Custo e necessidade de refits

Cada refit medido usou M=256, 2.000 eventos/classe de treino e referência fixa
com 4.000 eventos/classe. Regerou o nulo na referência; reutilizou a classe social.
Os tempos por worker refletem a carga existente na máquina, não oito núcleos
exclusivos. A preparação conjunta das duas referências sociais levou 96,76 s,
fora da coluna por refit.

| Célula | Refits completos | Matching médio | Treino médio | Referência nula média | Total por refit | CPU por refit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| a=0,10; r=0,70 | 40 | 19,27 s | 139,28 s | 141,93 s | 300,48 s; faixa 231,26–379,20 | 187,62 s |
| a=0,03; r=0,70 | 1 adicional | 16,44 s | 141,04 s | 148,58 s | 306,06 s | 181,90 s |

A otimização de transporte substitui a segunda ordenação por atribuição pelos
índices; testes de N completo conservaram exatamente os painéis de influência
congelados em a=0/0,03/0,10 e as estatísticas observadas. O ganho não autoriza
atribuir a diferença de custo inteira a essa otimização: a lei B também mudou.
O custo futuro M=1.024, convergência estrita e validação independente será maior
que o destes refits de sondagem.

| Prefixo de refits a=0,10 | Variância amostral da AUC na referência comum |
| ---: | ---: |
| 10 | 0,00000424954 |
| 20 | 0,00001928491 |
| 40 | 0,00008635846 |

A estimativa com 40 foi **20,32×** a de 10 e **4,48×** a de 20. O bloco 1
forneceu o ponto inicial do mapa, portanto essas três linhas são descritivas,
não uma amostra integralmente independente daquele desenvolvimento. Excluindo
somente esse bloco por proveniência, sem excluir falhas ou outliers, os prefixos
independentes condicionados ao mapa dão: B=10, 0,00000509092; B=20,
0,00001930841; B=30, 0,00006637845; B=39, **0,00008848769**, DP=0,009407.
Não há 40 refits integralmente independentes do desenvolvimento nesta entrega.

Em 34/40 ajustes o solver aceitou o ponto inicial já na primeira avaliação.
As poucas atualizações produziram caudas importantes: curtose empírica 7,96 nos
39 blocos, EP relativo de s² por diagnóstico de quarto momento ≈42,3%, não os
22,9% da aproximação normal. Esse diagnóstico sugere ordem de **112 refits**
para EP relativo de 25% sob essa mesma regra, mas é uma extrapolação imprecisa
de apenas 39 observações. Assim, 40 é piso de benchmark para o novo solver;
não há evidência de que 40 estabilize a variante de parada frouxa. Dez ou vinte
não são uma redução defensável. O novo critério exige refit numérico efetivo
antes da aceitação estatística justamente para não mascarar esse componente.

Os vinte refits regulares de a=0,03 e os stencils opcionais não terminaram antes
do teto e foram interrompidos; o custo dessa célula vem do probe separado,
bloco 9003. Não existe uma comparação 10/20/40 de variância nessa segunda célula,
nem validação empírica do bootstrap local de 2.000 draws. Seus testes atuais são
algébricos/de implementação. Essa ausência é bloqueante para adoção, não licença
para apresentar a aproximação como validada.

### Igualdade nula e exposição adicional

Com 20.000 redes/classe × dois eventos, rho=0,85, lambda=0 e LDA treinada em
2.000 eventos/classe, a referência a=0 produziu **AUC 0,50095585**, EP agrupado
**0,00204453**, z=0,468 em relação a 0,5. A geração dos 80.000 painéis levou
232,93 s em oito workers; treino e avaliação final levaram 51,91 s. Isso
corrobora a prova de igualdade e não foi obtido copiando painéis entre classes.

No teste separado de escores gaussianos idênticos, com efeitos de rede/evento
e nove forças dependentes, a banda incluiu o vetor verdadeiro em
**1.943/2.000 = 97,15%**, EP Monte Carlo 0,372 pp; largura média 0,04060,
40,59 s. Passaria o critério mecânico proposto. Não é o gate científico.

Exposição nova nesta medição: AUC média dos 40 refits em a=0,10 foi 0,756070,
faixa 0,731713–0,789686; o único probe adicional a=0,03 deu 0,589413.
Esses valores de calibração, condicionados às regras e referências acima,
foram vistos e não serão reutilizados como confirmação. Não motivaram mudança
de grade, alvo, r, discriminador ou mecanismos. As revisões dos planos de orçamento e do
mapa ocorreram por custo/resíduos de matching, antes de novas AUCs não nulas.
O probe adicional, bloco 9003, foi alocado após os primeiros refits para medir
o custo da segunda célula já prevista, sob o mesmo teto. A exigência de não parar no ponto inicial foi reforçada após observar o
comportamento dos refits e é uma correção operacional explicitamente não cega.

### Capacidade da máquina: gate, primário e escopo completo

A [conta de capacidade](../../../../experiments/exploratory/amendment-a-calibration/compute-projection.json)
usou 0,02194 CPU-s/painel como proxy B, derivados de 187,62 CPU-s por 8.550,4
painéis/refit, e 0,01298 s/painel para a=0, derivados do treino isolado.
É uma aproximação de capacidade, não benchmark da matriz inteira. Pressupõe
máquina dedicada, oito workers, quatro avaliações nulas por matching M=1.024,
sucesso na primeira tentativa e **25% de reserva**. Não presume a mesma taxa
sob a contenção observada; no probe o tempo de worker/CPU foi cerca de 1,60.

A conta explícita por célula não nula soma 66.528 painéis: 5.120 para mapa,
5.120 para matching, 8.192 para validação, 4.000 para treino, 8.000 para teste,
8.000 para referência e 28.096 para quatro stencils. No gate, o mapa fica
fixo e são 61.408 por repetição. A conta de a=0 usa 12.000 painéis por repetição
(treino + teste). O gate inclui ainda 40 benchmarks completos por célula não
nula, no novo regime; não reutiliza os refits expostos deste piloto.

| Entrega | Projeção de parede com oito workers e reserva |
| --- | ---: |
| Gate sucessor completo descrito acima | **37,2 h** |
| B principal observado, todas as 81 células | **5,1 h** |
| Gate + B principal observado | **42,3 h** |
| Quinze grades observadas, tratadas pela taxa B | **77,0 h** |
| Incremento dos três controles nos cinco nulos principais | **59,5 h** |
| Inventário limitado acima, antes dos extras abaixo | **136,5 h** |
| Gate + esse inventário | **173,7 h** |

As quinze grades são cinco nulos no principal, quatro sensibilidades de canal
com B e seis mecânicas com B (24 passos, b=0 e quatro ancoragens), cada uma com
81 células. Essa contagem **não autoriza reduzir o escopo** se o inventário
congelado exigir mais cruzamentos. Os controles foram orçados somente nos
cinco nulos principais; seu incremento supõe reutilização da classe social,
mas rematching/simulações nulas próprios, 51.408 painéis adicionais por célula
por canal. Mobilidade reutiliza os painéis, mas ainda acrescenta processamento.
Não estão incluídos o prêmio de custo do kernel de 24 passos, controles nas
sensibilidades, tentativas M=4.096, o tempo das 2.000 reamostragens locais por célula
(ainda não medido), ou falhas de implementação. Nulos mais
baratos e cache entre r/canais podem reduzir custos; nenhum ganho de cache
suficiente para fechar o pacote completo foi medido aqui.

**Conclusão operacional: o gate e B principal parecem provisionáveis; a proposta
A ainda não demonstra um confirmatório completo em ≤72 h.** A projeção limitada
já é cerca de 1,90× esse teto, antes de extras. Recomendar esta direção
metodológica não equivale a aprovar o pacote: é necessário demonstrar ganho
adicional no inventário completo, ou registrar inviabilidade. Não remover
controles/sensibilidades, não mover resultados para “opcional” e não vender
42,3 h como tempo de toda a entrega congelada.

### Verificação e preservação

Os protótipos estão somente em módulo novo e scripts de calibração; nenhum
runner congelado os importa. Houve TDD para igualdade, otimização, matching,
clusters, banda e propagação local. Passaram **188 testes do estudo**, incluindo
14 novos, Ruff e mypy. Duas fixtures antigas receberam somente correções de
assinatura/tipagem para o gate; nenhuma asserção científica foi removida.
O `just quality` integrado foi interrompido após **1.210 testes do workbench
passarem**, durante `test_focused_attempts_backup`, para limitar trabalho não
relacionado à medição. Não é declarado como matriz completa verde.

A auditoria de 1.673.642 materiais de sementes de calibração encontrou zero
colisões. Não executou sementes confirmatórias. O SHA-256 do pré-registro confere com o declarado no início; fora do módulo
novo, o diff dos arquivos científicos em `src/` contra `1d3c674` está vazio.
Passaram os sete checks de `check_repository.py`, com
`UV_CACHE_DIR=/private/tmp/uv-cache-cov2`, e os builds e wheel smokes dos dois
projetos. O README e o sumário versionado registram o manifesto e os hashes
dos outputs brutos.


## Riscos e decisão de execução

O transporte modifica a lei finita de B e a interpretação quantitativa de lambda;
isso é necessário para resolver o defeito de validade, mas não pode ser ocultado.
A igualdade nula é uma propriedade desse simulador, não de atitudes reais.
O mapa de dois momentos é mal condicionado perto da borda; reusar uma derivada
não elimina identificação fraca, múltiplos ótimos ou células inalcançáveis.
O bootstrap local pode falhar em fronteiras paramétricas, sob mudanças de postos
ou por curvatura. Referência finita, viés de parada, caudas da AUC e a quadratura
de componentes continuam sendo aproximações. A estabilidade de 40 refits é
limitada e não autoriza pooling indiscriminado entre a ou r.

A prova analítica em a=0, testes verdes e uma banda de surrogate não constituem
aprovação científica do sucessor. A proposta só pode ser adotada após implementar
as partes de produção ainda ausentes, fixar seu hash e passar o gate novo.
Se o inventário completo de controles/sensibilidades não couber nos tetos de 48 h + 72 h, registrar inviabilidade operacional. Não
prometer o orçamento contando apenas B principal, nem omitir o restante do
escopo congelado. Nenhuma semente confirmatória foi derivada ou executada.
