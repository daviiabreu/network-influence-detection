# Resultado do piloto de previsão probabilística

12/09/2026. O piloto foi executado e não atingiu o critério de continuidade.
As avaliações produziram diferenças, mas não apareceu uma preferência robusta
do W1 pelo congelamento enquanto o energy score favorecia o gerador dinâmico.
A recomendação é encerrar este ensaio delimitado e não iniciar o ESS nem
escolher a proposta B como artigo com base nele. Isso não demonstra que o
efeito inexiste fora das condições testadas.

## O que foi executado

O [protocolo congelado](protocol.md) compara cinco candidatos: ausência de
atualização, Deffuant, Deffuant com atividade episódica e drift de um décimo
em cada direção. Quatro deles geram os dados. Dois intervalos de interação
e duas amostras formam 16 configurações, oito dinâmicas e oito controles.
Cada trajetória tem duas ondas de treino e duas de teste. Todos os modelos
recebem o mesmo histograma observado e a mesma camada de amostragem.

| Lote | Trajetórias | Réplicas por previsão | Tempo medido |
| --- | ---: | ---: | ---: |
| Benchmarks de custo, excluídos da análise | 16 + 16 | 32 e 64 | 0,61 s + 1,23 s |
| Principal | 480 | 32 | 18,76 s |
| Precisão, mesmos dados do principal | 480 | 128 | 80,94 s |
| Confirmação, dados novos | 480 | 128 | 79,48 s |

Principal e confirmação somam 960 trajetórias independentes. A repetição
de precisão não aumenta esse número. Os três lotes analíticos levaram
179,18 segundos, contra 278,89 segundos projetados pela
[regra de custo](budget-decision.json), antes de examinar os scores.
Nenhuma configuração, semente ou repetição foi ampliada em função do resultado.

O alvo é a lei do histograma observado na onda seguinte. A população de
50 agentes é reinicializada a partir do histograma observado em cada onda.
Isso mantém o oracle correto para o alvo sintético, mas não representa uma
população latente persistente. Mesmo sem atualizações, há variação devida
às duas amostragens. A amostra de 550 respostas não elimina a incerteza da
população de 50 agentes. Não foram adquiridos dados humanos.

O baseline literal do benchmark publicado copia o histograma anterior;
o deste piloto passa pelas duas camadas de amostragem para representar uma
lei preditiva comparável. Portanto, estes resultados não explicam por si
só o congelamento observado naquele trabalho nem constituem sua reprodução.
[Moor-Smith–Carpentras, §§2.1–2.3](https://arxiv.org/html/2602.00876v1).

## Contraste central

O critério exigia a mesma configuração com oracle melhor em energy score
e pior em média W1, com os respectivos intervalos além de 1% da perda do
baseline, no principal, na repetição de precisão e na confirmação.
Nenhuma das oito configurações dinâmicas satisfez esse critério em qualquer
um dos três lotes.

A tabela mostra diferenças relativas ao baseline sem atualização. Valores
negativos favorecem o oracle. Cada tripla segue principal / precisão /
confirmação. São estimativas pontuais; não bastam para declarar o critério
cumprido. As diferenças e seus intervalos completos, inclusive todas as
células-controle e os cinco candidatos, estão na [análise](analysis-input.json).

| Gerador | Tentativas | Amostra | Média W1: diferença (%) | ES: diferença (%) | W1 do centro na confirmação (%) |
| --- | ---: | ---: | --- | --- | ---: |
| DW | 25 | 55 | +3,02 / -0,37 / +0,67 | -5,58 / -9,11 / -8,18 | -3,84 |
| DW | 25 | 550 | -0,75 / -0,14 / -0,33 | -12,30 / -12,18 / -13,10 | -6,30 |
| DW | 150 | 55 | -14,99 / -14,67 / -16,14 | -41,69 / -42,00 / -42,28 | -23,21 |
| DW | 150 | 550 | -24,05 / -23,85 / -23,17 | -50,01 / -50,17 / -54,50 | -35,10 |
| DW episódico | 25 | 55 | +1,68 / -0,39 / +0,52 | -1,11 / -3,52 / -3,03 | -0,47 |
| DW episódico | 25 | 550 | +0,16 / +2,70 / +1,30 | -1,32 / -2,21 / -3,83 | -3,46 |
| DW episódico | 150 | 55 | +1,01 / +1,09 / +2,86 | -18,28 / -16,41 / -15,32 | -4,20 |
| DW episódico | 150 | 550 | +1,80 / +2,33 / +1,56 | -22,27 / -20,41 / -21,39 | -11,04 |

Para DW com intervalo longo, os três scores principais favoreceram o gerador
nas duas amostras e nos três lotes. Portanto, o ensaio consegue distinguir
dinâmica em uma condição informativa sem depender de inverter a preferência
de uma avaliação por realização.

Na variante episódica com 150 tentativas e n=550, a confirmação deu ES
21,39% menor e média W1 1,56% maior. Entretanto, o intervalo da diferença de
média W1 foi [-0,00199873; 0,00414172], incluindo zero. O W1 do centro já
melhorou 11,04%. Esse caso ilustra a diferença entre avaliações, mas não
sustenta a afirmação central de congelamento robusto pelo W1.

Os intervalos são pontuais de 95%, calculados sobre 30 médias de trajetórias
por célula. Não são simultâneos, não tratam entrevistados ou ondas dependentes
como réplicas e não convertem exploração em validação registrada. A análise
de precisão registra diferenças pareadas com R maior e ensembles novos;
ela não isola um efeito determinístico exclusivo de R.

## Ajuste e controles

Cada perda escolheu um candidato usando apenas o treino, com o mesmo conjunto
e orçamento. A seleção foi congelada para o teste. Não houve recuperação
contínua de confiança, velocidade ou estrutura de rede.

| Gerador-controle | Tentativas | Amostra | Escolhas de dinâmica por ES: principal / precisão / confirmação |
| --- | ---: | ---: | --- |
| Sem atualização | 25 | 55 | 16/30 / 15/30 / 18/30 |
| Sem atualização | 25 | 550 | 14/30 / 12/30 / 14/30 |
| Sem atualização | 150 | 55 | 6/30 / 7/30 / 6/30 |
| Sem atualização | 150 | 550 | 6/30 / 2/30 / 2/30 |
| Drift positivo | 25 | 55 | 0/30 / 0/30 / 0/30 |
| Drift positivo | 25 | 550 | 0/30 / 0/30 / 0/30 |
| Drift positivo | 150 | 55 | 0/30 / 0/30 / 0/30 |
| Drift positivo | 150 | 550 | 0/30 / 0/30 / 0/30 |

No controle sem atualização, a confirmação selecionou dinâmica em 40/120
trajetórias, especialmente no intervalo curto. Houve ainda uma escolha de
drift incorreto; o kernel correto foi selecionado em 79/120 casos. Isso expõe
a fragilidade de seleção com duas ondas de treino. Não é evidência de que a
lei dinâmica tenha risco esperado melhor que a lei verdadeira: nenhum
candidato dinâmico teve intervalo de ES inteiramente favorável contra o
oracle em qualquer célula-controle ou lote. Também não basta para usar a
seleção como um teste de existência de influência.

No controle de drift, ES selecionou o gerador correto em 120/120 trajetórias
em cada lote. As comparações pareadas com esse oracle, além das comparações
com o baseline constante, estão na análise. O desempenho sintético não
valida automaticamente estimação de drift em surveys reais.

## Geometria e antecedentes

W1 usa a distância ordinal entre categorias; ES usa a norma euclidiana dos
vetores de proporções. Para separar esse efeito, também foram calculados
mean-L2 e central-L2 sobre os mesmos ensembles. No exemplo episódico longo
com n=550, mean-L2 piorou 8,64% na confirmação, enquanto ES melhorou.
O intervalo positivo de mean-L2 nessa confirmação não foi inteiramente
positivo nos dois lotes anteriores. Isso também não resgata o critério
principal, e a melhora do centro precisa permanecer visível.

A [checagem de fontes](source-check.md) encontrou avaliações probabilísticas
anteriores, incluindo Brier na previsão de interações por Kolic et al. e
na agregação com HK modificado por Douven et al. O próprio benchmark já
discute saídas com probabilidades diferentes. Assim, usar um score conhecido
ou mostrar uma ordenação diferente não estabelece novidade. A busca dirigida
também não certifica ausência de um antecedente para o contraste exato.

## Decisão e reprodução

Encerrar o piloto delimitado e preservar sua implementação e resultados.
O ensaio mostrou diferenças de avaliação e limites de seleção, mas não
entregou o contraste robusto previamente exigido. Ampliar agora parâmetros
ou sementes para procurar um caso positivo mudaria o objetivo desta execução.
Uma eventual nova investigação precisaria de justificativa independente e
protocolo sucessor; este relatório não elimina toda a linha probabilística.

O próximo trabalho recomendado é concluir o cruzamento de lacunas com a
síntese bibliográfica e a calibração humana pendente, antes de eleger outra
pergunta. A revisão sistemática formal e a seleção de venue continuam abertas.
Não há autorização científica implícita de uma pergunta pelo sucesso do código.

A execução está vinculada à revisão `71ae80cf313b6c467abad5eeedfa6a266e5daaa0`,
com implementação congelada no commit anterior `333938e`. O
[manifesto](run-manifest.json) registra todos os hashes, sementes, ambiente e
locais dos arquivos completos. A [receita de reprodução](reproduce.md)
permite verificar as linhas e regenerar resultados. O código usa aritmética
inteira exata para os pontos médios e as fronteiras dos bins, após um defeito
encontrado e corrigido pela [revisão da implementação](implementation-review.md).
As [afirmações submetidas](recommendation-input.md), a
[revisão dos resultados](results-review.md) e o
[registro de validação](validation.json) completam a trilha de evidência.
