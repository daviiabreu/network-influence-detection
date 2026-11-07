# Fronteira de detecção de padrões dinâmicos — rascunho sucessor

24/09/2026. Emenda anterior ao congelamento, em resposta à decisão 14 e à
revisão estatística de `eb083df`. Substitui as regras inferenciais e de
calibração do [rascunho anterior](redesign-and-preregistration-draft.md).
Permanece exploratório, sem registro nem experimento confirmatório. As versões,
especificações e saídas anteriores ficam preservadas. Não se alega novidade.

## Proveniência e exposição anterior

O log local `owner-decisions-20260924-session-log.md`, fora do Git, tinha SHA-256
`c9df760b03731c8cca897ffc002b7d7ad7a7dd3e1e8704ac2a2c7899f536a5ba` até a decisão
14. Durante esta implementação recebeu a decisão 15; o prefixo até 14 foi
verificado byte a byte pelo hash anterior. Hash integral então observado:
`74263613678a62c292ffa00fd9774cd8073f26696974fe3b8a8e40d63d0eab06`.
A decisão 15 abandona P4 e indica CoDiNG como antecedente adicional a diferenciar.
Isso não altera a grade ou a regra de inferência do presente piloto.

Os scripts lidos em `/Users/davi/.local/state/research-workbench/prereg-review-20260924/`
foram `sanity.py`, `sanity2.py`, `sanity3.py`, respectivamente com hashes
`93de7c2739614416842e390045c8cd7314f8a7a51620aab8868d0ea51ee88ddf`,
`6fbf7ca6e15ea10f891be924ed6f18eba961a3cf8882622b397c4b962268ccff` e
`215bbeae64d54bc7f58a8607f940835de75ed17808d2c35f7fd067c5cd006823`.
Eles investigam decaimento, traço+AR e distorção de canal; não foram reexecutados.

Foram vistos os gates de não degeneração da classificação anterior em r=0,65 e
r=0,70; a seleção anterior da força também usou classificação em r=0,80. Isso é
**exposição exploratória**, não teste confirmatório. A antiga força 0,4, o antigo
AR e seus gates deixam de definir a análise. Não serão vistos novos gates de BA
ou valores de AUC antes do teste redesenhado. A exceção autorizada é um único bit:
se a fronteira piloto em r=0,70 está no interior da grade fixa abaixo.

## Pergunta, estimando e alcance

Em um painel anual de onze ondas, qual parcela nominal de inovação direcionada
por interação é necessária para que um discriminador pré-declarado alcance AUC
0,70 contra traço + AR, após igualar marginais e lag-1 observados?
O estimando é `a*(r) = min{a em G: AUC(a,r) >= 0,70}`. Trata-se de uma fronteira
**na grade**, condicional à família, ao canal e ao treinamento especificados;
não se interpola uma fronteira contínua nem se impõe monotonicidade à AUC.
AUC 0,60 e 0,80 são alvos secundários, sem nova decisão de sucesso.

Resultados possíveis: fronteira finita pequena (`0 < a* <= 0,03`), grande
(`0,03 < a* <= 0,90`), ou não alcançada até 0,90. Um primeiro ponto já acima do
alvo é censura à esquerda e falha da referência a=0; não é influência detectada.
Uma fronteira na última posição é identificável apenas com resolução de borda.
O limiar 0,03 é uma convenção operacional fixada antes do piloto, sem significado
empírico estabelecido. Não alcançar o alvo é resultado negativo informativo;
IC amplo é inconclusivo. Nenhum dos dois justifica procurar outra grade após
olhar a AUC. As regiões serão atribuídas também ao intervalo, sem forçar um
rótulo pontual quando este atravessar pequena/grande/censurada.

O estudo distingue decaimentos e reorganizações **compatíveis com** modelos.
Não detecta influência social nem a identifica causalmente: faltam exposições
observadas, e a equivalência entre mecanismos permanece possível
([Manski 1993](https://doi.org/10.2307/2298123);
[Shalizi e Thomas 2011](https://doi.org/10.1177/0049124111404820)).

## Geometria, confiabilidade e canal

N=10.626, onze ondas: 7.084 entram em t=0 e 3.542 em t=5. Domicílios de duas
pessoas têm retenção anual 0,89, desistência definitiva e independente do estado
latente. Uma etapa dinâmica corresponde a um ano. A máscara é compartilhada
entre os braços de pareamento. É geometria aproximada ao SHP/P$$P04 em
1999–2009, não reprodução da máscara empírica. Mantêm-se as limitações documentadas
em [acesso e reprodução](empirical-data-access-and-reproduction.md).

Confiabilidade é fixada externamente em `R={0,50;0,55;0,60;0,65;0,70;0,75;0,80;0,85;0,90}`;
r=0,70 é primária, 0,65–0,80 é o núcleo das âncoras. Publicar toda a grade, sem
selecionar r. O [dossiê copiado](reliability-and-prior-art.md) documenta Alwin e
Tufiș (2023), Hout e Hastings (2016; 10.15195/v3.a43), ESS/Poses et al. (2021;
10.18148/srm/2021.v15i3.7816) e Turper e Aarts (2017). As métricas publicadas não
são idênticas nem estimam diretamente a confiabilidade de P$$P04.
A correção de 0,65 para 0,70 foi externa e anterior ao congelamento, embora
ambos os gates exploratórios tenham sido vistos.

Canal contínuo: `w=sqrt(r) z + sqrt(1-r) e`, com e normal independente. Para
z padronizado, corr²(w,z)=r em população. Depois, por onda e entre respondentes,
transportar os postos de w para categorias 0…10 equiprováveis, com contagens
fixas pelo quantil `(j+0,5)/n_t`. Assim, marginais observadas são iguais
exatamente entre braços com a mesma máscara; arredondamento é comum. Esta
transformação faz parte do modelo observacional. r descreve o canal contínuo,
não a confiabilidade final ordinal. O transporte artificial e seu uso da onda
completa limitam a generalização para um instrumento real.

No controle heterocedástico, `s(z)=1+2 exp(-z²/2)` normalizado para média de
s²=1 e erro `s(z)e`. Antes do transporte, 10% recebem w=0 por heaping; empates
são desfeitos aleatoriamente, independentemente dos estados. Ambos os braços
nessa comparação secundária recebem a mesma marginal-alvo: massa 0,1 extra na
categoria 5 e 0,9/11 em cada categoria. Só o nulo recebe o heaping estocástico.
Isso preserva o comparador marginal; não confundir corr² antes do heaping com
confiabilidade depois dele. Não reduzir a análise a diferenças de frequência
na categoria 5.

## Mecanismos e força fixada por quantidade externa ao discriminador

Braço de reorganização: oito permutações independentes da população geram uma
rede dirigida fixa. Cada pessoa recebe oito entradas e oito saídas contando
multiplicidade; repetições e autoarestas são permitidas, com pequena frequência
esperada nesta geometria. Redes são sorteadas independentemente entre réplicas.
É mudança explícita em relação aos oito parceiros distintos do piloto antigo.

Para cada agente, `D_i=media_j f(z_j-z_i)`; `f(g)=g` para `|g|<=1` e
`f(g)=-b g` fora. No principal b=0; b=0,25 é sensibilidade. Centralizar D e
dividir por seu DP transversal para obter d. Com ρ=0,85:

`u = ρ z + sqrt(1-ρ²)[sqrt(a) d + sqrt(1-a) ε]`; `z' = R_N(u)`.

`R_N` atribui quantis normais padronizados mantendo postos. Estado inicial é
normal por postos; sem burn-in, pois a reorganização desde a rede sorteada é
parte explícita do alvo. Não há retorno à opinião inicial. Se DP(D)=0 e a>0,
falha fechada, sem substituir silenciosamente o mecanismo.

`G={0;0,001;0,003;0,01;0,03;0,10;0,30;0,60;0,90}` fica fixada antes do piloto.
a é a parcela do orçamento **nominal de inovação pré-transporte** destinada a
d, cuja variância transversal é unitária. ε é independente e de variância
unitária: as parcelas esperadas são a e 1−a. Não é parcela da variância total
realizada de Δz: existe covariância entre z e d e o transporte muda a escala.
Esta definição física do simulador é externa à AUC; não é uma estimativa SHP.
Registrar futuramente também variâncias/covariâncias antes e depois do
transporte, sem redefinir a grade. A força antiga não é numericamente comparável.

Ancoragem inicial é somente secundária: `z'=R_N((1−ω)u+ω z0)`,
ω∈{0;0,25;0,50;0,75;1}. ω=0 é o principal. Esse contínuo não é reprodução
literal dos resets de Gestefeld e Lorenz. O caso degenerado ω=1 é controle
positivo de traço, não célula destinada a evitar teto.

Família nula, com início estacionário e inovações independentes:

| Braço | Gerador latente | Papel |
| --- | --- | --- |
| A | `z_t=x_t`, `x_t=φx_(t−1)+sqrt(1−φ²)ε_t` | atualização ativa; secundário |
| B | `z_t=sqrt(λ)T+sqrt(1−λ)x_t` | traço + atualização ativa; confirmatório |
| C | AR de A, canal heterocedástico e heaping acima | secundário |

T e x0 normais independentes, variância 1. Em B, `Cov(z_t,z_(t+k))=λ+(1−λ)φ^k`;
em A/C latente, `φ^k`. Não chamar A de persistência ou disposições estáveis.
B é confirmatório porque inclui estabilidade durável e atualização, pode
aproximar decaimentos mistos e contém A como λ=0. Evita vencer apenas um AR
simples. Ainda é uma família paramétrica limitada, não o conjunto de todas as
explicações sem interação.

## Pareamento e orçamento igual

Antes de treinar qualquer discriminador, gerar pelo menos 256 painéis
independentes de calibração por célula; no confirmatório planejam-se 1.024.
Reutilizar números aleatórios entre valores de a/r e tentativas de φ, nunca
entre calibração, treino e teste. Para B, estimar λ pelos dois primeiros
momentos latentes médios de calibração:
`λ=clip[(c2−c1²)/(1−2c1+c2),0,min(0,8,max(0,c1−0,05))]`.
É ajuste de nuisance cego à AUC; não se usa lag-2 observado de teste.
O clipping e a imperfeição da aproximação normal devem ser relatados. Em A/C,
λ=0. A capacidade adicional de B é intencional e pré-declarada.

Para cada r, resolver φ∈[0;0,999] pelo **mesmo** algoritmo e máximo de dezesseis
avaliações por braço. O alvo é a média das correlações Pearson lag-1 de cada
painel observado, reunindo todos os pares anuais válidos dentro do painel.
Não usar correlação latente, média de correlações anuais nem correlação de
uma amostra empilhada de painéis. Tolerância:
`|media(L1_social)−media(L1_nulo)| <= min(0,0003;0,1 DP_social;0,1 DP_nulo)`.
Marginais por onda são idênticas pelo transporte e mesma máscara, até a mesma
regra inteira de contagem. A meta não é igualdade de cada realização de lag-1.

Falha de bracket, de tolerância ou DP degenerado impede analisar aquela célula;
não vira ausência de detecção. Não relaxar tolerância nem selecionar réplicas.
Todas as famílias recebem o mesmo número de painéis, dezesseis avaliações
máximas e discriminador sem busca de hiperparâmetros. A/B/C não competem para
escolher o nulo com resultado mais favorável. O erro de matching e de λ entra
na inferência por reamostragem e novo ajuste, conforme abaixo.

## Discriminador e decomposição

Discriminador principal: LDA regularizada fixa, padronização pelo treino,
covariância `0,8 S + 0,2 I`, quatro entradas Pearson L2…L5, orientação de escore
fixada no treino (influência maior). L1 fica exclusivamente no matching.
AUC é a probabilidade de o escore de um painel do braço de reorganização
superar o escore de um painel nulo, com meio crédito para empate. Não há corte
de classificação, reversão pela AUC de teste ou ponto operacional a escolher.

Treinar o mesmo modelo, mesmo orçamento, separadamente nos controles:
latente mascarado; ordinal com r=1,0; observado com r da célula; correlações de
postos médios (Spearman por onda, com empates) no observado e no latente.
O controle de postos é invariante a transformação estritamente crescente antes
de nova discretização; não é invariante à perda de informação ou a novos
empates. Esses controles não substituem o estimando observado principal.

Mobilidade é análise separada: média de |Δ| por terço da posição em postos
na onda inicial do par. Não entra no classificador principal de decaimento;
classificador secundário de três entradas recebe orçamento idêntico. Registrar
cada canal separadamente. Mobilidade depende da escala, conforme
[Carpentras e Quayle (2023)](https://doi.org/10.1080/13645579.2022.2137938);
não usá-la para sustentar uma alegação geral de influência.

## Inferência, amostra e poder

Plano confirmatório, **não executado**: por célula e braço, 1.024 realizações
para matching; 1.000 redes × dois eventos para treino; 2.000 redes × dois
eventos para teste. Não há conjunto de tuning porque não há seleção de modelo.
A rede e a semente de evento são efeitos aleatórios: os eventos ficam aninhados
na rede, que é a unidade independente. Nulo recebe identificador de bloco
correspondente e eventos independentes, mesmo sem influência de arestas.
Mesmos blocos ao longo de a/r permitem reamostragem conjunta. Pesos iguais por
rede; pessoas e ondas nunca contam como réplicas independentes da AUC.

Bootstrap hierárquico: 2.000 réplicas externas, 200 internas por externa.
Reamostrar redes (e eventos dentro da rede) simultaneamente em toda a grade;
reamostrar também os painéis de matching e treino, separadamente do teste.
Em cada réplica reajustar λ/φ com os mesmos critérios, regenerar o nulo com
números aleatórios comuns e retreinar a LDA. As internas reamostram a lei
empírica da respectiva externa, incluindo o novo matching. Assim o DP de cada
réplica inclui a incerteza do matching, e não apenas escores condicionais a φ.
Não reutilizar um IC de escores fixos como se incluísse essa incerteza.

Calcular `T_b=max_(a,r) |(AUC_b−AUC_hat)/SE_b|`; quantil 0,95, multiplicado pelo
SE externo de cada célula, produz banda bootstrap-t simultânea de 95% nas
81 células. A banda cobre tanto r quanto a, evitando selecionar a primeira
força com um IC pontual. Para a* inverter a banda: limite inferior é o primeiro
a em que a banda superior alcança o alvo; superior é o primeiro a em que a
banda inferior alcança o alvo. Usar censura quando não houver cruzamento,
sem extrapolar ou descartar réplicas sem fronteira. Isso continua válido para
a definição discreta sem assumir monotonicidade da curva.

**Uma regra de decisão, unilateral:** rejeitar `H0: AUC(a,r)<=0,70` somente onde
a banda inferior simultânea for >0,70. Não acrescentar gate de BA ou teste
bilateral de diferença contra 0,5. r=0,70 é a descrição primária; demais r e
alvos são reportados integralmente, sem escolher o mais favorável. A banda é
bilateral conservadora para permitir também a inversão da fronteira. Falha
numérica/pareamento em qualquer réplica impede o IC completo: reportar falha,
não remover seletivamente réplicas nem reduzir o domínio depois de olhar AUC.

Argumento de poder **de planejamento**, sem contrastes piloto: n efetivo=2.000
redes por classe, ICC dentro de rede até 1 e aproximação normal da AUC. Usar
limite conservador de variância do U-estatístico `1/(2n)` e componente adicional
independente de matching/treino com DP=0,01. Isso supõe painéis entre classes
independentes e matching/treino separado do teste. SE planejado = 0,01871.
Para 81 células, referência Bonferroni bilateral
`z_(1−0,05/(2×81))=3,4239`; meia largura = 0,0641. A banda bootstrap-t efetiva
não está garantida por essa aproximação; ela será calculada, sem truncar seu
valor crítico à referência.

Sob essas hipóteses, poder de superar 0,70 é **97,3% se AUC=0,80**, **22,6% se
AUC=0,75**; 80% requer aproximadamente AUC=0,7798. Com componente de nuisance
DP=0,02, SE sobe para 0,02550 e o poder cai. Isso não é poder de estimar a*
em unidades de a: sua precisão depende da inclinação desconhecida e da
resolução fixa da grade. Próximo ao alvo, intervalos grandes/censurados são
esperados e serão publicados. Não aumentar n conforme o resultado de teste.
O custo do bootstrap completo é risco de viabilidade a resolver antes do
congelamento, sem usar novos gates primários como diagnóstico de custo.

## Sementes, piloto e parada

Piloto único: namespace `ic-detection-boundary-v1-calibration`; hash SHA-256 dos
campos `namespace|fase|papel|indice`, primeiros oito bytes como inteiro. Fases
permitidas: match, train, check; papéis state, null-state, network, mask, error.
As três fases são disjuntas. 256 matching, 64 treinos/classe e 64 checks/classe,
em r=0,70, em toda G. Teto de dez minutos, incluindo matching. Todas as células
são pareadas antes de treinar o primeiro classificador. O runner não oferece
fase confirmatória, não grava curvas/escores nem exibe AUC; só o bit de
interioridade, estado da execução, contagens, hashes e ledger de sementes.
O teste interior não exige IC piloto nem implica poder confirmatório.

Arquivos pré-piloto: [spec.json](../../../../experiments/exploratory/detection-boundary-v1/spec.json)
e [runner](../../../../experiments/exploratory/detection-boundary-v1/run.py).
O manifesto vincula revisão Git, todos os módulos científicos, lock, este
protocolo e parâmetros. Saídas completas são imutáveis; não repetir com nova
grade, outra força ou mais sementes porque o bit não agradou.

Reserva futura apenas nominal: `ic-detection-boundary-v1-confirmatory`, fases
match/train/test/bootstrap e índices abaixo das contagens declaradas; seeds
por hash com os mesmos campos. Nenhuma trajetória ou seed confirmatória nova
é gerada nesta tarefa. As reservas antigas não serão usadas. Antes de liberar
um confirmatório, auditar colisões numéricas com todos os ledgers antigos e
novos, validar o callback científico do bootstrap completo e ratificar a
versão do protocolo. O motor genérico de bootstrap implementado exige esse
callback: seus testes de orquestração **não** demonstram cobertura inferencial.

Parar o piloto por teto de tempo, matching impossível, falha de canal ou bug;
registrar incompleto, sem concluir censura científica. Se o bit for falso, não
ajustar G pela discriminação; manter a condição registrada ou abandonar a
pretensão de fronteira interior. No confirmatório, completar a amostra fixa
ou registrar falha operacional. Fronteira não alcançada não é abandono nem
licença para promover um braço secundário. Ausência de separação é compatível
com equivalência observacional sob esta família, não prova de ausência de
interações reais.

## Sobreposições e contribuição delimitada

[Kiley e Vaisey (2020)](https://doi.org/10.1177/0003122420921538), p.487, já
expõem a indistinguibilidade entre atualização frequente e disposições com
muito erro. Aqui se quantifica uma fronteira finita para kernels e geometria
especificados, incluindo seu nulo traço+AR; não se apresenta a ambiguidade como
achado novo. [Lersch (2023)](https://doi.org/10.1177/00031224231156456) já usa
SHP/P$$P04 e simulações de painéis: o acréscimo pretendido é matching observado
estrito, família nula e fronteira ao longo de r, não uso do SHP ou de onze ondas.
[Moor-Smith e Carpentras (2026)](https://doi.org/10.1007/978-3-032-31712-4_30)
já avaliam modelos com nulos e ruído; aqui o erro é somente observacional e
há trajetórias individuais, com controles explícitos de escala. Esses limites
estão detalhados no [dossiê](reliability-and-prior-art.md).

A decisão 15 aponta [CoDiNG, arXiv:2406.19204](https://arxiv.org/abs/2406.19204)
como antecedente próximo; a leitura comparativa completa desse item e do
capítulo Carpentras–Quayle 2026 continua necessária antes de alegar contribuição
incremental suficiente. Não tomar a afirmação do coordenador de ausência de
erro somente observacional como conclusão bibliográfica verificada aqui.

## P4: portão de sobreposição e definição preservada

P4 não será executada nesta rodada. A pergunta ampla “grupos alteram limiares”
não basta para go: [Iacopini et al. (2022)](https://doi.org/10.1038/s42005-022-00845-y)
estudam grupos, minorias comprometidas e massa crítica no Naming Game.
[Muslim et al. (2024)](https://doi.org/10.1016/j.physa.2023.129358), com
[preprint dos autores](https://arxiv.org/abs/2305.06053), estudam mídia no q-voter,
limiar de mídia e probabilidades de saída. Fontes consultadas em 24/09: resumo
e texto indexado do primeiro, resumo dos autores e página editorial do segundo;
não se alega auditoria integral de suplementos.

Portão antes de qualquer promoção de P4: preencher comparação dos dois textos
com (i) trios realmente sobrepostos, (ii) pares projetados com exposição/grau
e orçamento iguais, (iii) dose externa contínua com receptores fixos, (iv)
Pr(travamento)=0,5 e log-razão pareada. **No-go** se a contribuição se resumir
a grupos + mídia + limiar, se o controle projetado não isolar a estrutura, ou
se a mesma comparação já for recuperável dos estudos. Go exigiria documentar
uma diferença quantitativa substantiva em todos os controles relevantes e
reproduzir o resultado sobreposto antes de estender; incerteza documental
mantém no-go, não ausência presumida de precedente.

Estado atual: **no-go/abandonada conforme decisão 15**. Os antecedentes extras
citados pelo coordenador não foram auditados aqui; a decisão de não prosseguir
não constitui conclusão nossa de equivalência entre todos esses artigos.
O protocolo residual, para rastreabilidade, mantém redes de 198 nós/132 trios,
100 passos e definição de travamento do rascunho anterior. Substitui D pela
quantidade `Δ=log(d50_grupos/d50_pares)`. Estimação de d50 por PAVA decrescente
e primeira interpolação em 0,5; nenhuma extrapolação. d50=0 ou fora da grade
censura Δ. Margem de equivalência pré-declarada `±log(1,20)` (razão entre
1/1,20 e 1,20), escolhida por relevância operacional de 20%, não por pilotos.
Se reativada por uma nova decisão, 500 redes × dois eventos e bootstrap pareado
por rede; IC90% inteiramente dentro da margem indicaria equivalência e IC95%
excluindo zero indicaria deslocamento. Poder de equivalência, condicionado a
Δ verdadeiro=0 e DP por rede=0,5, usa SE≈0,02236: a margem excede 8 SE;
se DP=2, SE≈0,08944, a probabilidade normal aproximada de equivalência cai para
31%. Nenhuma dessas suposições foi estimada de contrastes piloto. Nova ativação
exige justificar precisão e leitura integral; não herda sucesso do piloto antigo.

## Implementação e estado de pré-registro

Novos módulos: `models/detection_panel.py`, `analysis/detection_boundary.py`,
`simulation/detection_calibration.py`. Testes escritos antes da implementação
cobrem update manual em |g|=1 e repulsão, corr² contínua e marginais, momentos
estacionários dos nulos, canal heterocedástico/heaping, invariância a postos,
AUC com empates, estatística de matching, censura, bootstrap-t e log-razão.
NumPy já pertence apenas às dependências e lock do estudo desde o redesenho
anterior; nenhuma nova dependência e nenhuma edição em `workbench/`.

O desenho e o piloto estão especificados; o estudo **não está congelado**.
Antes do confirmatório faltam validação da cobertura e do callback completo de
bootstrap, estimativa cega do seu custo, comparação dos antecedentes pendentes
e revisão científica desta emenda. Não confundir qualidade de código com
cobertura estatística, confiabilidade empírica de P$$P04 ou aprovação científica.
