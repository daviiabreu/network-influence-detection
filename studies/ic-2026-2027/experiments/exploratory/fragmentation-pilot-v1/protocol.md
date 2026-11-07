# Piloto exploratório: critérios de parada em DW

Versão 1, 12/09/2026. O usuário autorizou o piloto proposto com “pode ir”.
Este plano delimita a exploração da [proposta A](../../../research/questions/exploration/2026-09-12/README.md),
sem selecionar a pergunta final da IC, aceitar a síntese da revisão ou registrar
validação confirmatória. As escolhas operacionais e sementes estão em
[spec.json](spec.json), a congelar por hash e revisão Git antes das execuções.

## Modelo e fontes

Usar DW simétrico, opiniões escalares, confiança estrita e rede-base fixa.
Comparar seleção uniforme com probabilidades proporcionais a pesos adaptativos.
O [levantamento primário](source-check.md) registra o modelo de 2026, seu código
fixado e um antecedente de 2018 que já exige separação entre grupos.
Portanto, a separação por intervalos não será apresentada como ideia inédita.

A implementação local segue a atualização convexa simétrica do código, usando
as duas opiniões anteriores ao evento. Usa árvore de somas para amostragem,
sem nova dependência. A distribuição é proporcional aos pesos, mas a ordem de
soma em ponto flutuante difere do código externo; não se promete trajetória
idêntica por semente. Nenhum chamador da campanha publicada foi reproduzido.

Três observadores acompanham cada trajetória sem interrompê-la nas paradas
aproximadas: os testes com memória da implementação de referência, a equação
31 com componentes efetivos recalculados e o diâmetro combinado à separação
por intervalos em todas as arestas-base entre componentes. A certificação
termina a trajetória. Um limite de eventos produz censura, nunca uma
classificação automática como fragmentação. Não há observação em t=0.

O terceiro critério usa diâmetro menor que a tolerância, que é menor que c, e
separação pelo menos c+1e-12. Ele garante ausência de primeira interação externa
sob convexidade, confiança e topologia fixas. Não distingue valores-limite
coincidentes de componentes desconectados, nem promete tempo de convergência.
A margem é uma precaução numérica, sem alegar aritmética intervalar formal.

## Amostras e custo

O benchmark tem dez trajetórias com sementes próprias e limite de 50 mil
tentativas. Seu único papel é medir custo. A regra registrada escolhe entre
500 mil, 100 mil e 50 mil tentativas para o lote seguinte, usando o pior
desempenho medido e uma projeção conservadora de vinte minutos. Resultados do
benchmark não entram na frequência principal nem orientam escolha de parâmetros.

O lote principal tem 112 trajetórias: sete configurações de rede, duas
confianças, duas realizações de rede, duas opiniões iniciais por rede e dois
modelos. Completos usam N=100 e 200; ER separa variação de N a grau esperado
constante de aumento de grau com N constante. Redes modulares têm duas partes
e duas pontes, com grau interno esperado constante. A conectividade inicial é
registrada, sem descartar ou ressorteiar redes desconectadas. Cada opinião
inicial é uniforme em [0,1), escolha explícita deste ensaio reduzido.

Dez controles adicionais usam completo N=100, c=0,9 e cinco opiniões iniciais
por modelo, esperando consenso qualitativo sob grande confiança. Uma análise
de sensibilidade pré-definida repete dezesseis trajetórias de ER/modular N=100
com os mesmos inputs do lote principal e tolerância dez vezes menor. Ela serve
para comparação pareada de tolerância e não aumenta o tamanho amostral principal.

## Medições e critérios

Guardar a primeira parada de cada observador, suas opiniões e partição; a
primeira interação receptiva posterior entre grupos declarados distintos;
partição e opiniões no fim; pesos finais; eventos receptivos, mudanças
numéricas de opinião, tentativas, custo e desvio da média. Registrar interações
entre grupos evita perder uma invalidade transitória que desapareça no fim.

Frequências serão descritivas por configuração e modelo. Não agregar as quatro
trajetórias de uma célula como quatro redes independentes. Execuções censuradas
sem interação posterior observada são inconclusivas. Tempos serão reportados
com os limites de observação, sem médias que descartem silenciosamente censura.
Comparações dos critérios são pareadas dentro da mesma trajetória. Comparações
dos modelos compartilham rede, opiniões e uniformes do RNG, mas os pesos podem
produzir sequências de arestas diferentes.

Antes do lote: testes analíticos de confiança estrita, conservação da média,
microcaso de quatro nós, certificado, amostragem e reprodução por semente;
revisão isolada da implementação e especificação. Falha numérica interrompe a
trajetória, com status próprio. Resultados dependem de revisão do código exato,
configuração e ambiente registrados.

Continuar além do piloto exige controles válidos e um efeito fora do caso
construído que altere uma conclusão interpretável ou identifique uma região de
confiabilidade útil. Ausência de efeito neste lote pequeno não prova correção
geral nem descarta efeitos raros. Não ampliar configurações para obter resultado
positivo. Um antecedente que já responda à questão específica também pode
encerrar a linha. O próximo relatório deve recomendar prosseguir, restringir
ou abandonar a proposta com base no que foi observado.

## Proveniência

O executor grava JSONL com entrada completa, revisão Git, hashes do código,
lock, especificação, ambiente, sementes e uma linha por trajetória. Arquivos
novos usam criação exclusiva; dados concluídos ficam fora do Git e recebem
hash de conteúdo. Metadados, análise, revisão e hashes são versionados aqui.
Uma nova execução recebe identidade distinta; correções não reescrevem
resultados antigos. Se uma execução for interrompida, a ausência do registro
final `completed` impede tratá-la como lote completo.
