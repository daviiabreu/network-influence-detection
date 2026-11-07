# Resultado do piloto de fragmentação

Atualização de navegação em 16/09/2026: o piloto B citado abaixo também foi
concluído. O [mapa atual dos dois pilotos](../../../research/questions/exploratory-claim-map.md)
reúne resultados, fontes e limites. O texto seguinte preserva a conclusão
registrada ao término de A.

O piloto foi executado. **A recomendação é preservar o achado como nota de
reprodutibilidade e encerrar a expansão desta rodada de A.** Os resultados
ainda não sustentam escolher essa direção como tema principal da IC. A próxima
avaliação de viabilidade deve considerar a proposta B, de previsão
probabilística, antes de fixar pergunta ou venue.

Houve uma discrepância real no observador que mantém grupos antigos em memória,
em uma rede ER com condições iniciais sorteadas. Ela desapareceu no teste
pareado com tolerância menor. A regra que recalcula os componentes não mostrou
discrepâncias nas paradas observadas. Além disso, a busca encontrou um
[antecedente publicado em 2018](https://www.math.ucla.edu/~mason/papers/flora-published-2018.pdf),
seção III.B, p. 022312-6, que já combina separação entre grupos e pequena
amplitude interna. O valor científico de uma especialização desse princípio
precisa ser demonstrado além da correção de implementação.

## O que foi executado

O [protocolo](protocol.md) e a [especificação](spec.json) foram fixados antes
dos lotes. Todas as trajetórias usam DW simétrico, rede-base fixa e opiniões
iniciais uniformes em [0,1). Dois modelos de exposição e três observadores de
parada foram comparados. O código próprio fica no pacote `ic_study`; não houve
execução do código externo nem reprodução dos inputs da campanha publicada.

| Fase | Trajetórias | Certificadas | Censuradas | Finalidade |
| --- | ---: | ---: | ---: | --- |
| Benchmark | 10 | 8 | 2 | Escolher o orçamento pelo custo medido |
| Controles | 10 | 10 | 0 | Consenso em grafo completo com confiança 0,9 |
| Principal | 112 | 108 | 4 | Comparar os critérios em sete configurações de rede |
| Sensibilidade | 16 | 16 | 0 | Repetir um subconjunto com tolerância 0,001 |

O lote principal usa completos de 100 e 200 nós, redes ER com variação separada
de tamanho e grau esperado, e redes de duas comunidades com duas pontes.
As confianças são 0,1 e 0,3. Em cada célula há duas realizações de rede e duas
opiniões iniciais por rede, compartilhadas entre os modelos. Nos completos, a
topologia é determinística; as sementes distinguem as condições iniciais.
As confianças também reutilizam os mesmos inputs. Portanto, essas observações
não formam uma amostra de 112 redes independentes.

A [decisão de orçamento](budget-decision.json) aplicou a regra registrada e
fixou 100 mil tentativas por trajetória principal e de sensibilidade. As quatro
censuras principais ocorreram em redes modulares de 200 nós. Nenhuma delas
chegou a uma parada aproximada observada. Elas permanecem inconclusivas quanto
aos critérios, sem entrar como casos de fragmentação ou de ausência de falha.

## O caso que apresentou discrepância

O caso de índice 35 usa ER com 100 nós e grau esperado 9,9, confiança 0,1 e
exposição adaptativa. O observador correspondente à implementação de referência
congelou uma partição antiga; seus números não correspondiam mais aos
componentes efetivos no instante declarado como final.

| Observação | Tentativa | Grupos declarados | Componentes efetivos atuais | Separação certificada |
| --- | ---: | ---: | ---: | --- |
| Parada com partição em memória | 10.500 | 13 | 12 | Não |
| Diâmetro com componentes recalculados | 10.710 | 12 | 12 | Não |
| Diâmetro e separação por intervalos | 10.790 | 12 | 12 | Sim |

Na tentativa 10.500, o maior diâmetro dos componentes atuais era 0,011389,
acima da tolerância 0,01. Por isso, a regra textual recalculada não aceitaria
essa parada. Uma interação na aresta entre os nós 20 e 99, na tentativa 10.789,
cruzou os grupos que a partição antiga considerava separados. A classificação
final incorporou um agente isolado a um grupo de 19, que passou a ter 20;
o maior grupo permaneceu com 37 agentes.

Essa distinção delimita o achado: observou-se uma falha da lógica que retém a
partição, e não uma falha empírica da equação 31 recalculada nesse caso. O
contraexemplo analítico de quatro nós continua válido como demonstração de
possibilidade em grafos esparsos, mas não foi observado um caso equivalente de
reconexão depois da parada recalculada nas 108 paradas principais disponíveis.

No subconjunto de sensibilidade, o mesmo caso terminou com 12 grupos na
tentativa 12.270 para os três observadores. Não houve discrepância nos 16 testes
com tolerância 0,001. Isso não estabelece que reduzir a tolerância elimine o
problema em geral: o teste com memória continua sendo uma regra distinta.

## Tempos e alcance do resultado

A certificação acrescentou espera após a parada recalculada em três trajetórias:
80, 1.170 e 19.802 tentativas. As partições recalculadas desses casos permaneceram
iguais às certificadas. Espera adicional, por si, não demonstra erro da
classificação anterior; a condição suficiente pode ser conservadora.

Em um par ER de 200 nós, com confiança 0,3, a exposição adaptativa parecia
967 tentativas mais rápida sob a parada aproximada e ficou 203 mais lenta sob
a certificada. A mediana das diferenças pareadas daquela célula permaneceu
positiva: passou de 969 para 1.083,5 tentativas, com quatro pares. Logo, esse
caso individual não sustenta uma inversão geral do efeito da exposição.
Os demais contrastes e contagens por célula estão no
[registro de análise](analysis-input.json); comparações de tempos sem ambos
os membros certificados são identificadas como incompletas.

Não houve falhas numéricas registradas. O maior desvio absoluto da média foi
4,44×10⁻¹⁶. Os dez controles produziram consenso certificado. Os quatro lotes
consumiram aproximadamente 27,1 segundos neste ambiente, excluindo pesquisa,
implementação, testes e revisão. O tempo de uma reprodução futura pode variar.

## Decisão e próximos passos

O piloto encontrou um problema verificável fora do exemplo construído, mas
seu alcance foi estreito: um agrupamento mantido em memória, resolvido nesse
subconjunto por tolerância menor, sem falha observada do critério recalculado.
Com a prioridade genérica do certificado já contrariada por um antecedente,
a evidência disponível não justifica investir agora numa campanha ampla de A
como promessa de artigo principal.

Preservar esta reprodução permite retomá-la se a síntese encontrar uma lacuna
mais específica ou uma aplicação substantiva. O próximo investimento proposto
é avaliar o desenho sintético de B, com alvo probabilístico e comparação justa
dos modelos, sem escolher antecipadamente uma venue. Essa recomendação não
transforma B em pergunta final nem executa sua campanha. A revisão sistemática
formal também continua dependente das etapas registradas em
[READINESS](../../../research/literature/READINESS.md).

## Código, dados e verificação

A revisão Git executada é `a394f28e66868b0c5d2c9f6d032b5394bb354073`.
O [manifesto](run-manifest.json) registra cada lote com caminho local,
SHA-256, tamanho, ambiente e parâmetros; os JSONL completos ficam no
armazenamento externo por conteúdo. O [registro de autorização](authorization.json)
vincula a instrução “pode ir” ao escopo exploratório.

A [revisão da implementação](implementation-review.md) encontrou dois defeitos
antes das campanhas — estabilidade das sementes após serialização e um extremo
de arredondamento no sorteio —, corrigidos e rechecados. Os 23 testes do estudo,
lint, tipos, matriz `just quality` e instalação dos dois pacotes passaram.
O [roteiro de reprodução](reproduce.md) permite conferir hashes, resumos e o caso
observado. Os dois casos centrais, principal e de sensibilidade, foram
regenerados com todos os campos científicos idênticos. As limitações e números
foram conferidos na [revisão dos resultados](results-review.md), que também
reproduziu os dois casos e verificou as partições por um cálculo independente.
O [registro de validação](validation.json) reúne hashes e verificações da entrega.
