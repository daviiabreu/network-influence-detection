# Resposta à revisão independente

Registro de 12/09/2026. A revisão inicial e sua entrada foram preservadas. O
[pacote original](review-input.md) tem SHA-256
`a7d37c2ae60b93f8d57d7eda391e35ee0b638d6b517c2ed448443d194315d939`;
o [relatório independente](independent-review.md) registra os achados A1 e A2.
Esta resposta corrige a preparação exploratória, sem selecionar pergunta,
registrar protocolo experimental ou declarar aceite científico.

## A1 — Alvo e avaliação probabilística

A especificação corrigida é a lei
`Q_theta(H_(t+1) | H_t, n_t, n_(t+1), delta_t)` do histograma observado na
próxima onda. Onze categorias `0,...,10` usam representantes `k/10`; opiniões
contínuas entram no representante mais próximo, com empate para o maior.
Cada previsão de um passo parte do mesmo histograma anterior observado,
inclusive no trecho de validação, e usa o mesmo tamanho amostral futuro.

A inicialização proposta amostra `N` agentes de `H_t`, aplica a dinâmica por
`delta_t` e amostra o próximo histograma por uma multinomial de tamanho
`n_(t+1)`. O baseline constante usa a mesma inicialização e observação, com
zero atualizações. O drift só é ajustado no treino; o controle de parâmetros
geradores conhecidos recebe a mesma observação, sem estados latentes
privilegiados. Trata-se de um controle sintético, sem validar a observação ESS.

Para `R>=2` réplicas independentes, o energy score usa a norma euclidiana,
expoente 1 e o estimador
`mean_r ||X_r-y||_2 - sum_(r!=s) ||X_r-X_s||_2 / (2*R*(R-1))`.
As alternativas são a média de W1 por realização e W1 da média dos vetores,
sempre com o mesmo alvo observado. Comparam-se ordenações e diferenças
pareadas dentro de cada score, sem comparar suas magnitudes diretamente.
A incerteza Monte Carlo e as réplicas externas de avaliação permanecem
explícitas. Não se atribui propriedade estrita a uma versão de energia baseada
em W1. Parâmetros, números de réplicas e partições ainda serão fixados antes
da execução.

Essas definições estão no [memo empírico](empirical-evidence.md), seção
“Especificação comum para o contraste sintético”, e resumidas no
[relatório principal](README.md), proposta B. A alteração não torna uma
métrica anterior errada nem demonstra vantagem preditiva.

## A2 — Hipótese da garantia para grafos completos

A descrição corrigida declara que o teorema 4 identifica os grupos finais em
grafo completo sob `tol<c`; o uso numérico em outros grafos não recebe essa
garantia. O relatório principal passou a explicitar ambas as hipóteses. O
microcaso preserva `tol=0,01<c=0,1`, sem alterar seus parâmetros ou resultados.

## Consistência da regra de atualização

O revisor encontrou uma inconsistência de sinal nas equações 1 e 3 do HTML e
no texto extraído do PDF v2 do trabalho DW. O código fixado implementa a regra
simétrica convexa. O relatório principal e o memo mecanístico agora registram
explicitamente essa escolha para o contraexemplo e a futura reprodução. Isso
não foi interpretado como execução incorreta dos experimentos publicados.

A entrada da revisão não foi reescrita para remover os achados. A correção de
especificação e a validação matemática não medem frequência do problema,
novidade bibliográfica ou impacto experimental.
