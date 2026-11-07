# Emenda sucessora v4.3 — fronteira de detecção

25/09/2026. Implementação para revisão independente, autorizada por Davi nesta
branch. Sem congelamento v4, execução de gate ou liberação confirmatória.
A [revisão independente](v4-review-findings.md) e as
[decisões vinculantes 1–10](v4-review-decisions.md), copiadas literalmente,
fundamentam esta v4.3, juntamente com o item operacional 11 solicitado por Davi.
As [decisões sobre a revisão delta](v4-delta-review-decisions.md), copiadas
literalmente, fixam as correções adicionais 1–8 e reproduzem o item 11.
As decisões prevalecem sobre a redação anterior nos pontos corrigidos.
A [revisão R1–R8](amendment-v4-1-revision.md), copiada literalmente,
corrige esta implementação antes de qualquer congelamento ou gate.
A [especificação D1–D11](amendment-v4-decision-spec.md) foi copiada literalmente;
sua frase histórica «pending Davi's ratification» permanece nos bytes originais.
O pedido desta sessão autoriza implementar, testar, calibrar critérios artificiais
e medir custo sem discriminação em a>0. Não autoriza ultrapassar esta revisão.

Esta emenda sucede o [protocolo v1](detection-boundary-preregistration-frozen.md)
de `fd65d2a`, SHA-256
`fb6b4dcf43161a52c725e565bf2a4d2697423bec7d138ad1d30388547cfcd706`.
Preserva os bytes do protocolo, runners, resultados e registro de congelamento.
A exceção histórica no módulo de painel é registrada abaixo; não se afirma
que todos os módulos permaneceram intocados desde o freeze v1.
A base da v4 foi `9fbff6e`; a v4.1 sucede `cda3a92`, a v4.2 sucede
`688ab26` e esta v4.3 sucede `9effe1c5`, na branch
`research/detection-boundary-v4`. A especificação original e os artefatos
concluídos da v4 permanecem imutáveis; as decisões 1–11 desta revisão
prevalecem sobre R1–R8 nos pontos corrigidos.
A motivação é o [gate v1 reprovado](detection-boundary-coverage-check.md), as
identidades em a=0 e as falhas de solver e orçamento discutidas na
[proposta A](amendment-proposal-a.md) e na
[crítica da síntese](amendment-critique-codex-on-synthesis.md). Nenhuma AUC
interior v4 foi usada para selecionar lei, algoritmo, tolerância ou inventário.

## Alterações, seção a seção, em relação à v1

### Autoridade, evidência e exposição — D8

Acrescenta-se este histórico ao da v1. Já eram expostos gates de BA em r=0,65
e 0,70, seleção antiga em r=0,80 e o bit de interioridade da fronteira sob
cb457af. Depois foram vistos AUC(0,30;0,70)=0,943912 sob a lei v1, condicionada
a um ajuste e treino; 26 AUCs de refits v1 em a=0, r=0,70, média 0,530; e,
sob a lei de A com aceitação frouxa, 40 refits em a=0,10, média 0,756070,
intervalo 0,7317–0,7897, mais um probe em a=0,03 com 0,589413. A proposta B
expôs quantidades de matching em a>0. Esta entrega acrescenta apenas resultados
artificiais dos critérios e quantidades/custos de matching v4, sem nova AUC
científica. G2/G2c ainda não executados; seus critérios, quando executados,
serão acrescentados à exposição cumulativa.

Esses números não determinam a*(0,70) sob v4. A grade não impõe monotonicidade
e mudaram a lei finita e o algoritmo. r=0,70 é exposto para calibração, e o
método global foi escolhido após exposição parcial. O artigo descreverá uma
avaliação em sementes novas de protocolo emendado após exposição parcial,
não confirmação inteiramente cega. A curva completa em R continua primária;
os oito r restantes não são promovidos a um novo primário. Preserva-se a
proveniência por r e a distinção entre contraste exploratório e resultado futuro.

### Pergunta e estimandos — D1

AUC(a,r) passa a ser explicitamente a esperança, sobre o sorteio de matching
(M=1.024) e treino (1.000 redes × dois eventos por classe), da AUC populacional
da LDA congelada contra o nulo ajustado. É alvo condicionado a ajustes que
passam a validação. Falha de ajuste é lacuna, nunca realização removida de
uma média favorável. Em G2, todas as falhas permanecem no denominador.

Permanecem R={0,50;0,55;0,60;0,65;0,70;0,75;0,80;0,85;0,90},
G={0;0,001;0,003;0,01;0,03;0,10;0,30;0,60;0,90}, alvo principal 0,70,
alvos secundários 0,60/0,80, fronteiras primeira e sustentada, inversão
inclusiva, censura e proibição de interpolação ou correção por monotonicidade.
Uma lacuna impede declarar fronteira através dela. A banda é calculada nas
forças disponíveis. A primeira fronteira e cada extremidade do seu intervalo
só são declaradas antes da primeira lacuna; a sustentada só é declarada acima
da última lacuna, com todas as forças superiores disponíveis. O restante é
censurado com «gap at a=…». `completo inválido` decorre apenas do gate a=0
da própria unidade, inclusive a=0 inviável ou sem matching. Uma falha da B
em qualquer r elegível desliga a validade da curva principal, sem apagar as
fronteiras das outras unidades, que continuam relatadas com a marca de
invalidação principal. Não muda a unidade painel,
a limitação da LDA nem a ausência de identificação causal.

### Painel e canal de observação — D2/D9

Permanecem N=10.626, onze ondas, entradas 7.084/3.542, retenção domiciliar 0,89,
duas pessoas por domicílio, máscara independente da opinião, transporte ordinal,
confiabilidade, sensitividades c=0,25/0,50 e δ=0,10/0,20 e combinação exploratória
c=0,50 com δ=0,20. A justificativa empírica e suas limitações não mudam.

### Viabilidade anterior à discriminação — D4/D7

Preserva-se a regra operacional de teto de L1 e sua adaptação para c/δ, inclusive
a qualificação de que o limite contínuo não é um teorema ordinal universal.
O ajuste verifica o teto antes de discriminar. Limites de família, bracket sem
raiz e falhas numéricas permanecem lacunas, sem certificado de impossibilidade.
G0 publica somente estados, contagens, resíduos em unidades de EP e validação;
a máscara é materializada antes de treinamento. G0 cobre oito grades, não todo
o inventário. As demais comparações validam seus próprios ajustes antes do treino.

### Mecanismos e significado de a — D2

O mecanismo social, b=0,25, oito permutações dirigidas, transporte normal por
postos, ρ=0,85, definição nominal de a e os cenários b=0 e ω permanecem.
O transporte otimizado de A é reutilizado com testes de igualdade byte a byte
contra o gerador congelado. As 24 etapas por onda permanecem uma sensibilidade,
com o mesmo número de transportes em alternativa e nulo.

ω=1 é degenerescência explícita: todas as ondas latentes repetem a inicial,
independentemente de a. Isso não dá identidade com B dentro de φ≤0,999. Não se
atribui anchor-exact a qualquer ω>0; o gate a=0 de cada corrida continua exigido.
O controle analítico linear e seus limites interpretativos permanecem.

### Família nula e matching — D2/D3/D4

Muda a lei finita de A, B e E. Seja Xφ a recursão a=0 da influência, transportada
em cada etapa. A é Xφ. Em B, T é normal iid, independente de Xφ, sem transporte
prévio de T; z_t=R_N(√λT+√(1−λ)x_t). Em E, s é Bernoulli(π) independente e
z_t=R_N(s x_0+(1−s)x_t). λ e π são pesos nominais pré-transporte. Retiram-se
as identidades de covariância gaussiana λ+(1−λ)φ^k e π+(1−π)φ^k. D mantém a
recursão de persistência dependente do estado; γ=0 é Xφ. C aplica à nova A o
erro heteroscedástico, heaping e marginal comum congelados; não se afirma
identidade para C. Os controles ordinais r=1 continuam desligando erro/heaping.

Em λ=π=γ=0 e φ=0,85, A/B/D/E coincidem pathwise com a influência a=0 nas
mesmas sementes. Os testes usam N completo, todos os canais principais e de
controle, c, δ e 24 etapas. As classes são independentes em treino, teste e
referência. R5 esclarece D3: estado, máscara e erro são acoplados no
matching e dentro dos pares novos da validação de matching. A validação
usa namespace e sorteios independentes do ajuste. O esclarecimento mantém
o comportamento já implementado; testes agora cobrem expressamente as
duas fases acopladas e as três fases com classes independentes. T/s usam
null-state; o estado x usa state, com índices distintos entre classes fora do
matching. Índices 2i+1 identificam os pares acoplados.

Substitui-se Newton conjunto pelo perfil: fixar η, resolver L1 em φ; depois
resolver L2 em η. Predição linear pela Jacobiana de diferenças finitas na âncora inicia a
busca e o bracket externo. Soluções internas provisórias usam tolerância
mais larga longe da raiz externa, com inclinação interna atualizada por
secantes locais, apertada à tolerância de aceitação antes
de qualquer sucesso. Antes de declarar derivada degenerada ou reversão do perfil, os L1
envolvidos são refinados para separar erro da solução interna da derivada.
O passo externo usa Illinois, com bisseção de salvaguarda.
O orçamento passa a 96 avaliações nulas realmente executadas por tentativa,
incluindo as avaliações da Jacobiana usadas pela busca. Avaliações
reutilizadas do cache não consomem o orçamento novamente. A/C e controles
resolvem somente L1; o segundo parâmetro do controle vem do observado no mesmo
refit. Nenhum passo projetado nulo é considerado convergência.

Em cada momento ajustado, a tolerância é
min(5e-5,max(1e-6,0,25 EP_fit)), conforme R2. O resíduo limita o viés
a 0,25 EP, pois a variância centrada de D5 não carrega esse viés. O termo
quadrático é exatamente 0,25² = 6,25% da variância amostral do ajuste.
Mantém-se ao menos um passo real para o rótulo interior, exceto anchor-exact. A identidade exige igualdade de todos os
pares, não cancelamento da média. Na face η=0, reavalia-se o perfil em η=0,01
para verificar direção local não decrescente e a condição de fronteira; L1 tem
prioridade. O perfil é verificado em todos os pontos avaliados. Uma derivada
não positiva ou singular é falha, nunca um ajuste artificialmente aceito.

Estados aceitos: anchor-exact, interior e boundary. Demais estados:
no-L1-root, non-monotone-profile, ill-conditioned, numerical-limit,
family-limit-lower/upper e budget. Um endpoint aceito sem passo real recebe boundary, nunca interior.
Um endpoint atingido após passo real pode satisfazer as equações como interior;
boundary também designa a solução restrita na face inferior de η. São estados do
estimador, não inferências científicas de não-atingimento.

R1 corrige um erro da especificação: cada ajuste bem sucedido é validado
em 2.048 pares novos, exigindo |res_k|≤4√(EP_fit,k²+EP_val,k²) em todo
momento ajustado, inclusive L2 de B/D/E na face. EP_fit é calculado nos
pares de ajuste em θ̂; EP_val permanece separado para equivalência.
A regra antiga ignorava a incerteza de θ̂ e reprovava cerca de 14% dos
ajustes corretos em duas dimensões. A regressão sintética reproduz essa
falha e verifica a correção. Em falha, há uma única tentativa adicional
de matching com M=4.096, orçamento próprio de 96 avaliações e outra validação
nova com 2.048 pares. A relação EP_val/EP_fit≈0,71 vale na tentativa M=1.024;
no retry M=4.096 é ≈1,41. A forma com variância combinada vale em ambas.
Preservam-se as duas tentativas. Falha de solver não ganha
reinícios oportunistas. O segundo fracasso deixa lacuna.

Relatam-se também |res|+2,2414 EP contra 0,0003 e amplificação local: corrigir
linearmente o erro de matching pela Jacobiana e medir a distância de Mahalanobis
do deslocamento induzido em L3–L5. É o diagnóstico de amplificação de B,
recalculado sob v4, sem conversão para AUC. Seus stencils de matching em 0,01
são contabilizados à parte da busca de raízes e reutilizados em D5; âncora
exata tem amplificação zero. Singularidade deixa diagnóstico indisponível,
não produz aprovação.

### Discriminador e interpretação dos canais — D5/D9

Permanecem LDA, padronização no treino, covariância 0,8S+0,2I, L3–L5, orientação
dos escores, meio crédito para empates, canais latente/ordinal r=1/latent_rank,
e mobilidade separada. Controles mantêm a incerteza do η observado em cada
draw, além de reajustarem φ. Não se interpreta ruído como criação de informação.
A interpretação entre mecanismos depende de grades completas e válidas dos
nulos pertinentes; tier 1 sozinho compara apenas contra B.

### Inferência viável e validade — D5/D6

Substituem-se 40 refits por 2.000 draws locais. Reamostram-se diferenças
de matching sem centralizar (`data.differences[indices].mean(0)`),
preservando o resíduo ajustado e a regra de fronteira. Resolve-se Δθ pela Jacobiana e projeta-se no box. Na projeção de η, L1 é
re-resolvido em φ, preservando a prioridade do perfil. Nos controles, o η de
cada draw é o do observado correspondente. R3 substitui o drift por realização pelo deslocamento comum D·Δθ_b
nos atributos nulos de treino e referência. D é a Jacobiana da média de
L3–L5, estimada por diferenças finitas CRN nas realizações do matching.
O passo é 0,01, com sentido para dentro junto à face superior. G2 repete D5
em 0,005, sem escolher passo pelo resultado. Não há stencils de treino ou
referência no caminho dos tiers; o helper por realização fica apenas como
operação numérica genérica e contraponto diagnóstico histórico.

Somente G2 estima também a Jacobiana de covariância de treino e referência
nulos nos dois passos. Relata a correção de primeira ordem nos coeficientes
da LDA em escala original, incluindo padronização e shrinkage, e na AUC
gaussiana por momentos. Essa última é uma aproximação diagnóstica explícita:
covariância não determina a AUC empírica de postos. O máximo absoluto da
correção de AUC entre os 2.000 draws é comparado a 10% de √V_nuis; o excesso
gera uma flag, sem modificar os critérios calibrados. Os vetores completos
ficam selados. G2/G2c decidem adequação por dispersão real e refits.

D11 agora testa o deslocamento da média no nível vetorial contra regeneração
no ponto fixo φ=0,85, η=0,15, Δ=(0,001;−0,001), FD=0,01, 64 realizações
de matching em N completo. O denominador é a norma do próprio deslocamento
regenerado; não a norma do vetor de atributos. O teste exige erro inferior
a 5%, sem exigir acurácia por realização: o erro medido foi 2,0371%.
O anchor preserva Δθ≡0. A regressão R1 observou 411/3.000 falsas falhas
(13,7%) na regra antiga e 0/3.000 na nova, sem afirmar probabilidade zero.

Em cada draw, redes de treino são reamostradas separadamente por classe,
levando os dois eventos juntos; a LDA congelada é reestimada e avaliada na
referência fixa. Reamostragem de matching e das duas classes de treino usa
substreams distintos. Mesmo quando uma célula usou o retry, os índices de
redes de treino continuam alinhados entre forças. Uniformes comuns de até
4.096 posições definem os índices de matching nos dois tamanhos.

V_nuis é a variância centrada das AUCs locais, sem divisão por 2.000. Reportam-se
deslocamento médio, MCSE pela quarta potência e fração de projeções. Anchor-exact
recebe Δθ=0 e V_nuis=0 analiticamente, não a variância de uma referência finita.
Não se reutiliza a API congelada de 30–50 refits.

Permanecem 2.000 bootstraps de redes sobre escores fixos, referência de
2.000 redes × dois eventos por classe, SE_total²=SE_scores²+V_nuis, studentização
logit, piso 1/(2n), crítico max(max-t empírico;2,7729), inversão inclusiva e
fronteira sustentada. Os mesmos desvios locais centrados são adicionados nas
forças alinhadas; não são sorteados novamente como 40 refits. Reporta-se quando
o crítico empírico supera o piso. O gate individual a=0 e todas as invalidações
v1 permanecem. Bandas continuam por r, não simultâneas sobre os 81 pontos.

### Poder para resolução da fronteira e custo — D9

O alvo de precisão e a natureza hipotética do cálculo de poder v1 permanecem.
As contas antigas não são evidência de tempo da implementação nova. A entrega
mede a lei v4 e a busca de perfil sem treinar classificador em a>0. A
[projeção](../../../../experiments/exploratory/detection-boundary-v4/compute-projection-v42.json)
decompõe painel social/nulo, matching, validação, stencils, bootstrap e retries,
com oito workers e 25% de reserva. Seu cenário empírico usa quatro blocos em cada uma das seis células adicionais
B especificadas no item 11. A medição v4.1 de oito blocos em três células
permanece histórica; suas avaliações não são atribuídas ao solver novo.
Nenhuma dessas amostras estima a taxa de todo o inventário.

A janela fecha em 18/10/2026 às 23:59 America/Sao_Paulo,
`2026-10-19T02:59:00Z`. Substitui-se a regra v1 de parar e emendar por
inviabilidade pela execução ordenada dos tiers dentro dessa janela. Não se
muda ordem, amostra ou recursos por AUC, largura ou invalidade. Shards adicionais
exigem mesmo código e equivalência numérica. No fechamento, trabalho incompleto
é interrompido e preservado, sem completar apenas unidades favoráveis.

O [inventário máquina-legível](../../../../experiments/exploratory/detection-boundary-v4/inventory.json)
contém 46 grades de 81 células: B principal; A/C/D/E; três controles × cinco
nulos; mobilidade em três canais × cinco nulos; cinco cenários observacionais;
b=0 e quatro ω; 24 etapas. São 3.726 linhas e 414 unidades comparação/r de
nove forças. A mobilidade já prevista é explicitada em todos os nulos/canais
aplicáveis; não cria um novo alvo primário. Não se desconta computação por
reuso de painéis entre tarefas que o runner não demonstra.

Os seis tiers seguem D9. Cada unidade recebe «não iniciado», «parcial por
encerramento operacional», «completo inválido» ou «completo válido», preservando
tentativas. Só unidades previstas completas são apresentadas como resultados,
com inventário e ausências integrais. O executor existe antes do freeze: empilha escores (2.000,2,9) e desvios
nuisance (2.000,9) por unidade/r, aplica a banda, as lacunas, o gate a=0 e
as invalidações v1. A ordem é fixa, com barreira entre tiers, manifests de
shards e checkpoints retomáveis. Controles reutilizam parâmetros e deslocamentos η do observado
correspondente; não reexecutam seu pipeline. O bootstrap de escores ocorre
uma vez por curva, após o empilhamento. O fechamento interrompe trabalho incompleto
e publica o inventário inteiro. O runner exige freeze e gates aprovados;
nada foi executado, portanto todas as linhas permanecem «não iniciado».

### Sementes, execução e gate de cobertura — D7/D10

Substitui-se o namespace v3 de execução pela família v4 de calibração. O
material continua namespace|bloco|fase|papel|índice, SHA-256, oito bytes iniciais
big-endian. G0 usa ic-detection-boundary-v4-calibration; as repetições reais de
gate usam ic-detection-boundary-v4-gate-rNNNN-calibration. Nuisance, bootstrap,
validation e stencil têm namespaces v4 próprios terminados em calibration.
A reserva v3-confirmatory é aposentada; v4-confirmatory, nuisance-confirmatory,
bootstrap-confirmatory, validation-confirmatory e stencil-confirmatory são
implementados no plano separado do runner, sem alias com calibração.
O comando confirmatório exige preflight e todos os gates aprovados; os testes
verificam isolamento e alinhamento com dados artificiais, sem executar a curva.

Em namespaces compartilhados por propósito, o bloco codifica domínio de gate,
repetição, célula e tentativa sem aliases; repetição e subbloco são limitados
a 0…9.999 e tentativa a 0/1. G0 mantém CRN entre forças/r. Células de G2 são
independentes entre si, e as cem repetições independentes são agrupadas em
cinquenta pares disjuntos. Dentro de uma futura curva/r, os seeds de bootstrap
e nuisance são compartilhados entre forças. Stencils numéricos reutilizam
os streams da fase base para preservar CRN; o namespace stencil identifica a
operação, não uma inovação independente que destruiria a diferença finita.
Manifestos por fase vinculam código, ambiente, host e material de sementes.

R6 define dois vínculos. Antes do gate, o primeiro registro congelará
emenda, especificação D1–D11, revisão literal, achados e os dois arquivos de
decisões, código, inventário, critérios, regras de alocação,
sementes, ambiente e sonda numérica entre hosts. Ele declarará explicitamente
o vínculo posterior. Depois de G0 e antes de G2, um segundo registro
vinculará por SHA-256 o primeiro registro, a projeção de G0 contendo somente
estados, a lista concreta G2 e os critérios, incluindo eventual recalibração.
Também vincula a contagem de lacunas dos 54 ajustes B/observado de G0 nas
forças usadas por G2 (0 < a ≤ 0,30; nove valores de r). A taxa de falha técnica
por pipeline recebe priori de Jeffreys Beta(0,5; 0,5). Uma simulação
beta-binomial com semente fixa estima a probabilidade preditiva de cumprir,
conjuntamente, até 5/100 falhas por célula G2, até ceil(0,02 × pipelines)
no conjunto G2 e as cotas G2c de 3/100 e 2/40 refits. O segundo registro
guarda a contagem, os parâmetros posteriores, a semente, o número de simulações
e a probabilidade. Se esta for inferior a 0,80, a execução para antes de G2.
Esta regra evita gasto quando as falhas técnicas previstas inviabilizam o gate;
os critérios do próprio gate decidem a validade científica. Esta
entrega deliberadamente não cria esse registro. Os runners exigem o registro
já existente, vinculam oito shards locais a oito workers, usam BLAS de uma thread, checkpoints por
32 painéis e partição determinística por índice. Retomada não repete falhas
concluídas. Mudança de critério não permite rerodar um estágio até passar.

G0 exige identidades em a=0, nenhum budget e no máximo 1% de estados de
implementação. G1a são os testes de identidade e nuisance zero. G1b usa cinco
cenários de escores sintéticos com 2.000 redes × dois eventos/classe, nove
slots e 1.000 repetições por cenário: ICC 0, ICC 0,5, não gaussianidade,
empates e dependência entre slots. Exige 935 coberturas conjuntas por cenário.
Logo, são 5.000 repetições, não as 2.000 da conta preliminar da crítica.

G1c mantém 50 pipelines reais por r em {0,50;0,70;0,90}; todos anchor-exact,
no máximo três falhas pontuais em 150 no crítico 2,7729, média global a até
três EP de 0,5 e taxa de empates publicada. G2 mantém as sete células D7,
100 pipelines por célula, pares disjuntos, razão de variâncias de diferenças
logit e EPs logit somados. LOO e caudas em 0,00556 são diagnósticos, não
repetições independentes. O teste FD exige que a mediana por célula das razões V_nuis(0,005)/V_nuis(0,01)
esteja em [0,8;1,25]. O agregado é único por célula, calculado nos sucessos.
G2c mantém 100 refits em (0,10;0,70) e 40 em (0,03;0,70), com matching,
validação e treino novos; a referência nula é regenerada em θ_refit com
as sementes do baseline (`replace(seeds, repetition=0)`), usando números
aleatórios comuns. A referência social também usa as sementes fixas por célula. Dois baselines D5 adicionais fornecem os denominadores de comparação.

Todas as falhas técnicas permanecem nos denominadores planejados. G2 aceita
até 5 falhas por 100 por célula e até ⌈0,02 × pipelines G2 efetivamente
executados⌉ no agregado (14 quando são sete células e 700 pipelines). Pares com
qualquer falha são excluídos somente da razão de dispersões, com contagem
explícita; os pares restantes continuam disjuntos. G2c aceita até 3/100
e 2/40 falhas nos refits. G1c permanece exigindo todos anchor-exact. G2 não demonstra cobertura interior
absoluta. Se G0 tornar uma célula indisponível, tenta-se o próximo r elegível
rumo a 0,70 sem duplicar a mesma célula já alocada. Se não existir, a redução
obriga recalibração artificial antes de G2. A regra é prévia; a lista concreta
só pode ser materializada após G0. O segundo vínculo é criado antes de G2, reutilizando G0 pelo mesmo hash
de código. O primeiro registro nunca é reescrito. G2c exige o mesmo segundo
vínculo usado por G2; retomadas recusam mudanças de critério ou alocação. Não se
seleciona uma substituição pelos resultados G2.

### Antecedentes e contribuição delimitada

Nenhuma reivindicação de prioridade ou conclusão bibliográfica muda. Permanecem
as limitações de Manski, Shalizi–Thomas, Gestefeld–Lorenz, dos controles
observacionais e da comparação operacional por LDA. Os diagnósticos v4 e a
calibração artificial não são dados empíricos de P$$P04 nem validação causal.

## Calibração artificial dos critérios

O [registro verificado](../../../../experiments/exploratory/detection-boundary-v4/criteria-v43.json)
separa 3.000 experimentos de desenvolvimento de 3.000 de verificação, com
seeds distintos. Usa logit, sete células independentes, cem pipelines por
célula, cinquenta pares, dependência LOO, t com 5,2 graus de liberdade
(curtose ordinária 8), 2.000 draws locais e os denominadores 100/40 de G2c.
Cada intervalo usa 399 reamostragens: pares inteiros em G2; draws e refits
separadamente em G2c. A calibração não chama o simulador nem um discriminador.
Após as 48 medições reais de matching/validação, a calibração foi executada
novamente em arquivo novo. A v4.3 usa sete células e incorpora a cota agregada
escalável; o registro preserva a v4.2 por hash.

Os limiares G2 são aplicados aos limites bootstrap de 95%, por célula e
agregados: reprova se o limite superior for menor que o limiar inferior ou o
limite inferior maior que o limiar superior. Os valores não são limites de
aceitação diretos para a razão pontual. G2c usa os limites unilaterais de 95%
e os cortes 0,8 e 2,0 exigidos por D7. Os valores numéricos, probabilidades,
contagens e MCSEs estão no registro, juntamente com hashes do script e módulo.
R4 aceita explicitamente que G2c isolado não satisfaz a característica
operacional; G2 e G2+G2c satisfazem. Mantêm-se cortes 0,8/2,0 e 100/40 refits.
A recalibração v4.2 injeta falhas técnicas independentes a 1% e inclui o
agregado FD por célula. A distribuição de razões FD e as condições do modelo
ficam explícitas no registro sucessor; elas não garantem estabilidade FD real.
A meta é P(aprovado | EP correto, falhas 1%)≥0,95 e
P(aprovado | EP×0,8)≤0,20. G2 sozinho deve atender à meta de detectar
subestimação; G2c é uma checagem complementar de V_nuis.
A calibração v4 anterior permanece preservada, com sua hipótese histórica
de zero falhas; não representa as características operacionais desta revisão.

Os limiares recalibrados continuam 0.4976013738/1.2879137798
por célula e 0.8183809739/1.0545065407 no agregado.
Aplicam-se aos extremos dos intervalos bootstrap, não diretamente à razão pontual.

| EP artificial | G2 | G2c | G2+G2c | MCSE conjunta |
| --- | ---: | ---: | ---: | ---: |
| Correto | 2959/3.000 (98.6333%) | 2895/3.000 (96.5000%) | 2855/3.000 (95.1667%) | 0.3916 pp |
| ×0,8 | 130/3.000 (4.3333%) | 2166/3.000 (72.2000%) | 97/3.000 (3.2333%) | 0.3229 pp |
| ×1,4 | 39/3.000 (1.3000%) | 2042/3.000 (68.0667%) | 28/3.000 (0.9333%) | 0.1756 pp |

As probabilidades pontuais atendem às metas no modelo declarado. A estimativa
conjunta correta (95,1667%) fica perto de 95%; seu erro Monte Carlo é
0,3916 ponto percentual, portanto não constitui prova de que a probabilidade
verdadeira esteja acima de 95%. G2 sozinho atende à meta de discriminação.
G2c permanece complementar e condicionado à disponibilidade dos draws do
baseline; falha real desse baseline ainda bloqueia o estágio. O modelo injeta
falhas nos 700 pipelines G2 e nos 100/40 refits G2c, independentes dos dados;
não afirma ter modelado falhas adicionais dos dois baselines.

A razão FD individual é lognormal com log-média zero e log-DP 0,25,
agregada pela mediana por célula. O agregado passou em 3.000/3.000
experimentos de verificação, embora razões individuais possam sair da faixa.
A auditoria R6 usa os 54 ajustes B/observado de G0 nas forças de G2 e
predição beta-binomial conjunta das cotas G2 e G2c. A simulação fixa
200.000 amostras e a semente 250925006. Probabilidade inferior a 0,80
documenta a parada antes de G2 no segundo registro; a predição é somente
uma regra de economia, sem alterar os critérios de aceitação.

## Medições e projeção atualizada

As medições v4.1 estão em
[panel-cost-v41.json](../../../../experiments/exploratory/detection-boundary-v4/panel-cost-v41.json)
e [cost-fits-v41.json](../../../../experiments/exploratory/detection-boundary-v4/cost-fits-v41.json).
São sucessores dos registros v4 preservados. Usam N completo, oito processos,
BLAS de uma thread e namespaces de calibração. Nenhum treino ou AUC em a>0.
R7 extrai somente o canal e os resumos usados pela unidade; testes contra o
caminho congelado verificam igualdade byte a byte em A–E, todos os canais
e mobilidades declarados. Nos controles, erro/heaping não utilizados deixam
de ser calculados. Tempos CPU, soma de parede dos workers e parede do
coordenador permanecem separados.

CPU-s por painel (social/nulo), 64 painéis por operação:

| Canal e resumo | A | B | C | D | E |
| --- | ---: | ---: | ---: | ---: | ---: |
| observed / lags | 0.020668/0.014851 | 0.019400/0.021595 | 0.020313/0.017319 | 0.021106/0.016444 | 0.021055/0.022690 |
| latent / lags | 0.014493/0.010305 | 0.014665/0.016937 | 0.015364/0.010595 | 0.015135/0.011065 | 0.015435/0.017312 |
| ordinal_one / lags | 0.018965/0.014531 | 0.018663/0.020832 | 0.020142/0.015071 | 0.020591/0.015218 | 0.019157/0.021472 |
| latent_rank / lags | 0.019474/0.014219 | 0.020338/0.022434 | 0.019432/0.014757 | 0.019639/0.015715 | 0.019625/0.021696 |
| observed / mobility | 0.022446/0.017738 | 0.022621/0.024891 | 0.024376/0.021116 | 0.023643/0.018795 | 0.023086/0.025233 |
| latent / mobility | 0.019356/0.014524 | 0.019411/0.022008 | 0.020245/0.015075 | 0.021106/0.016052 | 0.019362/0.021865 |
| ordinal_one / mobility | 0.022705/0.017477 | 0.022000/0.024675 | 0.022447/0.017971 | 0.022632/0.018094 | 0.022126/0.024266 |

Outras operações (CPU-s/painel): anchor-social=0.015128; c050=0.020313; delta020=0.021536; omega100=0.019647; steps24-social=0.275961; steps24-null=0.182920.

Os registros v4.1 preservam 24 fits B em r=0,70: médias 23,625, 30,625 e
57,750 avaliações em a=0,003/0,03/0,30, sem retries observados. Essa evidência
motivou a extensão operacional do item 11; não é medição do solver otimizado.
O retry não observado passa a ser projetado conservadoramente com 96
avaliações por tentativa. Não se infere taxa zero de retry no inventário.

Os registros [antes](../../../../experiments/exploratory/detection-boundary-v4/cost-fits-v42-before.json)
e [depois](../../../../experiments/exploratory/detection-boundary-v4/cost-fits-v42-after.json)
contêm quatro blocos pareados (0–3) por célula, N=10.626 e
`SeedPlan(9001, bloco)`. Antes: fonte isolada de `688ab26`, orçamento 64;
depois: fonte otimizada, orçamento 96. Ambos executaram somente matching e
validação, sem treino ou AUC. A ordem das contagens abaixo é a dos blocos 0–3;
ela inclui fits que falharam.

| a | r | Avaliações antes | Avaliações depois | Validados antes → depois |
| ---: | ---: | --- | --- | ---: |
| 0,6 | 0,7 | 46, 48, 45, 46 | 42, 35, 34, 28 | 4/4 → 4/4 |
| 0,9 | 0,7 | 48, 48, 48, 48 | 13, 32, 36, 33 | 4/4 → 3/4 |
| 0,03 | 0,5 | 29, 26, 27, 25 | 15, 16, 14, 10 | 4/4 → 4/4 |
| 0,3 | 0,5 | 52, 8, 52, 44 | 24, 15, 27, 23 | 3/4 → 3/4 |
| 0,03 | 0,9 | 30, 30, 32, 32 | 8, 14, 13, 13 | 4/4 → 4/4 |
| 0,3 | 0,9 | 64, 64, 64, 64 | 19, 21, 26, 27 | 0/4 → 4/4 |

Antes, 19/24 fits foram validados: quatro lacunas `budget` em (0,30;0,90)
e uma `non-monotone-profile` no bloco 1 de (0,30;0,50). Depois, 22/24 foram
validados: permanece a lacuna de perfil nesse bloco e há uma `ill-conditioned`
no bloco 0 de (0,90;0,70). Essa célula perde uma validação em relação ao
baseline; a otimização não é apresentada como melhoria uniforme. Nenhuma
lacuna foi aceita por tolerância mais frouxa. Não houve retry nas duas amostras.
O máximo depois foi 42/96 avaliações. Os quatro budgets antigos passaram a
fits validados, com 19, 21, 26 e 27 avaliações.

Nos 18 pares que validaram nas duas versões, a média caiu de 39,3333 para
23,1667 avaliações (41,10%). Seis pares ficam fora apenas dessa comparação
condicional; continuam no denominador de 24 e no relato de falhas.
A média depois sobre todos os planejados é 22,4167; sobre os 22 validados,
23,1818. A projeção usa a maior delas, 23,1818, para impedir que falhas
precoces barateiem artificialmente o trabalho bem sucedido. O retry não
observado usa seu orçamento integral de 96 avaliações com M=4.096.

O [verificador de proveniência](../../../../experiments/exploratory/detection-boundary-v4/revision-verification-v42.json)
vincula as fontes efetivamente executadas, inclui snapshots reproduzíveis,
confere o baseline contra `688ab26`, as rotinas de matching contra a fonte
final, resíduos e tolerâncias, validação, auditoria de sementes e cópias literais.
Todos os sucessos satisfazem os mesmos critérios de matching e validação.
As execuções se sobrepuseram parcialmente no mesmo host; parede observada
não é uma medição isolada de speedup. Tempos CPU e parede permanecem separados.

Projeção em horas, oito workers dedicados e 25% de reserva:

| Fração hipotética de retry | Gate | Tiers 1–5 | Tier 6 | Bootstrap dos tiers | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0% observado na amostra | 75,51 | 145,71 | 34,53 | 0,28 | 256,04 |
| 25% | 206,61 | 425,21 | 93,51 | 0,28 | 725,61 |
| 100% | 599,90 | 1263,71 | 270,45 | 0,28 | 2134,34 |

O cenário com retry observado é condicional à pequena amostra, não uma
estimativa de zero retries ou da prevalência de lacunas no inventário.
A projeção não autoriza execução nem garante conclusão na janela. Mantém as
3.726 células, 414 unidades e todos os tiers; nenhum trabalho é retirado em
função desses resultados de matching.

A projeção preserva todos os seis tiers e explicita a extrapolação dos fits B
para as demais famílias/canais. Os preços por painel acima permanecem
medições históricas do mesmo gerador; a nova medição separa CPU e parede,
sem atribuir interferência de outros processos ao algoritmo. Ambos os
referenciais G2c são regenerados com sementes fixas por tarefa e cobrados;
CRN não significa cache compartilhado. A reserva de 25% para D5/LDA, I/O,
hashes e escalonamento permanece hipótese. Se a janela exigir outros hosts,
o coordenador usa oito shards locais, limitados a oito workers, com mesmo código e equivalência numérica,
sem reduzir tiers nem selecionar unidades por resultados.

## Selamento e limites operacionais

G2/G2c guardam estimativas, verdades disponíveis e EPs em JSONL fora de qualquer
checkout, sob `~/.local/state/research-workbench/sealed-v4-gate/`, diretórios
0700 e arquivos 0600. AUC em a>0 tem verdade populacional desconhecida; não se
inventa «truth» a partir da média dos pipelines. G1c registra truth=0,5.
Há SHA-256, validação de integridade nas leituras e log de acesso da API.
Stdout e relatórios públicos recebem somente critérios, contagens, razões,
MCSEs e aprovação/reprovação; exceções científicas ficam no armazenamento
privado, sem traceback público.

G2 mantém `mean_shift` em unidades de AUC somente no registro selado; stdout
contém razões e critérios. Resultados confirmatórios ficam selados até o
fechamento; o runner recusa liberação anterior e só libera unidades completas
acompanhadas do inventário e das invalidações. Isso não libera os registros
privados de G2/G2c. Erros de I/O, falta de memória, divergência na retomada e
interrupções suspendem a execução e permitem retomada; não se tornam lacunas
permanentes. Somente os estados científicos e numéricos declarados contam como
lacunas. 0700 não impede leitura direta por outro
processo do mesmo UID e o log da API não audita essas leituras: isolamento
forte exigiria outra conta/processo de confiança, fora da autorização desta
implementação. Essa limitação não é ocultada como garantia criptográfica.

## Registro da alteração posterior ao freeze v1 — decisão 10

`detection_panel.py` foi editado em
`d33bf4e4a485797f04775979618e25ba5f8b2ba9` depois do freeze v1.
O SHA-256 passou de
`a9d294e3a5c4ed77eeca234e172e763814627ea21c38381ddc0181cab48a513a` para
`aee847707ca82acb4004e4c6288634ac294c2582da097a9183e80b698ca40be1`.
A otimização evita permutações de rede e deriva social não utilizadas quando
a=0, preservando sorteios e a recursão de estado. A execução direta das
versões pai, commit e atual produziu bytes idênticos em onze ondas,
b=0,25, sementes de matching de calibração, N=600 e N=10.626.
Os hashes de saída foram, respectivamente,
`4df3049105b63e6d546e64af471d8b381fdb43fc76877ec57fb853623ba2aca5` e
`0bd67064acd8f37153373d67f69952f7f6ebd9f6cbeac05048761112e3900602`.
Isso documenta a exceção a D11; igualdade de saída não equivale a ausência
de edição do arquivo congelado.

## Limitações e verificação

A identidade em N=10.626 é testada byte a byte para máscara, valores medidos,
observados e atributos selecionados, em A/B/D/E, matching e validação,
nas duas tentativas, nos canais principal/mobilidade e nas sensitividades
c=0,25/0,50, δ=0,10/0,20, combinação c=0,50/δ=0,20 e 24 etapas.
Os controles `latent`, `ordinal_one` e `latent_rank`, além dos controles de
mobilidade disponíveis, também têm testes de identidade byte a byte em a=0,
N completo, matching e validação, nas duas tentativas.

Um verificador finito não prova monotonicidade em pontos nunca avaliados.
Mantêm-se a rejeição de reversões observadas e de derivada local degenerada.
E6 e bloco 7 de A continuam regressões por mapas numéricos declarados,
não replay integral dos painéis históricos. A propagação confirmatória usa
deslocamento médio; o diagnóstico de covariância gaussiana não substitui
a comparação empírica de G2/G2c.

Os testes do solver verificam o mesmo teto de resíduo, tolerância, validação
independente e regras de fronteira após predição, soluções internas inexatas
e Illinois. O orçamento de 96 é operacional: os 49–63 passos medidos em
a=0,30 deixavam pouca margem no limite 64 e poderiam gerar lacunas em
a=0,60/0,90. Não se altera a regra de retry por falha de validação,
nem se converte falha numérica em sucesso.

O registro sucessor de auditoria de sementes inclui G1b/G1c/G2c, stencil,
nuisance, bootstrap e validação, além dos planos anteriores. A validação
de engenharia e seus resultados finais ficam no README da execução;
não equivalem a freeze, execução do gate ou aprovação científica.
