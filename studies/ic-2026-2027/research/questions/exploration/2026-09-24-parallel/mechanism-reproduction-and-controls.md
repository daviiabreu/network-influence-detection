# Reprodução e controles baratos das candidatas de mecanismo

24/09/2026. Relato exploratório, sem pergunta selecionada, experimento
registrado, síntese aceita ou alegação de novidade. O [diretório de execução](../../../../experiments/exploratory/antecedent-reproduction-mechanisms/README.md)
guarda protocolos, comandos, hashes, scripts próprios e JSON completos. Foram
usadas oito sementes de avaliação (101–108), 32 sementes independentes de
calibração para a candidata 1 (9001–9032) e 120 oportunidades por réplica.
Parâmetros foram fixados antes do primeiro lote; duas correções de fidelidade
geraram sucessores, preservando as saídas anteriores. Não houve busca de
parâmetros ou sementes após observar os sinais.

## Antecedentes: fidelidade e discrepâncias

O [arquivo dos autores de Dong](https://zenodo.org/records/21820152),
`Code_Public.zip`, foi executado localmente a partir de cache privado,
SHA-256 `57afbe54…7cb3c9ad4ae` e MD5 conferido com o depósito. A
[API do registro Zenodo](https://zenodo.org/api/records/21820152) informa
`metadata.license.id = cc-by-4.0`; o ZIP não traz `LICENSE` separado. O código
não foi incorporado ao Git. Num caso reduzido com
`N=40`, dois temas, `gamma=1,5`, `K=1`, duas sementes 42–43 e
`alpha≈0,595`, o limiar calculado pelo código é `0,421` para `p=1` e `0,769`
para `p=2`. Após 800 passos de Euler (`dt=0,02`), o indicador `P` médio foi
`0,912` em `p=1` e `6,49×10^-8` em `p=2`; `|C|` foi praticamente igual a `P`
nesse caso. A separação concorda qualitativamente com o
[resumo publicado de Dong, Zhang e Liang](https://pubmed.ncbi.nlm.nih.gov/42684114/):
conformidade linear reduz o limiar, enquanto a não linear conserva o limiar
local. A primeira execução herdou `K=0,3` do construtor, incompatível com o
limiar `K=1`; sua saída neutra ficou preservada e não sustenta comparação.
Não reproduzimos as grades, a bifurcação subcrítica, as figuras nem o ajuste
nos 27 subreddits. O artigo integral permaneceu inacessível e os dados Reddit
não estão no ZIP: não há comparação numérica honesta com figura publicada.

No [código numérico de Dong](https://zenodo.org/records/21820152), a intervenção
`leader` sorteia nós com a semente `seed+7777`, chama `set_frozen_nodes` e,
em cada passo, fixa todos os seus temas em 0. O mesmo fluxo percorre `p=1` e
`p=2`. O observável `P` é `mean(x²)` sobre nós e temas: corresponde ao erro
quadrático relativo a 0, mas é denominado polarização pelos autores. Um
microteste local com dois nós congelados confirmou valores 0 em ambos os
casos e `P` igual à média dos quadrados (até arredondamento). Portanto, a
intervenção deles não demonstra redução de erro para uma verdade externa.
Na candidata 2, o gerador declara verdade 1 e mede `MSE=mean((1-x)²)`;
receber sinais em direção a 1 não equivale a congelar nós em 0. Essa leitura
não altera a identidade linear nem os resultados numéricos do controle
projeção/incidência, que não usou código de Dong. Ela impede usar `P` de Dong
como baseline de acurácia; um piloto posterior deve distinguir fonte
congelada de sinal repetido sob a mesma dose.

Para a candidata 1, o Exemplo 1 da
[formulação de Abedinzadeh–Akyol](https://arxiv.org/html/2603.21081)
foi reimplementado independentemente com os dois agentes, dois temas,
matriz estática e pesos de fonte do texto. Após 500 iterações, o tema 1 no
modelo vetorial ficou em `0,4545/0,4548`, contra `0/0` na aproximação
desacoplada; no tema 2, `0,8212/0,8464` contra `0,8766/0,8941`.
A diferença muito maior no tema 1 concorda com a descrição da Figura 2,
que diz haver boa concordância apenas no segundo tema. A versão vetorial ainda
mudava `2,85×10^-6` na última iteração; não reproduzimos seu ponto fixo com
tolerância `10^-10`, demonstração de contração ou experimento de rede real.

Para [Neuhäuser, Mellor e Lambiotte](https://arxiv.org/html/1910.09226v1),
uma implementação independente da regra 3CM em hipergrafo completo de dez
agentes, com oito opiniões 0 e duas 1, deu média final `0,1479` para
`lambda=-1`, `0,2000` para `lambda=0` e `0,2714` para `lambda=1`, partindo
de `0,2`. Reproduz o sentido da Figura 3 e a conservação linear, mas não
seus valores: o artigo usa 100 agentes e outra extensão temporal.

O código fixado de [Thompsky et al.](https://github.com/Yolandayx929/adaptive-edge-BCM/tree/5e33664982bda6b7576074ff47772791459ea22c)
foi obtido após a falha inicial de DNS. O substituto local, usando o kernel
escalar já existente no estudo, continua uma reprodução independente e
reduzida. Com `N=20`, oito sementes e critério
operacional próprio, o número médio de tentativas até estabilização foi
`887,5` adaptativo versus `837,5` uniforme no grafo completo, e `425`
adaptativo versus `537,5` uniforme no ciclo; zero censuras no limite de
10.000. As direções são opostas à tendência de rede densa/rarefeita relatada
no [artigo, Figuras 2–4](https://arxiv.org/html/2605.20418v2).
Diferenças de tamanho, topologia (ciclo versus Erdős–Rényi), critério de
parada e poucas sementes impedem tratá-las como refutação do resultado
publicado.

Uma execução posterior da função `DW` dos autores comparou um subconjunto
do [painel da Figura 2](https://arxiv.org/html/2605.20418v2): grafo completo
de 100 nós, `mu=0,3`, `z0=0,1`, `gamma=delta=0,1`, tolerância `0,01`,
baseline `(gamma,delta,z0)=(0,1,0,5)` e 20 sementes próprias por célula.
As médias de `log10(T)` para baseline/adaptativo foram, respectivamente,
`3,834/3,698` em `c=0,1`, `3,584/3,532` em `c=0,2`, `3,568/3,545` em
`c=0,3` e `3,135/3,152` em `c=0,5`; não houve bailout nas 160 execuções.
O menor tempo adaptativo em `c=0,1` concorda com o painel e com o texto
publicado. A diferença em `c=0,5` é pequena e em sentido contrário. O
repositório dos autores também apresenta um painel com `gamma=delta=0,1`;
não extraímos valores exatos da imagem nem reproduzimos as sementes deles.
A grade completa da Figura 2, as Figuras 3–4 e as redes empíricas permanecem
sem reprodução. O [registro de execução](../../../../experiments/exploratory/antecedent-reproduction-mechanisms/README.md)
documenta o hash do código, a única importação omitida em memória e os JSONs.

## Controles novos e custo

Na candidata 1, a matriz estática principal é a média das probabilidades
de exposição antes de cada uma das 3.840 oportunidades em 32 trajetórias
adaptativas independentes. Os braços de avaliação recebem a mesma fonte
verdadeira, 240 sinais por réplica, mesmo estado e sequência de uniformes.
Com acoplamento zero, o MSE médio do tema 2 nos três agentes inicialmente
errados foi exatamente `0,24257` nos três braços; o tema não informado
permaneceu imóvel. Com acoplamento `0,4`, os MSEs foram `0,12362` na mistura
uniforme, `0,13052` na mistura estática esperada e `0,13169` na adaptação.
O contraste principal adaptação menos estático esperado é `+0,00117` em média,
positivo em apenas quatro das oito sementes (variação `-0,00390` a `+0,01083`).
O contraste total adaptação menos uniforme é `+0,00807`. Contatos entre os
grupos: médias `62,4` adaptativo, `60,1` estático esperado, `71,1` uniforme.
A calibração inicial que usava só estados em `t=0` gerou uma diferença maior,
mas não estimava a exposição esperada ao longo do tempo; seu JSON foi
preservado como erro de desenho. O pequeno contraste corrigido, com sinais
mistos e sem margem de relevância fixada, não sustenta agora uma contribuição
de feedback temporal.

Na candidata 2, a regra linear de trio e a projeção construída pelas três
arestas de incidência concordaram no MSE até `2,22×10^-16`. A regra não
linear `exp(-|x_j-x_k|)` foi comparada com projeção estática de mesma força
vetorial no estado de referência `(0,25, 0,5, 0,75)`; essa igualdade não vale
fora dele. Com maioria inicialmente errada e fonte presente, MSE médio
`0,05874` no trio não linear versus `0,05478` no par projetado; média de
crença `0,75996` versus `0,76925`; variância `0,00112` versus `0,00153`.
Com maioria correta e mesma fonte, o sentido inverteu: MSE `0,01762` versus
`0,02296`. Sem fonte, as diferenças foram maiores: `0,40418` versus
`0,35713` para maioria errada; `0,12783` versus `0,15809` para maioria
correta. Os 240 sinais por execução com fonte, seus destinatários e o
calendário foram idênticos entre regras. O controle de maioria correta indica
que parte da diferença é reforço genérico da maioria, como já antecipado por
Neuhäuser; não isola uma descoberta sobre evidência corretiva.

O lote completo levou poucos segundos, abaixo do teto de 30 minutos.
Medianamente, cada réplica de pares levou `0,22–0,37 ms`, trio
`0,14–0,17 ms`, substituto de Thompsky `0,40–2,01 ms` e chamada local
de Dong `38,7–43,0 ms`; o script dos antecedentes levou `0,99 s` incluindo
as verificações próprias. O novo subconjunto com código de Thompsky levou
22,26 s nas 160 chamadas `DW`. Não se extrapola desses casos para grades
completas, dados empíricos, incerteza adequada ou custo de validação registrada.

## Encaminhamento por candidata

**Candidata 1 — reformular.** Neste gerador pequeno, o controle nulo passou e
o sinal total apareceu, mas quase todo o contraste caiu quando a mistura
estática passou a representar exposição esperada independente. A hipótese
específica de contribuição do feedback temporal não recebeu apoio robusto.
Qualquer continuação precisaria definir uma margem de MSE e justificar por que
a fonte deve transferir ao segundo tema pela regra aqui escolhida; também
faltam confronto mais amplo com o modelo de Thompsky e com o modelo
estático de Abedinzadeh–Akyol.

**Candidata 2 — investigar com escopo estreito.** A identidade linear passou,
e o contraste não linear com fonte teve o sentido conjecturado na maioria
errada, com inversão na maioria correta. O efeito é pequeno neste desenho e
compatível com reforço de maioria já conhecido. Antes de um piloto maior,
ler o método/resultados integrais de Dong, verificar antecedentes que cruzem
acurácia e fonte verdadeira, declarar uma margem relevante e testar se outra
normalização local preserva o contraste. Não há aqui aprovação da candidata
nem inferência de novidade.
