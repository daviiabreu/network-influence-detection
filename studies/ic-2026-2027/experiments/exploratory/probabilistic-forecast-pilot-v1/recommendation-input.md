# Afirmações candidatas para revisão isolada

12/09/2026. Pacote de verificação, sem decisão de aceitação. Entradas:
[protocolo](protocol.md), [especificação](spec.json), [fontes](source-check.md),
[manifesto](run-manifest.json), [análise completa](analysis-input.json) e
[revisão da implementação](implementation-review.md). Os JSONL externos do
manifesto contêm todos os dados e ensembles usados nos scores.

1. Concluídos cinco lotes: dois benchmarks de 16 trajetórias, principal de 480
   com R=32, precisão de 480 com R=128 e confirmação de 480 com R=128. Principal
   e confirmação têm 960 trajetórias independentes; precisão reutiliza as
   480 trajetórias observadas do principal. Cada lote cobre 16 células; oito
   têm gerador dinâmico e oito são controles. Os três lotes analíticos duraram
   179,18 segundos somados, abaixo da projeção de 278,89 segundos.
2. Nenhuma das oito células dinâmicas satisfez o critério central em qualquer
   lote: intervalos além de 1% da perda do baseline para oracle melhor em ES
   e pior em média W1. Logo, nenhuma satisfez a exigência conjunta nos três
   lotes. Isso é ausência do sinal exigido neste piloto, não demonstração de
   que não existe divergência em outras condições ou em uma amostra maior.
3. Em DW com 150 tentativas, os três scores principais favoreceram o oracle
   em ambas as escalas amostrais nos três lotes. Na confirmação, reduções
   pontuais relativas de média W1 foram 16,14% e 23,17%, e de ES 42,28% e
   54,50%. As magnitudes de métricas diferentes não são diretamente comparáveis.
4. Na célula episódica com 150 tentativas e n=550, a confirmação mostrou ES
   21,39% menor e média W1 1,56% maior. O intervalo da diferença de média W1
   inclui zero: [-0,00199873; 0,00414172]. W1 do centro foi 11,04% menor.
   O diagnóstico mean-L2 foi 8,64% maior, com intervalo estritamente positivo,
   mas esse sinal não teve intervalo estritamente positivo nos dois lotes
   anteriores. A célula é ilustrativa; não cumpre o critério principal e não
   isola uma contribuição probabilística nova.
5. Na confirmação do controle sem atualização, a seleção por ES no treino
   escolheu DW ou DW episódico 40/120 vezes, concentradas nos horizontes curtos:
   18/30 e 14/30, contra 6/30 e 2/30 nos longos. Nenhum candidato dinâmico
   teve intervalo de diferença de ES inteiramente favorável contra o oracle
   de qualquer célula-controle em qualquer lote. No controle de drift,
   ES escolheu o kernel verdadeiro 120/120 vezes em cada lote. A escolha com
   só duas ondas de treino é frágil sob ausência de atualização; não equivale
   a um teste confiável de existência de influência.
6. As fontes confirmam antecedentes de avaliação probabilística e a própria
   motivação do benchmark. A busca dirigida não certifica novidade do
   contraste exato. O kernel reinicializa a população a cada onda, com N=50
   e amostragem multinomial; não representa uma população latente persistente
   nem a amostragem complexa do ESS. O piloto não reproduz integralmente
   Moor-Smith–Carpentras e não identifica causalidade ou parâmetros contínuos.
7. Recomendação candidata: encerrar este piloto delimitado, preservar o código
   e a evidência como exploração metodológica, e não iniciar ESS ou eleger B
   como artigo com base nesses resultados. Há diferenças de avaliação, mas
   falta o contraste robusto pré-especificado e a seleção de mecanismo tem
   erros relevantes no controle. A próxima escolha de pergunta precisa
   voltar ao cruzamento de lacunas da síntese bibliográfica, ainda pendente;
   não ampliar parâmetros ou repetições para obter um resultado positivo.

Rubrica: conferir integridade e completude dos arquivos, reconstruir as
contagens e intervalos por trajetória, verificar compartilhamento de dados
principal/precisão e independência da confirmação, recalcular scores e
regenerar casos; confrontar todas as células e controles com a regra congelada;
desafiar interpretação, afirmações de novidade e decisão sugerida. Não
interpretar revisão por agente como aceitação científica do Research Owner.
