# Protocolo exploratório congelado antes da execução

24/09/2026. Este lote verifica apenas controles baratos e custo. Não é
experimento registrado, calibração científica nem escolha de pergunta. Sementes
de avaliação: 101–108; calibração separada da candidata 1: 9001–9032. O limite
de execução de todo o lote é 30 minutos. Nenhum parâmetro será ajustado após
examinar resultados.

## Candidata 1

Seis agentes, grafo completo (15 arestas), três inicialmente errados no tema 1
e três próximos da verdade 1. Tema 1 inicial: 0,15 ± 0,02 para os três primeiros,
0,85 ± 0,02 para os demais. Tema 2 independente uniforme em [0,2, 0,8].
Verdade sintética (1, 1). Aresta por oportunidade escolhida por uma mesma
sequência de uniformes. Adaptação: peso proporcional a
`exp(-4 |x_i,1-x_j,1|)` recalculado a cada evento. Controles: pesos uniformes
fixos; pesos estáticos dados pela média das probabilidades em 32 estados de
calibração independentes. A atualização de pares é simultânea, convexa, ganho
0,15 no tema 1 e `0,15 × acoplamento` no tema 2. Fonte verdadeira em 1 para
agentes 0 e 3 a cada evento, ganho 0,03; transferência direta ao tema 2 vale
`acoplamento × deslocamento da fonte no tema 1`. Acoplamento 0 ou 0,4.
São 120 oportunidades por réplica; mesma dose e destinatários. Desfechos:
MSE do tema 2 nos três agentes inicialmente errados, MSE total, contagens
de arestas entre grupos e tempo por braço. O controle nulo sem acoplamento
deve manter tema 2 idêntico ao inicial; não há teste estatístico de efeito.

## Candidata 2

Seis agentes, trios fixos `(0,1,4)`, `(1,2,5)`, `(2,3,4)`, `(0,3,5)` em
calendário cíclico. Maioria errada: agentes 0–3 em 0,2 ± 0,02, agentes 4–5 em
0,8 ± 0,02; maioria correta: valores trocados. Verdade sintética 1.
Fonte ausente ou sinal 1 para agentes 0 e 4 em cada evento, ganho 0,03.
Atualização simultânea de um trio por oportunidade, ganho 0,08, 120 eventos.
Regra linear: soma das duas diferenças para cada alvo. Regra não linear:
mesma soma multiplicada por `exp(-|x_j-x_k|)`; pares projetados por incidência
usam cada aresta do trio com mesmo ganho. Para o braço não linear, a projeção
estática recebe fator `exp(-0,25)`. Estado de referência declarado
`(0,25, 0,5, 0,75)`, simétrico sob inversão e com dispersão não nula:
nesse estado os vetores de força das duas regras coincidem. Fora dele a
igualdade local não é presumida. Sementes 101–108, mesmo estado inicial e
calendário em todos os braços. Desfechos: média, variância populacional e
MSE da crença contra 1. O caso linear deve coincidir com a projeção até
erro numérico; uma diferença de MSE não linear só na maioria errada é
insuficiente para continuação.

## Antecedentes

Reproduzir em escala reduzida, com parâmetros/execuções próprios e rotular
fidelidade separadamente. Para Dong, usar apenas `Code_Public.zip` verificado
por SHA-256 em cache privado fora de Git; nenhum byte do código dos autores
entra neste diretório. Para Thompsky, tentar executar código fixado no commit
nomeado no memo; se não houver acesso, registrar a falha e não chamar a
implementação local de execução do código dos autores. Para Neuhäuser, conferir
independentemente identidade linear e direção do deslocamento da média no
microcaso. Para Abedinzadeh–Akyol, reproduzir apenas um caso analítico de
contração da fonte em pares estáticos, se os parâmetros exatos forem acessíveis.

Substituto independente para Thompsky se o código dos autores não puder ser
obtido: reusar o kernel escalar local somente para testar a tendência de tempo
de estabilização, sem dizer que é execução do artigo. `N=20`, grafo completo e
ciclo simples, `c=0,2`, `mu=0,3`, `z0=0,1`, `gamma=0,5`, `delta=0,5`;
baseline uniforme com `gamma=0`, `delta=1`. Oito sementes 101–108,
opiniões uniformes em [0,1], 10.000 tentativas no máximo; verificar a cada
100 tentativas que toda aresta está fora de confiança ou tem distância
menor que `10^-3`. Uma réplica que não atinge esse diagnóstico é censurada.
Esse critério operacional e a escala diferem dos publicados; comparar apenas
a direção qualitativa, sem estimar a figura do artigo.
