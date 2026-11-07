# Crítica da síntese da emenda sucessora — Codex

25/09/2026. Parecer sobre Q1–Q4, não adoção nem liberação de execução.
**Veredito: adotar com as mudanças listadas ao final.** A direção de transporte
compartilhado e matching acoplado é defensável; a síntese atual ainda não é uma
especificação inferencial validada. S4, S6 e S8 precisam de correções substantivas.

Foram lidos a [proposta A](amendment-proposal-a.md), seu
[pacote de evidência](../../../../experiments/exploratory/amendment-a-calibration/README.md),
o [relatório do gate falho](detection-boundary-coverage-check.md), o
[pré-registro](detection-boundary-preregistration-frozen.md), o código
`src/ic_study/simulation/amendment_a.py` do estudo e o histórico até `038a6f3`,
incluindo as alterações iniciadas em `3bc4765`. A árvore estava limpa no início.
Não executei geradores, treino, refits nem qualquer nova AUC em a>0. Os cálculos
novos abaixo são apenas contagem de operações e álgebra de variância.

As fontes privadas de B e da síntese estão sob
`/private/tmp/claude-501/-Users-davi-Documents-github-research-workbench/ccea0cfa-cbfe-40e0-a2a0-91e611807839/scratchpad/`.
Identidades dos arquivos efetivamente examinados:

| Artefato | SHA-256 |
| --- | --- |
| `amendment-synthesis-draft.md` | `2ffabc4a694ce95e7bb88df505f6d3e72f690ffe8752727afa9e6b77332e529d` |
| `amendment-b/amendment-proposal-b.md` | `d5fc17492633158bc542d4a9a2a47c77f6aa73621836be526452014bf80c5bfa` |
| `amendment-b/e11_profile.py` | `1f2ffdadfb4efe46c1b176c09d704f6d343542a288593d4b4e0a7698f2eca668` |
| `amendment-b/manifest.sha256` | `e9288837f0c663bd9c338536a20ce4d43470366808c4ca1fb05da973abd742e7` |
| Pré-registro congelado | `fb6b4dcf43161a52c725e565bf2a4d2697423bec7d138ad1d30388547cfcd706` |

Os 21 arquivos listados no manifesto de B conferem. Os resultados E6/E11 foram
lidos, não reexecutados. A síntese e o texto de B têm hashes próprios acima.

## Q1 — O que manter e o que corrigir

### S1–S3: a direção é boa, mas as leis e o alvo precisam ser exatos

Aceito explicitar o alvo como `E_matching,treino[AUC_populacional]`. A quadratura
entre erro de teste e variabilidade do procedimento é coerente com esse alvo.
Não é, porém, uma prova de que o texto anterior só admitia essa interpretação.
O acoplamento altera a distribuição do matching finito, e o novo gerador altera
a lei nula: preserva-se a forma do funcional, não seu valor ou todo o procedimento.
Definir também o alvo quando há falha de matching. Fazer média somente dos
sucessos cria um alvo condicionado ao sucesso; omitir esse condicionamento
seria uma mudança silenciosa.

Há uma diferença concreta entre A e B que S2 chama indevidamente de convergência:
em A, `T` é normal iid; em `common.py` de B, `T=R_N(tau)`. Em N finito, a segunda
opção introduz a restrição transversal do grid no traço. Ambas dão a identidade
em lambda=0, mas não são a mesma lei quando lambda>0. Recomendo o traço normal
iid de A, mais próximo da definição congelada, e a recursão transportada comum.
É necessário testar novamente o solver/LNB dessa lei: E11 não valida diretamente
essa combinação. Também registrar explicitamente as mudanças em A, C e E;
a identidade gaussiana de covariância deixa de ser exata. D já tem transporte.

O uso de CRN somente no matching é apropriado. Treino, teste e referência
precisam manter classes independentes, fases disjuntas e os clusters de rede.
A igualdade em a=0 deve ser demonstrada no canal e na resolução efetivamente
usados, não extrapolada a C ou às ancoragens. AUC amostral continua aleatória.

### S6: prefiro o solver por perfil, com salvaguardas e aceitação independente

O perfil é uma boa alternativa ao Newton com clipping, mas a justificativa de
S6 mistura **dois algoritmos diferentes**. O resultado 0% contra 43,5% de falhas
em E6 vem de `v4`, um Gauss–Newton com conjunto ativo e regra de borda; não do
perfil de E11. E11 fornece três sucessos interiores, com 6, 7 e 13 avaliações,
todos em r=0,70 e M=256. Não demonstra robustez em M=1.024, em D/E, nas faces
superiores, nos controles ou em toda a grade. Não atribuir E6 ao perfil.

O código de E11 ainda contém uma secante interna com clipping, inclinação inicial
fixa 0,694 e divisão por diferenças que podem ser zero. Não há bracket interno
seguro, proteção explícita contra NaN/derivada nula, nem teste implementado da
monotonicidade alegada no texto. Um bracket externo com sinais opostos não prova
unicidade ou monotonicidade de todo o perfil. Além disso, no máximo de 64 ele
incrementa o contador para 65 antes de retornar `budget`; isso deve ser uma
contagem de tentativas distinta da contagem de avaliações executadas.

Implementar secante salvaguardada por bisseção/Brent dentro de um bracket válido,
com tolerâncias e orçamento totais explícitos. Distinguir ausência de raiz de L1,
perfil não monótono, Jacobiana mal condicionada, limite numérico e limite de família.
Se o perfil não for monotônico, falhar como **solver não certificado**; isso não
prova que a família não alcança o alvo. Na borda, o perfil prioriza L1 e minimiza
o desajuste remanescente de L2; não é automaticamente a solução do mínimo
quadrático conjunto de A. Essa prioridade deve ser parte da definição.

A aceitação é contraditória entre código, B e síntese. E11 usa
`max(2.326*SE2, min(0.0003, 0.1*SD_alvo2))`: pode aceitar acima de 0,0003.
B simultaneamente diz remover o cap e nunca excedê-lo. S6 não resolve isso com
uma frase. A regra interior deve escrever o mínimo dos limites exigidos,
incluindo os DPs de alvo/nulo se forem preservados; a condição numérica não deve
ficar mais frouxa quando aumenta o ruído Monte Carlo.

`|resíduo| <= 2.326*SE` significa não rejeitar uma diferença zero, não demonstrar
equivalência prática. Por isso é inferior à validação independente de A.
Recomendo exigir passo efetivo, salvo identidade analítica, e validar cada fit
em 4.096 pares novos com `|resíduo_k|+2.2414*SE_k <= 0.0003`, nos momentos que
a família realmente ajusta. A/C e controles de um parâmetro só exigem L1;
L2 é diagnóstico. Esse cap continua sendo uma convenção operacional, não prova
de resíduo irrelevante para L3–L5. Se falhar, a célula é não resolvida; MSE de
AUC não a salva. Deixar a validação somente em G0, sem consequência no fit
confirmatório, permite aceitar depois exatamente o defeito que G0 diagnosticou.

Uma tentativa maior pré-especificada, disparada por precisão de momentos antes
de qualquer treino, não é por definição seleção por AUC. Pode ser legítima,
mas altera o algoritmo finito e seu custo e deve entrar no gate. A projeção
abaixo fixa uma tentativa, sem aumento automático de M.

### S4: MSE e draws fora da caixa não fornecem a garantia alegada

Para `d_b=AUC_b-AUC_0`, a quantidade de B satisfaz
`mean(d_b²)=Var_emp(d_b)+mean(d_b)²` (variância com divisor B). Isso não torna
`mean(d_b)` uma estimativa validada do viés do estimador em relação a S1.
O passo não centrado também corrige o resíduo numérico do fit original,
aproximando-o de outro procedimento de matching. Sob S1, erro do procedimento
finito e distância a uma raiz ideal são objetos diferentes. Uma largura normal
baseada em RMSE não ganha cobertura nominal automaticamente.

Mais grave: B aumenta o denominador com MSE, mas centra os desvios usados no
max-t. A distribuição simulada perde justamente o deslocamento que motivou o
termo de viés. Isso pode reduzir o crítico empírico; o piso normal não corrige
automaticamente esse desencontro. Recomendo variância de draws centrados como
componente de nuisance, resíduo e deslocamento médio relatados separadamente,
e falha de equivalência tratada antes da inferência. Se se quiser intervalo
com correção de viés, especificar e validar essa inferência como tal.

O passo irrestrito `-J^-1*g_b` não replica o estimador com caixa e regra de
aceitação na borda. Pode dar lambda negativo ou phi>0,999. Não há ordenação
geral que torne sua AUC mais conservadora que a AUC do estimador restrito após
retreinar a LDA. A versão projetada de A é mais fiel ao algoritmo restrito,
mas também não tem validade automática na borda: é preciso replicar a regra
do perfil escolhido, inclusive os estados de falha, e testar o regime próximo
da borda. A referência citada por B é Andrews (2000), DOI
[10.1111/1468-0262.00114](https://doi.org/10.1111/1468-0262.00114), sobre
inconsistência do bootstrap na borda; não é um teorema de conservadorismo do
passo irrestrito. O registro bibliográfico foi localizado; a análise deste
procedimento específico aqui é algébrica e de inspeção de código.

O deslocamento constante `D*delta` de B só propaga a mudança das médias.
Uma mudança de covariância das características pode ser de primeira ordem
em delta, e altera a padronização, a LDA e as caudas. Não é justificável
declará-la de segunda ordem sem demonstração. A deriva por realização de A
retém mais informação, mas a rugosidade dos postos também exige validação.
Recomendo stencils de matching, treino e referência com CRN, dois passos por
parâmetro, e comparação com refits completos do **mesmo** solver/lei. Aprovar
a razão 0,8–1,25 é necessário como diagnóstico, não suficiente como prova:
duas aproximações igualmente enviesadas podem concordar.

400 draws não é um erro conceitual isolado. Sob desvios normais centrados,
o erro relativo da estimativa de variância é aproximadamente 7,1%, contra
3,2% em 2.000 draws. Para MSE, usar
`MCSE=sqrt((mean(d^4)-mean(d²)^2)/B)` como diagnóstico, com a ressalva de caudas.
O piloto A apresentou curtose alta; não assumir normalidade para garantir
precisão. Recomendo 2.000 draws pré-fixados, MCSE registrado e custo medido
em dados artificiais. Reduzir a 400 exige critério de precisão próprio; os
gates não transformam 400 automaticamente em uma escolha suficiente.

Em a=0 com identidade exata, a AUC populacional de qualquer escore treinado
independentemente é 0,5: sua variância de nuisance é **zero**. A dispersão
obtida retreinando sobre uma referência finita de 4.000 eventos/classe mede
também ruído dessa referência, não variabilidade da AUC populacional. Adotar
a exceção analítica de A. No interior, comparar referências independentes ou
tamanhos de referência pré-fixados para quantificar esse artefato; usar a mesma
referência finita nos dois métodos não valida o alvo populacional.

### S5, S7 e S8: separar mecânica, dispersão e cobertura absoluta

G1b é útil e barato. A afirmação de exatidão livre de distribuição precisa
das hipóteses: escores contínuos iid, classes independentes, condicionamento
em treino independente. Com clusters dependentes, a lei conjunta dos postos
depende da cópula intracluster; ICC=0,5 não a caracteriza. Empates também mudam
a lei. Os dois cenários propostos são testes de mecânica, não validação exata
de toda a família de escores. Independência entre nove slots não é universalmente
a dependência menos favorável sem hipóteses adicionais. Acrescentar cenários
artificiais de empates, dependência entre forças e clusters não gaussianos.

G1c em três r é um bom teste integrado após provar a identidade para todos os
r/canais aplicáveis. Não é necessário repetir 200 pipelines em cada r só para
redescobrir a identidade. Mas retirar a incerteza espúria da referência em a=0
é importante: senão a inflação da largura pode mascarar erros de escores.
O gate individual congelado continua ativo; reportar invalidade e não repetir
até obter uma curva aprovada.

**Manter `max(max-t empírico, 2.7729)` é aceitável**, por continuidade e porque,
para o mesmo centro/EP, sua banda contém a banda do piso. Bonferroni puro é
mais simples e dispensa a simulação conjunta; não é necessário trocá-lo para
tornar o gate viável. Pode-se validar a banda do piso separadamente, desde que
isso seja chamado de teste de uma banda contida, não reprodução do crítico
empírico de nove forças. Não se precisa gerar oito AUCs interiores adicionais
em cada G1c apenas para esse teste.

A garantia de Bonferroni depende de cada intervalo marginal ter erro total
no máximo 0,05/9; não depende de independência entre forças. G2 em sete células
não prova esse limite em todas as forças/r, famílias ou sensibilidades.
Validar EP médio e cobertura pontual de 95% tampouco verifica as caudas de
0,00556 necessárias. Em 700 repetições o número esperado dessas falhas é
aproximadamente 3,9. Aceitar até dez é uma triagem fraca de caudas, especialmente
quando a agregação pode esconder uma célula ruim. Nunca concluir de P1–P3b,
como faz B, que a cobertura conjunta já foi demonstrada. A banda permanece
por r; não é cobertura simultânea dos 81 pontos.

#### G2: a média leave-one-out não é uma verdade conhecida

Se `X_i` são estimativas iid de uma célula, com variância sigma², então
`D_i=X_i-media(X_-i)=R/(R-1)*(X_i-media(X))`. Logo:

```text
E[D_i] = 0
Var(D_i) = sigma² * R/(R-1)
Corr(D_i,D_j) = -1/(R-1), i != j
soma(D_i) = 0
```

A correção 100/99 para o segundo momento é razoável nesse caso simples.
Não transforma os 100 z-scores em observações independentes, nem os 700
indicadores de cobertura em binomiais independentes. EPs heterogêneos estimados,
logit, falhas e CRN entre células exigem tratamento adicional. As probabilidades
de aprovação listadas em B não podem ser transportadas sem recalibrar a
estatística completa, inclusive suas dependências, em dados artificiais.

Sob S1, se a AUC de teste for não enviesada condicionalmente e todas as
repetições estiverem definidas, a média é uma estimativa consistente do alvo
do procedimento. Ainda assim tem erro de referência: com R=100 seu EP é
cerca de um décimo do DP de uma execução. Um viés comum de implementação
ou o condicionamento por sucesso desaparece na comparação consigo mesma.
Para S1, transformar a média de AUCs por logit não equivale a fazer a média
dos logits. O runner precisa escolher a primeira e propagar a incerteza de
referência, caso use esse diagnóstico.

Recomendo preservar as sete células e os 100 pipelines/célula, mas chamar G2
de **calibração da dispersão do procedimento**. Usar 50 pares disjuntos por
célula para o teste de diferenças, como em A, e usar a média leave-one-out
somente como diagnóstico adicional. Fixar critérios com o R efetivo e não
reutilizar o limiar de A para 100 pares. Reportar variância empírica, média
dos EP², razão e incerteza por célula, com limites inferior e superior: os
limites só superiores de B deixam passar EP arbitrariamente inflado. A
referência independente de matching permanece obrigatória. Não declarar
cobertura absoluta interior; se essa for requisito de liberação, acrescentar
um estudo de referência independente com orçamento próprio antes de liberar.
Essa distinção entre alvo, desempenho e erro Monte Carlo segue a orientação
de [Morris, White e Crowther (2019)](https://discovery.ucl.ac.uk/10066118/1/2019%20-%20Morris%20-%20simulation%20studies%20tutorial%20-%20stat%20med.pdf),
DOI 10.1002/sim.8086; as identidades acima são derivadas aqui.

G2c com razão mínima 0,6 admite estimativa 40% menor da variância, ou EP de
nuisance cerca de 22,5% menor. B reconhece que pode aprovar razão verdadeira
0,5 em aproximadamente 24% dos casos: não é certificação forte. Quarenta
refits são piso para comparação, não garantia de estabilidade; o próprio A
mostra caudas e 34/40 paradas precoces no piloto frouxo. Exigir comparação
bilateral com incerteza Monte Carlo, deslocamento médio, referências e
diagnóstico de caudas, sob a versão corrigida. Zero/zero de variâncias na
identidade é caso analítico, não razão numérica.

Não adotar o fallback de excluir os dois r extremos de G2 pelo custo. É uma
mudança de domínio da validação e concentra ainda mais a evidência no r exposto.
Além disso, manter 648/700 ou 10/700 após reduzir a 500 observações é incoerente;
mesmo manter as proporções altera as probabilidades operacionais do gate.

## Q2 — Reconciliação e uma projeção corrigida

### Unidades e diferenças de desenho

Um painel é um evento completo: 1.000 redes × dois eventos = 2.000 painéis
**por classe**. Treino custa 4.000, teste 8.000 e referência 8.000 painéis.
Não multiplicar novamente por dois após somar as classes. Uma avaliação nula
de matching usa 1.024 painéis; o alvo social de 1.024 pode ser reutilizado
entre avaliações do mesmo fit. CRN não torna gratuita a regeneração do nulo.

| Componente por célula não nula | A, conta publicada | B, 13 avaliações de solver |
| --- | ---: | ---: |
| Mapa independente inicial | 5.120 | 0 |
| Matching: alvo + avaliações nulas | 5.120 (4 nulas) | 14.336 (13 nulas) |
| Validação independente | 8.192 | 0 por fit; síntese adiciona 2.048 só em G0 |
| Treino + teste + referência | 20.000 | 20.000 |
| Derivadas | 28.096 | 2.048 |
| Total | 66.528 | 36.384 |

A deriva quatro stencils (dois parâmetros × dois passos), cada um com
1.024 de matching + 2.000 de treino nulo + 4.000 de referência nula = 7.024.
B deriva duas perturbações somente nos 1.024 painéis de matching e aplica a
derivada **da média** a todas as características. Não são implementações
equivalentes com preços diferentes. Os cerca de 26.400 painéis nulos de B
correspondem a 16 avaliações nulas × 1.024 + 10.000 painéis nulos das três
fases. Mas 13+2=15: sob essa convenção o total correto é 25.360 nulos,
11.024 sociais, ou 36.384. Se reservar uma avaliação extra, são 37.408.

A conta de gate de A usa 61.408 por repetição porque amortiza o mapa inicial;
inclui 1.800 execuções em a=0 e 400 não nulas. B tem 150 em a=0 e 700 não
nulas, além de G0/G1b/G2c. Comparar 37 h com 25 h sem essa decomposição não
compara o mesmo gate. Também não se pode multiplicar diretamente o refit A
de 187,62 CPU-s: ele tinha M=256, em geral uma avaliação, sem teste, sem a
validação independente proposta e sem os stencils completos.

O inventário de A inclui 15 grades observadas e três controles nos cinco
nulos, antes do prêmio de 24 passos. B/síntese dizem controles apenas de B.
Isso retira 12 grades de controles se aplicado literalmente; não é só uma
economia de implementação. A não contou a combinação exploratória c/δ.
S9 deve repor controles A–E e nomear a combinação, preservando seu status
exploratório, ou declarar explicitamente a redução de escopo.

### Cenário único de planejamento recomendado

Esta projeção é para a versão **corrigida recomendada neste parecer**, não
uma nova medição nem a execução literal da síntese. Usa oito workers dedicados,
BLAS com uma thread, 13 avaliações nulas por fit, M=1.024, validação em 4.096
pares, quatro stencils completos, uma tentativa e nenhuma economia não
demonstrada entre r/famílias. As taxas vêm da
[projeção e medições de A](../../../../experiments/exploratory/amendment-a-calibration/compute-projection.json):

```text
q  = 0,021943262285974926 CPU-s/painel (187,62 / 8.550,4, com valores não arredondados)
q0 = 0,012978036875021644 s/painel em a=0 (proxy de worker isolado)
horas = 1,25 * trabalho_em_segundos / (8 * 3.600)
```

q é uma taxa média do piloto B de A, aplicada como proxy às outras famílias;
q0 não é uma medição multicore uniforme. Não aplicar novamente o fator de
contenção 1,60 dos refits antigos, nem chamar tempo somado de worker de CPU.
Os 25% são reserva de planejamento, não intervalo de confiança.

Uma célula não nula passa a ter **70.624 painéis**:
14.336 matching + 8.192 validação + 20.000 fases + 28.096 stencils.
São 4.096 acima dos 66.528 de A: saem 5.120 do mapa, entram 9.216 pelo solver
mais caro. Em a=0 com identidade, reservar 2.048 para verificar o matching
e 12.000 para treino/teste: 14.048; sem referência/stencils de nuisance.
Para C observado e para as quatro ancoragens, reservar a conta completa
também em a=0, à taxa q0, porque não se pressupõe identidade.

Por controle adicional, reutilizar só os 10.000 painéis sociais das fases
(treino/teste/referência): incremento 60.624 por célula não nula; 8.048 na
âncora exata. Manter quatro stencils no orçamento: mesmo com rematching de
um parâmetro, o segundo parâmetro herdado do observado é aleatório e sua
propagação aos controles não pode desaparecer. A conta conservadora cobra
60.624 em a=0 dos controles de C, sem antecipar economia por identidade.

Para tornar a aritmética auditável, defina
`F(p,z)=1,25*(72*p*q+9*z*q0)/(8*3600)` horas por grade. No bootstrap de
escores fixos, uso os 15,70 s medidos no relatório de falha para 2.000 draws
em nove forças; a divisão por nove para células isoladas é aproximação.
Os 40,59 s do diagnóstico de A são para Bonferroni com placements, **não**
para 2.000 execuções completas do max-t: não usar esse tempo no lugar.

| Gate corrigido | Conta principal | Horas com reserva |
| --- | --- | ---: |
| G0, cinco nulos + três controles B | `8*F(22.528,22.528)`, matching e validação, conservador em a=0 | 13,27 |
| G1b, 2.000 repetições sintéticas de nove slots | `2.000*15,70 s` antes de workers/reserva | 1,36 |
| G1c, 150 execuções em a=0 | `150*14.048*q0` | 1,19 |
| G2, sete células × 100 execuções | `700*70.624*q` | 47,08 |
| G2c, dois conjuntos de 40 refits | `80*30.528*q + 8.000*q` de referência social inicial | 2,33 |
| Bootstrap de escores de G1c/G2 | `(850/9)*15,70 s` | 0,06 |
| **Gate total** | | **65,30** |

Cada refit G2c tem 14.336 matching + 8.192 validação + 4.000 treino + 4.000
referência nula; não gera teste nem stencils de novo. G0 continua o inventário
de oito grades de B, com validação fortalecida. Os demais fits são validados
antes de seu próprio treino nos tiers; G0 não será chamado de máscara de todo
o estudo. Se a máscara completa tiver de ser publicada antes de qualquer
treino, será necessário antecipar esses fits, reutilizando-os por hash ou
contabilizando sua repetição.

| Tier corrigido | Inventário e conta | Horas com reserva |
| --- | --- | ---: |
| 1 | B principal: `F(70.624,14.048)` | **4,92** |
| 2 | A/C/D/E: três grades com âncora, C com custo completo em a=0 | **19,97** |
| 3 | Três controles × cinco nulos; mobilidade aproveita painéis/características armazenados | **63,86** |
| 4 | c=0,25/0,50; δ=0,10/0,20; combinação exploratória: cinco grades B | **24,60** |
| 5 | b=0 e quatro ω: cinco grades B, sem identidade presumida nos ω | **25,75** |
| 6 | Uma grade B de 24 passos: cenário de custo de painéis `24*F(70.624,14.048)` | **117,94** |
| **Tiers 1–5** | | **139,10** |
| **Tiers 1–6** | | **257,04** |
| **Gate + tiers 1–6** | | **322,35 h, cerca de 13,4 dias contínuos** |

As linhas dos tiers incluem bootstrap fixo a 15,70 s por r/grade. A grade de
24 passos multiplica conservadoramente todo o custo de painéis por 24; canais
e inicialização não se repetem integralmente. É um cenário explícito, não
benchmark nem limite superior demonstrado. Não há medição A que sustente uma
previsão pontual confiável de 60 h para esse tier. C/D/E, ancoragens e canais
também podem ter custos diferentes da proxy B.

O custo do LNB de 2.000 draws, derivadas/ajuste da mobilidade, testes de identidade,
checagens adicionais de referências e infraestrutura deve caber na reserva de
25% para que **322,35 h** seja a previsão total. Isso não foi medido: se exceder
a reserva, acrescentar a diferença; não alegar orçamento certificado. As
sensibilidades estão orçadas em B observado, sem controles adicionais nelas.
Preservar painéis ou resumos de mobilidade durante a geração é condição para
evitar regeneração; armazenamento/I/O precisam entrar no manifesto de custo.
Uma avaliação nula adicional em cada uma das 700 execuções G2 acrescenta cerca
de 0,68 h; esgotar 64 em lugar de 13 acrescentaria aproximadamente 34,8 h só
a esse bloco. O número 13 é hipótese de planejamento, não garantia de E11.

Portanto A tem a contagem mais explícita para validação e stencils; B tem uma
redução legítima do gate nulo e um solver promissor, mas sua conta de 25 h/35 h
não compra o procedimento corrigido nem o mesmo inventário. Nem 37 h/136 h de
A é a previsão correta para essa combinação. A projeção acima é uma só,
condicional e reproduzível; não autoriza o confirmatório em 72 h.

## Q3 — Exposição e o que o artigo pode afirmar

A exposição não justifica escolher a variante que produz a menor fronteira,
estreitar G/R ou dispensar controles. Os valores já vistos justificam declarar
desenvolvimento informado por resultados e usar sementes novas. Não determinam
qual solver tem validade; a decisão deve se apoiar nas identidades, resíduos,
testes de implementação e critérios fixados antes do próximo dado.

Retirar da síntese a frase de que `a*(0,70) em (0,03;0,10]` é muito provável.
Um resultado abaixo do alvo em 0,03 não exclui cruzamento em 0,001/0,003/0,01:
a grade congelada não impõe monotonicidade. Um probe condicionado e a média
de refits frouxos tampouco identificam a AUC média do novo procedimento.
Não permitem concluir sobre a fronteira sustentada, que requer todos os
pontos maiores. Mesmo a desigualdade sob v1 baseada em 0,943912 é evidência
condicional forte de cruzamento, não uma dedução exata sobre o alvo S1.
Corrigir `<0,30` para `<=0,30` resolve só o erro de grade, não esse problema.

Não basta rotular apenas r=0,70 e chamar os outros oito pontos de completamente
cegos. Seus contrastes diretos podem estar não expostos, mas o método global
foi escolhido após resultados em r=0,70 e há CRN/continuidade entre r. Isso
não inutiliza a execução futura; exige descrevê-la como avaliação em sementes
novas de um protocolo emendado após exposição parcial. Não é confirmação
inteiramente cega da curva. Conservar toda R primária, apresentar a proveniência
por r e não promover os oito restantes a um novo primário retrospectivo.

O artigo pode reportar o resultado futuro em r=0,70, com esse histórico e as
limitações de calibração. Deve distinguir as observações exploratórias já
vistas dos resultados da execução sucessora. O novo algoritmo e a lei do
traço tornam ainda menos justificável transferir os números de A como se
fossem expectativas de v4.

O selamento de G2 reduz acesso aos valores, mas não apaga exposição: critérios,
razões de variância e falhas ainda informam decisões. Diretório 0700 protege
outros usuários, não agentes sob o mesmo usuário. Guardar resultados fora do
checkout/contexto do coordenador, com separação de processo/acesso, hashes e
log de leitura; stdout/tracebacks não devem conter AUCs. Fixar previamente
quais bits podem sair e não repetir o gate até passar. Nada disso foi executado
nesta crítica.

## Q4 — O que falta para implementar e fechar a janela

O código A é protótipo isolado, com bootstrap local ainda não validado. E11 é
um script exploratório de B. Nenhum é o runner S1–S10 pronto. Antes de qualquer
execução sucessora, o pacote precisa dos seguintes contratos verificáveis:

1. Uma definição literal das leis, inclusive traço iid versus transportado,
   C, E e 24 subpassos; testes de identidade pathwise em N completo, canais e
   controles aplicáveis, mais classes independentes no teste. C/ω não recebem
   identidade fictícia; ω=1 merece caso explícito de degenerescência.
2. Solver com brackets, tolerâncias únicas, orçamento contado, secantes
   degeneradas e casos de todas as faces/cantos. Testar raízes conhecidas,
   perfil não monótono e ruído de momentos sem discriminador. Estatuto de falha
   nunca deve se converter em AUC abaixo do alvo ou em certificado de impossibilidade.
3. Propagação dos parâmetros observados aos controles: fixar o segundo
   parâmetro dentro de cada refit não o torna constante entre refits. Testar
   essa dependência, centros/variâncias, referência finita, stencils, empates,
   clusters e a combinação de draws de nuisance com os 2.000 draws de escores.
   A API congelada aceita 30–50 refits; criar caminho sucessor explícito,
   sem passar 400/2.000 linhas como se fossem refits completos independentes.
4. Gate fixado por código/hash antes de rodar, com critérios calibrados em
   dados artificiais para as dependências e denominadores reais. Falhas entram
   no denominador e são contadas também por célula; não podem desaparecer das
   estatísticas de EP por exclusão de casos. Não substituir célula G2 por outra
   já presente: a regra do r mais próximo precisa resolver duplicatas, empates
   e ausência de alternativa antes da execução.
5. Inventário máquina-legível de família × a × r × canal × sensibilidade,
   incluídos os controles A–E e a combinação exploratória. Nomear a dependência
   científica de cada claim: sem D/E/C completos e válidos não declarar
   evidência específica de interação por separação apenas contra B.
6. Manifesto de sementes por fase/replicação, incluindo validação independente,
   stencils, bootstrap e referência; auditoria de colisões e alinhamento entre
   forças; hashes do código/ambiente e equivalência numérica dos shards. Mesmo
   hash de código não garante mesmo BLAS, ordenação ou arredondamento em hosts
   diferentes. Retirar a reserva v3, sem executar v4 confirmatório antes do gate.

S9 pode ser adotado como política operacional, com correções. O fechamento em
**18/10/2026 às 23:59 America/Sao_Paulo** é auditável e deixa prazo de escrita;
registrar também `2026-10-19T02:59:00Z`, início da janela, oito workers reservados,
horas provisionadas, desempate da fila e regra para trabalhos em andamento.
Fixar ordem e recursos antes de ver resultados; não acelerar/desacelerar tiers
conforme AUC, largura ou invalidade. A duração do solver pode depender do
problema científico: um prazo fixo sozinho não torna as ausências aleatórias.

Não escrever “não executado” para um tier parcialmente executado. Registrar
`não iniciado`, `parcial por encerramento operacional`, `completo inválido`
ou `completo válido`, com todas as tentativas, células e hashes preservados.
Até o fechamento, manter resultados confirmatórios selados; publicar fronteiras
somente das unidades completas previstas, mas divulgar o inventário inteiro
e as ausências dos tiers incompletos. No instante fixado, interromper e marcar
jobs incompletos, sem completar apenas os mais favoráveis. Não confundir
interrupção operacional com falha científica nem apagar dados já gerados.

A janela nova substitui expressamente o antigo stop-and-amend por inviabilidade;
isso não autoriza afirmar que todo o estudo congelado foi entregue. Tier 1
sozinho sustenta apenas a comparação contra B; tier 2 é necessário para a
interpretação entre mecanismos, e tiers incompletos limitam os claims. A
projeção de 13,4 dias contínuos parece compatível com uma janela de várias
semanas, mas dedicação dos workers e demais custos ainda precisam ser
demonstrados antes da alocação. Não usar a data para ocultar essa incerteza.

## Verificação desta entrega

Os links locais resolvem e o hash do pré-registro permanece igual ao declarado.
O comando `UV_CACHE_DIR=/private/tmp/uv-cache-cov3 /Users/davi/.local/bin/uv run --locked python ../scripts/check_repository.py`,
executado em `workbench/`, passou nos sete checks. Foi usado o caminho absoluto
porque `uv` não estava no PATH desta sessão. A alteração é somente documental;
não houve execução de testes científicos, novos painéis ou novas AUCs.

## Veredito e mudanças exigidas

**Adotar com mudanças; não adotar como está.** O parecer recomenda uma emenda
revisada para implementação e validação, não a adoção científica dos resultados
ou a liberação imediata de sementes confirmatórias.

- Fixar S1 e a lei exata de S2, preferindo T normal iid; declarar mudanças de
  procedimento finito, alvos condicionados a sucesso e limites das identidades.
- Manter o perfil de B com salvaguardas; corrigir a atribuição E6/E11 e exigir
  equivalência independente por fit, sem usar ausência de significância como aceitação.
- Substituir MSE irrestrito por propagação fiel ao estimador restrito, com
  variância e deslocamento separados, 2.000 draws, stencils completos e nuisance
  exatamente zero na identidade; validar referências e comparar com refits.
- Manter o piso de Bonferroni e, se desejado, max-t; corrigir as alegações de
  exatidão de G1b e de cobertura de G2. Preservar sete células, tratar G2 como
  dispersão, recalibrar seus critérios e fortalecer G2c sem selecionar sucessos.
- Usar o orçamento corrigido e inventário completo explicitados em Q2; confirmar
  os custos ainda não medidos antes da execução. Não herdar 25 h/35 h como garantia.
- Corrigir exposição e claims da curva inteira; retirar a localização inferida
  da fronteira sem monotonicidade. Fixar tiers, dependências científicas e
  encerramento sem ocultar trabalho parcial ou invalidade.

Se essas correções não forem incorporadas e verificadas, rejeitar esta versão
da síntese para execução confirmatória. O pré-registro congelado e seus
artefatos permanecem inalterados.
