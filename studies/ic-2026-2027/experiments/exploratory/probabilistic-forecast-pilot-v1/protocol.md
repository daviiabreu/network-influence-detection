# Piloto sintético de previsão de histogramas

12/09/2026. Execução exploratória da proposta B, autorizada por “go on” após
a recomendação do piloto anterior. A [especificação](spec.json) será congelada
antes da execução. O [memo de origem](../../../research/questions/exploration/2026-09-12/empirical-evidence.md)
define o contraste; este documento fixa escolhas operacionais e limites.

## Alvo e mecanismo

Prever a lei do próximo vetor de contagens em onze categorias ordenadas. Cada
onda começa no mesmo histograma observado para todos os modelos. Amostrar
N=50 agentes dessa distribuição, aplicar o mecanismo e amostrar com reposição
55 ou 550 respostas da população resultante. Categorias representam k/10;
fronteiras (k+0,5)/10 pertencem à categoria maior. Começar todas as trajetórias
no histograma uniforme exato. Usar 25 ou 150 tentativas de interação por onda.

O gerador usa exatamente esse kernel condicional de reinicialização. Assim,
o oracle conhece o kernel verdadeiro, mas não a realização latente, os sorteios
ou o futuro. Esse fechamento é deliberado: evita atribuir ao score a falha de
um oracle que na verdade recebeu um problema de inferência diferente. Também
limita a validade externa. Reinicializar uma população a cada onda NÃO representa
o acompanhamento de uma população latente fixa. O controle sem atualização
não tem influência nem drift, mas seus histogramas ainda variam por duas
camadas de amostragem. Não será chamado de evidência sobre uma população real
constante ou sobre o desenho amostral do ESS.

Deffuant usa pares distintos uniformes no grafo completo, confiança estrita
c=0,35 e atualização simétrica com mu=0,5. A implementação direta evita
materializar o grafo completo; o núcleo será confrontado com o modelo já
testado no repositório. Para cumprir os empates sem arredondamento, representar
opiniões por inteiros em unidades de 1/(10·2^A), sendo A o máximo de tentativas.
Entradas k/10 e mu=0,5 garantem divisibilidade até A médias; comparações de
confiança e discretização são racionais exatas. O drift de um décimo também
é exato. Não se promete a mesma trajetória numérica de uma implementação
com ponto flutuante nas fronteiras. A variante `pulsed_dw` sorteia, uma vez por onda, se
o intervalo é ativo com probabilidade 0,5; quando inativo, não atualiza opiniões.
Isso produz uma fonte explícita de variabilidade de processo além dos pares
aleatórios. É uma variante sintética de atividade episódica, sem alegar que
reproduz Duggins ou que descreve empiricamente participação social.

Os outros candidatos são ausência de atualização e drift uniforme por onda
de -0,1 ou +0,1, truncado em [0,1]. O drift é definido por onda e não por
tentativa de interação. Não há ruído gaussiano. Os geradores são ausência de
atualização, DW, DW episódico e drift positivo. O produto com dois horizontes e
duas amostras forma 16 células. Cada lote contém 30 trajetórias independentes
por célula, quatro transições por trajetória, duas de treino e duas de teste.
A unidade de incerteza é a trajetória inteira, não cada onda ou entrevistado.

## Avaliação e ajuste separados

Gerar um único ensemble por modelo/onda e calcular as três perdas sobre ele:
média de W1 por realização; W1 do vetor médio; energy score com norma euclidiana
e estimador U fora da diagonal. W1 usa distância 0,1 entre categorias. O energy
score estima uma propriedade da lei e é não negativo em aritmética exata
pela desigualdade triangular. Não truncar arredondamentos silenciosamente;
valores abaixo de -1e-12 indicam falha numérica a investigar. W1 do centro é
um estimador plug-in e pode mudar com R. Scores
avaliam alvos distintos; nunca comparar suas magnitudes diretamente.

Como diagnóstico da geometria, registrar também média da distância euclidiana
por realização e distância euclidiana do centro, com a mesma seleção no treino.
Esses dois controles adicionais não substituem os três contrastes principais.
A comparação mean-L2 versus energy mantém a geometria e isola a correção de
dispersão. O [levantamento de fontes](source-check.md) explica por que nem
avaliação probabilística genérica nem comparação de métricas são novidade.

Primeiro, comparar cada candidato fixo e o oracle com o baseline, nos mesmos
casos. Separadamente, cada perda escolhe o menor risco médio no treino entre
os mesmos cinco candidatos, com as mesmas previsões e orçamento. Desempate
segue a ordem explícita da especificação. Congelar a escolha antes das duas
ondas de teste. Isso inclui estimar o sinal do drift somente pelo treino,
mas é uma busca discreta curta, não uma reprodução de TPE nem recuperação
contínua de parâmetros. A confiança e mu são conhecidos neste ensaio. Relatar
frequências de escolha, também nos controles, e risco do modelo escolhido.
Dois pontos de treino limitam a capacidade de seleção; não tirar conclusões
gerais de identificabilidade se ela falhar.

Sementes são hashes SHA256 de identificadores explícitos: lote, célula,
trajetória, onda, modelo e membro. Inicialização, eventos e observação recebem
subfluxos distintos. Saídas observadas são independentes dos ensembles. O lote
de precisão reutiliza somente os dados do principal, com ensembles novos; a
confirmação recebe dados e ensembles novos. Alterar a ordem das chaves de JSON
não altera entradas ou sorteios. Guardar todos os ensembles permite recalcular
scores sem simular novamente.

## Precisão, custo e decisão

Dois benchmarks de 16 trajetórias, R=32 e 64, têm sementes exclusivas. Não
entram na análise. O teto é vinte minutos projetados de execução dos três
lotes, com margem de 50%. Medir separadamente geração de ensembles e cálculo
de scores. Usar o maior tempo de geração normalizado por R e de scores
normalizado por R ao quadrado, mais o maior restante de overhead; a fórmula
está na especificação. Escolher R=128 para precisão e
confirmação se couber; senão R=64; se nenhum couber, registrar limitação de
custo. O principal usa R=32. Essa escolha usa somente tempo, nunca sinais
dos scores. Não aumentar amostra, trocar parâmetros ou selecionar células
depois de olhar os resultados para produzir significância.

Usar diferenças pareadas de perda por trajetória, médias, erro padrão e
intervalos t pontuais de 95% (29 graus de liberdade). Não são intervalos
simultâneos nem comprovação confirmatória após seleção de células. A menor
diferença operacional de interesse é 1% da perda média do baseline dentro
de cada score. O número é uma tolerância exploratória explícita, sem alegar
que equivale a relevância substantiva em dados reais.

O sinal buscado é oracle dinâmico melhor que o baseline em energy score e
pior em média W1, com os intervalos além da tolerância nos dois sentidos.
Exigir a mesma célula e o mesmo sentido no principal, na repetição de precisão
e na confirmação independente. Verificar se o W1 do centro já explica a
divergência: nesse caso restringir qualquer argumento à agregação, sem atribuir
o resultado apenas à avaliação probabilística. Relatar todas as células,
inclusive sinais fracos e reversões, e a sensibilidade pareada ao aumento de R
e ao novo ensemble.

Nos controles, registrar frequência de seleção indevida de dinâmica e risco
fora da amostra. Se houver vantagem replicada de dinâmica contra o oracle
nos controles sem atualização ou drift, revisar o procedimento antes de
prosseguir. Uma escolha errada com treino curto, isoladamente, não prova
vazamento: separar erro de seleção de violação da distribuição esperada.
Se o efeito central não replicar ou só demonstrar uma propriedade conhecida
do score num caso construído, não avançar automaticamente para ESS nem
afirmar uma contribuição publicável. Um resultado negativo encerra este
piloto delimitado, sem procurar novos parâmetros para revertê-lo.

## Evidência e limites

Testes analíticos, verificação de isolamento de sementes/dados e revisão
independente precedem os lotes. Guardar código, lock, ambiente, especificação,
sementes e dados completos por hash. Saídas externas usam criação exclusiva;
ausência do rodapé `completed` marca interrupção. Corrigir por sucessor.

Este piloto não reproduz integralmente o benchmark publicado, não mede ESS,
não identifica influência causal e não seleciona a pergunta definitiva da IC.
A amostra 550 não elimina incerteza de população finita N=50; ambas as camadas
são mantidas e reportadas. Análise de uma população persistente, outros N,
ou ajuste mais amplo são trabalho posterior, condicionado ao valor deste
resultado. A revisão sistemática e a escolha de venue permanecem separadas.
